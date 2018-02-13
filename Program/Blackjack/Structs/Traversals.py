#class Traversals:

# Static higher level function for pre order traversals
def pre_order(root, base_case, return_case):
    base_result = base_case(root)
    if base_result != -1: #need another base value (None, and False cannot be used)
        return base_result
    left = pre_order(root.left, base_case, return_case)
    right = pre_order(root.right, base_case, return_case)

    return return_case(left, right)


def pre_order_traverse(root, base_case, return_case):
    pass

def in_order(self):
    pass

def post_order(self):
    pass



# Recursively search via pre order traversal
def getNodeTraversal(self, parent, nodeValue):
    if parent == None:
        return None
    elif parent.value == nodeValue:
        return parent

    leftResult = self.getNodeTraversal(parent.left, nodeValue)
    rightResult = self.getNodeTraversal(parent.right, nodeValue)

    if leftResult is not None:
        return leftResult
    elif rightResult is not None:
        return rightResult
    return None

# pre-order
def getParentTraverse(self, parent, nodeToFind):
    if parent is None:
        return None
    if parent.left == nodeToFind or parent.right == nodeToFind:
        return parent
    left = self.getParentTraverse(parent.left, nodeToFind)
    right = self.getParentTraverse(parent.right, nodeToFind)
    if left is not None:
        return left
    elif right is not None:
        return right


#post-order
def compare_ST_Traverse(self, currentNode):
    if currentNode == None:
        return 0
    left = self.compare_ST_Traverse(currentNode.left)
    right = self.compare_ST_Traverse(currentNode.right)

    if left is False or right is False:
        return False
    elif abs(left - right) >= 2:
        if left > right:
            self.swap_max_LST(currentNode)
        else:
            self.swap_min_RST(currentNode)
        return False
    return left + right + 1

# in order
# For a binary search tree, this should be in ascending order.
def in_order_traversal(self, parent): # Always pass in the root node with initial call.
    if parent == None:
        return False
    self.in_order_traversal(parent.left)
    print(parent.value)
    self.in_order_traversal(parent.right)

# post order
def get_tree_size(self, parent):
    if parent == None:
        return 0
    left = self.get_tree_size(parent.left)
    right = self.get_tree_size(parent.right)
    return left + right + 1

# Post order traversal to count number of cards in a tree
def cardCountTraverse(self, parent):
    if parent == None:
        return 0
    leftTotal = self.cardCountTraverse(parent.left)
    rightTotal = self.cardCountTraverse(parent.right)
    return leftTotal + rightTotal + parent.countValue

"""
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
"""