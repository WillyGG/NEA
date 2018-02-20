from Card_Counter import Card_Counter
from Blackjack import Hand

class CC_AI:
    def __init__(self, parameters=None, hand=None, blackjack_instance=None):
        self.parameters = parameters
        self.CC = Card_Counter()
        self.Hand = hand
        self.ID = "CC_AI"
        self.blackjack = blackjack_instance
        if parameters is None:
            self.set_parameters_default()
        if hand is None:
            self.Hand = Hand(self.ID)
        if blackjack_instance:
            self.blackjack = blackjack_instance

    def get_move(self, game_state):
        chances = self.get_chances(game_state)

    # return True if wanting to hit
    def getNextAction(self, chances):
        # not exceeding the dealer, hit.
        belowBestPlayer = (chances["exceedBestPlayer"] < 1)
        belowBustThreshold = chances["bust"] <= self.parameteres["bust_tol"]
        highBlackjackChance = chances["backjack"] >= self.parameteres["blackjack_thresh"]

        if belowBestPlayer or belowBustThreshold:
            return True
        elif highBlackjackChance:
            belowRiskyBustThreshold = chances["bust"] <= self.parameteres["bust_tol"] * self.parameteres["riskTolerance"]
            if belowRiskyBustThreshold:
                return True
        return False

    # Sets the default parameters of the CCAI
    def set_parameters_default(self):
        # Change these parameters to change the behaviour of the CCAI
        # Chage these to personality parameters, then calculate these thresholds based on parameters
        self.parameteres = {
            "bust_tol" : 0.5,
            "blackjack_thresh" : 0.2,
            "exceedBestPlayer" : 0.3,
            "riskTolerance" : 1.3
        }

    # pass in the game state and generate the chances to win
    def get_chances(self, state):
        NN_Winning = state[0] == state[1]
        AI_hand = state[0]
        AI_hand_val = AI_hand.get_value()  # this is recalcualted a lot, maybe find a way to not have to do that as much?
        best_hand = state[1]
        best_hand_val = best_hand.get_value()
        chances = self.CC.calcChances(AI_hand, AI_hand_val, best_hand, best_hand_val, NN_Winning)
        return chances

    def decrement_CC(self, new_cards):
        self.CC.decrement_cards(new_cards)

