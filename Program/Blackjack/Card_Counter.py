import sys, os
sys.path.append(os.path.realpath("./Structs"))
from Card_Binary_Tree import Card_Binary_Tree
from Card_Binary_Tree import Card_Node
from Blackjack import Blackjack
from Blackjack import Hand
from Blackjack import Dealer_Hand

class Card_Counter:
    def __init__(self, range_of_values=None, num_of_suits=None):
        if range_of_values is None:
            self.rangeOfValues = [1,2,3,4,5,6,7,8,9,10,11]
        else:
            self.rangeOfValues = range_of_values
        if num_of_suits is None:
            self.num_of_suits = 4
        else:
            self.num_of_suits = num_of_suits
        self.deckIteration = 1
        self.CardRecord = Card_Binary_Tree()
        self.populate_tree_auto_maintain(self.rangeOfValues, self.num_of_suits)

        # maybe find a way to not hard code these values? Or maybe it's fine
        self.maxCard = self.rangeOfValues[-1]
        self.minCard = self.rangeOfValues[0]

    def populate_tree_auto_maintain(self, range_of_values, num_of_suits):
        for value in range_of_values:
            # implement this in a nice way
            #print(value)
            if value == 10:
                self.CardRecord.insert(Card_Node(value, num_of_suits * 4))
            else:
                self.CardRecord.insert( Card_Node(value, num_of_suits) )

    def init_tree(self):
        self.CardRecord.clearTree()
        self.populate_tree_auto_maintain(self.rangeOfValues, self.num_of_suits)
        self.deckIteration += 1

    def decrement_cards(self, *args):
        # Unpack the game state and decrement records
        deckUpdated = False
        newCards = []
        for hand in args:
            for card in hand:
                result = self.decrement_card(card)
                # if the deck has reset half way through the game, take these new cards and decrement them later
                # so that the records are all accurate for which card has been played
                if result == False:
                    deckUpdated = True
                    newCards.append(card)
        if deckUpdated:
            self.init_tree()
            self.decrement_cards(newCards)

        # if tree is fully empty
        elif self.CardRecord.root == None:
            self.init_tree()

    def decrement_card(self, card):
        if card.isRoyal():
            result = self.royal_decrement()  # update this so result does not have to be on 3 lines
        elif card.isAce():
            result = self.ace_decrement()
        else:
            result = self.CardRecord.decrement(card.value)
        return result

    def ace_decrement(self):
        result1 = self.CardRecord.decrement(1)
        result2 = self.CardRecord.decrement(11)
        return result1 or result2

    def royal_decrement(self):
        return self.CardRecord.decrement(10)

    # Next few methods define the CCAI behaviour as well as calcualte the chances.
    """
        - calcDealerExceeds?
    """

    # Calculates the probabilities of different critical scenarios. These are used to determine the next move.
    def calcChances(self, handValue, winning_value):
        bustChance = self.calcBustChance(handValue)
        blackjackChance = self.calcBlJaChance(handValue)
        alreadyExceeding = self.getExceedingWinningPlayer(handValue, winning_value)
        # if the ai tied to this card counter is winning
        if alreadyExceeding:
            exceedWinningPlayer = 1
        else:
            exceedWinningPlayer = self.calcExceedWinningPlayer(handValue, winning_value)

        chances = {
            "bust": bustChance,
            "blackjack": blackjackChance,
            "exceedWinningPlayer": exceedWinningPlayer,
            "alreadyExceedingWinningPlayer": alreadyExceeding
        }
        return chances

    # maybe convert this to a margin
    def getExceedingWinningPlayer(self, handValue, wnrValue):
        return handValue > wnrValue

    # Calc chance next hit will result in bust.
    def calcBustChance(self, handValue):
        nodeValue = (22 - handValue)
        if nodeValue > self.maxCard: # If cannot go bust
            return 0
        elif nodeValue <= 0:
            return 1 # already bust

        minExceedValue = int(nodeValue)
        turningNode = self.CardRecord.getNode(nodeValue)
        # if turning node is not available, will look for the next card up, until it finds one, or not possible
        while turningNode is None and minExceedValue <= self.maxCard:
            minExceedValue += 1
            turningNode = self.CardRecord.getNode(minExceedValue)
        if turningNode is None:
            return 0 # cannot go bust, because card needed is higher than highest card in play

        # Get total number of cards in right subtree of turning node
        numOfBustCards = self.CardRecord.cardCountGTET(turningNode)
        totalNumofCards = self.CardRecord.totalCardCount()
        return numOfBustCards / totalNumofCards

    # Calculate chance next hit will result in blackjack
    def calcBlJaChance(self, handValue):
        nodeValue = (21 - handValue)
        turningNode = self.CardRecord.getNode(nodeValue)
        if nodeValue > self.maxCard or turningNode is None:
            return 0 # Cannot get blackjack - either card needed is too large, or card needed is not in deck
        elif nodeValue == 0:
            return 1 #already blackjack'd
        # get total number of cards which will result in a blackjack
        numOfBlJaCards = turningNode.countValue
        totalNumofCards = self.CardRecord.totalCardCount() # Find a way to abstract this
        return numOfBlJaCards / totalNumofCards

    def calcExceedWinningPlayer(self, handValue, wnrValue):
        # Calc Chance to exceed dealer
        exceedValue = (wnrValue + 1) - handValue  # Value needed to exceed the dealer's current hand/
        if (wnrValue - handValue) <= 0:  # hand already exceeds dealers, or is equal to dealer's
            return 1
        elif exceedValue > self.maxCard:
            return 0

        minExceedValue = int(exceedValue)
        turningNode = self.CardRecord.getNode(exceedValue)
        # if turning node is not available, will look for the next card up, until it finds one, or not possible
        while turningNode is None and minExceedValue <= self.maxCard:
            minExceedValue += 1
            turningNode = self.CardRecord.getNode(minExceedValue)
        if turningNode is None:  # no cards available to provide the value needed
            return 0

        numOfExceed = self.CardRecord.cardCountGTET(turningNode)
        totalCards = self.CardRecord.totalCardCount()
        exceedChance = numOfExceed / totalCards
        return exceedChance

    def displayCardRecord(self):
        self.CardRecord.in_order_traversal(self.CardRecord.root)

# Interface between the game and the counting card AI.
class Counting_Interface:
    def __init__(self, blackjackInstance, countInstance, CCAI_Hand):
        self.blackjack = blackjackInstance
        self.CCAI = countInstance
        self.CCAI_Hand = CCAI_Hand

    def getGameState(self):
        playerHand = self.CCAI_Hand.hand
        dealerHand = self.blackjack.players["dealer"].hand
        playerValue = self.CCAI_Hand.get_value()
        dealerValue = self.blackjack.players["dealer"].get_value()
        return (playerHand, playerValue, dealerHand, dealerValue)

    def takeMove(self, chances = None):
        if chances == None:
            self.CCAI.calcChances(self.getGameState())


# Test Functions - might as well just do unit testing???
class Testing_Class:
    @staticmethod
    def leftDecrementTest( CI):
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.left.left))
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.left.left))

    @staticmethod
    def rightDecrementTest(CI):
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))
        CI.CardRecord.decrement(CI.CardRecord.root.right.right)
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))

    @staticmethod
    def decUntilDeleteTest(CI):
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))
        for x in range(4):
            CI.CardRecord.decrement(CI.CardRecord.root.right.right)
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))
        CI.CardRecord.in_order_traversal(CI.CardRecord.root)

    @staticmethod
    def blackjackChanceTesting(CI, testIters):
        CCAI_Hand = Hand("CC_AI")
        players = {
            "CC_AI" : CCAI_Hand,
            "dealer" : Dealer_Hand("dealer")
        }
        blackjack = Blackjack(players)
        CCAI_Interface = Counting_Interface(blackjack, CI, CCAI_Hand)
        # Get the game state then calc chances
        for x in range(testIters):
            print()

            blackjack.display_game()
            gameState = CCAI_Interface.getGameState()

            hand = gameState[0]
            handValue = gameState[1]
            dealer_hand = gameState[2]
            dealerValue = gameState[3]
            AI_Winning = hand == dealer_hand

            CI.decrement_cards(hand, dealer_hand)
            CI.displayCardRecord()
            chances = CI.calcChances(hand, handValue, dealer_hand, dealerValue, AI_Winning)
            for key in chances.keys():
                print(key, chances[key])
            blackjack.reset()

if __name__ == "__main__":
    range_of_values = [1,2,3,4,5,6,7,8,9,10,11]
    number_of_suits = 4
    CI = Card_Counter(range_of_values, number_of_suits)

    print("6:", CI.CardRecord.root)
    print("3:", CI.CardRecord.root.left)
    print("9:", CI.CardRecord.root.right)

    Testing_Class.blackjackChanceTesting(CI, 20)

    """
    range_of_values = [1,2,3,4,5,6,7,8,9,10,11]
    number_of_suits = 4
    CI = Card_Counter(range_of_values, number_of_suits)
    test = Testing_Class()
    totalNumofCards = CI.CardRecord.totalCardCount()
    #print(totalNumofCards)
    
    #test.decUntilDeleteTest(CI)
    test.blackjackChanceTesting(CI, 5)
    """

