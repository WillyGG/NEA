BASE_VALUES = [None, 0]

# Static higher level function for pre order traversals
def pre_order(root, base_case, node_processing):
    base_result = base_case(root)
    if base_result not in Traversals.BASE_VALUES:  # need another base value (None, and False cannot be used)
        return base_result

    processing_result = node_processing(root)
    if processing_result in Traversals.BASE_VALUES:
        return processing_result

    left = Traversals.pre_order(root.left, base_case, node_processing)
    right = Traversals.pre_order(root.right, base_case, node_processing)

    toReturn = None
    if left not in Traversals.BASE_VALUES:
        toReturn = left
    elif right not in Traversals.BASE_VALUES:
        toReturn = right
    return toReturn


def in_order(self):
    pass

def post_order(root, base_case, node_processing):
    base_result = base_case(root)
    if base_result != -1:
        return base_case

    left = Traversals.post_order(root.left, base_case, node_processing)
    right = Traversals.post_order(root.right, base_case, node_processing)
    return node_processing(root, left, right)  # --> pass the node?

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


def count_nodes(self, node):
    if node is None:
        return 0
    left = self.count_nodes(node.left)
    right = self.count_nodes(node.right)
    return left + right + 1

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