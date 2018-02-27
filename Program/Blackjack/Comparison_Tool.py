import Blackjack as BJ
from Simple_AI import Simple_AI
from CC_AI import CC_AI
import os,sys
sys.path.append(os.path.realpath("./NN_AI"))
from NN import NN
from Moves import Moves

class Comparison_Tool:
    ID_NN = "nn"
    ID_SIMPLE = "simple"
    ID_CC_AI = "cc_ai"
    param_types = ["default", "passive", "aggressive"]  # maybe convert this to an aggressive scale?

    def __init__(self, agents=None):
        self.agents = agents
        if agents is None:
            # The instances of all the angents
            self.agents = {
                Comparison_Tool.ID_NN: NN(),
                Comparison_Tool.ID_SIMPLE: Simple_AI(),
                Comparison_Tool.ID_CC_AI: CC_AI()
            }
        # Dictionary holding all the hands of the agents
        self.agents_hands = dict()
        self.populate_agent_hands()
        self.blackjack = BJ.Blackjack(self.agents_hands)

    def populate_agent_hands(self):
        self.agents_hands["dealer"] = BJ.Dealer_Hand()
        for agent_key in self.agents.keys():
            self.agents_hands[agent_key] = BJ.Hand(agent_key)

        # sets the hands in the agent class to the same ones in the agent hands dictionary
        for agent_id, agent in self.agents.items():
            agent.hand = self.agents_hands[agent_id]

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
        # initialise and populate the winrate structure
        win_records = {
            "dealer": 0
        }
        for agent_id in self.agents.keys():
            win_records[agent_id] = 0

        for i in range(no_games):
            # get the current player
            # get the next move from that player
            # repeat
            print(i)
            while self.blackjack.continue_game:
                ID_current_player = self.blackjack.get_current_player().id
                current_players = self.blackjack.get_all_players_playing()
                print(current_players)
                agent_current = self.agents[ID_current_player]
                next_move = agent_current.get_move(current_players) # pass in all player's hands
                if next_move == Moves.HIT:
                    self.blackjack.hit()
                elif next_move == Moves.STAND:
                    self.blackjack.stand()
                agent_current.update_end_turn()

            # PROCESS END OF GAME
            # get the winners, increment their wins
            self.blackjack.end_game()
            winners = self.blackjack.winners
            # increment the win_rates
            for winner in winners:
                win_records[winner] += 1
            self.update_agents(self.agents)
            self.blackjack.reset()

        # convert win records to % and return the win rates
        win_rates = {}
        for key in win_records.keys():
            win_rates[key] = win_records[key] / no_games * 100
        return win_rates

    def update_agents(self, players):
        new_cards = self.blackjack.new_cards
        deck_iteration = self.blackjack.deckIteration
        # pass new cards to card counters
        for player_id, player in players.items():
            player.update_end_game(new_cards)
        """
        for player_id, player in players.items():
            if "Card Counter" in player.type:
                player.decrement_CC(new_cards)
            if "nn" in player.type:
                player.rnn_cell_reset()
        """

    # pass in the data from X games and then process the game to show different stats
    # overall winner, winrates of each player,
    # extend this to compare winrates of each player, based on each parameter setting
    def process_data(self, data):
        pass

    # output the data as a graph and a file/database
    def output_data(self):
        pass

if __name__ == "__main__":
    p = {
        Comparison_Tool.ID_CC_AI: CC_AI(),
        Comparison_Tool.ID_SIMPLE: Simple_AI()
    }
    print(True == Moves.HIT)
    ct = Comparison_Tool(agents=p)
    print(ct.get_data(no_games=100))
