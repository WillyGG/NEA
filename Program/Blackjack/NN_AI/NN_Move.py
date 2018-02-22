# Figure this out later
class NN_Move:
    def __init__(self):
        pass

    @staticmethod
    def choose_action(exploring=False):
        policy = self.parameters["policy"]
        if policy == "e-greedy":
            return NN_Move.choose_action_e_greedy(exploring=exploring)

    @staticmethod
    def choose_action_e_greedy(exploring):
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