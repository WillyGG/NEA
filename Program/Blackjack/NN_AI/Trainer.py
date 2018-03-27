import sys,os
sys.path.append(os.path.realpath(".."))
sys.path.append(os.path.realpath("../DB"))
import Blackjack
from DB_Wrapper import DB_Wrapper
from Moves import Moves
from CC_AI import CC_AI
from experience_buffer import experience_buffer
from datetime import datetime
import numpy as np
import tensorflow as tf

# todo split into composed classes => fresh train and pre batch train
class Trainer:
    def __init__(self, nn_inst, training_params=None):
        self.NN = nn_inst
        self.exp_buffer = experience_buffer()
        self.parameters = training_params
        # todo insert some default params
        if training_params is None:
            self.parameters = {}

    def gen_step_reward(self, nn_hand_val_after, move, nn_winning):
        agent_value = nn_hand_val_after
        hand_val_norm_const = self.parameters["hand_val_norm_const"]
        win_value = (agent_value + 1) * hand_val_norm_const # change this so that it is paramaterised
        loss_value = (-agent_value - 1) * hand_val_norm_const
        normal_reward = agent_value * hand_val_norm_const
        scaled_value = 0
        if move == Moves.HIT:
            if agent_value > 21:
                scaled_value = loss_value
            else:
                scaled_value = normal_reward
        # rewards for standing
        elif move == Moves.STAND:
            if nn_winning:
                scaled_value = normal_reward
            else:
                scaled_value = loss_value
        return scaled_value

    def gen_end_reward(self, agent_value, nn_in_winners):
        hand_val_norm_const = self.parameters["hand_val_norm_const"]
        win_value = (agent_value + 1) * hand_val_norm_const
        loss_value = (-agent_value - 1) * hand_val_norm_const
        scaled_value = 0
        if nn_in_winners:
            scaled_value = win_value
        else:
            scaled_value = loss_value
        return scaled_value

# training via internal blackjack environment of class
# class defines and runs blackjack game and tehn updates the nn based on its actions
class Init_Trainer(Trainer):
    def __init__(self, nn_inst, training_params=None, training_type="dealer_only"):
        super().__init__(nn_inst, training_params)
        self.group_agents = {}
        self.blackjack = self.init_blackjack(training_type)

    def init_blackjack(self, training_type):
        nn_hand = Blackjack.Hand(self.NN.ID)
        self.NN.Hand = nn_hand
        dealer_hand = Blackjack.Dealer_Hand()
        hands = {
            self.NN.ID: nn_hand,
            "dealer": dealer_hand
        }
        if training_type == "group_cc_ai":
            self.init_CC_AI(hands)
        elif training_type == "group_simple":
            self.init_Simple_AI(hands)
        elif training_type == "group_all":
            self.init_CC_AI(hands)
            self.init_Simple_AI(hands)

        return Blackjack.Blackjack(hands)

    def init_CC_AI(self, hands):
        cc_ai_hand = Blackjack.Hand("cc_ai")
        self.group_agents["cc_ai"] = CC_AI(hand=cc_ai_hand)
        hands["cc_ai"] = cc_ai_hand

    def init_Simple_AI(self, hands):
        cc_ai_hand = Blackjack.Hand("simple")
        self.group_agents["simple"] = CC_AI(hand=cc_ai_hand)
        hands["simple"] = cc_ai_hand

        # TODO DECIDE HOW MANY OF THESE PARAMS YOU ACTUALLY WANT TO PASS

    def process_NN_agent_action(self, game_num, all_hands, game_state, episode_buffer, exp_buffer):
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        exploring = (game_num <= explore_steps)
        action = self.NN.get_move(all_hands, exploring)
        self.process_action(action)
        new_game_state = self.get_train_game_state(all_hands)
        reward = self.gen_reward(action)
        action = Moves.convert_to_bit(action)
        # push action to buffer, for sampling later
        episode_buffer.append(np.reshape(np.array([game_state, action, reward,
                                                   new_game_state, self.blackjack.continue_game]), [1, 5]))
        if game_num % update_frequency == 0 and not exploring:
            self.NN.update_networks(exp_buffer)
        return action, new_game_state

    def train(self, sess):
        train_iterations = self.parameters["train_steps"]

        self.sess = sess
        self.NN.Target_Network.updateTarget(sess)

        for game_num in range(train_iterations):
            print(game_num)
            all_hands = self.blackjack.get_all_hands()
            episode_buffer = []
            game_state = self.get_train_game_state(all_hands)
            action = None
            new_game_state = None
            # step in game, get reward and new state
            while self.blackjack.continue_game:  # change this to just take a move when it's the AIs turn
                current_agent = self.blackjack.get_current_player()
                # print(current_agent.id)
                if current_agent.id != self.NN.ID:
                    move = self.group_agents[current_agent.id].get_move(all_hands)
                    self.process_action(move)
                    new_game_state = self.get_train_game_state(
                        all_hands)  # TODO DECIDE IF YOU NEED A DIFFERENT STATE COPARED TO OTHER AGENT
                else:  # is the nn agent's turn
                    # getting state and chances is execute twice, for a single state, maybe simplify this so that you can pass it here
                    action, new_game_state = self.process_NN_agent_action(game_num, all_hands, game_state,
                                                                          episode_buffer, self.exp_buffer)
                game_state = new_game_state  # update the game state
            # PROCESS END OF GAME
            # GET THE END OF GAME REWARD
            self.end_game()
            reward = self.gen_reward()
            if action is None:
                print("NO MOVES EXECUTED")
            # decide if you want to append this
            action = Moves.convert_to_bit(action)
            episode_buffer.append(np.reshape(np.array([game_state, action, reward,
                                                       new_game_state, self.blackjack.continue_game]), [1, 5]))
            # Add the episode to the experience buffer
            bufferArray = np.array(episode_buffer)
            episodeBuffer = list(zip(bufferArray))
            self.exp_buffer.add(episodeBuffer)
            self.reset()
        self.NN.save_model()

    def get_train_game_state(self, all_hands):
        # [agent_hand_val_normalised, best_player_hand_val_normalised, chances (in order of key )]
        AI_and_best_hand = self.NN.get_state(all_hands)  # should return [agent_hand_val, best_player_val]
        chances = self.NN.get_chances(AI_and_best_hand)
        toReturn = self.NN.get_features(chances, AI_and_best_hand)
        return toReturn

    def process_action(self, action):
        if action == Moves.HIT:
            # check if current turn (or check in the training mainloop)
            # hit
            self.blackjack.hit()
        elif action == Moves.STAND:  # defensive programming?
            self.blackjack.stand()
        else:
            print("invalid move")

    # generate reward based on how close to 21
    # loss if bust
    # extra reward if win
    # normalise all rewards
    # TODO SORT OUT THE REWARD SYSTEM
    # nn_hand_val_after, move, nn_winning
    def gen_reward(self, move=None):
        nn_hand = self.blackjack.players["nn"]
        agent_value = nn_hand.get_value()
        current_winners = self.blackjack.compare_hands()
        scaled_value = 0
        # Win and loss rewards regardless of last action - if absolute winner/loser
        if move is None:  # end of game rewards
            if self.blackjack.check_game_over():
                nn_is_winner = nn_hand.id in current_winners
                scaled_value = super().gen_end_reward(agent_value, nn_is_winner)
        # rewards for hit and cost for bust
        else:
            nn_winning = nn_hand.id in current_winners
            scaled_value = super().gen_step_reward(agent_value, move, nn_winning)
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


# training via querying the database
class Batch_Trainer(Trainer):
    def __init__(self, nn_inst, training_params=None):
        super().__init__(nn_inst, training_params)
        self.db_wrapper = DB_Wrapper()

    # gets all the games which have not been used for training yet
    def pop_new_games(self):
        # cross table param sql
        # gets all the cc data for the moves the nn took part in
        get_q = """
                SELECT Card_Counter_Record.*
                FROM Card_Counter_Record, Moves
                WHERE Moves.player_id='{0}' AND Card_Counter_Record.trained=0 AND Moves.game_id=Card_Counter_Record.game_id
                      AND Moves.turn_num=Card_Counter_Record.turn_num;
                """.format(self.NN.ID)

        update_popped_q = """
                           UPDATE Card_Counter_Record
                           SET trained=1
                           WHERE trained=0;
                           """
        new_games = self.db_wrapper.execute_queries(get_q, get_result=True)
        self.db_wrapper.execute_queries(update_popped_q)
        return new_games

    # converts a single record to an array of features, train ready
    # pass in a query result where everything from card counter record has been fetched
    def convert_cc_rec_to_features(self, record):
        # game_state => [nn_hand_val, best_hand_val, ]
        game_id = record[0]
        turn_num = record[1]
        hand_val_norm_const = self.parameters["hand_val_norm_const"]
        # get best hand and best ai hand
        q = """
            SELECT hand_val_before, next_best_val
            FROM Moves
            WHERE game_id={0} AND turn_num={1};
            """.format(game_id, turn_num)
        hand_val_res = self.db_wrapper.execute_queries(q, get_result=True)[0]

        # convert record to part of the features
        chances = {
            "bust" : record[2],
            "blackjack": record[3],
            "exceedWinningPlayer": record[4],
            "alreadyExceedingWinningPlayer": record[5]
        }
        return self.NN.get_features(chances, hand_val_res)

    # todo complete this!!
    def convert_new_games(self):
        #episode_buffer.append(np.reshape(np.array([game_state, action, reward,
        #                                           new_game_state, self.blackjack.continue_game]), [1, 5]))
        games_as_features = []
        new_moves = self.pop_new_games()
        for move in new_moves:
            game = []
            game_id = move[0]
            features = self.convert_cc_rec_to_features(move)