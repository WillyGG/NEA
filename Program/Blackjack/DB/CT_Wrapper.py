"""
    - wrapper and interface for the database for comparison tool
    - push move method
    - get moves for a given agent
    - update win for give agent
"""
from DB import DB
import os,sys
sys.path.append(os.path.realpath(".."))
from Moves import Moves
from os import remove

class CT_Wrapper(DB):
    def __init__(self, db_path="Blackjack.sqlite"):
        super().__init__(db_path)
        #self.game_id = self.get_next_game_id()

    def push_move(self, agent_id, move, turn_num, next_best_val, hand_val_before, hand_val_after):
        move = Moves.convert_to_bool(move)
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
        for card in hand:
            if hand_as_text == "":
                hand_as_text += "({0} of {1})".format(card.value, card.suit)
            else:
                hand_as_text += ", ({0} of {1})".format(card.value, card.suit)
        return hand_as_text

    # pass in agent name, and a game_id
    # returns the turn_num, hand_before, move and hand_after
    def get_moves(self, agent, game_id):
        query = """SELECT turn_num, hand_before, move, hand_after 
                   FROM Moves WHERE player_id={0} AND game_id={1}""".format(agent, game_id)
        connection, cursor = self.execute_queries(query, keep_open=True)
        results = cursor.fetchall()
        connection.close()

        toReturn = []
        for result in results:
            record = list(result)
            move_as_move = Moves.convert_to_move(record[2])
            record[2] = move_as_move
            toReturn.append(record)
        return tuple(toReturn)

    # abstract method for incrementing a field in the agents table
    def inc_agent(self, field, agent_id):
        get_curr_win_query = "SELECT {0} FROM Agents".format(field)
        connection, cursor = self.execute_queries(get_curr_win_query, keep_open=True)
        games_won = cursor.fetchone()[0]
        connection.close()

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
        while result is not None:
            game_id_test += 1
            query = """SELECT Moves.game_id FROM Moves, Game_Record 
                       WHERE Moves.game_id={0} AND Moves.game_id=Game_Record.game_id;""".format(game_id_test)
            connection, cursor = self.execute_queries(query, keep_open=True)
            result = cursor.fetchone()
            connection.close()
        return game_id_test

if __name__ == "__main__":
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
    ct_w.execute_queries("INSERT INTO 'Agents' (agent_id, description, games_won, games_played) VALUES ('asdf', 'adsfdf', 0, 0);")
    for x in range(2):
        ct_w.inc_agent_win("asdf")
    connection, cursor = ct_w.execute_queries("SELECT * FROM Agents", keep_open=True)
    for i in cursor:
        print(i)
    connection.close()

    remove("Blackjack.sqlite")