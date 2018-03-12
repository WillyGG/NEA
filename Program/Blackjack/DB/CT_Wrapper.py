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
        self.game_id = self.get_next_game_id()

    def push_move(self, agent_id, move, turn_num, hand_before, hand_after):
        move = Moves.convert_to_bool(move)
        hand_before = self.convert_hand_to_text(hand_before)
        hand_after = self.convert_hand_to_text(hand_after)
        query = """INSERT INTO "Moves" 
                   (player_id, game_id, turn_num, hand_before, move, hand_after) \
                   VALUES ("{0}", {1}, {2}, "{3}", {4}, "{5}");""".format(agent_id, self.game_id, turn_num,
                                                                          hand_before, move, hand_after)
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

    def get_moves(self, agent, game_id=None):
        pass

    def inc_agent_win(self, agent_id):
        pass

    def get_next_game_id(self):
        query = "SELECT MAX(game_id) FROM Moves;"
        connection, cursor = self.execute_queries(query, keep_open=True)
        next_game_id = 3132#cursor[0] + 1
        connection.close()
        return next_game_id

if __name__ == "__main__":
    ct_w = CT_Wrapper()
    ct_w.read_queries_from_file("Create_Games_Record")
    ct_w.execute_queries("INSERT INTO 'Moves' (player_id, game_id, turn_num, hand_before, move, hand_after) VALUES ('asdf', 1, 3, 'asdf', 0, 'sadf');")
    print(ct_w.get_next_game_id())

    remove("Blackjack.sqlite")