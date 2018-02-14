from Structs.Binary_Tree import Card_Binary_Tree
from Structs.Binary_Tree import Card_Node
from Blackjack import Blackjack
from Blackjack import Hand
from Blackjack import Dealer_Hand

# TODO Make blackjack interface for this AI, getting the data it needs, implement prediction functionality, and play functionality test and compare to NN based system. After that DOCUMENT.
class Counting_AI:
    def __init__(self, range_of_values, num_of_suits):
        self.rangeOfValues = range_of_values
        self.num_of_suits = num_of_suits
        self.CardRecord = Card_Binary_Tree()
        #self.populate_tree_complete(range_of_values, num_of_suits)
        self.populate_tree_auto_maintain(range_of_values, num_of_suits)

        # maybe find a way to not hard code these values? Or maybe it's fine
        self.maxCard = range_of_values[-1]
        self.minCard = range_of_values[0]

        # Change these parameters to change the behaviour of the CCAI
        # Chage these to personality parameters, then calculate these thresholds based on parameters
        self.thresholds = {
            "bust" : 0.5,
            "blackjack" : 0.2,
            "exceedDlrNoBust" : 0.3,
            "riskTolerance" : 1.3
        }

    def populate_tree_auto_maintain(self, range_of_values, num_of_suits):
        for value in range_of_values:
            # implement this in a nice way
            if value == 10:
                self.CardRecord.insert(Card_Node(value, num_of_suits * 3))
            else:
                self.CardRecord.insert( Card_Node(value, num_of_suits) )

    def init_tree(self):
        self.CardRecord.clearTree()
        self.populate_tree_auto_maintain(self.rangeOfValues, self.num_of_suits)

    def decrement_cards(self, *args):
        # Unpack the game state -> consider ACE
        for hand in args:
            for card in hand:
                # if card is ace -> ace decrement()
                # elif hand is royal -> royal decrement
                if card.isRoyal():
                    self.royal_decrement()
                elif card.isAce():
                    self.ace_decrement()
                else:
                    self.CardRecord.decrement(card.value)

    def ace_decrement(self):
        self.CardRecord.decrement(1)
        self.CardRecord.decrement(11)

    def royal_decrement(self):
        self.CardRecord.decrement(10)

    # Next few methods define the CCAI behaviour as well as calcualte the chances.

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
        hand = gameState[0]
        handValue = gameState[1]
        dealer_hand = gameState[2]
        dealerValue = gameState[3]

        self.decrement_cards(hand, dealer_hand)

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
        turningNode = self.CardRecord.getNode(nodeValue)
        if turningNode is None: # card needed for blackjack not in deck
            return 0
        # get total number of cards which will result in a blackjack
        numOfBlJaCards = turningNode.countValue
        totalNumofCards = self.CardRecord.totalCardCount() # Find a way to abstract this

        return numOfBlJaCards / totalNumofCards

    # Calculate the chance next hit will exceed dealer's hand
    def calcExceedDlrNoBust(self, handValue, dlrValue, bustChance = False):
        # Calc Chance to exceed dealer
        exceedValue = (dlrValue + 1) - handValue# Value needed to exceed the dealer's current hand/
        if (dlrValue - handValue) < 0: # hand already exceeds dealers
            return 1
        if exceedValue > self.maxCard:
            return 0
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
    def __init__(self, blackjackInstance, countInstance, CCAI_Hand):
        self.blackjack = blackjackInstance
        self.CCAI = countInstance
        self.CCAI_Hand = CCAI_Hand
        self.deck_iteration = self.blackjack.deckIteration

    def getGameState(self):
        playerHand = self.CCAI_Hand.hand
        dealerHand = self.blackjack.players["dealer"].hand
        playerValue = self.CCAI_Hand.get_value()
        dealerValue = self.blackjack.players["dealer"].get_value()
        return (playerHand, playerValue, dealerHand, dealerValue)

    def takeMove(self, chances = None):
        if self.deck_iteration != self.blackjack.deckIteration:
            self.CCAI.init_tree()
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
            CI.displayCardRecord()
            blackjack.display_game()
            gameState = CCAI_Interface.getGameState()
            chances = CI.calcChances(gameState)
            for key in chances.keys():
                print(key, chances[key])
            blackjack.reset()

if __name__ == "__main__":
    range_of_values = [1,2,3,4,5,6,7,8,9,10,11]
    number_of_suits = 4
    CI = Counting_AI(range_of_values, number_of_suits)

    print("6:", CI.CardRecord.root)
    print("3:", CI.CardRecord.root.left)
    print("9:", CI.CardRecord.root.right)

    Testing_Class.blackjackChanceTesting(CI, 100)

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

