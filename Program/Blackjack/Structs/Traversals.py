BASE_VALUES = [None, 0]

# Static higher level function for pre order traversals
def pre_order(root, base_case, node_processing):
    base_result = base_case(root)
    if base_result != -1:  # need another base value (None, and False cannot be used)
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

def in_order(self):
    pass


def post_order(root, base_case, node_processing):
    base_result = base_case(root)
    if base_result != -1:
        return base_result

    left = Traversals.post_order(root.left, base_case, node_processing)
    right = Traversals.post_order(root.right, base_case, node_processing)

    processing_result = node_processing(root, left, right)
    return processing_result  # --> pass the node?


# in order
# For a binary search tree, this should be in ascending order.
def in_order_traversal(self, parent): # Always pass in the root node with initial call.
    if parent == None:
        return False
    self.in_order_traversal(parent.left)
    print(parent.value)
    self.in_order_traversal(parent.right)

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