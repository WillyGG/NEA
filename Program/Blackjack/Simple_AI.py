from Blackjack import Blackjack
from Blackjack import Hand

class Simple_AI:
    def __init__(self, hand=None, parameters=None):
        self.ID = "Simple"
        self.blackjack_value = 21
        self.maxCard = 11
        self.bust_value = self.blackjack_value + 1
        self.hand = hand

        if parameters is None:
            self.set_parameters(setting="default")
        if hand is None:
            self.hand = Hand(self.ID)

    def set_parameters(self, setting="default"):
        if setting == "default":
            self.bust_threshold = 5
        elif setting == "aggressive":
            self.bust_threshold = 3
        elif setting == "passive":
            self.bust_threshold = 7

    # returns decision to hit or not -> true => hit, false => stand
    def get_move(self, best_player_hand):
        hand_value = self.hand.get_value()
        best_value = best_player_hand.get_value()

        # if blackjack'd
        if hand_value == self.blackjack_value:
            return False

        # If cannot go bust then hit
        elif (hand_value < (self.bust_value - self.maxCard)
              or self.edge_move_calc(hand_value, best_value)):
            return True

        return False

    def edge_move_calc(self, hand_value, best_value):
        bustDiff = abs(hand_value - self.bust_value) # how far off being bust SAI is
        LTBestPlayer = hand_value < best_value
        if LTBestPlayer or bustDiff <= self.bust_threshold:
            return True
        return False

class Simple_Agent_Interface:
    def __init__(self):
        pass