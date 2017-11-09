from Deck import Deck

def dealCommunity(num, comm_cards, Deck):
    for x in range(num):
        comm_cards.append(Deck.pop())

# TODO ADD HAND ANALYSIS AND WINNER COMPARISON
class Hand:
    def __init__(self, cards):
        self.__hand = cards

    def displayHand(self):
        for card in self.__hand:
            print(card)

    def calcValue(self):
        pass


HAND_SIZE = 2
TSUNAMI = 3
RIVER = 1
WAVE = 1
deals = [TSUNAMI, RIVER, WAVE]

deck = Deck()

hand1 = []
hand2 = []
comm_cards = []
for x in range(HAND_SIZE):
    hand1.append(deck.pop())
    hand2.append(deck.pop())

player1 = Hand(hand1)
player2 = Hand(hand2)
players = [player1, player2]

for deal in deals:
    pl_no = 1
    for player in players:
        print(pl_no)
        pl_no += 1
        player.displayHand()
    print("comm:")
    for card in comm_cards:
        print(card)
    print("\n")
    dealCommunity(deal, comm_cards, deck)
