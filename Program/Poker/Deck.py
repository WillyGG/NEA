from Stack import Stack
from enum import Enum
from random import shuffle

class Suits(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Royals(Enum):
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, suit, value):
        self.__suit = suit
        self.__value = value

    @property
    def value(self):
        return self.__value

    @property
    def suit(self):
        return self.__suit

    def __str__(self):
        return "{} {}".format(self.__suit, self.__value)

class Deck(Stack):
    def __init__(self):
        self.__DECK_SIZE = 52
        self.__suits = [suit for suit in Suits]
        self.__values = [num for num in range(2, 11)] + [royal for royal in Royals]
        super().__init__(self.__DECK_SIZE)
        self.init_deck()

    # Shuffled deck
    def init_deck(self):
        temp_deck = []
        for suit in self.__suits:
            for value in self.__values:
                temp_deck.append(Card(suit, value))
        shuffle(temp_deck)
        for card in temp_deck:
            self.push(card)

def display_and_empty(deck):
    while not deck.isEmpty:
        print(deck.pop())

if __name__ == "__main__":
    d = Deck()
