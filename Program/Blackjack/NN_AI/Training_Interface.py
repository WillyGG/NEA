import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
from experience_buffer import experience_buffer

class Training_Interface:
    def __init__(self, parameters, Primary_Network, Target_Network, Blackjack_Interface):
        self.parameters = parameters
        self.Primary_Network = Primary_Network
        self.Target_Network = Target_Network
        self.BlJa_Interface = Blackjack_Interface
        self.exp_buffer = experience_buffer()
        self.sess = None

    def load_model(self): # update this to take in the inital variables
        path = self.parameters["path"]
        if self.parameters["load_model"] == True:
            print('Loading Model...')
            ckpt = tf.train.get_checkpoint_state(path)
            saver.restore(self.sess, ckpt.model_checkpoint_path)
        #sess.run(init)

    def train_default(self, sess):
        train_iterations = self.parameters["train_steps"]
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        save_frequency = self.parameters["save_model_frequency"]
        hidden_size = self.parameters["hidden_size"]

        self.sess = sess
        self.load_model()
        self.Target_Network.updateTarget(sess)
        self.rnn_updated = False
        for i in range(train_iterations):
            #self.BlJa_Interface.reset() # Implement this
            self.game_state = self.BlJa_Interface.get_game_state()
            episode_buffer = []
            self.rnn_state = (np.zeros([1, hidden_size]), np.zeros([1, hidden_size]))  # Reset the recurrent layer's hidden state

            # step in game, get reward and new state
            while self.BlJa_Interface.continue_game():
                self.action = self.choose_action(i)
                self.BlJa_Interface.process_action(self.action) # IMPLEMENT
                new_game_state = self.BlJa_Interface.get_game_state()
                new_rnn_state = self.get_new_rnn_state()
                reward = self.BlJa_Interface.gen_step_reward()
                episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                          new_game_state, self.BlJa_Interface.continue_game()]), [1, 5]))

                exploring = (i <= explore_steps)
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

    # figure out if this causes two steps instead of 1
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
        pass

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

    def choose_action(self, i):
        policy = self.parameters["policy"]
        exploration_steps = self.parameters["explore_steps"]
        if policy == "e-greedy":
            exploring = i <= exploration_steps
            return self.choose_action_e_greedy(exploring=exploring)

    def choose_action_e_greedy(self, exploring):
        e = self.parameters["epsilon"]

        # random exploration if explore stage or prob is less than epsilon
        if np.random.rand(1) < e or exploring:
            end_range = self.parameters["no_actions"]
            a = np.random.randint(0, end_range)
        else:
            a, new_rnn_state = self.sess.run([self.Primary_Network.predict, self.Primary_Network.rnn_state],
                                    feed_dict={
                                        self.Primary_Network.input_layer: [self.game_state],
                                        self.Primary_Network.trainLength: 1,
                                        self.Primary_Network.state_in: self.rnn_state,
                                        self.Primary_Network.batch_size: 1}
                                    )
            a = a[0]

        # decrement epsilon
        if not exploring:
            if self.parameters["epsilon"] > self.parameters["end_epsilon"]:
                self.parameters["epsilon"] -= self.parameters["epsilon_step"]

        return a

    # maybe find a way to abstract this with the training code
    def test_performance(self, sess):
        test_iterations = self.parameters["test_steps"]

        self.sess = sess
        self.load_model()
        total_games = 0
        games_won = 0
        games_stood = 0
        games_good_stood = 0
        total_actions = 0
        total_stood_value = 0
        for i in range(test_iterations):
            # self.BlJa_Interface.reset() # Implement this
            self.game_state = self.BlJa_Interface.get_game_state()
            episode_buffer = []

            # step in game, get reward and new state
            while self.BlJa_Interface.continue_game():
                self.action = self.choose_action(i)

                if self.action == 1:
                    total_stood_value += self.game_state[1] * 30
                    if self.game_state[1] * 30 > 17:
                        games_good_stood += 1
                    games_stood += 1
                total_actions += 1

                self.BlJa_Interface.process_action(self.action)  # IMPLEMENT
                new_game_state = self.BlJa_Interface.get_game_state()
                reward = self.BlJa_Interface.gen_step_reward()
                episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                           new_game_state, self.BlJa_Interface.continue_game()]), [1, 5]))
                self.game_state = new_game_state

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
                print(games_won)
                print((games_won / total_games * 100), "% games won after",total_games,"games")
                print((games_good_stood / games_stood), "% games good stood out of",games_stood,"games stood")
                print(total_stood_value/games_stood,"<- average stood value")

                #print("no times hit",no_times_hit,"out of",no_actions,"actions")

            self.BlJa_Interface.reset()

