"""
    - Abstract class implementing and initialise needed properties and methods
    - every agent should inheret from this and overrdide the behaviours implemented in this class
"""
from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, ID="", type=None):
        self.ID = ID
        self.type = type
        super().__init__()

    @abstractmethod
    def update_end_game(self):
        pass

    @abstractmethod
    def get_move(self):
        pass

    def set_parameters(self, setting="default"):
        pass

    # not necessarily going to be anyone but the current agent
    # pass in list of hands, returns the best hand value, not including tehe agent
    def get_best_hand(self, hands):
        best_hand_value = 0
        best_hand_hand = None
        # find the second best player
        for player in hands:
            if player.id == self.ID or player.bust:
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

    # pass in list of hands, returns the hand which the agent corresponds to
    def get_agent_hand(self, hands):
        for player in hands:
            if player.id == self.ID:
                return player