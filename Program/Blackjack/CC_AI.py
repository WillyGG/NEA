from CC_Agent import CC_Agent
from Blackjack import Hand
from Moves import Moves

class CC_AI(CC_Agent):
    def __init__(self, parameters=None, hand=None):
        super().__init__(ID="cc_ai")
        self.parameters = parameters
        self.Hand = hand
        if parameters is None:
            self.set_parameters(setting="default")
        if hand is None:
            self.Hand = Hand(self.ID)

    # return True if wanting to hit
    def getNextAction(self, chances, game_state):
        # not exceeding the dealer, hit.
        belowBestPlayer = not chances["alreadyExceedingWinningPlayer"]
        belowBustThreshold = chances["bust"] <= self.parameteres["bust_tol"]
        highBlackjackChance = chances["blackjack"] >= self.parameteres["blackjack_thresh"]

        # BEHAVIOUR: Hit IF:
        # - losing or below the bust threshold
        # - or winning, above the bust threshold and below the risky bust threshold
        if belowBestPlayer or belowBustThreshold:
            return Moves.HIT
        elif highBlackjackChance:
            belowRiskyBustThreshold = chances["bust"] <= self.parameteres["bust_tol"] * self.parameteres["riskTolerance"]
            if belowRiskyBustThreshold:
                return Moves.HIT
        return Moves.STAND

    # Sets the default parameters of the CCAI
    def set_parameters(self, setting="default"):
        # Change these parameters to change the behaviour of the CCAI
        # Chage these to personality parameters, then calculate these thresholds based on parameters
        if setting == "default":
            self.parameteres = {
                "bust_tol" : 0.5,
                "blackjack_thresh" : 0.2,
                "exceedBestPlayer" : 0.3,
                "riskTolerance" : 1.3
            }
        elif setting == "aggressive":
            pass
        elif setting == "passive":
            pass