import Blackjack as BJ
from Simple_AI import Simple_AI
from CC_AI import CC_AI
import os,sys
sys.path.append(os.path.realpath("./NN_AI"))
sys.path.append(os.path.realpath("./NN_AI/nn_data"))
sys.path.append(os.path.realpath("./DB"))
sys.path.append(os.path.realpath("./Structs"))

from Circular_Queue import Circular_Queue as cQ
from NN import NN
from Moves import Moves
from CT_Wrapper import CT_Wrapper
import matplotlib.pyplot as plt

# maybe change this into static class?
class Comparison_Tool:
    ID_NN = "nn"
    ID_SIMPLE = "simple"
    ID_CC_AI = "cc_ai"
    param_types = ["default", "passive", "aggressive"]  # maybe convert this to an aggressive scale?

    def __init__(self):
        self.blackjack_val = 21
        # Dictionary holding all the hands of the agents
        self.db_wrapper = CT_Wrapper()

    def init_agents(self):
        # The instances of all the agents
        self.agents = {
            Comparison_Tool.ID_NN: NN(Training=False),
            Comparison_Tool.ID_SIMPLE: Simple_AI(),
            Comparison_Tool.ID_CC_AI: CC_AI()
        }
        self.agents_hands = dict()
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
    def get_data(self, *args, no_games=1000):
        # Initialise the agent hands and the agents playing
        self.agents = {}
        self.agents_hands = {}
        self.init_agents()

        agent_hands_playing = {}
        agents_playing = {}
        for id_agent in args:
            if id_agent in self.agents_hands:
                agent_hands_playing[id_agent] = self.agents_hands[id_agent]
                agents_playing[id_agent] = self.agents[id_agent]

        blackjack = BJ.Blackjack(agent_hands_playing) # local instance of blackjack
        move_q = cQ(10)
        # play the games and get the win rates
        for game_num in range(no_games):
            while blackjack.continue_game:
                turn_num = blackjack.turnNumber
                ID_current_player = blackjack.get_current_player().id
                all_hands = blackjack.get_all_hands()
                agent_current = self.agents[ID_current_player]

                hand_val_before = agent_current.hand.get_value()

                hand_before = list(agent_current.hand.hand) # TODO DELETE THIS

                next_best_hand = self.get_next_best_hand(ID_current_player, all_hands)
                next_move = agent_current.get_move(all_hands) # pass in all player's hands

                if next_move == Moves.HIT:
                    blackjack.hit()
                elif next_move == Moves.STAND:
                    blackjack.stand()

                hand_val_after = agent_current.hand.get_value()

                if next_move == Moves.HIT and hand_val_before == hand_val_after:
                    print("hand before:")
                    for card in hand_before:
                        print(card)

                    print("\nhand after")
                    for card in agent_current.hand.hand:
                        print(card)

                    print("hand val before", hand_val_before)
                    print("hand val after",hand_val_after)
                    print("\n\n\n")



                move_info = (ID_current_player, turn_num, next_move,
                             next_best_hand, hand_val_before, hand_val_after)
                move_q.push(move_info)
            # PROCESS END OF GAME
            # get the winners, increment their wins, update the agents
            blackjack.end_game()

            # push all moves to db
            while not move_q.isEmpty():
                move_info = move_q.pop()
                self.db_wrapper.push_move(agent_id=move_info[0], turn_num=move_info[1],
                                          move=move_info[2], next_best_val=move_info[3],
                                          hand_val_before=move_info[4], hand_val_after=move_info[5])
            # push winners to db
            winners = blackjack.winners
            winning_hands = []
            for winner_id in winners:
                winning_hands.append(agent_hands_playing[winner_id])
            self.db_wrapper.push_game(winners, winning_hands, blackjack.turnNumber, agents_playing)

            #update agents and reset
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
            if hand.id == agent_id:
                continue
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
    def get_general_agent_analysis(self, agent_id):
        agent_data = self.db_wrapper.get_agent_moves(agent_id)
        analysis = self.process_move_data(agent_data)
        analysis["total_winrate"] = self.db_wrapper.get_agent_win_rate(agent_id)
        return analysis

    # pass in the data from X games and then process the game to show different stats
    # data should follow this format: turn_num, next_best_val, hand_val_before, move, hand_val_after
    # overall winner, winrates of each player,
    # extend this to compare winrates of each player, based on each parameter setting
    # 18 march 2018 -> currrently only analyses agents in isolation, not much relational analysis
    def process_move_data(self, data):
        aggresive_threshold = 17 # TODO make this more sophisticated -> maybe make it so that it takes into account win margin?

        analysis = {
            "aggressive_hits" : 0, # hits when winning and larger than 17
            "total_stand_value" : 0, # used to calculate average stand value later on
            "no_times_stood" : 0,
            "no_times_hit" : 0,
            "sample_size" : len(data),
            "no_times_bust" : 0,
            "no_times_bust_after_aggressive_hit" : 0,
            "average_stand_value" : 0,
        }
        print(data[0])
        # iterate over data and count different cases
        for move in data:
            next_best = move[1]
            val_before = move[2]
            action = move[3]
            val_after = move[4]
            went_bust = False

            # aggressive check
            # TODO add a win margin!!!
            if action == Moves.STAND:
                analysis["total_stand_value"] += val_before
                analysis["no_times_stood"] += 1
            if val_after > self.blackjack_val: # and move = Moves.HIT ??
                analysis["no_times_bust"] += 1
                went_bust = True
            if action == Moves.HIT:
                analysis["no_times_hit"] += 1
            if val_before > next_best and val_before >= aggresive_threshold and action == Moves.HIT:
                analysis["aggressive_hits"] += 1
                if went_bust:
                    analysis["no_times_bust_after_aggressive_hit"] += 1
        analysis["average_stand_value"] = analysis["total_stand_value"] / analysis["no_times_stood"]
        analysis["%_hit"] = analysis["no_times_hit"] / analysis["sample_size"]
        analysis["%_stood"] = analysis["no_times_stood"] / analysis["sample_size"]

        """
            - TODO: insert some abritary measurements here about aggression
        """

        return analysis

    # output the data as a graph and a file/database
    def output_data(self):
        pass

    # outputs graph of player winrate over games played
    # pass in player id
    # todo change this to getting data, plot in the gui class??
    def output_player_wr(self, id):
        games = self.db_wrapper.get_games_won_by_id(id)

        d_win_rate = []
        games_won = 0
        win_rate = 0
        batch_count = 0
        for record in games:
            batch_count += 1
            game_id = record[0]
            games_won += 1
            win_rate = games_won / game_id
            if batch_count % 10 == 0: # batches of 10
                next_game = [game_id, win_rate]  # todo batch this into games of x
                d_win_rate.append(next_game)
                batch_count = 0

        x_vals = [d[0] for d in d_win_rate]
        y_vals = [d[1] for d in d_win_rate]

        self.output_2d(x_vals, y_vals, title=id + "'s Win Rate Over Time", x_lbl="no games",
                       y_lbl="win rate")

    # pass in player id, get back aggresion rating
    # calculate the average stand value
    # calculate the standard deviation
    # see how far along the averages the player / agent is
    def get_aggression_rating(self, id):
        pass

    # aggression with context
    # pass in data -> [turn_num, next_best_val, hand_val_before, move, hand_val_after]
    # for a move to be aggressive it must be above a critical threshold
    # the player must be winning,
    # depending on the win margin -> hitting even with "high" win margin => aggressive
    def get_aggression_rating_move(self, move):
        pass

    # pass in agent id
    # outputs graph of average stand value against games played
    def output_avg_stand_value(self, id):
        games = self.db_wrapper.get_stand_data_by_id(id)

        x_vals = []
        y_vals = []
        total_stand_value = 0
        batch_count = 0
        for game in games:
            game_num = game[0]
            stand_value = game[1]
            total_stand_value += stand_value
            avg_stand_value = total_stand_value / game_num

            if batch_count % 10 == 0:
                x_vals.append(game_num)
                y_vals.append(avg_stand_value)
                batch_count = 0


        self.output_2d(x_vals, y_vals, title=id+"'s Avg Stand Val Over Time", x_lbl="no games", y_lbl="avg stand value")

    def output_aggression_win_realtion(self):
        pass

    # outputs a graph displaying hand values when players have stood, and their % frequency
    def output_stand_dist(self):
        get_all_stands_query = """
                               SELECT hand_val_before
                               FROM Moves
                               WHERE move=0;
                               """
        all_stands = self.db_wrapper.execute_queries(get_all_stands_query, get_result=True)

        frequencies = self.get_freq(all_stands)
        stand_values = [int(key) for key in frequencies.keys()]
        stand_values.sort() # change this to mergesort
        no_stands = len(all_stands)

        # converts dictionary to array for each stand value, in the corresponding index
        y_vals = [(frequencies[str(stand_values[i])]/no_stands) for i in range(len(stand_values))]

        self.output_2d(stand_values, y_vals, title="Stand Distribution", x_lbl="Stand Value", y_lbl="% Frequency")

    # outputs a graph displaying hand values when players have hit, and their % frequency
    def output_hit_dist(self):
        get_all_hits_query = """
                             SELECT hand_val_before
                             FROM Moves
                             WHERE move=1;
                             """
        all_hits = self.db_wrapper.execute_queries(get_all_hits_query, get_result=True)
        frequencies = self.get_freq(all_hits)
        hit_values = [int(key) for key in frequencies.keys()]
        hit_values.sort()
        no_hits = len(all_hits)

        y_vals = [(frequencies[str(hit_values[i])]/no_hits) for i in range(len(hit_values))]
        self.output_2d(hit_values, y_vals, title="Hit Distribution", x_lbl="Hit Value", y_lbl="% Frequency")

    # pass in a 2d list of values
    # returns a dictionary where key is a value the corresponding value is the frequency of that value from the dataset
    def get_freq(self, all_events):
        frequencies = {}
        for event in all_events:
            val = event[0]
            val_as_key = str(val)
            if val_as_key not in frequencies:
                frequencies[val_as_key] = 0
            frequencies[val_as_key] += 1
        return frequencies

    # pass in x and y values and optional labels
    # outputs new figure and plots
    def output_2d(self, x, y, **kwargs):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        if "title" in kwargs:
            fig.suptitle(kwargs["title"])
        if "x_lbl" in kwargs:
            plt.xlabel(kwargs["x_lbl"])
        if "y_lbl" in kwargs:
            plt.ylabel(kwargs["y_lbl"])

        ax.plot(x,y)
        plt.show()


    # get series of stand values
    # get games won when standing on said value
    # get number of games when stood of value
    # outputs the chances to win against values stood on
    def output_stand_vs_wr(self):
        get_distinct_vals = """
                            SELECT DISTINCT hand_val_before
                            FROM Moves
                            WHERE move=0;
                            """
        distinct_vals_res = self.db_wrapper.execute_queries(get_distinct_vals, get_result=True)
        stand_values = [i[0] for i in distinct_vals_res] # all distinct hand values
        stand_values.sort()

        total_games_stood = [] # total number of games stood with value coressponding to stand_values
        games_won = [] # games won with value coressponding to stand_values

        for value in stand_values:
            total_games_query = """
                                SELECT COUNT(*)
                                FROM Moves
                                WHERE move=0 AND hand_val_before={0};
                                """.format(value)
            # cross param sql
            no_games_won_query = """
                                 SELECT COUNT(*)
                                 FROM Moves, Game_Record
                                 WHERE Moves.move=0 AND Game_Record.winner_ids LIKE '%'||Moves.player_id||'%'
                                 AND Game_Record.game_id=Moves.game_id AND hand_val_before={0};
                                 """.format(value)

            total_games = self.db_wrapper.execute_queries(total_games_query, get_result=True)[0][0]
            no_games = self.db_wrapper.execute_queries(no_games_won_query, get_result=True)[0][0]

            total_games_stood.append(total_games)
            games_won.append(no_games)

        y_vals = [games_won[i]/total_games_stood[i] for i in range(len(stand_values))]

        self.output_2d(stand_values, y_vals, title="Chance to Win Based on Stand Value",
                       x_lbl="Stand Value", y_lbl="Win Rate")

    def output_hit_vs_br(self):
        distinct_hit_vals_q = """
                              SELECT DISTINCT hand_val_before
                              FROM Moves
                              WHERE move=1;
                              """
        distinct_vals_res = self.db_wrapper.execute_queries(distinct_hit_vals_q, get_result=True)
        hit_values = [i[0] for i in distinct_vals_res]  # all distinct hand values
        hit_values.sort()

        total_times_hit = []  # total number of games stood with value coressponding to stand_values
        games_bust = []  # games won with value coressponding to stand_values
        for value in hit_values:
            total_times_query = """
                                SELECT COUNT(*)
                                FROM Moves
                                WHERE move=1 AND hand_val_before={0};
                                """.format(value)
            # cross param sql
            no_games_bust_query = """
                                  SELECT COUNT(*)
                                  FROM Moves
                                  WHERE move=1 AND hand_val_before={0} AND hand_val_after > 21;
                                  """.format(value)

            total_games = self.db_wrapper.execute_queries(total_times_query, get_result=True)[0][0]
            no_games = self.db_wrapper.execute_queries(no_games_bust_query, get_result=True)[0][0]

            if value == 21:
                test_q = """
                         SELECT *
                         FROM Moves
                         WHERE move=1 AND hand_val_before=21 AND hand_val_after < 22;
                         """
                print(self.db_wrapper.execute_queries(test_q, get_result=True))

                print(no_games)
                print(total_games)

            total_times_hit.append(total_games)
            games_bust.append(no_games)

        y_vals = [games_bust[i] / total_times_hit[i] for i in range(len(hit_values))]

        self.output_2d(hit_values, y_vals, title="Chance to Go Bust Based on Hit Value",
                       x_lbl="Hit Value", y_lbl="Bust Rate")

if __name__ == "__main__":
    ct = Comparison_Tool()
    #Comparison_Tool.ID_CC_AI, Comparison_Tool.ID_NN, Comparison_Tool.ID_SIMPLE
    print(ct.get_data(Comparison_Tool.ID_SIMPLE, Comparison_Tool.ID_CC_AI, Comparison_Tool.ID_NN,  no_games=10000))
    #connection, cursor = ct.db_wrapper.execute_queries(
    #    "SELECT * FROM Game_Record", keep_open=True)
    #print(cursor.fetchone())
    #connection.close()

    #connection, cursor = ct.db_wrapper.execute_queries(
    #    "SELECT * FROM Moves WHERE player_id='simple'", keep_open=True
    #)
    #print(cursor.fetchall())
    #connection.close()

    #agent_to_analyse = Comparison_Tool.ID_SIMPLE
    #print(agent_to_analyse, ct.get_agent_analysis(agent_to_analyse))

    #ct.output_player_wr(agent_to_analyse)
    #ct.output_avg_stand_value(agent_to_analyse)

    #print(ct.db_wrapper.get_stand_val_avg())
    #print(ct.db_wrapper.get_stand_val_std_dev())
    #ct.output_stand_dist()
    #ct.output_hit_dist()

    #ct.output_stand_vs_wr()
    #ct.output_hit_vs_br()