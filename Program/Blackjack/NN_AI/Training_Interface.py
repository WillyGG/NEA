import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
from CC_Interface import CC_Interface
from experience_buffer import experience_buffer
from NN_Move import NN_Move
import sys,os
sys.path.append(os.path.realpath(".."))
from Moves import Moves
from datetime import datetime


class Training_Interface:
    def __init__(self, parameters, Primary_Network, Target_Network, Blackjack_Interface):
        self.parameters = parameters
        self.Primary_Network = Primary_Network
        self.Target_Network = Target_Network
        self.BlJa_Interface = Blackjack_Interface
        self.exp_buffer = experience_buffer()
        self.sess = None
        self.saver = tf.train.Saver(max_to_keep=5)
        self.NN_ID = "nn"

    def train_default(self, sess):
        train_iterations = self.parameters["train_steps"]
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        save_frequency = self.parameters["save_model_frequency"]
        hidden_size = self.parameters["hidden_size"]

        self.sess = sess
        self.Target_Network.updateTarget(sess)
        self.rnn_updated = False
        for i in range(train_iterations):
            #self.BlJa_Interface.reset() # Implement this
            self.game_state = self.BlJa_Interface.get_game_state()
            episode_buffer = []
            self.rnn_state = (np.zeros([1, hidden_size]), np.zeros([1, hidden_size]))  # Reset the recurrent layer's hidden state

            # step in game, get reward and new state
            while self.BlJa_Interface.continue_game():
                exploring = (i <= explore_steps)
                self.action = self.choose_action(exploring)
                self.BlJa_Interface.process_action(self.action) # IMPLEMENT
                new_game_state = self.BlJa_Interface.get_game_state()
                new_rnn_state = self.get_new_rnn_state()
                reward = self.BlJa_Interface.gen_step_reward()
                episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                          new_game_state, self.BlJa_Interface.continue_game()]), [1, 5]))


                if i % update_frequency == 0 and not exploring:
                    self.update_networks()

                self.game_state = new_game_state
                self.rnn_state = new_rnn_state# UPDATE RNN CELL STATE

            # PROCESS END OF GAME
            # GET THE END OF GAME REWARD
            self.BlJa_Interface.end_game()
            reward = self.BlJa_Interface.gen_step_reward()

            # decide if you want to append this
            episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                       self.game_state, self.BlJa_Interface.continue_game()]), [1, 5]))

            # Add the episode to the experience buffer
            bufferArray = np.array(episode_buffer)
            episodeBuffer = list(zip(bufferArray))
            self.exp_buffer.add(episodeBuffer)

            if i % save_frequency == 0:
                self.save_model()
            self.BlJa_Interface.reset()

    def training_group(self, sess):
        train_iterations = self.parameters["train_steps"]
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        save_frequency = self.parameters["save_model_frequency"]
        hidden_size = self.parameters["hidden_size"]

        self.sess = sess
        self.Target_Network.updateTarget(sess)

        for i in range(train_iterations):
            # self.BlJa_Interface.reset() # Implement this
            self.game_state = self.BlJa_Interface.get_game_state()
            episode_buffer = []
            self.rnn_state = np.zeros([1, hidden_size]), np.zeros(
                [1, hidden_size])  # Reset the recurrent layer's hidden state

            # step in game, get reward and new state
            while self.BlJa_Interface.continue_game():  # change this to just take a move when it's the AIs turn
                current_agent = self.BlJa_Interface.get_current_player()
                if current_agent.id != self.BlJa_Interface.NN_ID:
                    move = self.BlJa_Interface.get_aux_move()
                    self.BlJa_Interface.process_action(move)
                    new_game_state = self.BlJa_Interface.get_game_state()
                else:  # is the nn agent's turn
                    exploring = (i <= explore_steps)
                    self.action = self.choose_action(exploring)
                    self.BlJa_Interface.process_action(self.action)
                    new_game_state = self.BlJa_Interface.get_game_state()
                    new_rnn_state = self.get_new_rnn_state()
                    reward = self.BlJa_Interface.gen_step_reward()

                    self.action = Moves.convert_to_bool(self.action)
                    episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                               new_game_state, self.BlJa_Interface.continue_game()]),
                                                     [1, 5]))
                    if i % update_frequency == 0 and not exploring:
                        self.update_networks()
                    self.rnn_state = new_rnn_state  # UPDATE RNN CELL STATE

                self.game_state = new_game_state

            # PROCESS END OF GAME
            # GET THE END OF GAME REWARD
            self.BlJa_Interface.end_game()
            reward = self.BlJa_Interface.gen_step_reward()

            # decide if you want to append this
            self.action = Moves.convert_to_bool(self.action)
            episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                       self.game_state, self.BlJa_Interface.continue_game()]), [1, 5]))
            # Add the episode to the experience buffer
            bufferArray = np.array(episode_buffer)
            episodeBuffer = list(zip(bufferArray))
            self.exp_buffer.add(episodeBuffer)
            self.BlJa_Interface.reset()
        self.save_model() 

    # Start out simple with one player
    def training_CC_Interface(self, sess):
        train_iterations = self.parameters["train_steps"]
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        save_frequency = self.parameters["save_model_frequency"]
        hidden_size = self.parameters["hidden_size"]

        self.sess = sess
        self.Target_Network.updateTarget(sess)

        for i in range(train_iterations):
            # self.BlJa_Interface.reset() # Implement this
            self.game_state = self.BlJa_Interface.get_game_state()
            episode_buffer = []
            self.rnn_state = np.zeros([1, hidden_size]), np.zeros([1, hidden_size])  # Reset the recurrent layer's hidden state

            # step in game, get reward and new state
            while self.BlJa_Interface.continue_game(): # change this to just take a move when it's the AIs turn
                exploring = (i <= explore_steps)
                self.action = self.choose_action(exploring)
                self.BlJa_Interface.process_action(self.action)
                new_game_state = self.BlJa_Interface.get_game_state()
                new_rnn_state = self.get_new_rnn_state()
                reward = self.BlJa_Interface.gen_step_reward()

                self.action = Moves.convert_to_bool(self.action)
                if self.action is None:
                    print("converted_action", self.action)
                episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                       new_game_state, self.BlJa_Interface.continue_game()]), [1, 5]))
                if i % update_frequency == 0 and not exploring:
                    self.update_networks()
                self.rnn_state = new_rnn_state  # UPDATE RNN CELL STATE

                self.game_state = new_game_state

            # PROCESS END OF GAME
            # GET THE END OF GAME REWARD
            self.BlJa_Interface.end_game()
            reward = self.BlJa_Interface.gen_step_reward()

            # decide if you want to append this
            self.action = Moves.convert_to_bool(self.action)
            episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                       self.game_state, self.BlJa_Interface.continue_game()]), [1, 5]))
            # Add the episode to the experience buffer
            bufferArray = np.array(episode_buffer)
            episodeBuffer = list(zip(bufferArray))
            self.exp_buffer.add(episodeBuffer)

            if i % save_frequency == 0:
                self.save_model()

            self.BlJa_Interface.reset()

    # figure out if this causes two steps instead of 1
    # should not matter because the weights do not change and the game state does not change between here and getting move
    def get_new_rnn_state(self):
        new_rnn_state = self.sess.run(self.Primary_Network.rnn_state,
                                      feed_dict={
                                        self.Primary_Network.input_layer: [self.game_state],
                                        self.Primary_Network.trainLength: 1,
                                        self.Primary_Network.state_in: self.rnn_state,
                                        self.Primary_Network.batch_size: 1 }
                                      )
        return new_rnn_state

    def save_model(self):
        path = self.parameters["path_default"]
        # Make a path for our model to be saved in.
        if not os.path.exists(path):
            os.makedirs(path)
        # eg. 28-02-2018,15-30-10
        model_version = datetime.now().strftime("%d-%m-%Y,%H-%M-%S")
        model_type = "/model-default-"
        self.saver.save(self.sess, (path + model_type + model_version + ".cptk"))

    def update_networks(self):
        batch_size = self.parameters["batch_size"]
        hidden_size = self.parameters["hidden_size"]
        trace_length = self.parameters["trace_length"]
        y = self.parameters["gamma"]

        self.Target_Network.updateTarget(self.sess)
        rnn_state_update = (np.zeros([batch_size, hidden_size]), np.zeros([batch_size, hidden_size]))
        trainBatch = self.exp_buffer.sample(batch_size, trace_length)  # Get a random batch of experiences.

        # Below we perform the Double-DQN update to the target Q-values
        primary_out = self.sess.run(self.Primary_Network.predict, feed_dict={
            self.Primary_Network.input_layer: np.vstack(trainBatch[:, 3]),
            self.Primary_Network.trainLength: trace_length,
            self.Primary_Network.state_in: rnn_state_update,
            self.Primary_Network.batch_size: batch_size
        })

        target_out = self.sess.run(self.Target_Network.Qout, feed_dict={
            self.Target_Network.input_layer: np.vstack(trainBatch[:, 3]),
            self.Target_Network.trainLength: trace_length,
            self.Target_Network.state_in: rnn_state_update,
            self.Target_Network.batch_size: batch_size}
        )

        end_multiplier = -(trainBatch[:, 4] - 1)
        doubleQ = target_out[range(batch_size * trace_length), primary_out]
        targetQ = trainBatch[:, 2] + (y * doubleQ * end_multiplier)
        # Update the network with our target values.
        self.sess.run(self.Primary_Network.updateModel,
                 feed_dict={
                     self.Primary_Network.input_layer: np.vstack(trainBatch[:, 0]),
                     self.Primary_Network.targetQ: targetQ,
                     self.Primary_Network.actions: trainBatch[:, 1],
                     self.Primary_Network.trainLength: trace_length,
                     self.Primary_Network.state_in: rnn_state_update,
                     self.Primary_Network.batch_size: batch_size}
        )

    def choose_action(self, exploring=False):
        bool_move = NN_Move.choose_action(self.parameters,
                                     self.Primary_Network,
                                     self.game_state,
                                     self.rnn_state,
                                     self.sess,
                                     exploring=exploring)
        if bool_move == True:
            return Moves.HIT
        elif bool_move == False:
            return Moves.STAND
        else:
            print("bool_move", bool_move)

    # maybe put all load models into one method and just pass the type
    def load_model_default(self):
        path = self.parameters["path_default"]
        ckpt = tf.train.get_checkpoint_state(path)  # gets the checkpoint from the last checkpoint file
        self.saver.restore(self.sess, ckpt.model_checkpoint_path)

    # maybe find a way to abstract this with the training code
    def test_performance(self, sess):
        test_iterations = self.parameters["test_steps"]
        hidden_size = self.parameters["hidden_size"]
        self.sess = sess
        #self.load_model_default()
        total_games = 0
        games_won = 0
        games_stood = 1 # figure out why the game hits non stop
        games_good_stood = 0
        total_actions = 0
        total_stood_value = 0
        for i in range(test_iterations):
            # self.BlJa_Interface.reset() # Implement this
            self.game_state = self.BlJa_Interface.get_game_state()
            episode_buffer = []
            self.rnn_state = np.zeros([1, hidden_size]), np.zeros([1, hidden_size])  # Reset the recurrent layer's hidden state
            # step in game, get reward and new state
            while self.BlJa_Interface.continue_game():
                self.action = self.choose_action(exploring=False)
                if self.action == Moves.STAND:
                    total_stood_value += self.game_state[1] * 30
                    if self.game_state[1] * 30 > 17:
                        games_good_stood += 1
                    games_stood += 1
                total_actions += 1

                self.BlJa_Interface.process_action(self.action)  # IMPLEMENT
                new_game_state = self.BlJa_Interface.get_game_state()
                new_rnn_state = self.get_new_rnn_state()

                reward = self.BlJa_Interface.gen_step_reward()
                episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                           new_game_state, self.BlJa_Interface.continue_game()]), [1, 5]))
                self.game_state = new_game_state
                self.rnn_state = new_rnn_state  # UPDATE RNN CELL STATE

            # PROCESS END OF GAME
            # GET THE END OF GAME REWARD
            self.BlJa_Interface.end_game()
            reward = self.BlJa_Interface.gen_step_reward()

            # decide if you want to append this
            episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                       self.game_state, self.BlJa_Interface.continue_game()]), [1, 5]))

            # Add the episode to the experience buffer
            bufferArray = np.array(episode_buffer)
            episodeBuffer = list(zip(bufferArray))

            total_games += 1
            if self.BlJa_Interface.agent_is_winner():
                games_won += 1

            # outputting simple play information about the performance
            if total_games % 100 == 0:
                print((games_won / total_games * 100), "% games won after",total_games,"games")
                print((games_good_stood / games_stood), "% games good stood out of",games_stood,"games stood")
                print(total_stood_value / games_stood,"<- average stood value")
                #print("no times hit",no_times_hit,"out of",no_actions,"actions")

            self.BlJa_Interface.reset()


