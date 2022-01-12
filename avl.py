from bst import *

class AVLTreeNode(BSTreeNode):
    def __init__(self, key=None, val=None, left=None, right=None):
        super().__init__(key, val, left, right)
        self.H = 1 # TODO factor?

class AVLTree(BSTree):
    def _TreeNodeType(self, key, val):
        '''Build a new TreeNode(key, val)

        Args:
            key (Object): key of TreeNode to build
            val (Object): val of TreeNode to build

        Returns:
            AVLTreeNode
        '''
        return AVLTreeNode(key, val)

    def _height(self, tree: Optional[AVLTreeNode]):
        return tree.H if tree else 0

    def _cal_height(self, tree: Optional[AVLTreeNode]):
        return max(self._height(tree.left), self._height(tree.right)) + 1 if tree else 0

    def _cal_factor(self, tree: Optional[AVLTreeNode]):
        return self._height(tree.left) - self._height(tree.right)

    def _updateAfterRotate(self, preChild: Optional[AVLTreeNode], preRoot: Optional[AVLTreeNode]) -> None:
        '''Update AVLTreeNode attribution after rotation

        Args:
            preChild (AVLTreeNode): The child node before rotation
            preRoot (AVLTreeNode): The root node before rotation

        Returns:
            None: Just update attribution of AVLTreeNode
        '''
        super()._updateAfterRotate(preChild, preRoot)
        preRoot.H = self._cal_height(preRoot)
        preChild.H = self._cal_height(preChild)


    def _put_maintain(self, tree: Optional[AVLTreeNode]) ->  Optional[AVLTreeNode]:
        '''Maintian good features of AVLTree in insertion procedure

        Args:
            tree (AVLTreeNode): The AVLTreeNode in insertion recursion

        Returns:
            RootNode that complete insertion and maintains good features that we want
        '''
        # AVL insertion: keep balanced feature
        # Prove it: Just one time rotatiton to balance BST in insert case.
        # TODO So it can be optimized to check one time, but make it correct first
        tree.H = self._cal_height(tree)
        factor = self._cal_factor(tree)
        # Find the min unbalaced tree
        if factor > 1 and key < tree.left.key:  # LL case
            tree = self._rotateRight(tree)  # RotateRight
        elif factor > 1 and key > tree.left.key:  # LR case
            tree.left = self._rotateLeft(tree.left)  # RotateLeft first
            tree = self._rotateRight(tree)  # RotateRight following
        elif factor < -1 and key > tree.right.key:  # RR
            tree =  self._rotateLeft(tree)  # RoatteLeft
        elif factor < -1 and key < tree.right.key:  # RL case
            tree.right = self._rotateRight(tree.right)  # RotateRight first
            tree = self._rotateLeft(tree)  # RotateLeft following
        return tree

    def _delete_maintain(self, tree: Optional[AVLTreeNode]) -> Optional[AVLTreeNode]:
        '''Maintian good features of AVLTree in deletion prodecure

        Args:
            tree (AVLTreeNode): The AVLTreeNode in deletion recursion

        Returns:
            RootNode that coomplete deletion and maintains good features that we want
        '''
        # AVL deletion: keep balanced feature
        tree.H = self._cal_height(tree)
        factor = self._cal_factor(tree)
        # Its four cases just a little bit different with insertion
        if factor > 1 and self._cal_factor(tree.left) >= 0:
            tree = self._rotateRight(tree)
        elif factor > 1 and self._cal_factor(tree.left) < 0:
            tree.left = self._rotateLeft(tree.left)
            tree = self._rotateRight(tree)
        elif factor < -1 and self._cal_factor(tree.right) <= 0:
            tree = self._rotateLeft(tree)
        elif factor < -1 and self._cal_factor(tree.left) > 0:
            tree.right = self._rotateRight(tree.right)
            tree = self._rotateLeft(tree)
        return tree
