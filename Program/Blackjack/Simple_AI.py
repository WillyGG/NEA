from Blackjack import Blackjack
from Blackjack import Hand
from Agent import Agent
from Moves import Moves

class Simple_AI(Agent):
    def __init__(self, hand=None, parameters=None):
        super().__init__(ID="Simple", type=["Simple"])
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
    def get_move(self, all_players):
        best_player_value = self.get_best_hand_value(all_players)
        hand_value = self.hand.get_value()
        agent_winning = hand_value > best_player_value

        # if blackjack'd
        if hand_value == self.blackjack_value or agent_winning:
            return Moves.STAND
        # If cannot go bust, or edge case satisfied then hit
        elif (hand_value < (self.bust_value - self.maxCard)
              or self.edge_move_calc(hand_value, best_player_value)):
            return Moves.HIT
        return Moves.STAND

    def get_best_hand_value(self, all_players):
        all_hand_values = self.get_hand_values(all_players)
        return all_hand_values[0] # this is the best player hand value

    # pass in list of hands
    # get back hand values of each hand - best hand being first
    def get_hand_values(self, hands):
        hand_vals = []
        for hand in hands:
            if hand.bust:
                continue
            value = hand.get_value()
            hand_vals.append(value)
        return sorted(hand_vals, reverse=True)

    def edge_move_calc(self, hand_value, best_value):
        bustDiff = abs(hand_value - self.bust_value) # how far off being bust SAI is
        LTBestPlayer = hand_value < best_value
        if LTBestPlayer or bustDiff <= self.bust_threshold:
            return True
        return False

    def update_end_game(self, new_cards):
        pass

class Simple_Agent_Interface:
    def __init__(self):
        pass