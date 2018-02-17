import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import random
import os
import sys
from Blackjack_Agent_Interface import Blackjack_Agent_Interface
from Training_Interface import Training_Interface
import matplotlib.pyplot as plt

class Q_Net():
    def __init__(self, input_size, hidden_size, output_size, rnn_cell, myScope):
        self.init_feed_forward(input_size, hidden_size, output_size, myScope)
        self.rnn_processing(rnn_cell, hidden_size, myScope)
        self.split_streams(hidden_size, output_size)
        self.predict()
        self.gen_loss(output_size)
        self.train_update()

    def rnn_processing(self, rnn_cell, hidden_size, myScope):
        # We take the output from the final fully connected layer and send it to a recurrent layer.
        # The input must be reshaped into [batch x trace x units] for rnn processing,
        # and then returned to [batch x units] when sent through the upper levles.
        self.trainLength = tf.placeholder(dtype=tf.int32)
        self.batch_size = tf.placeholder(dtype=tf.int32, shape=[])
        output_flat = tf.reshape(self.final_hidden, [self.batch_size, self.trainLength, hidden_size])
        self.state_in = rnn_cell.zero_state(self.batch_size, tf.float32)
        self.rnn, self.rnn_state = tf.nn.dynamic_rnn(
            inputs=output_flat, cell=rnn_cell, dtype=tf.float32, initial_state=self.state_in, scope=myScope + '_rnn')
        self.rnn = tf.reshape(self.rnn, shape=[-1, hidden_size])

    def init_feed_forward(self, inp_size, hidden_size, output_size, myScope):
        # Establish feed-forward part of the network
        self.input_layer = tf.placeholder(shape=[None, inp_size], dtype=tf.float32)

        hidden_layer1 = slim.fully_connected(self.input_layer, hidden_size,
                                            biases_initializer=None,
                                            activation_fn=tf.nn.relu,
                                            scope=(myScope+"_hidden1"))  # Rectified linear activation func.

        #dropout1 = slim.dropout(hidden_layer1, scope=myScope)

        hidden_layer2 = slim.fully_connected(hidden_layer1, hidden_size,
                                             biases_initializer=None,
                                             activation_fn=tf.nn.relu,
                                             scope=(myScope+"_hidden2"))

        #dropout2 = slim.dropout(hidden_layer2, scope=myScope)

        self.final_hidden = slim.fully_connected(hidden_layer2, hidden_size,
                                                 activation_fn=tf.nn.relu,
                                                 biases_initializer=None,
                                                 scope=(myScope+"_final_hidden"))  # Softmax activation func. -> changed to relu, as no longer output

        #self.action = tf.argmax(self.output_layer, 1)

    def split_streams(self, hidden_size, output_size):
        # The output from the recurrent player is then split into separate Value and Advantage streams
        self.streamA, self.streamV = tf.split(self.rnn, 2, 1)
        self.AW = tf.Variable(tf.random_normal([hidden_size // 2, output_size]))
        self.VW = tf.Variable(tf.random_normal([hidden_size // 2, 1]))
        self.Advantage = tf.matmul(self.streamA, self.AW)
        self.Value = tf.matmul(self.streamV, self.VW)
        self.salience = tf.gradients(self.Advantage, self.input_layer) #self.imageIn

    def predict(self):
         # Then combine them together to get our final Q-values.
        self.Qout = self.Value + tf.subtract(self.Advantage, tf.reduce_mean(self.Advantage, axis=1, keep_dims=True))
        self.predict = tf.argmax(self.Qout, 1)

    def gen_loss(self, output_size):
        # Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
        self.targetQ = tf.placeholder(shape=[None], dtype=tf.float32)
        self.actions = tf.placeholder(shape=[None], dtype=tf.int32)
        self.actions_onehot = tf.one_hot(self.actions, output_size, dtype=tf.float32)

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

    def updateTarget(self, sess):
        op_holder = self.ops
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


#Setting the training parameters
parameters = {
    "batch_size" : 8, #How many experience traces to use for each training step.
    "trace_length" : 2, #How long each experience trace will be when training
    "update_freq" : 2, #How often to perform a training step.
    "gamma" : .99, #Discount factor on the target Q-values
    "start_epsilon" : 1, #Starting chance of random action
    "epsilon" : 1, # tracking value for epsilon - MAKE THIS AN ATTRIBUTE?
    "end_epsilon" : 0.001, #Final chance of random action
    "annealing_steps" : 1000, #How many steps of training to reduce startE to endE.
    "train_steps" : 20000, #How many episodes of game environment to train network with.
    "explore_steps" : 1000, #How many steps of random actions before training begins.
    "load_model" : False, #Whether to load a saved model.
    "path" : "./nn_data", #The path to save our model to.
    "hidden_size" : 32, #The size of the final convolutional layer before splitting it into Advantage and Value streams.
    "no_features" : 2, # How many features to input into the network
    "no_actions" : 2, # No actions the network can take
    "max_epLength" : 50, #The max allowed length of our episode.
    "time_per_step" : 1, #Length of each step used in gif creation
    "summaryLength" : 100, #Number of epidoes to periodically save for analysis
    "tau" : 0.001,
    "policy" : "e-greedy",
    "save_model_frequency" : 50, # how often to save the model
    "update_frequency" : 10, # how often to update the network weights
    "test_steps" : 20000 # how many iterations to test
}

rewards = {
    "winReward": 3,
    "lossCost": -3,
    "bustCost": 0,
    "hand_value_discount": 1 / 2
}

no_features = parameters["no_features"]
hidden_size = parameters["hidden_size"]
no_actions = parameters["no_actions"]
tau = parameters["tau"]
start_epsilon = parameters["start_epsilon"]
end_epsilon = parameters["end_epsilon"]
annealing_steps = parameters["annealing_steps"]
path = parameters["path"]
load_model = parameters["load_model"]

tf.reset_default_graph()
# We define the cells for the primary and target q-networks
rnn_cell = tf.contrib.rnn.BasicLSTMCell(num_units=hidden_size, state_is_tuple=True)
target_rnn_cell = tf.contrib.rnn.BasicLSTMCell(num_units=hidden_size, state_is_tuple=True)
mainQN = Q_Net(no_features, hidden_size, no_actions, rnn_cell, 'main')
targetQN = Target_Net(no_features, hidden_size, no_actions, target_rnn_cell, 'target')
blja = Blackjack_Agent_Interface(rewards)
trainer = Training_Interface(parameters, mainQN, targetQN, blja)

init = tf.global_variables_initializer()
saver = tf.train.Saver(max_to_keep=5)
trainables = tf.trainable_variables()

targetOps = targetQN.updateTargetGraph(trainables, tau)
#experience_buffer = experience_buffer()

# Set the rate of random action decrease.
parameters["epsilon"] = start_epsilon
parameters["epsilon_step"] = (start_epsilon - end_epsilon) / annealing_steps

# create lists to contain total rewards and steps per episode - turn this into a class?
jList = []
rList = []
total_steps = 0

# Make a path for our model to be saved in.
if not os.path.exists(path):
    os.makedirs(path)

with tf.Session() as sess:
    sess.run(init)
    trainer.train_default(sess)
    trainer.test_performance(sess)



