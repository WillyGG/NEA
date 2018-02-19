from Deck import Deck
from Deck import Royals
from Structs.Circular_Queue import Circular_Queue

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
    def __init__(self, playersDict=None):
        self.deck = Deck()
        self._blackjack = 21 # The winning value
        self._winners = None
        self.auto_reset = False

        if playersDict is None:
            playersDict = {
                "dealer" : Dealer_Hand("dealer")
            }
        if bool(playersDict) is False or "dealer" not in playersDict.keys():
            playersDict["dealer"] = Dealer_Hand("dealer")

        # Hand for each player - Do i need this??
        self.players = playersDict

        # queue which holds the players, keeps track of whose turn it is
        # queue of player names (turn this into a queue of hand instances?
        self.players_queue = self.create_player_queue()

        self.continue_game = True # the way this is implemented is weird - maybe method with same purpose?
        self.deckIteration = self.deck.deckIteration
        self.new_cards = [] # each time a new card is added to the game this it is appended to here

        # Deals to each player
        self.init_deal()

    @property
    def winners(self):
        return self._winners

    def blackjack(self):
        return self._blackjack

    def create_player_queue(self):
        playerList = [self.players[key] for key in self.players.keys() if self.players[key].id != "dealer"]
        cQ = Circular_Queue(len(playerList))
        for player in playerList:
            cQ.push(player)
        return cQ

    def get_current_player(self):
        return self.players_queue.peek()
      
    # Reset the hands and the tracking variables
    def reset(self):
        for key in self.players.keys():
            self.players[key].reset()
        self.continue_game = True
        self.init_deal()
        self.players_queue = self.create_player_queue()
        self.new_cards = []

    def init_deal(self):
        for key in self.players.keys():
            for x in range(2):
                self.deal(self.players[key])

# compares the hands of the passed players
    def compare_hands(self):
        best_hand = []
        best_value = 0
        for key in self.players.keys():
            current_player = self.players[key]
            current_player_name = current_player.id
            current_player_value = current_player.get_value()
            if current_player.bust:
                continue
            elif best_hand is []:
                best_value = current_player_value
                best_hand.append(current_player_name)
                continue
            elif current_player_value >= best_value:
                # if equal to, going to append anyways, so do not need to do anything if equal to.
                if current_player_value == best_value:
                    pass
                elif current_player_value > best_value:
                    best_hand[:] = []
                    best_value = current_player_value
                best_hand.append(current_player_name)
        return best_hand

    # Deals a card to players passed
    def deal(self, *args):
        cardsHit = []
        for player in args:
            next_card = self.deck.pop()
            cardsHit.append(next_card)
            player.hit(next_card)
        self.dickIteration = self.deck.deckIteration

    # A hits the player's hand. If they are bust, stops the game - public
    def hit(self):
        current_player = self.players_queue.pop()
        self.deal(current_player)
        if current_player.bust:
            self.check_game_over()
        else:
            self.players_queue.push(current_player)

    # Stands, ends game. Public
    def stand(self):
        current_player = self.players_queue.pop()
        current_player.stand()
        self.check_game_over()

    # Prints the current state of the game - each hand followed by their current value.
    def display_game(self):
        for key in self.players.keys():
            currentPlayer = self.players[key]
            print(currentPlayer.id, end = " ")
            for card in currentPlayer.hand:
                print(card, end = " ")
            p_total = currentPlayer.get_value()
            print(str(p_total))

    # Calls all the methods associated with ending the game, and return winner
    def end_game(self):
        self.players["dealer"].dealer_end(self.deck) # Should this not be handled in this class?
        self._winners = self.compare_hands()
        if self.auto_reset:
            self.reset()
        return self._winners

    # check if everyone has bust or stood
    def check_game_over(self):
        if self.players_queue.isEmpty():
            self.continue_game = False
            #self.end_game() # end game manually
            return True
        return False

    def whoseTurnIsIt(self):
        player = self.players_queue.peek().id
        if player is None:
            return "game over man! game over!"
        return player

    # converts player queue to array and returns the ids of all players currently in play
    def get_all_players_playing(self):
        players = []
        while not self.players_queue.isEmpty():
            current_player = self.players_queue.pop()
            players.append(current_player)
        for player in players:
            self.players_queue.push(player)
        return players

class Hand:
    def __init__(self, id):
        self._id = id
        self._hand = []
        self.__has_stood = False
        self._bust = False
        self.blackjack = 21
        self.Royals = {  # Defines the values for the royals
            Royals.JACK: 10,
            Royals.QUEEN: 10,
            Royals.KING: 10,
            Royals.ACE: 11
        }

    @property # MAKE THIS A HASHED ID TO PREVENT CONFLICTS
    def id(self):
        return self._id

    @property
    def hand(self):
        return self._hand

    @property
    def has_stood(self):
        return self.__has_stood

    @property
    def bust(self):
        return self._bust

    # Only blackjack parent class will have access to the deck, will pass it to cards
    def hit(self, card):
        self._hand.append(card)
        hand_value = self.get_value()
        if hand_value > self.blackjack:
            self._bust = True

    def stand(self):
        self.__has_stood = True

    # Calculate the total value of the passed hand (where hand is an array of cards)
    def get_value(self):
        total = 0
        noAces = 0
        for card in self._hand:
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
        self._hand = []
        self.__has_stood = False
        self._bust = False

    def bust_or_stood(self):
        return self.bust or self.__has_stood

    def get_hand_size(self):
        return len(self._hand)

    def __str__(self):
        return self.id

    def __eq__(self, other):
        if not isinstance(other, Hand):
            return False
        return self.id == other.id

class Dealer_Hand(Hand):
    def __init__(self, id="dealer"):
        super().__init__(id)

    # should you not do this in the blackjack class?
    def dealer_end(self, deck):
        while self.get_value() < 17:
            self.hit(deck.pop())

"""
    - Have a player class which creates a hand for each player and then passes this into the blackjack class
    - this could have game records and be used for the database side of the project
"""
class Player:
    pass

class Blackjack_Tests:
    @staticmethod
    def setUp_Blackjack_Instance():
        player1 = Hand("mariusz")
        player2 = Hand("vince")
        dealer = Dealer_Hand("dealer")

        # testhand = Hand("mariusz")
        # print(testhand == player1)

        players = {
            "player1": player1,
            "player2": player2,
            "dealer": dealer
        }
        bj = Blackjack(players)
        return bj

    @staticmethod
    def manual_test():
        bj = Blackjack_Tests.setUp_Blackjack_Instance()
        for x in range(2):
            while bj.continue_game:
                bj.display_game()
                currPlayer = bj.whoseTurnIsIt()
                c = input("\n" + currPlayer + ": would you like to hit (h) or (s) ")
                if c is "h":
                    bj.hit()
                elif c is "s":
                    bj.stand()
                else:
                    print("please input h or s")
            bj.display_game()
            bj.end_game()
            print(bj.winners, "are the winners!")
            bj.reset()

    @staticmethod
    def get_players_playing_test():
        bj = Blackjack_Tests.setUp_Blackjack_Instance()
        for i in bj.get_all_players_playing():
            print(i)

if __name__ == "__main__":
    Blackjack_Tests.get_players_playing_test()


