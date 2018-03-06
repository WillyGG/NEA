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

class CT_Wrapper(DB):
    def __init__(self, db_path="Blackjack.sqlite"):
        super().__init__(db_path)
        game_id = self.get_next_game_id()

    def push_move(self, agent_id, move, turn_num, hand_before, hand_after):
        move = Moves.convert_to_bool(move)
        hand_before = self.convert_hand_to_text(hand_before)
        hand_after = self.convert_hand_to_text(hand_after)
        query = """INSERT INTO "Moves" 
                   (player_id, game_id, turn_num, hand_before, move, hand_after) \
                   VALUES ("{0}", {1}, {2}, "{3}", {4}, "{5}")""".format(agent_id, self.game_id, turn_num,
                                                                         hand_before, move, hand_after)

    def convert_hand_to_text(self, hand):
        pass

    def get_moves(self, agent, game_id=None):
        pass

    def inc_agent_win(self, agent_id):
        pass