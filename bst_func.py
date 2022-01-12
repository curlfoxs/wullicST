from typing import Optional, Callable
from random import randint
from copy import deepcopy

class TreeNode:
    def __init__(self, key=None, val=None, left=None, right=None):
        self.key = key
        self.val = val
        self.left = left
        self.right = right

# Get TreeNode.key
def bst_key(tree: Optional[TreeNode]):
    return tree.key if tree else None

# Get TreeNode.val
def bst_val(tree: Optional[TreeNode]):
    return tree.val if tree else None

# Common method to get the minimum TreeNode of tree
def bst_min(tree: Optional[TreeNode]) -> TreeNode:
    if tree is None or tree.left is None:
        return tree
    return bst_min(tree.left)

# Common method to get the maximum TreeNode of tree
def bst_max(tree: Optional[TreeNode]) -> TreeNode:
    if tree is None or tree.right is None:
        return tree
    return bst_max(tree.right)

# Common method to get the TreeNode of given key
def bst_get(tree: Optional[TreeNode], key) -> Optional[TreeNode]:
    if tree is None:
        return None
    if key < tree.key:
        return bst_get(tree.left, key)
    elif tree.key < key:
        return bst_get(tree.right, key)
    else:
        return tree

# Common method to put the TreeNode(key, val) to tree and return the root node
def bst_put(tree: Optional[TreeNode], key, val, nodeType=TreeNode, maintainFunc: Optional[Callable]=None) -> Optional[TreeNode]:
    '''Insert a new TreeNode(key, val) to BSTree

    Args:
        tree (TreeNode): The root of BSTree to insert
        key (Object): key of TreeNode to insert
        val (Object): val of TreeNode to insert
        nodeType (class): Type class to build new TreeNode
        func (Function): Function to execute in recursion procedure to maintain BST feature

    Raises:
        RuntimeError

    Returns:
        Root of tree that has completed insertion
    '''
    if tree is None:
        return nodeType(key, val)
    if key < tree.key:
        tree.left = bst_put(tree.left, key, val, nodeType, maintainFunc)
    elif tree.key < key:
        tree.right = bst_put(tree.right, key, val, nodeType, maintainFunc)
    else:
        tree.val = val
    # Function Hook to Do More: Caculate size, height, color ...
    # Update TreeNode attribute
    if maintainFunc:
        tree = maintainFunc(tree)
    return tree

def bst_delete(tree: Optional[TreeNode], key, maintainFunc: Optional[Callable]=None) -> Optional[TreeNode]:
    '''Delete the TreeNode of given key

    Args:
        tree (TreeNode): The root of BSTree to delete
        key (Object): key of TreeNode to delete
        nodeType (class): class of TreeNode type to build new TreeNode
        func (Function): Function to execute in recursion procedure to maintain BST feature

    Raises:
        RuntimeError

    Returns:
        Root of tree that has completed deletion
    '''
    if tree is None:
        return None
    if key < tree.key:
        tree.left = bst_delete(tree.left, key, maintainFunc)
    elif key > tree.key:
        tree.right = bst_delete(tree.right, key, maintainFunc)
    else:
        if tree.left is None:
            return tree.right
        elif tree.right is None:
            return tree.left
        r = randint(0, 1)
        if r == 0:
            t = bst_min(tree.right)
            tree.right = bst_delete(tree.right, t.key)
        else:
            t = bst_max(tree.left)
            tree.left = bst_delete(tree.left, t.key)
        tree.key  = deepcopy(t.key)
        tree.val = deepcopy(t.val)
    if maintainFunc:
        tree = maintainFunc(tree)
    return tree

def bst_rotate_right(tree: Optional[TreeNode], updateAttr: Optional[Callable]=None) -> Optional[TreeNode]:
    x = tree.left
    tree.left = x.right
    x.right = tree
    if updateAttr:
        x = updateAttr(x, tree)
    return x

def bst_rotate_left(tree: Optional[TreeNode], updateAttr: Optional[Callable]=None) -> Optional[TreeNode]:
    x  = tree.right
    tree.right = x.left
    x.left = tree
    if updateAttr:
        x = updateAttr(x, tree)
    return x

def _display_aux(tree):
    """Returns list of strings, width, height, and horizontal coordinate of the root."""
    # No child.
    if tree.right is None and tree.left is None:
        line = '%s' % tree.key
        width = len(line)
        height = 1
        middle = width // 2
        return [line], width, height, middle

    # Only left child.
    if tree.right is None:
        lines, n, p, x = _display_aux(tree.left)
        s = '%s' % tree.key
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
        second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
        shifted_lines = [line + u * ' ' for line in lines]
        return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

    # Only right child.
    if tree.left is None:
        lines, n, p, x = _display_aux(tree.right)
        s = '%s' % tree.key
        u = len(s)
        first_line = s + x * '_' + (n - x) * ' '
        second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
        shifted_lines = [u * ' ' + line for line in lines]
        return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

    # Two children.
    left, n, p, x = _display_aux(tree.left)
    right, m, q, y = _display_aux(tree.right)
    s = '%s' % tree.key
    u = len(s)
    first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
    second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
    if p < q:
        left += [n * ' '] * (q - p)
    elif q < p:
        right += [m * ' '] * (p - q)
    zipped_lines = zip(left, right)
    lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
    return lines, n + m + u, max(p, q) + 2, n + u // 2
