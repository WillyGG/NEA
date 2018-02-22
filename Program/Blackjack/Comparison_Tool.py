import Blackjack as BJ
from Simple_AI import Simple_AI
from CC_AI import CC_AI
from enum import Enum
import os,sys
sys.path.append(os.path.realpath("./NN_AI"))
from NN import NN

class Moves(Enum):
    HIT = True
    STAND = False

class Comparison_Tool:
    ID_NN = "nn"
    ID_SIMPLE = "simple"
    ID_CC_AI = "cc_ai"
    param_types = ["default", "passive", "aggressive"]  # maybe convert this to an aggressive scale?

    def __init__(self):
        nn = NN()
        Simple = Simple_AI()
        cc_ai = CC_AI()
        self.agents = {
            Comparison_Tool.ID_NN: nn,
            Comparison_Tool.ID_SIMPLE: Simple,
            Comparison_Tool.ID_CC_AI: cc_ai
        }
        self.players_dict = dict()
        self.populate_players()
        self.blackjack = BJ.Blackjack(self.players_dict)



    def populate_players(self):
        self.players_dict = {
            Comparison_Tool.ID_NN: BJ.Hand(Comparison_Tool.ID_NN),
            Comparison_Tool.ID_SIMPLE: BJ.Hand(Comparison_Tool.ID_SIMPLE),
            Comparison_Tool.ID_CC_AI : BJ.Hand(Comparison_Tool.ID_CC_AI),
            "dealer" : BJ.Hand("dealer")
        }
        # sets the hands in the agent class to the same ones in the players dictionary
        for agent_id in self.agents.keys():
            agent = self.agents[agent_id]
            agent.hand = self.players_dict[agent_id]

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
    # create and manage a mainloop game of blackjack
    # TODO TEST TF OUT OF THIS
    def get_data(self, no_games=5000):
        win_records = {
            Comparison_Tool.ID_NN: 0,
            Comparison_Tool.ID_SIMPLE: 0,
            Comparison_Tool.ID_CC_AI: 0
        }

        for i in range(no_games):
            ID_current_player = self.blackjack.get_current_player()
            # get the current player
            # get the next move from that player
            # repeat
            while self.blackjack.continue_game():
                agent_current = self.agents[ID_current_player]
                next_move = agent_current.get_move(self.blackjack) # pass in the blackjack instance, so they can interact with the interfaces to get the necessary information and next move
                if next_move is Moves.HIT:
                    self.blackjack.hit()
                elif next_move is Moves.STAND:
                    self.blackjack.stand()
            # PROCESS END OF GAME
            # get the winners, increment their wins
            self.blackjack.end_game()
            winners = self.blackjack.winners
            for winner in winners:
                if winner is "dealer":
                    continue
                win_records[winner] += 1
        # convert win records to % and return the win rates
        win_rates = {}
        for key in win_records.keys():
            win_rates[key] = win_records[key] / no_games
        return win_rates

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
