from bst import *

class AVLTreeNode(BSTreeNode):
    def __init__(self, key=None, val=None, left=None, right=None):
        super().__init__(key, val, left, right)
        self.H = 1 # TODO factor?

class WullicAVL(WullicBST):
    def _height(self, tree: Optional[AVLTreeNode]):
        return tree.H if tree else 0

    def _cal_height(self, tree: Optional[AVLTreeNode]):
        return max(self._height(tree.left), self._height(tree.right)) + 1 if tree else 0

    def _cal_factor(self, tree: Optional[AVLTreeNode]):
        return self._height(tree.left) - self._height(tree.right)

    def _recal_info_afterRotateRight(self, preLeft, preRoot):
        preRoot.H = self._cal_height(preRoot)
        preLeft.H = self._cal_height(preLeft)

    def _recal_info_afterRotateLeft(self, preRight, preRoot):
        preRoot.H = self._cal_height(preRoot)
        preRight.H = self._cal_height(preRight)

    def _put(self, tree: Optional[AVLTreeNode], key, val) -> Optional[AVLTreeNode]:
        if tree is None:
            return AVLTreeNode(key, val)
        # BST common steps: keep basic feature
        if key < tree.key:
            tree.left = self._put(tree.left, key, val)
        elif tree.key < key:
            tree.right = self._put(tree.right, key, val)
        else:
            tree.val = val
        tree.N = self._cal_size(tree)
        # AVL steps: keep balanced feature
        # Prove it: Just one time rotatiton to balance BST in insert case.
        # TODO So it can be optimized to check one time, but make it correct first
        tree.H = self._cal_height(tree)
        factor = self._cal_factor(tree)
        # Find the min unbalaced tree
        if factor > 1 and key < tree.left.key:
            # LL case
            # RotateRight
            return self._rotateRight(tree)
        elif factor > 1 and key > tree.left.key:
            # LR case
            # RotateLeft first
            tree.left = self._rotateLeft(tree.left)
            # RotateRight following
            return self._rotateRight(tree)
        elif factor < -1 and key > tree.right.key:
            # RR case
            # RoatteLeft
            return self._rotateLeft(tree)
        elif factor < -1 and key < tree.right.key:
            # RL case
            # RotateRight first
            tree.right = self._rotateRight(tree.right)
            # RotateLeft following
            return self._rotateLeft(tree)
        return tree

    def _delete(self, tree: Optional[AVLTreeNode], key) -> Optional[AVLTreeNode]:
        # BST common steps: keep basic feature
        if tree is None:
            return None
        if key < tree.key:
            tree.left = self._delete(tree.left, key)
        elif tree.key < key:
            tree.right = self._delete(tree.right, key)
        else:
            if tree.left is None:
                return tree.right
            elif tree.right is None:
                return tree.left
            r = randint(0, 1)
            if r == 0:
                t = self._min(tree.right)
                tree.right = self._delete(tree.right, t.key)
            else:
                t = self._max(tree.left)
                tree.left = self._delete(tree.left, t.key)

            tree.key  = t.key # deepcopy(t.key)
            tree.val = t.val #deepcopy(t.val)
        tree.N = self._cal_size(tree)
        # AVL steps: keep balanced feature
        tree.H = self._cal_height(tree)
        factor = self._cal_factor(tree)
        # It just a little bit different with insertion
        if factor > 1 and self._cal_factor(tree.left) >= 0:
            return self._rotateRight(tree)
        elif factor > 1 and self._cal_factor(tree.left) < 0:
            tree.left = self._rotateLeft(tree.left)
            return self._rotateRight(tree)
        elif factor < -1 and self._cal_factor(tree.right) <= 0:
            return self._rotateLeft(tree)
        elif factor < -1 and self._cal_factor(tree.left) > 0:
            tree.right = self._rotateRight(tree.right)
            return self._rotateLeft(tree)
        return tree
