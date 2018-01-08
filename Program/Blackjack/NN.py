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
    - TODO: Update blackjack interface -> create a higher level function get a winner#
    
    12 Dec
    - Added performance tester section - Network performance currently at about 40% win rate
    - Playing with reward numbers, update frequency, hit reward, hand value reward.
    
    13 Dec
    - Refactored the blackjack code into the blackjack game interface and the interface for the agent into two classes, for separation of concerns
    TODO: Add a different network structure and then test performance w/ betting, and w/o
    
    15 Dec
    - Started working on counting AI - an Ai which bases its moves based on what it knows is left in the deck, and 
      acts according to these probabilities. The purpose of this is to compare the NN AI to something
    - BST used to store the deck and how many of each value is left in the deck
    - Started working on self made BST
    - Completed functionality apart from deletion
    
    16 Dec
    - Completed deletion behaviour for all cases,
    - refactored tree, includes inheritance for specific case where i need to track a value and a counter variable with it
      for this deck of cards purpose
    
"""

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
from Blackjack import Blackjack
import matplotlib.pyplot as plt

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
        self.responsible_outputs = tf.gather(tf.reshape(self.output_layer, [-1]), self.indexes)  # Gathers and reshapes oup to a workable form

        return -tf.reduce_mean(tf.log(self.responsible_outputs) * self.reward_holder)  # loss function - vanilla policy

    def gen_updated_gradients(self, learn_rate):
        tvars = tf.trainable_variables()
        self.gradient_holders = []
        for ind, var in enumerate(tvars):
            placeholder = tf.placeholder(tf.float32, name = str(ind) + '_holder')
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

def discount_rewards(rewards):
    disc_rewards = np.zeros_like(rewards)
    total = 0
    for ind in reversed(range(0, rewards.size)):
        total = total * discount_multiplier + rewards[ind]
        disc_rewards[ind] = total
    return disc_rewards

tf.reset_default_graph()
discount_multiplier = 0.99  # Gamma
BigBoiBenny = Agent(learn_rate=1e-2, inp_size=4, hidden_size=8, output_size=2)
blackjack = Blackjack()
rewardDict = {
    "winReward" : 3,
    "lossCost" : -3,
    "bustCost" : 0,
    "hand_value_discount" : 1 / 2
}
blackjack_agent_interface = Blackjack_Agent_Interface(blackjack, rewardDict)

#Training Parameters
num_train_ep = 15000
update_frequency = 5 # 1 => 41%, 10 => 42%, 5 => 42.8%


init = tf.global_variables_initializer()
with tf.Session() as sess:
    sess.run(init)
    ep_num = 0
    total_reward = []
    total_length = []

    # Populate the grad buffer with zeros
    gradBuffer = sess.run(tf.trainable_variables())
    for ind, grad in enumerate(gradBuffer):
        gradBuffer[ind] = grad * 0

    print("Training", end = "")
    while ep_num < num_train_ep:
        blackjack.reset() # hard reset of blackjack game
        running_reward = 0
        ep_history = []
        no_moves = 0
        game_state = blackjack_agent_interface.get_game_state()  # Returns num of cards in each players hand and hand value of each player
        while blackjack.continue_game:
            # Probabilitisically pick an action from current network weighting
            # Then create a distribution and pick and action randomly if ...
            action_dist = sess.run(BigBoiBenny.output_layer, feed_dict={BigBoiBenny.input_layer:[game_state]})
            action = np.random.choice(action_dist[0], p=action_dist[0])
            action = np.argmax(action_dist == action)

            BigBoiBenny.perform_action(action) # Perform action
            reward = blackjack_agent_interface.gen_step_reward()
            new_state = blackjack_agent_interface.get_game_state()

            if blackjack.continue_game:
                ep_history.append([game_state, action, reward, new_state])

            game_state = new_state
            running_reward += reward
            no_moves += 1

        # TODO FIGURE OUT HOW TO INTEGRATE THIS INTO REWARD SYSTEM
        agent_won = blackjack.end_game()
        reward += blackjack_agent_interface.gen_end_reward(agent_won)
        new_state = blackjack_agent_interface.get_game_state()
        ep_history.append([game_state, action, reward, new_state])

        running_reward += reward

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

        if ep_num % (1000) == 0:
            print(".", end="")
        ep_num += 1

    # TODO TEST NETWORK PERFORMANCE AND UPDATE DOCUMENTED DESIGN
    # TODO FIDDLE WITH THE FUNCTIONALITY AND THE PERFORMANCE TO FIND OUT WHY THE NETWORK ALWAYS STANDS

    print()
    # Network performance test
    num_test_games = 1000
    won_games = 0
    no_times_stood = 0
    no_times_good_stood = 0
    hit = False
    for _ in range(num_test_games):
        blackjack.reset()
        game_state = blackjack_agent_interface.get_game_state()
        while blackjack.continue_game:
            hit = False
            action_dist = sess.run(BigBoiBenny.output_layer, feed_dict={BigBoiBenny.input_layer: [game_state]})
            action = np.random.choice(action_dist[0], p=action_dist[0])
            action = np.argmax(action_dist == action)
            BigBoiBenny.perform_action(action)  # Perform action
            new_state = blackjack_agent_interface.get_game_state()
            game_state = new_state

            if action == 1 and hit == False:
                no_times_stood += 1
                if new_state[1] * 30 >= 17 and new_state[1] <= 21:
                    no_times_good_stood += 1
            elif action == 0:
                hit = True

        agent_won = blackjack.end_game()
        if agent_won:
            won_games += 1
    print("{0}% games won over {1} games".format((won_games * 100 / num_test_games), num_test_games))

    if no_times_stood == 0:
        print("never stood..")
    else:
        print("{0}% times good stood in {1} games".format((no_times_good_stood * 100 / no_times_stood), num_test_games))

    print("{0}% games stood, no hit".format((no_times_stood * 100 / num_test_games)))
