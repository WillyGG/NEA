import sys,os
sys.path.append(os.path.realpath(".."))

from Card_Counter import Card_Counter
import Blackjack as BJ

class CC_Interface:
    def __init__(self, NN_Instance, CC_Instance, Blackjack_Instance):
        self.NN = NN_Instance
        self.CC = CC_Instance
        self.Blackjack = Blackjack_Instance
        self.NN_ID = "NN"

    def get_chances(self):
        state = self.get_game_state()
        NN_Winning = state[0] == state[1]

        AI_hand = state[0]
        AI_hand_val = AI_hand.get_value() # this is recalcualted a lot, maybe find a way to not have to do that as much?
        best_hand = state[1]
        best_hand_val = best_hand.get_value()

        chances = self.CC.calcChances(AI_hand, AI_hand_val, best_hand, best_hand_val, NN_Winning)
        return chances

    def get_game_state(self):
        dealer_hand = self.Blackjack.players["dealer"]
        player_hands_all = self.Blackjack.get_all_players_playing() + [dealer_hand]
        needed_player_hands = []
        needed_player_hands.append(self.get_AI_hand(player_hands_all)) # gets the AIs hand
        needed_player_hands.append(self.get_best_hand(player_hands_all)) # get the best players hand
        return needed_player_hands

    def get_AI_hand(self, player_hands_all):
        for hand in player_hands_all:
            if hand.id == self.NN_ID:
                return hand

    def get_best_hand(self, player_hands_all):
        best_hand = None
        best_hand_val = 0
        for hand in player_hands_all:
            current_hand_val = hand.get_value()
            if (best_hand_val == 0 and best_hand is None) or (current_hand_val > best_hand_val):
                best_hand = hand
                best_hand_val = current_hand_val
        return best_hand


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