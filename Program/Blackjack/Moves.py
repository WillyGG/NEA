from enum import Enum

class Moves(Enum):
    HIT = True
    STAND = False

    @staticmethod
    def convert_to_bit(move):
        if isinstance(move, bool):
            return move
        elif isinstance(move, int) and move == 0 or move == 1:
            return move
        elif move == Moves.HIT:
            return 1
        elif move == Moves.STAND:
            return 0

    @staticmethod
    def convert_to_move(boolean):
        if isinstance(boolean, bool):
            return boolean
        elif boolean == True:
            return Moves.HIT
        elif boolean == False:
            return Moves.STAND

if __name__ == "__main__":
    print(Moves.convert_to_bit(Moves.HIT))
    print(Moves.convert_to_move(1))
