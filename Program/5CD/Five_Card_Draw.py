from Deck import Deck

class Five_Card_Draw:
    def __init__(self):
        self.deck = Deck()
        self.dealerHand = []
        self.playerHand = []

        self.deal(self.playerHand, self.dealerHand)



    # Deals a card to players passed
    def deal(self, *args):
        for player in args:
            player.append(self.deck.pop())