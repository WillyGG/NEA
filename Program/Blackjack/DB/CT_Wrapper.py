"""
    - wrapper and interface for the database for comparison tool
    - push move method
    - get moves for a given agent
    - update win for give agent
"""
import os,sys
sys.path.append(os.path.realpath(".."))
from DB_Wrapper import DB_Wrapper
from Moves import Moves
from os import remove
from math import sqrt

class CT_Wrapper(DB_Wrapper):
    def __init__(self, db_path="Blackjack.sqlite"):
        super().__init__(db_path)
        self.__tables_id = ["Agents", "Moves", "Game_Record"]
        self.init_tables()
        self.init_default_agents()
        self.game_id = self.get_next_game_id()

    # Creates the required tables - harcoded in -> TODO Change this from hardcoded?
    def init_tables(self):
        global db_dir_path
        self.execute_queries_from_file(db_dir_path + "Create_Games_Record.sql")
        self.execute_queries_from_file(db_dir_path + "Create_Agents_Table.sql")

    # pushes the agents into the table
    # TODO CHANGE THIS SO THAT IT CHECKS FI THEY EXIST FIRST
    def init_default_agents(self):
        agents = [
            ["nn", "Neural Network based AI, card counter"],
            ["cc_ai", "Card Counting, threshold based AI"],
            ["simple", "Simple AI based on game state thresholds"]
        ]
        self.populate_agents_table(agents[0], agents[1], agents[2])

    # pass in all the parameters required to push a move to the move table
    # this method will push the move to the move table
    # TODO INSERT SOME ERROR HANDLING AND DEFENSIVE PROGRAMMING
    def push_move(self, agent_id, turn_num, move, next_best_val, hand_val_before, hand_val_after):
        move = Moves.convert_to_bit(move)
        query = """INSERT INTO "Moves" 
                   (player_id, game_id, turn_num, next_best_val, hand_val_before, move, hand_val_after) \
                   VALUES ("{0}", {1}, {2}, {3}, {4}, {5}, {6});""".format(agent_id, self.game_id, turn_num,
                                                                           next_best_val, hand_val_before, move,
                                                                           hand_val_after)
        self.execute_queries(query)

    # pass in a hand of cards
    # returns the hand as a string in the format:
    # "({value} of {suit}), ({value} of {suit})" .. -> etc
    def convert_hand_to_text(self, hand):
        hand_as_text = ""
        for card in hand.hand:
            if hand_as_text == "":
                hand_as_text += "({0} of {1})".format(card.value, card.suit)
            else:
                hand_as_text += ", ({0} of {1})".format(card.value, card.suit)
        return hand_as_text

    # pass in agent name, and a game_id
    # returns the turn_num, next_best_val, hand_val_before, move, hand_val_after
    # TEST TEST TEST TEST
    def get_agent_moves(self, agent, game_id=None):
        if game_id is None:
            query = """SELECT turn_num, next_best_val, hand_val_before, move, hand_val_after 
                       FROM Moves WHERE player_id='{0}'""".format(agent)
        else:
            query = """SELECT turn_num, next_best_val, hand_val_before, move, hand_val_after 
                       FROM Moves WHERE player_id='{0}' AND game_id={1}""".format(agent, game_id)
        results = self.execute_queries(query, get_result=True)
        # convert moves from bit to move
        toReturn = []
        for result in results:
            record = list(result)
            move_as_move = Moves.convert_to_move(record[3])
            record[3] = move_as_move
            toReturn.append(record)
        return tuple(toReturn)

    # abstract method for incrementing a field in the agents table
    def inc_agent(self, field, agent_id):
        get_curr_query = "SELECT {0} FROM Agents WHERE agent_id='{1}'".format(field, agent_id)
        games_won = self.execute_queries(get_curr_query, get_result=True)[0]

        inc_win_query = """
                        UPDATE Agents
                        SET {0}={1}
                        WHERE agent_id='{2}';
                        """.format(field, games_won + 1, agent_id)
        self.execute_queries(inc_win_query)

    # increments the win field of the passed agent
    def inc_agent_win(self, agent_id):
        self.inc_agent("games_won", agent_id)

    # increments the games played for each of the agents passed
    def inc_games_played(self, *args):
        for agent_id in args:
            self.inc_agent("games_played", agent_id)

    # returns the next available game id
    # game id has to exist in both the moves table and the game record table
    def get_next_game_id(self):
        game_id_test = 0
        result = 0
        while result != []:
            game_id_test += 1
            query = """SELECT Moves.game_id FROM Moves, Game_Record 
                       WHERE Moves.game_id={0} AND Moves.game_id=Game_Record.game_id;""".format(game_id_test)
            result = self.execute_queries(query, get_result=True)
        return game_id_test

    # pass in array of agent instances
    # returns string which is formatted for database suitability
    def convert_agents_to_text(self, agents):
        agent_text = ""
        for agent in agents:
            if isinstance(agent, str):
                agent_name = agent
            else: # TODO CHANGE THIS IN A WAY SO THAT ITS NOT SHIT
                agent_name = agent.id
            agent_text += agent_name + ";"
        return agent_text

    # queries the database for a game id and converts the players field from TEXT to
    # an array of strings which are agent ids
    def get_agent_ids_from_game(self):
        pass

    # pass a game id, query the db for winning values
    # return array of ints for the winning values
    def get_winning_values(self):
        pass

    # push the a game to the game record table
    # agents => array of Agents Instances
    # winning_hand => Hand Instance
    # convert winners to text
    # auto updates game id
    def push_game(self, winners, winning_hands, num_of_turns, agents):
        wnr_hands = ""
        wnr_vals = ""
        for hand in winning_hands:
            hand_as_text = self.convert_hand_to_text(hand)
            wnr_hands += hand_as_text + ";"
            
            winning_val = hand.get_value()
            wnr_vals += str(winning_val) + ";"
        agents_as_text = self.convert_agents_to_text(agents)
        wnr_ids = ";".join(winners)
        query = """
                INSERT INTO Game_Record 
                (game_id, winner_ids, winning_hands, winning_values, num_of_turns, players)
                VALUES ({0}, '{1}', '{2}', '{3}', {4}, '{5}');
                """.format(self.game_id, wnr_ids, wnr_hands, wnr_vals, num_of_turns, agents_as_text)
        self.execute_queries(query)
        self.game_id += 1 #self.get_next_game_id()

        # increment the winners and the games played in the database
        for agent_id in winners:
            if agent_id == "dealer":
                continue
            self.inc_agent_win(agent_id)
        for agent_id in agents:
            self.inc_games_played(agent_id)
            pass

    # pass in arrays [agents ids, desc], method will populate them in the database
    # TODO UPDATE THIS SO THAT IT CHECKS IF THE AGENT ALREADY EXISTS BEFORE INSERTION
    def populate_agents_table(self, *args):
        queries = []
        for arg in args:
            agent_name = arg[0]
            agent_desc = arg[1]
            queries.append("""
                INSERT INTO Agents (agent_id, description, games_won, games_played)
                VALUES ('{0}', '{1}', 0, 0);
            """.format(agent_name, agent_desc))
        self.execute_queries(queries)

    # pass in an agent id and get the winrate as a decimal
    def get_agent_win_rate(self, agent_id):
        # get the number of wins
        query = """
                SELECT games_won, games_played
                FROM Agents 
                WHERE agent_id='{0}'
                """.format(agent_id)
        result = self.execute_queries(query, get_result=True)[0]
        winrate = result[0] / result[1]
        return winrate

    # pass in agent id
    # returns 2d array => [  [game_id, win_rate after x games], ...  ]
    def get_agent_wins_per_game(self, agent_id):
        agent_id_as_text = self.convert_agents_to_text([agent_id])
        # gets all the game record numbers which the user has played in
        games_query = """
                          SELECT game_id, winner_ids
                          FROM Game_Record 
                          WHERE players LIKE '%{0}%'
                          ORDER BY game_id ASC;
                          """.format(agent_id_as_text) # add validation by selecting from users table


        # get the data from the database
        games = self.execute_queries(games_query, get_result=True)

        d_win_rate = []
        games_won = 0
        win_rate = 0
        for record in games:
            game_id = record[0]
            winners = record[1]
            if agent_id_as_text in winners:
                games_won += 1
                win_rate = games_won / game_id
            next_game = [game_id, win_rate] # todo batch this into games of x
            d_win_rate.append(next_game)

        return d_win_rate

    # todo contextualise this value -> look at opponents hand values before stand also
    # queries database, returns average stand value players stand on
    #todo test test test
    def get_avg_stand_val(self):
        query = """
                SELECT AVG(hand_val_before) 
                FROM Moves
                WHERE move=0;
                """
        result = self.execute_queries(query, get_result=True)
        return result[0]

    # gets the standard deviation to the mean of the average value which the players stand on
    # todo test test test
    def get_std_dev_stand_val(self):
        avg_val = self.get_avg_stand_val()

        query = """
                SELECT hand_val_before
                FROM Moves
                WHERE move=0;
                """
        results = self.execute_queries(query, get_result=True)

        s = 0 # sum of (x - xbar)^2
        n = len(results)
        for result in results:
            s += (result[0] - avg_val) ** 2

        std_dev = sqrt(s / (n-1))
        return std_dev



if __name__ == "__main__":
    db_dir_path = ""

    ct_w = CT_Wrapper()
    ct_w.execute_queries_from_file("Create_Games_Record.sql")
    ct_w.execute_queries("INSERT INTO 'Moves' (player_id, game_id, turn_num, next_best_val, hand_val_before, move, hand_val_after) VALUES ('asdf', 1, 3, 5, 0, 0, 10);")
    ct_w.execute_queries("INSERT INTO 'Moves' (player_id, game_id, turn_num, next_best_val, hand_val_before, move, hand_val_after) VALUES ('asdf', 2, 3, 5, 0, 0, 10);")

    ct_w.execute_queries("INSERT INTO 'Game_Record' (game_id, winner_id, winning_hand, winning_hand_value, num_of_turns, players) VALUES (1, 'asdf', 'agfdsg', 3, 5, 'asdf');")
    ct_w.execute_queries("INSERT INTO 'Game_Record' (game_id, winner_id, winning_hand, winning_hand_value, num_of_turns, players) VALUES (2, 'asdf', 'agfdsg', 3, 5, 'asdfsad');")
    print(ct_w.get_next_game_id())
    connection, cursor = ct_w.execute_queries("SELECT * FROM Moves", keep_open=True)
    for i in cursor:
        print(i)
    connection.close()

    ct_w.execute_queries_from_file("Create_Agents_Table")
    ct_w.execute_queries("INSERT INTO Agents (agent_id, description, games_won, games_played) VALUES ('asdf', 'adsfdf', 0, 0);")
    for x in range(2):
        ct_w.inc_agent_win("asdf")
    connection, cursor = ct_w.execute_queries("SELECT * FROM Agents", keep_open=True)
    for i in cursor:
        print(i)
    connection.close()

    remove("Blackjack.sqlite")
else:
    db_dir_path = "DB/"