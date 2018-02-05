import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import random
import os
import Blackjack
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
        self.trainLength = tf.placeholder(dtype=tf.int32)
        # We take the output from the final fully connected layer and send it to a recurrent layer.
        # The input must be reshaped into [batch x trace x units] for rnn processing,
        # and then returned to [batch x units] when sent through the upper levles.
        self.batch_size = tf.placeholder(dtype=tf.int32, shape=[])
        output_flat = tf.reshape(slim.flatten(self.final_hidden), [self.batch_size, self.trainLength, hidden_size])
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
                                            scope=(myScope+"hidden1"))  # Rectified linear activation func.

        #dropout1 = slim.dropout(hidden_layer1, scope=myScope)

        hidden_layer2 = slim.fully_connected(hidden_layer1, hidden_size,
                                             biases_initializer=None,
                                             activation_fn=tf.nn.relu,
                                             scope=(myScope+"hidden2"))

        #dropout2 = slim.dropout(hidden_layer2, scope=myScope)

        self.final_hidden = slim.fully_connected(hidden_layer2, hidden_size,
                                                 activation_fn=tf.nn.softmax,
                                                 biases_initializer=None,
                                                 scope=(myScope+"final_hidden"))  # Softmax activation func.

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
    def __init__(self, rewardDict, blackjack_instance = None, hand_instance = None): # Without dealer for now?
        # defensive programming - populating the blackjack class depending on whether one was passed or not
        if blackjack_instance is None or hand_instance is None:
            self.init_blackjack()
        else:
            if blackjack_instance is not None:
                self.blackjack = blackjack_instance
            if hand_instance is not None:
                self.agent_hand = hand_instance

        # TODO consider adding a hit reward
       # self.winReward = rewardDict["winReward"] #2
        #self.lossCost = rewardDict["lossCost"] #-2
        #self.bustCost = rewardDict["bustCost"]

        self.last_action = None

        #self.hand_value_discount = rewardDict["hand_value_discount"] #1 / 21
        self.hand_size_norm_const = 1 / 10
        self.hand_val_norm_const = 1 / 30

    def init_blackjack(self):
        self.agent_hand = Blackjack.Hand("agent")
        players = {
            "dealer": Blackjack.Dealer_Hand("dealer"),
            "agent": self.agent_hand
        }
        self.blackjack = Blackjack.Blackjack(players)

    def get_game_state(self):  # Normalised
        player_hand_size = self.agent_hand.get_hand_size() * self.hand_size_norm_const
        player_hand_value = self.agent_hand.get_value() * self.hand_val_norm_const
        #dealer_hand_size = len(self.blackjack.dealer) * self.hand_size_norm_const
       #dealer_hand_value = self.blackjack.assess_hand(self.blackjack.dealer) * self.hand_val_norm_const
        return [player_hand_size, player_hand_value] #dealer_hand_size, dealer_hand_value]

    def gen_step_reward(self):
        agent_value = self.agent_hand.get_value()
        current_winners = self.blackjack.compare_hands()
        win_value = (agent_value + 1) * self.hand_val_norm_const
        loss_value = (-agent_value - 1) * self.hand_val_norm_const
        normal_reward = agent_value * self.hand_val_norm_const
        normal_cost = -agent_value * self.hand_val_norm_const
        scaled_value = 0
        # Win and loss rewards regardless of last action - if absolute winner/loser
        if self.blackjack.check_game_over():
            if self.agent_hand in current_winners:
                scaled_value = win_value
            else:
                scaled_value = loss_value
        # rewards for hit and cost for bust
        elif self.last_action == "hit":
            if self.agent_hand.bust:
             scaled_value = loss_value
            else:
                scaled_value = normal_reward
        # rewards for standing
        elif self.last_action == "stand":
            if self.agent_hand in current_winners:
                scaled_value = normal_reward
            else:
                scaled_value = loss_value
        return scaled_value

    def reset(self):
        pass

    def continue_game(self):
        return self.blackjack.continue_game

    def process_action(self, action):
        self.last_action = action


class Training_Interface:
    def __init__(self, parameters, Primary_Network, Target_Network, Blackjack_Interface):
        self.parameters = parameters
        self.Primary_Network = Primary_Network
        self.Target_Network = Target_Network
        self.BlJa_Interface = Blackjack_Interface
        self.exp_buffer = experience_buffer()
        self.sess = None

    def load_model(self):
        if self.parameters["load_model"] == True:
            print('Loading Model...')
            ckpt = tf.train.get_checkpoint_state(path)
            saver.restore(sess, ckpt.model_checkpoint_path)
        #sess.run()

    def train(self, sess):
        train_iterations = self.parameters["train_steps"]
        explore_steps = self.parameters["explore_steps"]
        update_frequency = self.parameters["update_frequency"]
        save_frequency = self.parameters["save_model_frequency"]
        hidden_size = self.parameters["hidden_size"]

        self.sess = sess
        self.load_model()
        self.Target_Network.updateTarget(sess)
        for i in range(train_iterations):
            print(i)
            self.BlJa_Interface.reset() # Implement this
            self.game_state = self.BlJa_Interface.get_game_state()
            episode_buffer = []
            self.rnn_state = (np.zeros([1, hidden_size]), np.zeros([1, hidden_size]))  # Reset the recurrent layer's hidden state

            # step in game, get reward and new state
            while self.BlJa_Interface.continue_game():
                self.action = self.choose_action(i)
                print("action", self.action)
                self.BlJa_Interface.process_action(self.action) # IMPLEMENT
                new_game_state = self.BlJa_Interface.get_game_state()
                new_rnn_state = self.get_new_rnn_state()
                reward = self.BlJa_Interface.gen_step_reward()
                episode_buffer.append(np.reshape(np.array([self.game_state, self.action, reward,
                                                          new_game_state, self.BlJa_Interface.continue_game]), [1, 5]))

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
                                                       self.game_state, self.BlJa_Interface.continue_game]), [1, 5]))


            # Add the episode to the experience buffer
            bufferArray = np.array(episode_buffer)
            episodeBuffer = list(zip(bufferArray))
            self.exp_buffer.add(episodeBuffer)

            if i % save_frequency == 0:
                self.save_model()

    # figure out if this causes two steps instead of 1
    def get_new_rnn_state(self):
        new_rnn_state = self.sess.run(mainQN.rnn_state,
                                      feed_dict={
                                        mainQN.input_layer: [self.game_state],
                                        mainQN.trainLength: 1,
                                        mainQN.state_in: self.rnn_state,
                                        mainQN.batch_size: 1 }
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
        primary_out = self.sess.run(mainQN.predict, feed_dict={
            mainQN.input_layer: [self.game_state],
            mainQN.trainLength: trace_length,
            mainQN.state_in: rnn_state_update,
            mainQN.batch_size: batch_size}
        )

        target_out = self.sess.run(targetQN.Qout, feed_dict={
            targetQN.input_layer: [self.game_state],
            targetQN.trainLength: trace_length,
            targetQN.state_in: rnn_state_update,
            targetQN.batch_size: batch_size}
        )

        end_multiplier = -(trainBatch[:, 4] - 1)
        doubleQ = target_out[range(batch_size * trace_length), primary_out]
        targetQ = trainBatch[:, 2] + (y * doubleQ * end_multiplier)
        # Update the network with our target values.
        self.sess.run(mainQN.updateModel,
                 feed_dict={
                     mainQN.input_layer: [self.game_state],
                     mainQN.targetQ: targetQ,
                     mainQN.actions: trainBatch[:, 1],
                     mainQN.trainLength: trace_length,
                     mainQN.state_in: rnn_state_update,
                     mainQN.batch_size: batch_size}
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
            end_range = self.parameters["no_actions"]-1
            a = np.random.randint(0, 4)
        else:
            a, self.new_rnn_state = self.sess.run(mainQN.predict,
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
parameters = {
    "batch_size" : 4, #How many experience traces to use for each training step.
    "trace_length" : 8, #How long each experience trace will be when training
    "update_freq" : 5, #How often to perform a training step.
    "gamma" : .99, #Discount factor on the target Q-values
    "startE" : 1, #Starting chance of random action
    "endE" : 0.1, #Final chance of random action
    "annealing_steps" : 10000, #How many steps of training to reduce startE to endE.
    "train_steps" : 10000, #How many episodes of game environment to train network with.
    "explore_steps" : 10000, #How many steps of random actions before training begins.
    "load_model" : False, #Whether to load a saved model.
    "path" : "./nn_data", #The path to save our model to.
    "hidden_size" : 16, #The size of the final convolutional layer before splitting it into Advantage and Value streams.
    "no_features" : 2, # How many features to input into the network
    "no_actions" : 2, # No actions the network can take
    "max_epLength" : 50, #The max allowed length of our episode.
    "time_per_step" : 1, #Length of each step used in gif creation
    "summaryLength" : 100, #Number of epidoes to periodically save for analysis
    "tau" : 0.001,
    "policy" : "e-greedy",
    "save_model_frequency" : 50,
    "update_frequency" : 10
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
startE = parameters["startE"]
endE = parameters["endE"]
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
experience_buffer = experience_buffer()

# Set the rate of random action decrease.
parameters["epsilon"] = startE
parameters["epsilon_step"] = (startE - endE) / annealing_steps

# create lists to contain total rewards and steps per episode - turn this into a class?
jList = []
rList = []
total_steps = 0

# Make a path for our model to be saved in.
if not os.path.exists(path):
    os.makedirs(path)

with tf.Session() as sess:
    sess.run(init)
    trainer.train(sess)




