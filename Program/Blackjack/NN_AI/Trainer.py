import sys,os
sys.path.append(os.path.realpath(".."))
import Blackjack
from Moves import Moves
from CC_AI import CC_AI
from experience_buffer import experience_buffer
from datetime import datetime
import numpy as np
import tensorflow as tf

class Trainer:
    def __init__(self, nn_inst, training_params=None, training_type="dealer_only"):
        self.NN = nn_inst
        self.blackjack = self.init_blackjack(training_type)
        self.group_agents = {}
        # insert some default params
        if training_params is None:
            self.parameters = {}

    # initialises each hand and blackjack instance
    def init_blackjack(self, training_type):
        nn_hand = Blackjack.Hand(self.NN.id)
        self.NN.Hand = nn_hand
        dealer_hand = Blackjack.Dealer_Hand()
        hands = {
            self.NN.ID: nn_hand,
            "dealer": dealer_hand
        }

        if training_type == "group_cc_ai":
            cc_ai_hand = Blackjack.Hand("cc_ai")
            self.group_agents["CC_AI"] = CC_AI(hand=cc_ai_hand)
            hands["CC_AI"] = cc_ai_hand

        return Blackjack.Blackjack(hands)


    # TODO DECIDE HOW MANY OF THESE PARAMS YOU ACTUALLY WANT TO PASS
    def process_NN_agent_action(self, game_num, all_hands, game_state, episode_buffer):
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        # put this in its own method?
        exploring = (game_num <= explore_steps)
        action = self.NN.get_move(all_hands, exploring)
        self.process_action(action)
        new_game_state = self.get_train_game_state()
        new_rnn_state = self.NN.get_new_rnn_state()
        reward = self.gen_step_reward(action)
        action = Moves.convert_to_bool(action)
        # push action to buffer, for sampling later
        episode_buffer.append(np.reshape(np.array([game_state, action, reward,
                                                   new_game_state, self.blackjack.continue_game]), [1, 5]))
        if game_num % update_frequency == 0 and not exploring:
            self.NN.update_networks()
        self.NN.rnn_state = new_rnn_state  # UPDATE RNN CELL STATE
        return action, new_game_state

    def train(self, sess):
        train_iterations = self.parameters["train_steps"]
        hidden_size = self.parameters["hidden_size"]
        exp_buffer = experience_buffer()
        self.sess = sess
        self.NN.Target_Network.updateTarget(sess)

        for game_num in range(train_iterations):
            game_state = self.get_train_game_state()
            episode_buffer = []
            action = None
            # step in game, get reward and new state
            while self.blackjack.continue_game:  # change this to just take a move when it's the AIs turn
                current_agent = self.blackjack.get_current_player()
                all_hands = self.blackjack.get_all_hands()
                if current_agent.id != self.NN.ID:
                    move = self.group_agents[current_agent.id].get_next_move(all_hands)
                    self.process_action(move)
                    new_game_state = self.get_train_game_state()  # TODO DECIDE IF YOU NEED A DIFFERENT STATE COPARED TO OTHER AGENT
                else:  # is the nn agent's turn
                    action, new_game_state = self.process_NN_agent_action(game_num, all_hands, game_state, episode_buffer)
                game_state = new_game_state # update the game state
                # PROCESS END OF GAME
                # GET THE END OF GAME REWARD
                self.end_game()
                reward = self.gen_step_reward(action)
                if action is None:
                    print("NO MOVES EXECUTED")
                # decide if you want to append this
                action = Moves.convert_to_bool(action)
                episode_buffer.append(np.reshape(np.array([game_state, action, reward,
                                                           new_game_state, self.blackjack.continue_game]), [1, 5]))
                # Add the episode to the experience buffer
                bufferArray = np.array(episode_buffer)
                episodeBuffer = list(zip(bufferArray))
                exp_buffer.add(episodeBuffer)
                self.reset()
            self.NN.save_model()

    def get_train_game_state(self):
        toReturn = []  # [agent_hand_val_normalised, best_player_hand_val_normalised, chances (in order)]
        AI_and_best_hand = self.NN.get_state() # should return [agent_hand_val, best_player_val]
        chances = self.NN.get_chances(AI_and_best_hand)
        for hand in AI_and_best_hand:  # adds the hand to the return array
            hand_value_normalised = hand.get_value() * self.parameters["hand_val_norm_const"]
            toReturn.append(hand_value_normalised)
        for key in sorted(chances):  # sorted so that it is returned in the same order every time
            toReturn.append(chances[key])
        return toReturn

    def process_action(self, action):
        if action == Moves.HIT:
            # check if current turn (or check in the training mainloop)
            # hit
            self.blackjack.hit()
        elif action == Moves.STAND: # defensive programming?
            self.blackjack.stand()
        else:
            print("invalid move")

    # generate reward based on how close to 21
    # loss if bust
    # extra reward if win
    # normalise all rewards
    # TODO SORT OUT THE REWARD SYSTEM
    def gen_step_reward(self, move):
        nn_hand = self.blackjack.players["nn"]
        hand_val_norm_const = self.parameters["hand_val_norm_const"]

        agent_value = nn_hand.get_value()
        current_winners = self.blackjack.compare_hands()
        win_value = (agent_value + 1) * hand_val_norm_const
        loss_value = (-agent_value - 1) * hand_val_norm_const
        normal_reward = agent_value * hand_val_norm_const
        scaled_value = 0
        # Win and loss rewards regardless of last action - if absolute winner/loser
        if self.blackjack.check_game_over():
            if nn_hand.id in current_winners:
                scaled_value = win_value
            else:
                scaled_value = loss_value
        # rewards for hit and cost for bust
        elif move == Moves.HIT:
            if nn_hand.bust:
                scaled_value = loss_value
            else:
                scaled_value = normal_reward
        # rewards for standing
        elif move == Moves.STAND:
            if nn_hand.id in current_winners:
                scaled_value = normal_reward
            else:
                scaled_value = loss_value
        elif nn_hand.bust:
            scaled_value = loss_value
        return scaled_value

    # decrement cc's
    # end the blackjack game
    def end_game(self):
        self.blackjack.end_game()
        new_cards = self.blackjack.new_cards
        for key, agent in self.group_agents.items():
            if "Card Counter" in agent.type:
                agent.decrement_CC(new_cards)

    # reset rnn state
    # reset blackjack
    def reset(self):
        self.NN.rnn_state_reset()  # Reset the recurrent layer's hidden state
        self.blackjack.reset()