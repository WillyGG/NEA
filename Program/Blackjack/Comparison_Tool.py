import Blackjack as BJ
from Simple_AI import Simple_AI
from CC_AI import CC_AI
import os,sys
sys.path.append(os.path.realpath("./NN_AI"))
from NN import NN

class Comparison_Tool:
    def __init__(self):
        nn = NN()
        Simple = Simple_AI()
        cc_ai = CC_AI()
        self.agents = {
            "nn": nn,
            "simple": Simple,
            "cc_ai": cc_ai
        }
        param_types = ["default", "passive", "aggressive"] # maybe convert this to an aggressive scale?

    # sets the parametrs, takes in a dictionary as an argument to set the parameters
    def set_params(self, **kwargs):
        if "nn" not in kwargs:
            kwargs["nn"] = "default"
        if "simple" not in kwargs:
            kwargs["simple"] = "default"
        if "cc_ai" not in kwargs:
            kwargs["cc_ai"] = "default"

        for key in self.agents.keys():
            self.agents[key].set_parameters(kwargs[key])

    # run X games of blackjack, get the winner then return it
    def get_data(self):
        pass

    # pass in the data from X games and then process the game to show different stats
    # overall winner, winrates of each player,
    # extend this to compare winrates of each player, based on each parameter setting
    def process_data(self, data):
        pass

    # output the data as a graph and a file/database
    def output_data(self):
        pass

if __name__ == "__main__":
    ct = Comparison_Tool()
