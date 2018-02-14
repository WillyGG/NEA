"""
28 Dec:
    - Find a way to maintain the complete property from within the tree class
    - find a way to abstract away the pre/in/post order traversals
"""

class Binary_Tree:
    def __init__(self, rootNode=None):
        self._root = rootNode

    @property
    def root(self):
        return self._root

    def getNode(self, nodeValue):
        toPass = nodeValue
        if isinstance(nodeValue, Node):
            toPass = nodeValue.value

        def base_case(node):
            if node is None:
                return None
            return -1

        def node_processing(node):
            if node.value == toPass:
                return node
            return -1

        returnNode = Traversals.pre_order(self._root, base_case=base_case, node_processing=node_processing)
        #returnNode = self.getNodeTraversal(self._root, toPass)
        return returnNode

    def insert(self, node):
        if isinstance(node, int):
            node = Node(node)
        if self.getNode(node) is not None:
            return False
        if self._root is None:
            self._root = node
            return True

        nextNode = self._root
        nextParent = None
        lastParentLeft = True

        # Find a way to abstract this
        if node.value < nextNode.value:
            nextParent = nextNode
            nextNode = nextNode.left
            lastParentLeft = True
        elif node.value > nextNode.value:
            nextParent = nextNode
            nextNode = nextNode.right
            lastParentLeft = False
        while nextNode is not None:
            if node.value < nextNode.value:
                nextParent = nextNode
                nextNode = nextNode.left
                lastParentLeft = True
            elif node.value > nextNode.value:
                nextParent = nextNode
                nextNode = nextNode.right
                lastParentLeft = False
        if lastParentLeft:
            nextParent.left = node
        else:
            nextParent.right = node
        self.compareSubtrees()

    def getParent(self, nodeToFind):
        def base_case(node):
            if node is None:
                return None
            return -1
        def node_processing(node):
            if node.left == nodeToFind or node.right == nodeToFind:
                return node
            return -1

        return Traversals.pre_order(self._root, base_case=base_case, node_processing=node_processing)

    def get_tree_size(self):
        def base_case(node):
            if node is None:
                return 0
            return -1
        def node_processing(node, left, right):
            return (left + right + 1)
        return Traversals.post_order(self._root, base_case=base_case, node_processing=node_processing)

    def compareSubtrees(self):
        def base_case(node):
            if node is None:
                return 0
            return -1

        def node_processing(node, left, right):
            #print("node:",node)
            #print("left",left)
            #print("right",right)
            if left == -1 or right == -1:
                return -1
            elif abs(left - right) >= 2:
                if left > right:
                    self.swap_max_LST(node)
                else:
                    self.swap_min_RST(node)
                return -1
            return left + right + 1

        completed_comparing = -1
        while completed_comparing == -1:
            completed_comparing = Traversals.post_order(self._root, base_case=base_case, node_processing=node_processing)

    def swap_max_LST(self, swapRoot):
        """
        replace the parent with the max in LST
        - newRoot.right = oldRoot (oldRoot keeps left subtree)
        - if newRoot is direct parent
        return False to start again
        """
        max_LST = self.get_max_LST(swapRoot)
        parent = self.getParent(swapRoot)

        if swapRoot.left != max_LST:
            self.delete(max_LST) # one child guarenteed -> one call
            max_LST.left = swapRoot.left
        swapRoot.left = None # Will this break the subtree?
        max_LST.right = swapRoot

        if parent == None:
            self._root = max_LST
        else:
            parent.left = max_LST

    def swap_min_RST(self, swapRoot):
        """
        swap nodes:
        replace parent with minRST
                - newRoot.left <- oldRoot
                - if directChild then keep RST
                - else then newRoot.right <- OldRoot.Right
            return False to start again
        """
        # get -> delete -> swap
        min_RST = self.get_min_RST(swapRoot)
        parent = self.getParent(swapRoot)

        # if direct child, it keeps its old RST, and is not deleted before swapping
        if swapRoot.right != min_RST:
            self.delete(min_RST)
            min_RST.right = swapRoot.right
        swapRoot.right = None # Will this break the subtree?
        min_RST.left = swapRoot

        if parent == None:
            self._root = min_RST
        else:
            parent.right = min_RST

    def get_max_LST(self, root):
        current_node = root.left
        while current_node.right is not None:
            current_node = current_node.right
        # current_node.left, current_node.right = None, None
        return current_node

    def get_min_RST(self, root):
        current_node = root.right
        while current_node.left is not None:
            current_node = current_node.left
        return current_node

    def delete(self, node):
        nodeParent = self.getParent(node)
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
            max_LST = self.get_max_LST(node)

            # Recursively delete the old node from its old position, since it is the max node in left tree, it cannot
            # have a right child, therefore this will be called recursively once at max.
            self.delete(max_LST)
            max_LST.right = node.right
            if nodeIsLeft:
                nodeParent.left = max_LST
            else:
                nodeParent.right = max_LST

    # For a binary search tree, this should be in ascending order.
    def in_order_traversal(self, parent): # Always pass in the root node with initial call.
        if parent == None:
            return False
        self.in_order_traversal(parent.left)
        print(parent.value)
        self.in_order_traversal(parent.right)

    def clearTree(self):
        self._root = None

    """
        - finish this if you need to, however, probs not worth the time rn. You can manually check the structure
    
    def display_tree_structure(self):
        tree_size = self.get_tree_size(self._root)
        tree_queue = Circular_Queue(tree_size)
        tree_queue.push(self._root)
        power = 0
        while not tree_queue.isEmpty():
            if tree_queue.num_elements == (2 ** power):
                power += 1
                print()
            current_node = tree_queue.pop()
            if current_node.left is not None:
                tree_queue.push(current_node.left)
            if current_node.right is not None:
                tree_queue.push(current_node.right)
            print(current_node, end=" ")
    """

class Traversals:
    # Static higher level function for pre order traversals
    @staticmethod
    def pre_order(root, base_case, node_processing):
        base_result = base_case(root)
        if base_result != -1:  # need another base value (None, and False cannot be used) (maybe a false base object?)
            return base_result
        processing_result = node_processing(root)
        if processing_result != -1:
            return processing_result

        left = Traversals.pre_order(root.left, base_case, node_processing)
        right = Traversals.pre_order(root.right, base_case, node_processing)

        if left is not None:
            return left
        elif right is not None:
            return right

    @staticmethod
    def in_order(self):
        pass

    @staticmethod
    def post_order(root, base_case, node_processing):
        base_result = base_case(root)
        if base_result != -1:
            return base_result

        left = Traversals.post_order(root.left, base_case, node_processing)
        right = Traversals.post_order(root.right, base_case, node_processing)

        processing_result = node_processing(root, left, right)
        return processing_result


class Card_Binary_Tree(Binary_Tree):
    def __init__(self, rootNode=None):
        super().__init__(rootNode)

    def decrement(self, nodeValue):
        if nodeValue == None:
            return False
        elif isinstance(nodeValue, Node): # defensive programming?
            nodeValue = nodeValue.value

        # if node does not exist in the tree
        node_to_dec = self.getNode(nodeValue)
        if node_to_dec == None:
            return False

        elif node_to_dec.value == nodeValue:
            node_to_dec.countValue -= 1
            if node_to_dec.countValue == 0:
                self.delete(node_to_dec)
            return True

    # Counts number of cards at current value and larger (Greater than, equal to)
    def cardCountGTET(self, parent):
        total = parent.countValue
        GTturningNode = parent
        # If the passed parent is in left subtree, include count in right subtree and all of values above.
        # this is achieved by creating temp tree where parent is the root
        if parent.value < self._root.value:
            tmpTree = self.createCountingTree(parent)
            total += tmpTree.root.countValue
            GTturningNode = tmpTree.root.right
        total += self.totalCardCount(GTturningNode)
        return total

    # Post order traversal to count number of cards in a tree
    def totalCardCount(self, parent=False):
        if parent == False:
            parent = self._root
        def base_case(node):
            if node == None:
                return 0
            return -1
        def node_processing(node, left, right):
            return left + right + 1

        return Traversals.post_order(parent, base_case=base_case, node_processing=node_processing)

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
            # Make a copy of the node, just in case (inefficient)
            tmpParent = Card_Node(parent.value, parent.countValue) # This should not affect the node in the main tree, as python passes variables by value
            countTree.insert(tmpParent)
        self.populateCountTree(parent.left, countTree)
        self.populateCountTree(parent.right, countTree)

    # prints count values as well as node value
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
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return False

    def __str__(self):
        return str(self.value)

class Card_Node(Node):
    def __init__(self, value, countValue):
        super().__init__(value)
        self.countValue = countValue


# Testing the functionality
if __name__ == "__main__":
    node_value = 1
    insertion_arr = [2,3,4,5]
    b = Binary_Tree( Node(node_value) )
    for num in insertion_arr:
        print(num)
        b.insert( Node(num) )

    #print(b.getNode(3))

    print("6:", b.root)
    print("3:", b.root.left)
    print("9:", b.root.right)
    print(b.root.right.left )

    #print(b.root.right.left)
    #b.compareSubtrees()
    #print(b.root.left.right)


    #print(b.get_max_LST(b.root))
    #print(b.get_min_RST(b.root))
    #print(b.get_max_LST(b.root))

    ## print(b.getParent(8))


    #b.testfunc()
    #b.display_tree_structure()

 #   b.in_order_traversal(b.root)

    #b.decrement(Card_Node(3, 0))
    #print()
    #b.in_order_traversal(b.root)
    #print(b.root.left.countValue)