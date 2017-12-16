class Binary_Tree:
    def __init__(self, rootValue, rootCountValue):
        self.__root = Node(rootValue, rootCountValue)

    @property
    def root(self):
        return self.__root

    # TODO Fix this
    def insert(self, node):
        parentNode = self.__root
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

    def decrement(self, node):
        parent = self.__root
        nextParent = None

        while parent != node and parent != None:
            if node.value < parent.value:
                nextParent = parent.left
            if node.value > parent.value:
                nextParent = parent.right
            parent = nextParent

        if parent == None:
            return False

        elif parent == node:
            parent.countValue -= 1
            if parent.countValue == 0:
                self.delete(parent)

    # TODO complete delete
    def delete(self, node):
        maxLeft = 0


    # For a binary search tree, this should be in ascending order.
    def post_order_traversal(self, parent):
        if parent == None:
            return False
        self.post_order_traversal(parent.left)
        print(parent.value)
        self.post_order_traversal(parent.right)

class Node:
    def __init__(self, value, countValue):
        self.value = value
        self.countValue = countValue
        self.left = None
        self.right = None

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.value == other.value:
                return True
        return False


if __name__ == "__main__":
    b = Binary_Tree(3, 4)
    b.insert(Node(1, 3))
    b.insert(Node(5, 1))
    b.post_order_traversal(b.root)

    b.decrement(Node(1, 0))
    #print(b.root.left.countValue)
