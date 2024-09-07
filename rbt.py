from bst import *

RED = True
BLACK = False

class RBTreeNode(BSTreeNode):
    def __init__(self, key=None, val=None, left=None, right=None):
        super().__init__(key, val, left, right)
        self.color = RED

class RBTree(BSTree):
    def _treeNodeType(self, key, val):
        return RBTreeNode(key, val)

    def _isRed(self, tree):
        return tree.color == RED if tree else False

    def _updateAfterRotate(self, preChild: Optional[RBTreeNode], preRoot: Optional[RBTreeNode]) -> None:
        super()._updateAfterRotate(preChild, preRoot)
        tmp = preChild.color
        preChild.color = preRoot.color
        preRoot.color = tmp

    def flip_colors(self, tree):
        tree.left.color = BLACK
        tree.right.color = BLACK
        tree.color = RED

    @validKey
    def put(self, key, val=None):
        self.root = self._put(self.root, key, val)
        self.root.color = BLACK

    def _put_maintain(self, tree, key, val):
        if self._isRed(tree.right):
            tree = self._rotateLeft(tree)
        if (self._isRed(tree.left) and self._isRed(tree.left.left)):
            tree = self._rotateRight(tree)
        if self._isRed(tree.left) and self._isRed(tree.right):
            self.flip_colors(tree)
        return tree

    def notTwoLink(self, tree):
        return self._isRed(tree) or self._isRed(TreeNode.left)

    def isTwoLink(self, tree):
        return not self._isRed(tree) and not self._isRed(tree.left)

    def isLeaf(self, tree):
        return tree.left is None or tree.right is None

    @validKey
    def delete(self, key):
        self.root = self._delete(self.root, key)
        if self.root:
            self.root.color = BLACK

    def moveRedtoRight(self, tree):
        if self._isRed(tree.left.left): # 兄弟够借
            tree.right.color = RED
            tree = self._rotateRight(tree)
            tree.left.color = BLACK
        else: # 只能借父母
            tree.color = BLACK
            tree.left.color = RED
            tree.right.color = RED
        return tree

    def moveRedtoLeft(self, tree):
        if self._isRed(tree.right.left): # 兄弟够借
            tree.left.color = RED
            tree.right = self._rotateRight(tree.right)
            tree = self._rotateLeft(tree)
            tree.right.color = BLACK
        else: # 只能借父母
            tree.color = BLACK
            tree.left.color = RED
            tree.right.color = RED
        return tree

    def _delete(self, tree, key):
        if tree is None:
            return None
        if key < tree.key:
            if not self.isLeaf(tree) and self.isTwoLink(tree.left):
                tree = self.moveRedtoLeft(tree)
            tree.left = self._delete(tree.left, key)
        else:
            if tree.right is None:
                if key == tree.key: # Leaf Node
                    if tree.left:
                        tree.left.color = BLACK
                    return tree.left
                return tree
            if self._isRed(tree.left):
                 tree = self._rotateRight(tree)
            if self.isTwoLink(tree.right):
                tree = self.moveRedtoRight(tree)
            if key == tree.key:
                t = tree
                tree = self._min(t.right)
                tree.right = self._delete(t.right, tree.key) # 无论如何我们要往右走最小的successor
                tree.left = t.left # 在后头
                tree.color = t.color
            else:
                tree.right = self._delete(tree.right, key)
        tree.N = self._cal_size(tree)
        # Unbalance case only Two:
        # 1. one-right red link
        # 2. left-ringt red links
        if self._isRed(tree.left) and self._isRed(tree.right):
            self.flip_colors(tree)
        if self._isRed(tree.right):
            tree = self._rotateLeft(tree)
        return tree

    # Testing
    def show_path_length(self):
        self.m = 0
        self.h = 0
        self.com = -1
        def trl(t, l):
            if t is None:
                if self.h > self.m:
                    self.m = self.h
                return
            if t.left is None and t.right is None:
                if self.com == -1:
                    self.com = l
                else:
                    assert self.com == l, " Whhos, {0} != {1}, It's not a rbt!".format(l, self.com)
                print(t.key, l)
            self.h += 1
            cnt = 0 if self._isRed(t.left) else 1
            trl(t.left, l+cnt)
            cnt = 0 if self._isRed(t.right) else 1
            trl(t.right, l+cnt)
            self.h -= 1
        trl(self.root, 0)
        # print('Tree high = ' + str(self.m))

    # Testing
    def destory_rbt(self):
        for _ in range(self.size()):
            k = randint(0, self.size()-1)
            self.delete(self.select(k))
            # self.display()
            self.show_path_length()
