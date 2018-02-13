from Structs.Binary_Tree import Card_Binary_Tree
from Structs.Binary_Tree import Card_Node
from Blackjack import Blackjack

# TODO Make blackjack interface for this AI, getting the data it needs, implement prediction functionality, and play functionality test and compare to NN based system. After that DOCUMENT.
class Counting_AI:
    def __init__(self, range_of_values, num_of_suits):
        self.rangeOfValues = range_of_values
        self.num_of_suits = num_of_suits
        self.CardRecord = None
        self.populate_tree_complete(range_of_values, num_of_suits)

        # maybe find a way to not hard code these values? Or maybe it's fine
        self.maxCard = 11
        self.minCard = 1

        # Change these parameters to change the behaviour of the CCAI
        # Chage these to personality parameters, then calculate these thresholds based on parameters
        self.thresholds = {
            "bust" : 0.5,
            "blackjack" : 0.2,
            "exceedDlrNoBust" : 0.3,
            "riskTolerance" : 1.3
        }

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
                self.CardRecord.decrement(card.value)

    # return True if wanting to hit
    def getNextAction(self, chances):
        # not exceeding the dealer, hit.
        belowDealer = (chances["exceedDlrNoBust"] < 1)
        belowBustThreshold = chances["bust"] <= self.thresholds["bust"]
        highBlackjackChance = chances["backjack"] >= self.thresholds["blackjack"]

        if belowDealer or belowBustThreshold:
            return True
        elif highBlackjackChance:
            belowRiskyBustThreshold = chances["bust"] <= self.thresholds["bust"]*self.thresholds["riskTolerance"]
            if belowRiskyBustThreshold:
                return True
        return False

    """
        - calcDealerExceeds?
    """

    # Calculates the probabilities of different critical scenarios. These are used to determine the next move.
    def calcChances(self, gameState):
        handValue = gameState[2]
        dealerValue = gameState[3]

        bustChance = self.calcBustChance(handValue)
        blackjackChance = self.calcBlJaChance(handValue)
        exceedDealerNoBust = self.calcExceedDlrNoBust(handValue, dealerValue)

        chances = {
            "bust" : bustChance,
            "blackjack" : blackjackChance,
            "exceedDlrNoBust" : exceedDealerNoBust
        }

        return chances

    # Calc chance next hit will result in bust.
    def calcBustChance(self, handValue):
        nodeValue = (22 - handValue)
        if nodeValue > self.maxCard: # If cannot go bust
            return 0
        elif nodeValue <= 0:
            return 1 # already bust
        turningNode = self.CardRecord.getNode(nodeValue)
        # Get total number of cards in right subtree of turning node
        numOfBustCards = self.CardRecord.cardCountGTET(turningNode)
        totalNumofCards = self.CardRecord.totalCardCount()

        return numOfBustCards / totalNumofCards

    # Calculate chance next hit will result in blackjack
    def calcBlJaChance(self, handValue):
        nodeValue = (21 - handValue)
        if nodeValue > self.maxCard:
            return 0 # Cannot get blackjack
        elif nodeValue == 0:
            return 1 #already blackjack'd
        turningNode = self.CardRecord.getNode(nodeValue) # Sometime returns none?????
        # get total number of cards which will result in a blackjack
        numOfBlJaCards = turningNode.countValue
        totalNumofCards = self.CardRecord.totalCardCount() # Find a way to abstract this

        return numOfBlJaCards / totalNumofCards

    # Calculate the chance next hit will exceed dealer's hand
    def calcExceedDlrNoBust(self, handValue, dlrValue, bustChance = False):
        # Calc Chance to exceed dealer
        if (dlrValue - handValue) < 0: # hand already exceeds dealers
            return 1
        exceedValue = (dlrValue + 1) - handValue # Value needed to exceed the dealer's current hand/
        turningNode = self.CardRecord.getNode(exceedValue)
        numOfExceed = self.CardRecord.cardCountGTET(turningNode)
        totalCards = self.CardRecord.totalCardCount()
        exceedChance = numOfExceed / totalCards
        if not bustChance: # option to pass in the bustChance, for efficiency
            bustChance = self.calcBustChance(handValue)
        return exceedChance - bustChance

    def getHandValue(self, hand):
        value = 0
        for card in hand:
            value += card.value
        return value

    def displayCardRecord(self):
        self.CardRecord.in_order_traversal(self.CardRecord.root)

# Interface between the game and the counting card AI.
class Counting_Interface:
    def __init__(self, blackjackInstance, countInstance):
        self.blackjack = blackjackInstance
        self.CCAI = countInstance

    def getGameState(self):
        playerHand = self.blackjack.player
        dealerHand = self.blackjack.dealer
        playerValue = self.blackjack.assess_hand(playerHand)
        dealerValue = self.blackjack.assess_hand(dealerHand)
        return (playerHand, dealerHand, playerValue, dealerValue)

    def takeMove(self, chances = None):
        if chances == None:
            self.CCAI.calcChances(self.getGameState())

# Test Functions - might as well just do unit testing???
class Testing_Class:
    def leftDecrementTest(self, CI):
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.left.left))
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.left.left))

    def rightDecrementTest(self, CI):
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))
        CI.CardRecord.decrement(CI.CardRecord.root.right.right)
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))

    def decUntilDeleteTest(self, CI):
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))
        for x in range(4):
            CI.CardRecord.decrement(CI.CardRecord.root.right.right)
        print(CI.CardRecord.cardCountGTET(CI.CardRecord.root.right.right))
        CI.CardRecord.in_order_traversal(CI.CardRecord.root)

    def blackjackChanceTesting(self, CI, testIters):
        blackjack = Blackjack()
        CCAI_Interface = Counting_Interface(blackjack, CI)

        # Get the game state then clac chances
        for x in range(testIters):
            print()
            CI.displayCardRecord()
            blackjack.reset()
            blackjack.display_game()
            gameState = CCAI_Interface.getGameState()
            chances = CI.calcChances(gameState)
            for key in chances.keys():
                print(key, chances[key])

if __name__ == "__main__":
    range_of_values = [1,2,3,4,5,6,7,8,9,10,11]
    number_of_suits = 4
    CI = Counting_AI(range_of_values, number_of_suits)
    CI.CardRecord.display_tree_structure()

    """
    range_of_values = [1,2,3,4,5,6,7,8,9,10,11]
    number_of_suits = 4
    CI = Counting_AI(range_of_values, number_of_suits)
    test = Testing_Class()
    totalNumofCards = CI.CardRecord.totalCardCount()
    #print(totalNumofCards)
    
    #test.decUntilDeleteTest(CI)
    test.blackjackChanceTesting(CI, 5)
    """

