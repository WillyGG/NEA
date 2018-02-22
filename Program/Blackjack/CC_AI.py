from Card_Counter import Card_Counter
from Blackjack import Hand

class CC_AI:
    def __init__(self, parameters=None, hand=None):
        self.parameters = parameters
        self.CC = Card_Counter()
        self.Hand = hand
        self.ID = "cc_ai"
        if parameters is None:
            self.set_parameters(setting="default")
        if hand is None:
            self.Hand = Hand(self.ID)

    def get_move(self, blackjack_inst):
        game_state = self.get_state(blackjack_inst)
        chances = self.get_chances(game_state)
        move_next = self.getNextAction(chances)
        return move_next

    def get_state(self, blackjack_inst):
        agent_hand = blackjack_inst.players[self.ID]
        player_hands_all = blackjack_inst.get_all_players_playing()
        best_hand_value = 0
        best_hand_hand = None
        # find the second best player - maybe move this functionality into the blackjack class?
        for player in player_hands_all:
            if player.id == self.ID:
                continue
            player_value = player.get_value()
            if player_value > best_hand_value:
                best_hand_value = player_value
                best_hand_hand = player
        return [agent_hand, best_hand_hand]


    # return True if wanting to hit
    def getNextAction(self, chances):
        # not exceeding the dealer, hit.
        belowBestPlayer = not chances["AIWinning"]
        belowBustThreshold = chances["bust"] <= self.parameteres["bust_tol"]
        highBlackjackChance = chances["backjack"] >= self.parameteres["blackjack_thresh"]

        # BEHAVIOUR: Hit IF:
        # - losing or below the bus threshold
        # - or winning, above the bust threshold and below the risky bust threshold
        if belowBestPlayer or belowBustThreshold:
            return True
        elif highBlackjackChance:
            belowRiskyBustThreshold = chances["bust"] <= self.parameteres["bust_tol"] * self.parameteres["riskTolerance"]
            if belowRiskyBustThreshold:
                return True
        return False

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

    # pass in the game state and generate the chances to win
    # state = [AIHAND, Best hand (not including CCAI)]
    # what if state[1] is None: No people left playing - handle this (defensive programming)
    # TODO: Refactor this to work with best/second best hands as second arg (ie it will no longer be the agent)
    # TODO: Implement a win margin chance/feature
    def get_chances(self, state):
        # unpack the state
        AI_hand = state[0]
        AI_hand_val = AI_hand.get_value()  # this is recalcualted a lot, maybe find a way to not have to do that as much?
        best_hand = state[1]
        best_hand_val = best_hand.get_value()
        NN_Winning = AI_hand >= best_hand_val
        chances = self.CC.calcChances(AI_hand_val, best_hand_val, NN_Winning)
        return chances

    def decrement_CC(self, new_cards):
        self.CC.decrement_cards(new_cards)

