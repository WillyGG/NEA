"""
    - Define neural network using TF and train with BlackJ game
    - Include performance statistics
    - Use exploration vs exploitation techniques and configure for different personalities
    - Utilise recurrence and have an experience buffer
    -
"""

"""
    - Created a simple policy based agent to test libraries and prototype playing blackjack
    - Changed blackjack interface to return state of the game, and to return reward based on every action.
    
    10 Dec
    - Tested training performance
    - Agent always stood, was an issue with the reward return
    - updated reward method in blackjack file
    - agent always stood
    - increased win reward
    - agent hit no matter what
    - playing with numbers...
    - Bad implementation of the blackjack interface - forgot to deal dealers hand, and compare the new hands
    - TODO: Update blackjack interface -> create a higher level function get a winner
"""

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
from Blackjack import Blackjack
import matplotlib.pyplot as plt

discount_multiplier = 0.99 # Gamma

def discount_rewards(rewards):
    disc_rewards = np.zeros_like(rewards)
    total = 0
    for ind in reversed(range(0, rewards.size)):
        total = total * discount_multiplier + rewards[ind]
        disc_rewards[ind] = total
    return disc_rewards

class Agent:
    def __init__(self, learn_rate, inp_size, hidden_size, output_size):
        self.init_feed_forward(inp_size, hidden_size, output_size)
        self.loss = self.gen_loss()
        self.gen_updated_gradients(learn_rate)

    def init_feed_forward(self, inp_size, hidden_size, output_size):
        # Establish feed-forward part of the network
        self.input_layer = tf.placeholder(shape=[None, inp_size], dtype=tf.float32)
        hidden_layer = slim.fully_connected(self.input_layer, hidden_size,
                                            biases_initializer=None,
                                            activation_fn=tf.nn.relu)  # Rectified linear activation func.
        self.output_layer = slim.fully_connected(hidden_layer, output_size,
                                                 activation_fn=tf.nn.softmax,
                                                 biases_initializer=None)  # Softmax activation func.
        self.action = tf.argmax(self.output_layer, 1)

    def gen_loss(self):
        # Backpropagate the chosen action and the reward to compute loss and update agent.
        self.reward_holder = tf.placeholder(shape=[None], dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[None], dtype=tf.int32)

        self.indexes = tf.range(0, tf.shape(self.output_layer)[0]) * tf.shape(self.output_layer)[1] + self.action_holder
        self.responsible_outputs = tf.gather(tf.reshape(self.output_layer, [-1]),
                                             self.indexes)  # Gathers and reshapes oup to a workable form

        return -tf.reduce_mean(tf.log(self.responsible_outputs) * self.reward_holder)  # loss function - vanilla policy

    def gen_updated_gradients(self, learn_rate):
        tvars = tf.trainable_variables()
        self.gradient_holders = []
        for ind, var in enumerate(tvars):
            placeholder = tf.placeholder(tf.float32, name=str(ind) + '_holder')
            self.gradient_holders.append(placeholder)

        self.gradients = tf.gradients(self.loss, tvars)  # Calculates the gradients loss with respect to tvars

        optimizer = tf.train.AdamOptimizer(learning_rate=learn_rate)  # Adam Optimization algorithm
        self.update_batch = optimizer.apply_gradients(
            zip(self.gradient_holders, tvars))  # Generates batch of updated weights

    def perform_action(self, action_value):
        if action_value == 0:
            blackjack.hit()
        elif action_value == 1:
            blackjack.stand()

tf.reset_default_graph()
"""
    TODO: decide how you're going to organieze the layers:
    eg. node for each card and total? Node for hand structure?
    - 1) num of cards (dealer), 2) total card value (dealer), 3) num of cards in hand (agent), 4) total card value (agent)
    
"""

BigBoiBenny = Agent(learn_rate=1e-2, inp_size = 4, hidden_size = 8, output_size = 2)
blackjack = Blackjack()
num_train_ep = 10000
update_frequency = 5

won = 0
lost = 0
draw = 0

init = tf.global_variables_initializer()
with tf.Session() as sess:
    sess.run(init)
    ep_num = 0
    total_reward = []
    total_length = []

    gradBuffer = sess.run(tf.trainable_variables())
    for ind, grad in enumerate(gradBuffer):
        gradBuffer[ind] = grad * 0

    while ep_num < num_train_ep:
        blackjack.__init__() # hard reset of blackjack game
        running_reward = 0
        ep_history = []
        no_moves = 0
        game_state = blackjack.get_game_state()  # Returns num of cards in each players hand and hand value of each player
        while blackjack.continue_game:
            # Probabilitisically pick an action from current network weighting
            # Then create a distribution and pick and action randomly if ...
            action_dist = sess.run(BigBoiBenny.output_layer, feed_dict={BigBoiBenny.input_layer:[game_state]})
            action = np.random.choice(action_dist[0], p=action_dist[0])
            action = np.argmax(action_dist == action)

            BigBoiBenny.perform_action(action) # Perform action
            reward = blackjack.gen_reward()
            new_state = blackjack.get_game_state()
            ep_history.append([game_state, action, reward, new_state])

            game_state = new_state
            #running_reward += reward
            no_moves += 1

        # TODO FIGURE OUT HOW TO INTEGRATE THIS INTO REWARD SYSTEM
        blackjack.deal_dealer_end()
        blackjack.compare_hands()
        reward = blackjack.gen_reward()
        new_state = blackjack.get_game_state()
        ep_history.append([game_state, action, reward, new_state])

        game_state = new_state
        running_reward += reward

        if reward > 0:
            won += 1
        elif reward < 0:
            lost += 1
        else:
            draw += 1

        #Update the network after each game
        ep_history = np.array(ep_history)
        ep_history[:, 2] = discount_rewards(ep_history[:, 2])
        feed_dict = {
            BigBoiBenny.reward_holder : ep_history[:,2],
            BigBoiBenny.action_holder : ep_history[:,1],
            BigBoiBenny.input_layer : np.vstack(ep_history[:,0])
        }

        grads = sess.run(BigBoiBenny.gradients, feed_dict=feed_dict)
        for ind, grad in enumerate(grads):
            gradBuffer[ind] += grad
        if ep_num % update_frequency == 0 and ep_num != 0:
            feed_dict = dictionary = dict(zip(BigBoiBenny.gradient_holders, gradBuffer))
            _ = sess.run(BigBoiBenny.update_batch, feed_dict=feed_dict)
            for ind, grad in enumerate(gradBuffer):
                gradBuffer[ind] = grad * 0

        total_reward.append(running_reward)
        total_length.append(no_moves)

        if ep_num % 500 == 0:
            print("won", won)
            print("lost", lost)
            print("draw", draw)
            print(np.mean(total_reward[-500:]))
        ep_num += 1

# TODO TEST NETWORK PERFORMANCE AND UPDATE DOCUMENTED DESIGN