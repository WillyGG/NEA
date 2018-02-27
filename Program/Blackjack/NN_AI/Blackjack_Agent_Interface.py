import sys,os
sys.path.append(os.path.realpath(".."))
import Blackjack
from Moves import Moves

class Blackjack_Agent_Interface: # Maybe make this a static class?
    def __init__(self, rewardDict, blackjack_instance = None, hand_instance = None): # Without dealer for now?
        # defensive programming - populating the blackjack class depending on whether one was passed or not
        if blackjack_instance is None or hand_instance is None:
            self.init_blackjack()
        if blackjack_instance is not None:
            self.blackjack = blackjack_instance
        elif hand_instance is not None:
            self.agent_hand = hand_instance

        # TODO consider adding a hit reward
       # self.winReward = rewardDict["winReward"] #2
        #self.lossCost = rewardDict["lossCost"] #-2
        #self.bustCost = rewardDict["bustCost"]

        self.last_action = None

        #self.hand_value_discount = rewardDict["hand_value_discount"] #1 / 21
        self.hand_size_norm_const = 1 / 10
        self.hand_val_norm_const = 1 / 30

    def init_blackjack(self):
        self.agent_hand = Blackjack.Hand("agent")
        players = {
            "dealer": Blackjack.Dealer_Hand("dealer"),
            "agent": self.agent_hand
        }
        self.blackjack = Blackjack.Blackjack(players)

    def get_game_state(self):  # Normalised
        player_hand_size = self.agent_hand.get_hand_size() * self.hand_size_norm_const
        player_hand_value = self.agent_hand.get_value() * self.hand_val_norm_const
        #dealer_hand_size = len(self.blackjack.dealer) * self.hand_size_norm_const
        #dealer_hand_value = self.blackjack.assess_hand(self.blackjack.dealer) * self.hand_val_norm_const
        return [player_hand_size, player_hand_value] #dealer_hand_size, dealer_hand_value]

    def gen_step_reward(self):
        agent_value = self.agent_hand.get_value()
        current_winners = self.blackjack.compare_hands()
        win_value = (agent_value + 1) * self.hand_val_norm_const
        loss_value = (-agent_value-1) * self.hand_val_norm_const
        normal_reward = agent_value * self.hand_val_norm_const
        scaled_value = 0
        # Win and loss rewards regardless of last action - if absolute winner/loser
        if self.blackjack.check_game_over():
            if self.agent_hand.id in current_winners:
                scaled_value = win_value
            else:
                scaled_value = loss_value
        # rewards for hit and cost for bust
        elif self.last_action == Moves.HIT:
            if self.agent_hand.bust:
             scaled_value = loss_value
            else:
                scaled_value = normal_reward
        # rewards for standing
        elif self.last_action == Moves.STAND:
            if self.agent_hand.id in current_winners:
                scaled_value = normal_reward
            else:
                scaled_value = loss_value
        return scaled_value

    def continue_game(self):
        return self.blackjack.continue_game

    def process_action(self, action):
        if action == Moves.HIT:
            self.last_action = Moves.HIT
            # check if current turn (or check in the training mainloop)
            # hit
            self.blackjack.hit()
        elif action == Moves.STAND: # defencive programming?
            self.last_action = Moves.Stand
            self.blackjack.stand()

    def end_game(self):
        self.blackjack.end_game()

    def agent_is_winner(self):
        #print(self.blackjack.compare_hands())
        return self.blackjack.check_game_over() and self.agent_hand.id in self.blackjack.compare_hands()

    def reset(self):
        self.blackjack.reset()
