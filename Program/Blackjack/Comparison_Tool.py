import Blackjack as BJ
from Simple_AI import Simple_AI
from CC_AI import CC_AI
import os,sys
sys.path.append(os.path.realpath("./NN_AI"))
sys.path.append(os.path.realpath("./NN_AI/nn_data"))
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
                Comparison_Tool.ID_NN: NN(Training=False),
                Comparison_Tool.ID_SIMPLE: Simple_AI(),
                Comparison_Tool.ID_CC_AI: CC_AI()
            }
        # Dictionary holding all the hands of the agents
        self.agents_hands = dict()
        self.populate_agent_hands()

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
    # pass the id's of the agents who are playing - DEALER IS NOT AUTOMATICALLY INCLUDED
    # TODO TEST TF OUT OF THIS
    def get_data(self, *args, no_games=5000):
        # Initialise the agent hands and the agents playing
        agent_hands_playing = {}
        agents_playing = {}
        for id_agent in args:
            if id_agent in self.agents_hands:
                agent_hands_playing[id_agent] = self.agents_hands[id_agent]
                agents_playing[id_agent] = self.agents[id_agent]
        blackjack = BJ.Blackjack(agent_hands_playing) # local instance of blackjack

        # initialise and populate the winrate structure
        win_records = {}
        for agent_id in agent_hands_playing.keys():
            win_records[agent_id] = 0

        # play the games and get the win rates
        for game_num in range(no_games):
            turn_no = 0
            while blackjack.continue_game:
                turn_no += 1
                ID_current_player = blackjack.get_current_player().id
                all_hands = blackjack.get_all_hands()
                agent_current = self.agents[ID_current_player]
                next_move = agent_current.get_move(all_hands) # pass in all player's hands
                if next_move == Moves.HIT:
                    blackjack.hit()
                elif next_move == Moves.STAND:
                    blackjack.stand()
            # PROCESS END OF GAME
            # get the winners, increment their wins, update the agents
            blackjack.end_game()
            winners = blackjack.winners
            # increment the win_rates
            for winner in winners:
                win_records[winner] += 1
            self.update_agents(agents_playing, blackjack)
            blackjack.reset()

        # convert win records to % and return the win rates
        win_rates = {}
        for key in win_records.keys():
            win_rates[key] = win_records[key] / no_games * 100
        return win_rates

    # pass in the hands of all the agents playing, returns
    def get_agents_playing(self, agent_hand_playing):
        toReturn = {}
        for key in agent_hand_playing.keys():
            if key == "dealer":
                continue
            toReturn[key] = self.agents[key]
        return toReturn

    def update_agents(self, agents_playing, blackjack_instance):
        new_cards = blackjack_instance.new_cards
        deck_iteration = blackjack_instance.deckIteration
        # pass new cards to card counters
        for player_id, player in agents_playing.items():
            player.update_end_game(new_cards)

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
    #Comparison_Tool.ID_CC_AI, Comparison_Tool.ID_NN, Comparison_Tool.ID_SIMPLE
    print(ct.get_data(Comparison_Tool.ID_NN))
