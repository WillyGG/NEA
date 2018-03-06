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

    def train(self, sess):
        train_iterations = self.parameters["train_steps"]
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        hidden_size = self.parameters["hidden_size"]

        exp_buffer = experience_buffer()
        self.sess = sess
        self.NN.Target_Network.updateTarget(sess)

        for game_num in range(train_iterations):
            game_state = self.get_train_game_state()
            episode_buffer = []
            self.NN.rnn_state_reset() # Reset the recurrent layer's hidden state
            action = None
            # step in game, get reward and new state
            while self.blackjack.continue_game:  # change this to just take a move when it's the AIs turn
                current_agent = self.blackjack.get_current_player()
                all_hands = self.blackjack.get_all_hands()
                if current_agent.id != self.NN.ID:
                    move = self.group_agents[current_agent.id].get_next_move(all_hands)
                    self.process_action(move)
                    new_game_state = self.get_train_game_state() # TODO FIGURE OUT WHAT KIND OF STATE YOU NEED
                else:  # is the nn agent's turn
                    # put this in its own method?
                    exploring = (game_num <= explore_steps)
                    action = self.NN.get_move(exploring) ## TODO FINISH THIS LATER
                    self.process_action(action)
                    new_game_state = self.get_game_train_state()
                    new_rnn_state = self.NN.get_new_rnn_state()
                    reward = self.gen_step_reward()

                    if reward == 0:
                        print("0 gamestate",game_state)
                        print("0 agent hand val", game_state[0]*30)
                        print("0 best hand val", game_state[1]*30)
                        print("0 new agent", new_game_state[0]*30)
                        print("0 action", action)

                    action = Moves.convert_to_bool(action)
                    episode_buffer.append(np.reshape(np.array([game_state, action, reward,
                                                               new_game_state, self.blackjack.continue_game]),
                                                     [1, 5]))
                    if game_num % update_frequency == 0 and not exploring:
                        self.NN.update_networks()
                    self.NN.rnn_state = new_rnn_state  # UPDATE RNN CELL STATE

                game_state = new_game_state

                # PROCESS END OF GAME
                # GET THE END OF GAME REWARD
                self.end_game()
                reward = self.gen_step_reward()

                # decide if you want to append this
                if action is None:
                    print("NO MOVES EXECUTED")
                action = Moves.convert_to_bool(action)
                episode_buffer.append(np.reshape(np.array([game_state, action, reward,
                                                           new_game_state, self.blackjack.continue_game]),
                                                 [1, 5]))
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