class Binary_Tree:
    def __init__(self, rootNode):
        self._root = rootNode

    @property
    def root(self):
        return self._root

    # TODO Fix this???? IS IT EVEN BROKEN
    def insert(self, node):
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
    def post_order_traversal(self, parent):
        if parent == None:
            return False
        self.post_order_traversal(parent.left)
        print(parent.value)
        self.post_order_traversal(parent.right)

class Card_Binary_Tree(Binary_Tree):
    def __init__(self, rootNode):
        super().__init__(rootNode)

    def decrement(self, node):
        parentParent = None
        parent = self._root
        nextParent = None

        while parent != node and parent != None:
            if node.value < parent.value:
                nextParent = parent.left
            elif node.value > parent.value:
                nextParent = parent.right
            # Increment the Parents
            parentParent = parent
            parent = nextParent

        if parent == None:
            return False

        elif parent == node:
            parent.countValue -= 1
            if parent.countValue == 0:
                self.delete(parent, parentParent)

class Node:
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

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.value == other.value:
                return True
        return False

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
    b.post_order_traversal(b.root)

    b.decrement(Card_Node(3, 0))
    print()
    b.post_order_traversal(b.root)
    #print(b.root.left.countValue)
