from Blackjack import Blackjack

class Simple_Agent:
    def __init__(self, instance):
        self.instance = instance
        self.blackjack = 21
        self.maxCard = 11
        self.hand = []
        self.dealer = []
        self.handValue = 0
        self.dealerValue = 0

    # returns decision to hit or not -> true => hit, false => stand
    def chooseNextMove(self):
        self.handValue = self.getHandValue(self.hand)
        self.dealerValue = self.getHandValue(self.dealer)

        # if blackjack'd
        if self.handValue == self.blackjack:
            return True

        # If cannot go bust then hit
        elif self.handValue <= (self.blackjack - self.maxCard) or self.chooseDlrBustDifferenceHit():
            return True

        return False

    def chooseDlrBustDifferenceHit(self):
        dealerBustDiff = abs(self.dealerValue - (self.blackjack+1))
        bustDiff = abs(self.handValue - (self.blackjack+1))
        aboveDealer = bustDiff < dealerBustDiff
        if aboveDealer:
            if self.dealerValue >= 17 or bustDiff >= 5:
                return True
        return False

    def getHandValue(self, hand):
        return self.instance.assess_hand(hand)

class Simple_Agent_Interface:
    def __init__(self):
        pass

