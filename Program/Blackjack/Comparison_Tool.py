import Blackjack as BJ
from Simple_AI import Simple_AI
from CC_AI import CC_AI
import os,sys
sys.path.append(os.path.realpath("./NN_AI"))
sys.path.append(os.path.realpath("./NN_AI/nn_data"))
sys.path.append(os.path.realpath("./DB"))
from NN import NN
from Moves import Moves
from CT_Wrapper import CT_Wrapper

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
        self.blackjack_val = 21
        # Dictionary holding all the hands of the agents
        self.agents_hands = dict()
        self.populate_agent_hands()
        self.db_wrapper = CT_Wrapper()

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

        # play the games and get the win rates
        for game_num in range(no_games):
            print(game_num)
            while blackjack.continue_game:
                turn_num = blackjack.turnNumber
                ID_current_player = blackjack.get_current_player().id
                all_hands = blackjack.get_all_hands()
                agent_current = self.agents[ID_current_player]
                hand_val_before = agent_current.hand.get_value()
                next_move = agent_current.get_move(all_hands) # pass in all player's hands
                if next_move == Moves.HIT:
                    blackjack.hit()
                elif next_move == Moves.STAND:
                    blackjack.stand()
                hand_val_after = agent_current.hand.get_value()
                next_best_hand = self.get_next_best_hand(ID_current_player, all_hands)
                self.db_wrapper.push_move(ID_current_player, turn_num, next_move,
                                          next_best_hand, hand_val_before, hand_val_after)
            # PROCESS END OF GAME
            # get the winners, increment their wins, update the agents
            blackjack.end_game()
            # TODO TEST THIS
            winners = blackjack.winners
            winning_hands = []
            for winner_id in winners:
                winning_hands.append(agent_hands_playing[winner_id])
            self.db_wrapper.push_game(winners, winning_hands, blackjack.turnNumber, agents_playing)
            self.update_agents(agents_playing, blackjack)
            blackjack.reset()

        # convert win records to % and return the win rates
        win_rates = 0 # TODO CONVERT THIS TO QUERY THE DATABASE AND GET THE WINRATES
        return win_rates

    # pass in agent id
    # returns the hand value of the next best agent
    # will return 0 if all other agents are bust
    def get_next_best_hand(self, agent_id, all_hands):
        best_value = 0
        for hand in all_hands:
            hand_val = hand.get_value()
            if hand_val > best_value:
                best_value = hand_val
        return best_value

    # pass in the hands of all the agents playing, returns dictionary mapping strings to agent instances
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

    # pass in agent id, returns values on agent analysis
    def get_agent_analysis(self, agent_id):
        agent_data = self.db_wrapper.get_agent_moves(agent_id)
        return self.process_data(agent_data)

    # pass in the data from X games and then process the game to show different stats
    # data should follow this format: turn_num, next_best_val, hand_val_before, move, hand_val_after
    # overall winner, winrates of each player,
    # extend this to compare winrates of each player, based on each parameter setting
    # 18 march 2018 -> currrently only analyses agents in isolation, not much relational analysis
    def process_data(self, data):
        aggresive_threshold = 17 # TODO make this more sophisticated -> maybe make it so that it takes into account win margin?

        analysis = {
            "aggressive_hits" : 0, # hits when winning and larger than 17
            "total_stand_value" : 0, # used to calculate average stand value later on
            "sample_size" : len(data),
            "no_times_bust" : 0,
            "no_times_bust_after_aggressive_hit" : 0,
            "average_stand_value" : 0
        }

        # iterate over data and count different cases
        for move in data:
            next_best = move[1]
            val_before = move[2]
            action = move[3]
            val_after = move[4]
            went_bust = False

            # aggressive check
            # TODO add a win margin!!!
            if move == Moves.STAND:
                analysis["total_stand_value"] += val_before
            if val_after > self.blackjack_val: # and move = Moves.HIT ??
                analysis["no_times_bust"] += 1
                went_bust = True
            if val_before > next_best and val_before >= aggresive_threshold and action == Moves.HIT:
                analysis["aggressive_hits"] += 1
                if went_bust:
                    analysis["no_times_bust_after_aggressive_hit"] += 1
        analysis["average_stand_value"] = analysis["total_stand_value"] / analysis["sample_size"]

        """
            - TODO: insert some abritary measurements here about aggression
        """

        return analysis

    # output the data as a graph and a file/database
    def output_data(self):
        pass

if __name__ == "__main__":
    ct = Comparison_Tool()
    #Comparison_Tool.ID_CC_AI, Comparison_Tool.ID_NN, Comparison_Tool.ID_SIMPLE
    print(ct.get_data(Comparison_Tool.ID_SIMPLE))
    connection, cursor = ct.db_wrapper.execute_queries(
        "SELECT * FROM Game_Record", keep_open=True
    )
    print(cursor.fetchone())