from Card_Counter import Card_Counter
from Blackjack import Hand

class CC_AI:
    def __init__(self, parameters=None, hand=None):
        self.parameters = parameters
        self.CC = Card_Counter()
        self.Hand = hand
        self.ID = "CC_AI"
        if parameters is None:
            self.set_parameters_default()
        if hand is None:
            self.Hand = Hand(self.ID)

    def get_move(self, game_state):
        pass


    # Sets the default parameters of the CCAI
    def set_parameters_default(self):
        # Change these parameters to change the behaviour of the CCAI
        # Chage these to personality parameters, then calculate these thresholds based on parameters
        self.parameteres = {
            "bust" : 0.5,
            "blackjack" : 0.2,
            "exceedDlrNoBust" : 0.3,
            "riskTolerance" : 1.3
        }