import sys,os
sys.path.append(os.path.realpath(".."))

from Card_Counter import Card_Counter
import Blackjack as BJ
from Blackjack_Agent_Interface import Blackjack_Agent_Interface

class CC_Interface(Blackjack_Agent_Interface):
    def __init__(self, Blackjack_Instance=None):
        self.NN_ID = "nn"
        super().__init__(None, Blackjack_Instance, BJ.Hand(self.NN_ID))
        self.CC = Card_Counter()

    def get_chances(self, state=None):
        if state is None:
            state = self.get_game_state_CC()
        NN_Winning = state[0] == state[1]

        AI_hand = state[0]
        AI_hand_val = AI_hand.get_value() # this is recalcualted a lot, maybe find a way to not have to do that as much?
        best_hand = state[1]
        best_hand_val = best_hand.get_value()

        chances = self.CC.calcChances(AI_hand_val, best_hand_val, NN_Winning)
        return chances

    def get_game_state_CC(self):
        dealer_hand = self.blackjack.players["dealer"]
        player_hands_all = self.blackjack.get_all_players_playing() + [dealer_hand]
        needed_player_hands = []
        needed_player_hands.append(self.get_AI_hand(player_hands_all)) # gets the AIs hand
        needed_player_hands.append(self.get_best_hand(player_hands_all)) # get the best players hand
        return needed_player_hands

    # Returns the AI hand, best player hand, and the chances as a single array
    # called with each iteration of the game
    def get_game_state(self):
        toReturn = []
        AI_and_best_hand = self.get_game_state_CC()
        chances = self.get_chances(AI_and_best_hand)
        for hand in AI_and_best_hand: # adds the hand to the return array
            hand_value_normalised = hand.get_value() * self.hand_val_norm_const
            toReturn.append(hand_value_normalised)
        for key in sorted(chances): # sorted so that it is returned in the same order every time
            toReturn.append(chances[key])
        return toReturn

    def get_AI_hand(self, player_hands_all):
        return self.blackjack.players[self.NN_ID]

    # decrements the new cards from the cc
    def decrement_CC(self, new_cards):
        self.CC.decrement_cards(new_cards)

    # change this to best player not including AI, then find the disparity?
    def get_best_hand(self, player_hands_all):
        best_hand = None
        best_hand_val = 0
        for hand in player_hands_all:
            if hand.id == self.ID:
                continue
            current_hand_val = hand.get_value()
            if (best_hand_val == 0 and best_hand is None) or (current_hand_val > best_hand_val):
                best_hand = hand
                best_hand_val = current_hand_val
        return best_hand

    # method to end the game and reset everything
    def end_game(self):
        new_cards = self.blackjack.new_cards
        self.decrement_CC(new_cards)
        self.blackjack.end_game()

class CC_Interface_Tests:
    @staticmethod
    def test():
        range_of_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        number_of_suits = 4
        players = {
            "NN": BJ.Hand("NN"),
            "dealer": BJ.Dealer_Hand(),
            "mariusz": BJ.Hand("mariusz")
        }
        CC_Inst = Card_Counter(range_of_values, number_of_suits)
        BJ_Inst = BJ.Blackjack(players)

        CC_Iface = CC_Interface(None, CC_Inst, BJ_Inst)

        BJ_Inst.display_game()
        for hand in CC_Iface.get_game_state():
            print(hand)

        chances = CC_Iface.get_chances()
        for key in chances.keys():
            print(key, chances[key])

if __name__ == "__main__":
    CC_Interface_Tests.test()