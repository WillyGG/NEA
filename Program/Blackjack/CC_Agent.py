"""
    - abstract class which all card counter agents will inheret
    - provides basic functionality and interface for the card counter class
"""
from Card_Counter import Card_Counter
from Agent import Agent
from abc import abstractmethod

# TODO: Test if this class works
class CC_Agent(Agent):
    def __init__(self, ID, extra_type=None):
        if extra_type is None:
            extra_type = []
        super().__init__(ID=ID, type=["Card Counter"] + extra_type)
        self.CC = Card_Counter()

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
        NN_Winning = AI_hand_val >= best_hand_val
        chances = self.CC.calcChances(AI_hand_val, best_hand_val, NN_Winning)
        return chances

    def get_move(self, all_players):
        game_state = self.get_state(all_players)
        chances = self.get_chances(game_state)
        move_next = self.getNextAction(chances, game_state)
        return move_next

    @abstractmethod
    def getNextAction(self, chances, game_state):
        pass

    def decrement_CC(self, new_cards):
        self.CC.decrement_cards(new_cards)

    def get_state(self, hands):
        agent_hand = self.get_agent_hand(hands)
        best_player_hand = self.get_best_player(hands)
        return [agent_hand, best_player_hand]

    def get_agent_hand(self, hands):
        for player in hands:
            if player.id == self.ID:
                return player

    # not necessarily going to be anyone but the current agent
    def get_best_player(self, hands):
        best_hand_value = 0
        best_hand_hand = None
        # find the second best player
        for player in hands:
            if player.id == self.ID:
                continue
            player_value = player.get_value()
            if player_value > best_hand_value:
                best_hand_value = player_value
                best_hand_hand = player
        # should never go to this section, because the dealer always plays last and cannot be bust
        if best_hand_hand == None:
            print("its happening again dude!")
            for player in hands:
                if player.id == "dealer":
                    for card in player.hand:
                        print(card)
                    print(player.get_value())
            best_hand_hand = self.get_agent_hand(hands)
        return best_hand_hand
