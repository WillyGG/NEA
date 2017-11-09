from Deck import Deck
from Deck import Royals

"""
1) Player gets two cards (2 u), dealer gets 2 cards (1u 1d)
2) Player can hit until bust, stand or blackjack
3) Dealer hits until >=17
4) Closest to 21 wins, unless bust
"""

"""
TODO:
  - Test Ace functionality
  - start prototyping reinforcement learning model
  - learn tensorflow
"""

class Blackjack:
    # TODO make this for more than one player
    def __init__(self):
        self.deck = Deck()
        self.Royals = { # Defines the values for the royals
            Royals.JACK : 10,
            Royals.QUEEN : 10,
            Royals.KING : 10,
            Royals.ACE : 11
        }
        self.blackjack = 21 # The winning value
        # Hand for each player
        self.player = []
        self.dealer = []
        self.bust = False
        self.continue_game = True
        # Deals to each player
        for _ in range(2):
            self.deal(self.player, self.dealer)

    # Calculate the total value of the passed hand (where hand is an array of cards)
    def assess_hand(self, hand):
        total = 0
        hasAce = False
        for card in hand:
            cValue = card.value
            if isinstance(cValue, Royals):
                cValue = self.Royals[cValue]
                if cValue == Royals.ACE:
                    hasAce = True
            total += cValue
        if hasAce:
            total = self.choose_ace(total)
        return total

    # If bust, changes the ace to a 1. TODO: TEST THIS
    def choose_ace(self, total):
        if total > self.blackjack:
            total -= 10
        return total

    # compares the hands of the passed players
    def compare_hands(self):
        player_total = self.assess_hand(self.player)
        dealer_total = self.assess_hand(self.dealer)
        winner_msg = ""
        if not self.bust and dealer_total <= self.blackjack:
            if player_total > dealer_total:
                winner_msg = "player wins"
                win_tot = player_total
            elif player_total < dealer_total:
                winner_msg = "dealer wins"
                win_tot = dealer_total
            else:
                winner_msg = "draw"
        else:
            if self.bust:
                winner_msg = "dealer wins, bust"
                win_tot = dealer_total
            elif dealer_total > self.blackjack:
                winner_msg = "player wins"
                win_tot = player_total

        return winner_msg + " " + str(win_tot) + "\n"

    # Deals a card to players passed
    def deal(self, *args):
        for player in args:
            player.append(self.deck.pop())

    # At the end of the game, deals cards to the dealer, until value of their hand is above 17
    def deal_dealer_end(self):
        while self.assess_hand(self.dealer) < 17:
            self.deal(self.dealer)

    # A hits the player's hand. If they are bust, stops the game - public
    def hit(self):
        self.deal(self.player)
        if self.assess_hand(self.player) > self.blackjack:
            self.bust = True
            self.continue_game = False

    # Stands, ends game. Public 
    def stand(self):
        self.continue_game = False

    # Outputs the current state of the game - each hand followed by their current value.
    def display_game(self):
        print("Dealer:", end=" ")
        for card in self.dealer:
            print(card, end = " ")
        print("\nPlayer:", end = " ")
        for card in self.player:
            print(card, end = " ")
        p_total = self.assess_hand(self.player)
        print(str(p_total))

if __name__ == "__main__":
    bj = Blackjack()
    for x in range(2):
        ui = ""
        while bj.continue_game:
            bj.display_game()
            ui = input("h for hit, s for stand ")
            if ui == "h":
                bj.hit()
            elif ui == "s":
                bj.stand()
        bj.deal_dealer_end()
        bj.display_game()
        print(bj.compare_hands())
        bj.__init__()
