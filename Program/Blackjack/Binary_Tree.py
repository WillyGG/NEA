"""
28 Dec:
    - Find a way to maintain the complete property from within the tree class
    - find a way to abstract away the pre/in/post order traversals

"""
from Circular_Queue import Circular_Queue


class Binary_Tree:
    def __init__(self, rootNode):
        self._root = rootNode

    @property
    def root(self):
        return self._root

    def getNode(self, nodeValue):
        toPass = nodeValue
        if isinstance(nodeValue, Node):
            toPass = nodeValue.value
        returnNode = self.getNodeTraversal(self._root, toPass)
        return returnNode

    # Recursively search via pre order traversal
    def getNodeTraversal(self, parent, nodeValue):
        if parent == None:
            return None
        elif parent.value == nodeValue:
            return parent

        leftResult = self.getNodeTraversal(parent.left, nodeValue)
        rightResult = self.getNodeTraversal(parent.right, nodeValue)

        if leftResult != None:
            return leftResult
        elif rightResult != None:
            return rightResult

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

    # TODO test
    def compareSubtrees(self):
        completed_comparing = False
        while not completed_comparing:
            self.compare_ST_Traverse(self._root, None)

    # TODO test
    def compare_ST_Traverse(self, currentNode, parent):
        if currentNode == None:
            return 0
        left = self.compare_ST_Traverse(currentNode.left, currentNode)
        right = self.compare_ST_Traverse(currentNode.right, currentNode)

        if left is False or right is False:
            return False

        elif abs(left - right) == 2: # should never be larger than two, as increment in steps of 1
            if left > right:
                """
                    replace the parent with the max in LST
                         - newRoot.right = oldRoot (oldRoot keeps left subtree)
                         - if newRoot is direct parent 
                    return False to start again
                """
                max_LST = self.get_max_LST(currentNode)
                parent.left = max_LST
                max_LST.right = currentNode
            # more in RST
            else:
                """
                    replace parent with minRST
                        - newRoot.left <- oldRoot
                        - if directChild then keep RST
                        - else then newRoot.right <- OldRoot.Right 
                    return False to start again
                """
                min_RST = self.get_min_RST(currentNode)
                parent.right = min_RST
                min_RST.left = currentNode
            currentNode.left, currentNode.right = None, None
            return False

        return left + right + 1

    # TODO test
    def get_max_LST(self, root):
        current_node = root.left
        while current_node.right is not None:
            current_node = current_node.right
        # current_node.left, current_node.right = None, None
        return current_node

    # TODO test
    def get_min_RST(self, root):
        current_node = root.right
        while current_node.left is not None:
            current_node = current_node.left
        return current_node

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
        self._root = None

    def get_tree_size(self, parent):
        if parent == None:
            return 0
        left = self.get_tree_size(parent.left)
        right = self.get_tree_size(parent.right)
        return left + right + 1

    def display_tree_structure(self):
        tree_size = self.get_tree_size(self._root)
        tree_queue = Circular_Queue(tree_size)
        tree_queue.push(self._root)
        power = 0

        while not tree_queue.isEmpty():
            current_node = tree_queue.pop()

            if tree_queue.num_elements == (2 ** power):
                power += 1
                print()

            if current_node.left != None:
                tree_queue.push(current_node.left)
            if current_node.right != None:
                tree_queue.push(current_node.right)
            print(current_node, end=" ")

    def testfunc(self):
        print(self._root)
        print(self._root.left)
        print(self._root.right)


class Card_Binary_Tree(Binary_Tree):
    def __init__(self, rootNode):
        super().__init__(rootNode)

    def decrement(self, nodeValue):
        if nodeValue == None:
            return False
        elif isinstance(nodeValue, Node):
            nodeValue = nodeValue.value

        parentParent = None
        parent = self._root
        nextParent = None

        while parent.value != nodeValue and parent != None:
            if nodeValue < parent.value:
                nextParent = parent.left
            elif nodeValue > parent.value:
                nextParent = parent.right
            # Increment the Parents
            parentParent = parent # make copy?
            parent = nextParent

        if parent == None:
            return False

        elif parent.value == nodeValue:
            parent.countValue -= 1
            if parent.countValue == 0:
                self.delete(parent, parentParent)
            return True

    # Counts number of cards at current value and larger (Greater than, equal to)
    def cardCountGTET(self, parent):
        total = parent.countValue
        GTturningNode = parent
        # If the passed parent is in left subtree, include count in right subtree.
        if parent.value < self._root.value:
            tmpTree = self.createCountingTree(parent)
            total += tmpTree.root.countValue
            GTturningNode = tmpTree.root.right
        total += self.cardCountTraverse(GTturningNode)
        return total

    def totalCardCount(self):
        return self.cardCountTraverse(self._root)

    # Post order traversal to count number of cards in a tree
    def cardCountTraverse(self, parent):
        if parent == None:
            return 0
        leftTotal = self.cardCountTraverse(parent.left)
        rightTotal = self.cardCountTraverse(parent.right)
        return leftTotal + rightTotal + parent.countValue

    # When counting cards in left subtree, create a new subtree where the root is the turning node, then count everything on the right of this
    def createCountingTree(self, countRoot):
        # make a copy of the node and then make a counting tree
        countNode = Card_Node(countRoot.value, countRoot.countValue)
        countingTree = Card_Binary_Tree(countNode)
        self.populateCountTree(self._root, countingTree)
        return countingTree

    # preorder traverse the tree to populate the count tree
    def populateCountTree(self, parent, countTree):
        if parent == None:
            return False
        elif parent.value != countTree.root.value:
            # Make a copy of the node, just incase (inefficient)
            tmpParent = Card_Node(parent.value, parent.countValue) # This should not affect the node in the main tree, as python passes variables by value
            countTree.insert(tmpParent)
        self.populateCountTree(parent.left, countTree)
        self.populateCountTree(parent.right, countTree)

    def in_order_traversal(self, parent):
        if parent == None:
            return False
        self.in_order_traversal(parent.left)
        print(parent.value, parent.countValue)
        self.in_order_traversal(parent.right)


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
    b = Binary_Tree( Node(6) )
    for num in [3,9,2,1,4,5,8,7,10,11]:
        b.insert( Node(num) )

    #b.testfunc()
    b.display_tree_structure()

 #   b.in_order_traversal(b.root)

    #b.decrement(Card_Node(3, 0))
    #print()
    #b.in_order_traversal(b.root)
    #print(b.root.left.countValue)
