from enum import Enum

class Moves(Enum):
    HIT = True
    STAND = False

    @staticmethod
    def convert_to_bool(move):
        if isinstance(move, bool):
            return move
        elif move == Moves.HIT:
            return True
        elif move == Moves.STAND:
            return False

    @staticmethod
    def convert_to_move(boolean):
        if isinstance(boolean, bool):
            return boolean
        elif boolean == True:
            return Moves.HIT
        elif boolean == False:
            return Moves.STAND

if __name__ == "__main__":
    print(Moves.convert_to_bool(Moves.HIT))