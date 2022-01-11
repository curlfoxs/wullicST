from typing import Optional

from bst import BSTreeNode, WullicBST


class AVLTreeNode(BSTreeNode):
    def __init__(self, key=None, val=None, left=None, right=None):
        super().__init__(key, val, left, right)
        self.H = 1 # TODO factor?

class WullicAVL(WullicBST):
    def _height(self, tree: Optional[AVLTreeNode]):
        return tree.H if tree else 0

    def _cal_height(self, tree: Optional[AVLTreeNode]):
        return max(self._height(tree.left), self._height(tree.right)) + 1 if tree else 0

    def _factor(self, tree: Optional[AVLTreeNode]):
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
        if key < tree.key:
            tree.left = self._put(tree.left, key, val)
        elif tree.key < key:
            tree.right = self._put(tree.right, key, val)
        else:
            tree.val = val
        tree.N = self._cal_size(tree)
        # Prove it: Just one time rotatiton to balance BST in insert case.
        # TODO So it can be optimized to check one time, but make it correct first
        tree.H = self._cal_height(tree)
        factor = self._factor(tree)
        # Find the min unbalaced tree
        if factor > 1 and key < tree.left.key:
            # LL case
            # RotateRight
            tree = self._rotateRight(tree)
        elif factor > 1 and key > tree.left.key:
            # LR case
            # RotateLeft first
            tree.left = self._rotateLeft(tree.left)
            # RotateRight following
            tree = self._rotateRight(tree)
        elif factor < -1 and key > tree.right.key:
            # RR case
            # RoatteLeft
            tree = self._rotateLeft(tree)
        elif factor < -1 and key < tree.right.key:
            # RL case
            # RotateRight first
            tree.right = self._rotateRight(tree.right)
            # RotateLeft following
            tree = self._rotateLeft(tree)
        return tree

    # def _delete(self, tree: Optional[BSTreeNode], key: int) -> Optional[BSTreeNode]:
    #     if tree is None:
    #         return None
    #     # Find the node to be deleted
    #     # Avoid getting parent node, just find the node in one recurrsion, fantastic.
    #     if key < tree.key:
    #         tree.left = self._delete(tree.left, key)
    #     elif key > tree.key:
    #         tree.right = self._delete(tree.right, key)
    #     else:
    #         # Simplify the problem to delete the root node ~
    #         if tree.left is None:
    #             return tree.right
    #         elif tree.right is None:
    #             return tree.left
    #         # Simpplify the problem to delete the Min of right tree or the Max of left tree ~
    #         t = tree
    #         r = randint(0, 1)
    #         if r == 0:
    #             tree = self._min(tree.right)
    #             tree.right = self._deletemin(tree.right)
    #             tree.left = t.left
    #         else:
    #             tree = self._max(tree.left)
    #             tree.left = self._deletemax(tree.left)
    #             tree.right = t.right
    #     tree.N = self._size(tree.left) + self._size(tree.right) + 1
    #     return tree
