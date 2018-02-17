class CC_Interface:
    def __init__(self, NN_Instance, CC_Instance, Blackjack_Instance):
        self.NN = NN_Instance
        self.CC = CC_Instance
        self.Blackjack = Blackjack_Instance
        self.NN_ID = "NN"

    def get_chances(self):
        state = self.get_game_state()

        AI_hand = state[0]
        AI_hand_val = AI_hand.get_value() # this is recalcualted a lot, maybe find a way to not have to do that as much?
        best_hand = state[1]
        best_hand_val = best_hand.get_value()

        chances = self.CC.calcChances(AI_hand, AI_hand_val, best_hand, best_hand_val)
        return chances

    def get_game_state(self):
        player_ids = self.Blackjack.get_all_players_playing() + ["dealer"]
        player_hands_all = []
        for id in player_ids:
            hand = self.Blackjack.players[id]
            player_hands_all.append(hand)
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
            current_hand_val = hand.get_value
            if (best_hand_val == 0 and best_hand is None) or (current_hand_val > best_hand_val):
                best_hand = hand
                best_hand_val = current_hand_val
        return best_hand