"""
28 Dec:
    - Find a way to maintain the complete property from within the tree class
    - find a way to abstract away the pre/in/post order traversals

"""

class Binary_Tree:
    def __init__(self, rootNode):
        self._root = rootNode

    @property
    def root(self):
        return self._root

    # Recursively search via pre order traversal
    def getNode(self, parent, nodeValue):
        if parent.value == nodeValue:
            return parent
        elif parent == None:
            return False

        self.getNode(parent.left, nodeValue)
        self.getNode(parent.right, nodeValue)

    def insert(self, node):
        #print(node)
        parentNode = self._root
        nextParent = None
        lastParentLeft = True

        if node.value < parentNode.value:
            nextParent = parentNode.left
            lastParentLeft = True
        elif node.value > parentNode.value:
            nextParent = parentNode.right
            lastParentLeft = False
        while nextParent != None:
            parentNode = nextParent
            if node.value < parentNode.value:
                nextParent = parentNode.left
                lastParentLeft = True
            elif node.value > parentNode.value:
                nextParent = parentNode.right
                lastParentLeft = False
        if lastParentLeft:
            parentNode.left = node
        else:
            parentNode.right = node

    def delete(self, node, nodeParent):
        nodeIsLeft = nodeParent.left == node

        # No children
        if (not node.hasLeft() and not node.hasRight()):
            if nodeIsLeft:
                nodeParent.left = None
            else:
                nodeParent.right = None
        # Has one child
        elif (node.hasLeft() != node.hasRight()):
            childIsLeft = node.hasLeft()
            if nodeIsLeft:
                if childIsLeft:
                    nodeParent.left = node.left
                else:
                    nodeParent.left = node.right
            else:
                if childIsLeft:
                    nodeParent.right = node.left
                else:
                    nodeParent.right = node.right
        else:
            # Find max node in left subtree and replace the node to delete with it
            maxLeftNodeParent = node
            maxLeftNode = node.left
            nextNode = node.left
            while nextNode != None:
                if nextNode.hasRight():
                    maxLeftNodeParent = nextNode
                    maxLeftNode = nextNode.right
                    nextNode = nextNode.right
                else:
                    nextNode = None

            # Recursively delete the old node from its old position, since it is the max node in left tree, it cannot
            # have a right child, therefore this will be called recursively once at max.
            self.delete(maxLeftNode, maxLeftNodeParent)

            maxLeftNode.right = node.right
            if nodeIsLeft:
                nodeParent.left = maxLeftNode
            else:
                nodeParent.right = maxLeftNode

    # For a binary search tree, this should be in ascending order.
    def in_order_traversal(self, parent): # Always pass in the root node with initial call.
        if parent == None:
            return False
        self.in_order_traversal(parent.left)
        print(parent.value)
        self.in_order_traversal(parent.right)

    def clearTree(self, nodeParent):
        self.root = None

class Card_Binary_Tree(Binary_Tree):
    def __init__(self, rootNode):
        super().__init__(rootNode)

    def decrement(self, nodeValue):
        parentParent = None
        parent = self._root
        nextParent = None

        while parent != nodeValue and parent != None:
            if nodeValue < parent.value:
                nextParent = parent.left
            elif nodeValue > parent.value:
                nextParent = parent.right
            # Increment the Parents
            parentParent = parent
            parent = nextParent

        if parent == None:
            return False

        elif parent == nodeValue:
            parent.countValue -= 1
            if parent.countValue == 0:
                self.delete(parent, parentParent)

    # Counts number of cards at current value and larger (Greater than, equal to)
    def cardCountGTET(self, parent):
        total = 0
        turningNode = parent
        # If the passed parent is in left subtree, include count in right subtree.
        if parent.value < self._root.value:
            tmpTree = self.createCountingTree(parent)
            turningNode = tmpTree.root
        total += self.cardCountTraverse(turningNode)

    # Post order traversal to count number of cards in a tree
    def cardCountTraverse(self, parent):
        if parent == None:
            return 0
        leftTotal = self.postOrderTraversalCount(parent.left)
        rightTotal = self.postOrderTraversalCount(parent.right)
        return leftTotal + rightTotal + parent.countValue

    # When counting cards in left subtree, create a new subtree where the root is the turning node, then count everything on the right of this
    def createCountingTree(self, countRoot):
        countingTree = Card_Binary_Tree(countRoot)
        self.populateCountTree(self._root, countingTree)
        return countingTree

    def populateCountTree(self, parent, countTree):
        if parent == None:
            return False
        elif parent != countTree.root.value:
            tmpParent = parent # This should not affect the node in the main tree, as python passes variables by value
            tmpParent.left = None # Test to see if this messes with the recursion
            tmpParent.right = None
            countTree.insert(tmpParent)
        self.populateCountTree(parent.left, countTree)
        self.populateCountTree(parent.right, countTree)

class Node: # Association via composition
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def hasLeft(self):
        return (not self.left == None)

    def hasRight(self):
        return (not self.right == None)

    def hasChildren(self):
        return (not self.left == None) or (not self.right == None)

    def numOfChildren(self):
        num = 0
        if self.hasLeft():
            num += 1
        if self.hasRight():
            num += 1
        return num

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.value == other.value:
                return True
        return False

    def __str__(self):
        return str(self.value)

class Card_Node(Node):
    def __init__(self, value, countValue):
        super().__init__(value)
        self.countValue = countValue


# Testing the functionality
if __name__ == "__main__":
    b = Card_Binary_Tree(Card_Node(5, 4))
    b.insert(Card_Node(3, 1))
    b.insert(Card_Node(2, 1))
    b.insert(Card_Node(1, 1))
    b.insert(Card_Node(4, 1))

    b.insert(Card_Node(6, 1))
    b.in_order_traversal(b.root)

    b.decrement(Card_Node(3, 0))
    print()
    b.in_order_traversal(b.root)
    #print(b.root.left.countValue)
