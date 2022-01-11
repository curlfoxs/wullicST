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
        if factor == 2 or factor == -2:
            if factor == 2:
            # Find the min unbalaced tree
                leftTree = tree.left
                if self._factor(leftTree) == 1:
                    # LL Rotate
                    tree.left = leftTree.right
                    leftTree.right = tree
                    tree = leftTree
                elif self._factor(leftTree) == -1:
                    # LR Rotate
                    # L rotate first
                    lrTree = leftTree.right
                    leftTree.right = lrTree.left
                    lrTree.left = leftTree
                    # R rotate following
                    tree.left = lrTree.right
                    lrTree.right =  tree
                    tree = lrTree
                else:
                    raise Exception("Something woosp~")
            elif factor == -2:
                rightTree = tree.right
                if self._factor(rightTree) == -1:
                    # RR Rotate
                    tree.right = rightTree.left
                    rightTree.left = tree
                    tree = rightTree
                elif self._factor(rightTree) == 1:
                    # RL Rotate
                    # R rotate first
                    rlTree = rightTree.left
                    rightTree.left = rlTree.right
                    rlTree.right = rightTree
                    # L rotate following
                    tree.right = rlTree.left
                    rlTree.left = tree
                    tree = rlTree
                else:
                    raise Exception("Something woosp~")
            # Cal height and size. TODO it could be optimized
            tree.left.H = self._cal_height(tree.left)
            tree.right.H = self._cal_height(tree.right)
            tree.H = self._cal_height(tree)
            tree.left.N = self._cal_size(tree.left)
            tree.right.N = self._cal_size(tree.right)
            tree.N = self._cal_size(tree)
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
