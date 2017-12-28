from Blackjack import Blackjack
from Binary_Tree import Card_Binary_Tree
from Binary_Tree import Card_Node

# TODO Make blackjack interface for this AI, getting the data it needs, implement prediction functionality, and play functionality test and compare to NN based system. After that DOCUMENT.
class Counting_AI:
    def __init__(self, range_of_values, num_of_suits):
        self.rangeOfValues = range_of_values
        self.num_of_suits = num_of_suits
        self.populate_tree_complete(range_of_values, num_of_suits)

        self.bustChance = 0
        self.blackjackChance = 0
        self.exceedDealerChance = 0


    # TODO maintain this from the tree class
    # Populate the tree in such a way that maintains a complete structure for the binary tree.
    def populate_tree_complete(self, range_of_values, num_of_suits):
        middle_value = range_of_values[len(range_of_values) // 2]  # Gets the middle value.
        self.CardRecord = Card_Binary_Tree(Card_Node(middle_value, num_of_suits))
        # Populate the card record with each possible value and how many of each card are in the deck, in a binary way.
        middle_ind = len(range_of_values) // 2
        start_ind = 0
        end_ind = len(range_of_values)-1

        first_half_middle = (start_ind + middle_ind) // 2
        second_half_middle = (middle_ind + end_ind + 1) // 2  # + 1 because the middle value has already been inserted

        i = first_half_middle
        j = second_half_middle

        # Figure out how to abstract this away
        while i >= 0 and j >= (middle_ind + 1):
            self.CardRecord.insert( Card_Node(range_of_values[i], num_of_suits) )
            self.CardRecord.insert( Card_Node(range_of_values[j], num_of_suits) )
            i -= 1
            j -= 1
        i = first_half_middle + 1
        j = second_half_middle + 1
        while i < middle_ind and j <= end_ind:
            self.CardRecord.insert( Card_Node(range_of_values[i], num_of_suits) )
            self.CardRecord.insert( Card_Node(range_of_values[j], num_of_suits) )
            i += 1
            j += 1

    def init_tree(self):
        self.CardRecord.clearTree()
        self.populate_tree_complete(self.rangeOfValues, self.num_of_suits)

    def decrement_cards(self, gameState):
        # Unpack the game state
        for hand in gameState:
            for card in hand:
                self.CardRecord.decrement(card.value)#

    """
        - calcBust:
            - Traverse Tree unti find "turning node", then take the chance of drawing that and everything in r subtree
        - calcBlackjack
            - same as calcBust, but for that single node
        - calcExceedDealer w/o bust:
            - same as calcBust, - bustChance
        - calcDealerExceeds?
    """
    def calcChances(self, gameState):
        pass

    def calcBustChance(self, playerHand):
        handValue = self.getHandValue(playerHand)
        turningNode = self.CardRecord.getNode(21 - handValue)
        # Get total number of cards in right subtree of turning node
        numOfBustCards = self.CardRecord.cardCount(turningNode.right)
        totalNumofCards = self.CardRecord.cardCount(self.CardRecord.root)

        return numOfBustCards / totalNumofCards

    def getHandValue(self, hand):
        value = 0
        for card in hand:
            value += card.value
        return value

class Counting_Interface:
    def __init__(self, blackjackInstance):
        self.blackjack = blackjackInstance

    def getGameState(self):
        playerHand = self.blackjack.player
        dealerHand = self.blackjack.dealer
        return (playerHand, dealerHand)



if __name__ == "__main__":
    range_of_values = range(1, 12)
    number_of_suits = 4
    CI = Counting_AI(range_of_values, number_of_suits)

