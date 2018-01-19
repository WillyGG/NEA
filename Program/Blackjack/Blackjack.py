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
    def __init__(self, playersDict):
        self.deck = Deck()
        self.blackjack = 21 # The winning value
        self.winner = None

        # Hand for each player
        self.players = playersDict

        # turn this into a circular queue
        self.playerNames = [player for player in list(self.players.keys()) if player.lower() != "dealer"]

        self.continue_game = True # the way this is implemented is weird - maybe method with same purpose?
        self.newDeck = True

        # Deals to each player
        self.init_deal()

    # Reset the hands and the tracking variables
    def reset(self):
        for key in self.players.keys():
            self.players[key].reset()
        self.continue_game = True
        self.init_deal()

    def init_deal(self):
        for player in self.players:
            self.deal(player)

    # Calculate the total value of the passed hand (where hand is an array of cards)
    # TODO CHECK IF YOU NEED THIS
    def assess_hand(self, hand):
        return hand.get_value()

# compares the hands of the passed players
    def compare_hands(self):
        best_hand = []
        best_value = 0
        for key in self.players.keys():
            current_player = self.players[key]
            current_player_value = current_player.get_value()
            if current_player.bust:
                continue
            elif best_hand is []:
                best_hand.append(current_player)
                best_value = current_player_value
                continue
            elif current_player_value >= best_value:
                # if equal to, going to append anyways, so do not need to do anything if equal to.
                if current_player_value == best_value:
                    pass
                elif current_player_value > best_value:
                    best_hand[:] = []
                    best_value = current_player_value
                best_hand.append(current_player)
        return best_hand

    # Deals a card to players passed
    def deal(self, *args):
        for player in args:
            player.hit(self.deck.pop())

    # A hits the player's hand. If they are bust, stops the game - public
    def hit(self, player_id):
        self.deal(self.players[player_id])
        if self.players[player_id].bust:
            self.check_game_over()

    # Stands, ends game. Public
    def stand(self, player_id):
        self.players[player_id].stand()

    # Prints the current state of the game - each hand followed by their current value.
    def display_game(self):
        print("Dealer:", end=" ")
        for card in self.dealer.hand:
            print(card, end = " ")
        print("\nPlayer:", end = " ")
        for card in self.player.hand:
            print(card, end = " ")
        p_total = self.assess_hand(self.player)
        print(str(p_total))

    # Calls all the methods associated with ending the game, and return winner
    def end_game(self):
        self.dealer.dealer_end()
        self.winner = self.compare_hands()
        return self.winner

    # check if everyone has bust or stood
    def check_game_over(self):
        all_bust_or_stood = True
        for key in self.players.keys():
            if self.players[key].bust_or_stood() is not True:
                all_bust_or_stood = False
                break
        if all_bust_or_stood:
            self.continue_game = False
        return all_bust_or_stood

class Hand:
    def __init__(self, id):
        self._id = id
        self._hand = []
        self.__has_stood = False
        self.bust = False
        self.blackjack = 21
        self.Royals = {  # Defines the values for the royals
            Royals.JACK: 10,
            Royals.QUEEN: 10,
            Royals.KING: 10,
            Royals.ACE: 11
        }

    @property
    def id(self):
        return self._id

    @property
    def hand(self):
        return self._hand

    @property
    def has_stood(self):
        return self.__has_stood

    # Only blackjack parent class will have access to the deck, will pass it to cards
    def hit(self, card):
        self.__hand.append(card)
        hand_value = self.get_value()
        if hand_value > self.blackjack:
            self.bust = True

    def stand(self):
        self.__has_stood = True

    # Calculate the total value of the passed hand (where hand is an array of cards)
    def get_value(self):
        total = 0
        noAces = 0
        for card in self.__hand:
            cValue = card.value
            if isinstance(cValue, Royals):
                cValue = self.Royals[cValue]
                if cValue == Royals.ACE:
                    noAces += 1
            total += cValue
        if noAces > 0:
            total = self.__choose_ace(total, noAces)
        return total

    # If bust, changes the ace to a 1.
    def __choose_ace(self, total, noAces):
        for _ in range(noAces):
            if total > self.blackjack:
                total -= 10
        return total

    def reset(self):
        self.__hand = []
        self.__has_stood = False
        self.bust = False

    def bust_or_stood(self):
        return self.bust or self.__has_stood

class Dealer_Hand(Hand):
    def __init__(self, id):
        super().__init__(id)

    def dealer_end(self, deck):
        while self.get_value() < 17:
            self.hit(deck.pop())

"""
    - Have a player class which creates a hand for each player and then passes this into the blackjack class
    - this could have game records and be used for the database side of the project
"""
class Player:
    pass

if __name__ == "__main__":
    player1 = Hand("player")
    player2 = Hand("player")
    dealer = Dealer_Hand("dealer")
    players = {
        "player1": player1,
        "player2": player2,
        "dealer": dealer
    }
    bj = Blackjack(players)


