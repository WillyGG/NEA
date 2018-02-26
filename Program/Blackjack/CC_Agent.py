"""
    - abstract class which all card counter agents will inheret
    - provides basic functionality and interface for the card counter class
"""
from Card_Counter import Card_Counter

# TODO: Test if this class works
class CC_Agent:
    def __init__(self):
        self.type = "Card Counter"
        self.CC = Card_Counter()
        self.ID = "" # OVERRIDE IN CHILD CLASSES

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

    def get_move(self, current_players):
        game_state = self.get_state(current_players)
        chances = self.get_chances(game_state)
        move_next = self.getNextAction(chances)
        return move_next

    # OVERRIDE THIS IN CHILD CLASSES
    def getNextAction(self, chances):
        pass

    def decrement_CC(self, new_cards):
        self.CC.decrement_cards(new_cards)

    def get_state(self, current_players):
        agent_hand = self.get_agent_hand(current_players)
        best_player_hand = self.get_best_player(current_players)
        return [agent_hand, best_player_hand]

    def get_agent_hand(self, current_players):
        for player in current_players:
            if player.id == self.ID:
                return player

    def get_best_player(self, current_players):
        best_hand_value = 0
        best_hand_hand = None
        # find the second best player
        for player in current_players:
            if player.id == self.ID:
                continue
            player_value = player.get_value()
            if player_value > best_hand_value:
                best_hand_value = player_value
                best_hand_hand = player
        return best_hand_hand
