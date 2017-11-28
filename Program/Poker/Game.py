from Deck import Deck

"""
28 Nov 2017
- Wrote the prototype for the hand and the poker interface
- added equivalence checker for a card

"""

# TODO Test this class
class Hand:
    def __init__(self, initialPot):
        self.__hand = [] # Perhaps update to circular queue
        self.__pot = initialPot

    @property
    def pot(self):
        return self.__pot

    def is_in_hand(self, card):
        for c in self.__hand:
            if c == card:
                return True
        return False

    def clear_hand(self):
        self.__hand = []

    def deal(self, *args):
        if len(args) <= 2:
            for card in args:
                self.__hand.append(card)
                return True
        else:
            return False

    def bet(self, amount):
        if self.__pot - amount > 0:
            self.__pot -= amount
            return amount
        else:
            return 0

def test_hand_class():
    d = Deck()
    h = Hand(500)

    card1 = d.pop()
    card2 = d.pop()
    card3 = d.pop()

    print( h.deal(card1, card2, card3) )
    print( h.deal(card1, card2) )

    print(h.is_in_hand(card1))
    print(h.is_in_hand(card2))

test_hand_class()
