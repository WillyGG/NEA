import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import random
import os
from Blackjack import Blackjack
import matplotlib.pyplot as plt


class Q_Net():
    def __init__(self, input_size, hidden_size, output_size, rnn_cell, myScope):
        self.init_feed_forward(input_size, hidden_size)
        self.split_streams(hidden_size, output_size)
        self.rnn_processing(rnn_cell, hidden_size)
        self.predict()
        self.gen_loss()
        self.train_update()

    def rnn_processing(self, rnn_cell, hidden_size):
        self.trainLength = tf.placeholder(dtype=tf.int32)
        # We take the output from the final fully connected layer and send it to a recurrent layer.
        # The input must be reshaped into [batch x trace x units] for rnn processing,
        # and then returned to [batch x units] when sent through the upper levles.
        self.batch_size = tf.placeholder(dtype=tf.int32, shape=[])
        #self.convFlat = tf.reshape(slim.flatten(self.conv4), [self.batch_size, self.trainLength, hidden_size])
        self.state_in = rnn_cell.zero_state(self.batch_size, tf.float32)
        self.rnn, self.rnn_state = tf.nn.dynamic_rnn(
            inputs=self.final_hidden, cell=rnn_cell, dtype=tf.float32, initial_state=self.state_in, scope=myScope + '_rnn')
        self.rnn = tf.reshape(self.rnn, shape=[-1, hidden_size])

    def init_feed_forward(self, inp_size, hidden_size):
        # Establish feed-forward part of the network
        self.input_layer = tf.placeholder(shape=[None, inp_size], dtype=tf.float32)

        hidden_layer1 = slim.fully_connected(self.input_layer, hidden_size,
                                            biases_initializer=None,
                                            activation_fn=tf.nn.relu)  # Rectified linear activation func.

        dropout1 = slim.dropout(hidden_layer1)

        hidden_layer2 = slim.fully_connected(dropout1, hidden_size,
                                             biases_initializer=None,
                                             activation_fn=tf.nn.relu)

        dropout2 = slim.dropout(hidden_layer2)

        self.final_hidden = slim.fully_connected(dropout2, hidden_size,
                                                 activation_fn=tf.nn.softmax,
                                                 biases_initializer=None)  # Softmax activation func.

        #self.action = tf.argmax(self.output_layer, 1)

    def split_streams(self, hidden_size, output_size):
        # The output from the recurrent player is then split into separate Value and Advantage streams
        self.streamA, self.streamV = tf.split(self.rnn, 2, 1)
        self.AW = tf.Variable(tf.random_normal([hidden_size // 2, output_size]))
        self.VW = tf.Variable(tf.random_normal([hidden_size // 2, 1]))
        self.Advantage = tf.matmul(self.streamA, self.AW)
        self.Value = tf.matmul(self.streamV, self.VW)
        self.salience = tf.gradients(self.Advantage, self.imageIn)

    def predict(self):
         # Then combine them together to get our final Q-values.
        self.Qout = self.Value + tf.subtract(self.Advantage, tf.reduce_mean(self.Advantage, axis=1, keep_dims=True))
        self.predict = tf.argmax(self.Qout, 1)

    def gen_loss(self):
        # Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
        self.targetQ = tf.placeholder(shape=[None], dtype=tf.float32)
        self.actions = tf.placeholder(shape=[None], dtype=tf.int32)
        self.actions_onehot = tf.one_hot(self.actions, 4, dtype=tf.float32)

        self.Q = tf.reduce_sum(tf.multiply(self.Qout, self.actions_onehot), axis=1)

        self.td_error = tf.square(self.targetQ - self.Q)

        # In order to only propogate accurate gradients through the network, we will mask the first
        # half of the losses for each trace as per Lample & Chatlot 2016
        self.maskA = tf.zeros([self.batch_size, self.trainLength // 2])
        self.maskB = tf.ones([self.batch_size, self.trainLength // 2])
        self.mask = tf.concat([self.maskA, self.maskB], 1)
        self.mask = tf.reshape(self.mask, [-1])
        self.loss = tf.reduce_mean(self.td_error * self.mask)


    def train_update(self):
        self.trainer = tf.train.AdamOptimizer(learning_rate=0.0001)
        self.updateModel = self.trainer.minimize(self.loss)


class Target_Net(Q_Net):
    def __init__(self, input_size, hidden_size, output_size, rnn_cell, myScope):
        super().__init__(input_size, hidden_size, output_size, rnn_cell, myScope)
        self.ops = None

    #These functions allows us to update the parameters of our target network with those of the primary network.
    def updateTargetGraph(self, tfVars, tau):
        total_vars = len(tfVars)
        op_holder = []
        for idx,var in enumerate(tfVars[0:total_vars//2]):
            op_holder.append(tfVars[idx+total_vars//2].assign((var.value()*tau) + ((1-tau)*tfVars[idx+total_vars//2].value())))
        self.ops = op_holder
        return op_holder

    def updateTarget(self, op_holder, sess):
        for op in op_holder:
            sess.run(op)
        total_vars = len(tf.trainable_variables())
        a = tf.trainable_variables()[0].eval(session=sess)
        b = tf.trainable_variables()[total_vars//2].eval(session=sess)
        if a.all() == b.all():
            pass
            #print("Target Set Success")
        else:
            print("Target Set Failed")


# This class allows the network to draw from a batch of experiences, rather than just one at a time
class experience_buffer():
    def __init__(self, buffer_size=1000):
        self.buffer = []
        self.buffer_size = buffer_size

    def add(self, experience):
        if len(self.buffer) + 1 >= self.buffer_size:
            self.buffer[0:(1 + len(self.buffer)) - self.buffer_size] = []
        self.buffer.append(experience)

    def sample(self, batch_size, trace_length):
        sampled_episodes = random.sample(self.buffer, batch_size)
        sampledTraces = []
        for episode in sampled_episodes:
            point = np.random.randint(0, len(episode) + 1 - trace_length)
            sampledTraces.append(episode[point:point + trace_length])
        sampledTraces = np.array(sampledTraces)
        return np.reshape(sampledTraces, [batch_size * trace_length, 5])

class Blackjack_Agent_Interface:
    def __init__(self, blackjack_instance, rewardDict):
        # TODO consider adding a hit reward
        self.blackjack = blackjack_instance
        self.winReward = rewardDict["winReward"] #2
        self.lossCost = rewardDict["lossCost"] #-2
        self.bustCost = rewardDict["bustCost"]

        self.hand_value_discount = rewardDict["hand_value_discount"] #1 / 21
        self.hand_size_norm_const = 1 / 10
        self.hand_val_norm_const = 1 / 30

    def get_game_state(self):  # Normalised
        player_hand_size = len(self.blackjack.player) * self.hand_size_norm_const
        player_hand_value = self.blackjack.assess_hand(self.blackjack.player) * self.hand_val_norm_const
        dealer_hand_size = len(self.blackjack.dealer) * self.hand_size_norm_const
        dealer_hand_value = self.blackjack.assess_hand(self.blackjack.dealer) * self.hand_val_norm_const
        return [player_hand_size, player_hand_value, dealer_hand_size, dealer_hand_value]

    def gen_step_reward(self):
        return 0

    def gen_end_reward(self, player_won):
        # TODO decide if dealer going bust should be rewarded
        reward = 0
        hand_value_reward = int(self.blackjack.assess_hand(self.blackjack.player) * self.hand_value_discount)
        if hand_value_reward > self.blackjack.blackjack:
            hand_value_reward += self.bustCost
        if player_won:
            reward += self.winReward
        else:
            reward += self.lossCost
        return reward

    def reset(self):
        pass

    def continue_game(self):
        return self.blackjack.continue_game

class Training_Interface:
    def __init__(self, parameters, Primary_Network, Target_Network, Blackjack_Interface):
        self.parameters = parameters
        self.Primary_Network = Primary_Network
        self.Target_Network = Target_Network
        self.BlJa_Interface = Blackjack_Interface

    def train(self):
        train_iterations = self.parameters["train_steps"]
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        save_frequency = self.parameters["save_model_frequency"]
        exp_buffer = experience_buffer()
        reward_record = []
        for i in range(train_iterations):
            game_state = self.BlJa_Interface.reset() # Implement this
            episode_reward = 0
            episode_buffer = []
            self.rnn_state = (np.zeros([1, h_size]), np.zeros([1, h_size]))  # Reset the recurrent layer's hidden state
            while self.BlJa_Interface.continue_game():
                action = self.choose_action(i)
                self.process_action(action)
                new_game_state = self.BlJa_Interface.get_game_state()
                new_rnn_state = self.get_new_rnn_state(self.rnn_state)
                reward = self.BlJa_Interface.gen_step_reward()
                episode_buffer.append(np.reshape(np.array([game_state, action, reward,
                                                          new_game_state, self.BlJa_Interface.continue_game]), [1, 5]))

                exploring = (i <= explore_steps)
                if i % update_frequency == 0 and not exploring:
                    self.update_networks()

                episode_reward += reward
                game_state = new_game_state
                self.rnn_state = new_rnn_state# UPDATE RNN CELL STATE

            # PROCESS END OF GAME
            # GET THE END OF GAME REWARD

            # Add the episode to the experience buffer
            bufferArray = np.array(episode_buffer)
            episodeBuffer = list(zip(bufferArray))
            exp_buffer.add(episodeBuffer)
            reward_record.append(episode_reward)

            if i % save_frequency == 0:
                self.save_model()

    # figure out if this causes two steps instead of 1
    def get_new_rnn_state(self, rnn_state):
        new_rnn_state = sess.run(mainQN.rnn_state,
                                      feed_dict={ mainQN.trainLength: 1,
                                        mainQN.state_in: rnn_state,
                                        mainQN.batch_size: 1 }
                                      )
        return new_rnn_state

    def save_model(self):
        pass

    def update_networks(self):
        pass

    def process_action(self, action):
        pass

    def choose_action(self, i):
        policy = self.parameters["policy"]
        exploration_steps = self.parameters["explore_steps"]
        if policy == "e-greedy":
            exploring = i <= exploration_steps
            return self.choose_action_e_greedy(exploring=exploring)

    def choose_action_e_greedy(self, exploring):
        h_size = self.parameters["h_size"]
        train_iterations = self.parameters["train_steps"]
        e = self.parameters["epsilon"]
        explore_steps = self.parameters["explore_steps"]

        # random exploration if explore stage or prob is less than epsilon
        if np.random.rand(1) < e or exploring:
            a = np.random.randint(0, 4)
        else:
            a, self.new_rnn_state = sess.run(mainQN.predict,
                                    feed_dict={ mainQN.trainLength: 1,
                                         mainQN.state_in: self.rnn_state,
                                         mainQN.batch_size: 1 }
                                    )
            a = a[0]

        # decrement epsilon
        if not exploring:
            if self.parameters["epsilon"] > self.parameters["end_epsilon"]:
                self.parameters["epsilon"] -= self.parameters["epsilon_step"]

        return a

#Setting the training parameters
batch_size = 4 #How many experience traces to use for each training step.
trace_length = 8 #How long each experience trace will be when training
update_freq = 5 #How often to perform a training step.
y = .99 #Discount factor on the target Q-values
startE = 1 #Starting chance of random action
endE = 0.1 #Final chance of random action
anneling_steps = 10000 #How many steps of training to reduce startE to endE.
num_episodes = 10000 #How many episodes of game environment to train network with.
pre_train_steps = 10000 #How many steps of random actions before training begins.
load_model = False #Whether to load a saved model.
path = "./nn_data" #The path to save our model to.
h_size = 512 #The size of the final convolutional layer before splitting it into Advantage and Value streams.
no_features = 4 # How many features to input into the network
no_actions = 2 # No actions the network can take
max_epLength = 50 #The max allowed length of our episode.
time_per_step = 1 #Length of each step used in gif creation
summaryLength = 100 #Number of epidoes to periodically save for analysis
tau = 0.001

tf.reset_default_graph()
# We define the cells for the primary and target q-networks
rnn_cell = tf.contrib.rnn.BasicLSTMCell(num_units=h_size, state_is_tuple=True)
target_rnn_cell = tf.contrib.rnn.BasicLSTMCell(num_units=h_size, state_is_tuple=True)

mainQN = Q_Net(no_features, h_size, no_actions, rnn_cell, 'main')
targetQN = Target_Net(no_features, h_size, no_actions, target_rnn_cell, 'target')

init = tf.global_variables_initializer()
saver = tf.train.Saver(max_to_keep=5)
trainables = tf.trainable_variables()

targetOps = Target_Net.updateTargetGraph(trainables, tau)
experience_buffer = experience_buffer()

# Set the rate of random action decrease.
e = startE
stepDrop = (startE - endE) / anneling_steps

# create lists to contain total rewards and steps per episode - turn this into a class?
jList = []
rList = []
total_steps = 0

# Make a path for our model to be saved in.
if not os.path.exists(path):
    os.makedirs(path)


with tf.Session() as sess:
    if load_model == True:
        print('Loading Model...')
        ckpt = tf.train.get_checkpoint_state(path)
        saver.restore(sess, ckpt.model_checkpoint_path)
    sess.run()
    Target_Net.updateTarget(targetOps, sess)

    for ep_number in range(num_episodes):
        pass



