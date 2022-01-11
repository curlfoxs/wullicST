from typing import Optional

from random import randint
from copy import deepcopy

from bst_func import *

class BSTreeNode(TreeNode):
    def __init__(self, key=None, val=None, left=None, right=None):
        super().__init__(key, val, left, right)
        self.N = 1

class BSTree:
    ''' A Binary Search Tree reasonable implementation '''
    def __init__(self):
        self.root = None

    # Check the key object whether comparable
    def is_comparable(self, obj) -> bool:
         cls = obj.__class__
         return cls.__lt__ != object.__lt__ or \
             cls.__gt__ != object.__gt__

    def check_validkey(self, key):
        '''We should check the key object whether valid
        If BST is empty, key object must be comparable
        If BST is not empty, key object must be instance of existed key object's __class__
        '''
        if key is None:
            raise TypeError("Key is None!")
        if not self.empty():
            nodeType = self.select(0).__class__
            if not isinstance(key, nodeType):
                raise TypeError("Existed key isinstance of {1}. But {0} is not!".format(key, nodeType))
        else:
            if not self.is_comparable(key):
                raise TypeError("{} is not comparable!".format(key))

    # # tmp code
    # def copytree_tmp(self, tree, keyname, valname):
    #     # For basic testing
    #     if tree:
    #         self.put(getattr(tree, keyname), getattr(tree, valname))
    #         self.copytree(tree.left, keyname, valname)
    #         self.copytree(tree.right, keyname, valname)

    # tmp code
    def get_tmp(self, key) -> Optional[BSTreeNode]:
        # For basic testing
        self.check_validkey(key)
        return self._get(self.root, key)

    def _key(self, tree):
        return bst_key(tree)

    def _val(self, tree):
        return bst_val(tree)

    def _min(self, tree):
        return bst_min(tree)

    def _max(self, tree):
        return bst_max(tree)

    # Common method to get size of tree
    def _size(self, tree: Optional[BSTreeNode]) -> int:
        return tree.N if tree else 0

    # Common method to calcute size(node counts) of tree
    def _cal_size(self,  tree: Optional[BSTreeNode]) -> int:
        return 0 if not tree else self._size(tree.left) + self._size(tree.right) + 1

    # Get the kth largest TreeNode
    def _select_kthlargest(self, tree: Optional[BSTreeNode], kth: int) -> Optional[BSTreeNode]:
        return self._select_kthsmallest(tree, self._size(tree) - kth - 1)

    # Get the kth smallest TreeNode
    def _select_kthsmallest(self, tree: Optional[BSTreeNode], kth: int) -> Optional[BSTreeNode]:
        if tree is None:
            return None
        t = self._size(tree.left)
        if t < kth:
            return self._select_kthsmallest(tree.right, kth - t - 1)
        elif kth < t:
            return self._select_kthsmallest(tree.left, kth)
        else:
            return tree

    def _get(self, tree, key):
        return bst_get(tree, key)

    def _put(self, tree, key, val):
        def updateSize(tree: BSTreeNode) -> BSTreeNode:
            tree.N = self._cal_size(tree)
            return tree
        return bst_put(tree, key, val, BSTreeNode, updateSize)

    def _delete(self, tree, key):
        def updateSize(tree: BSTreeNode) -> BSTreeNode:
            tree.N = self._cal_size(tree)
            return tree
        return bst_delete(tree, key, updateSize)

    # # Delete the minimun node of tree, return root node
    # def _deletemin(self, tree):
    #     if tree is None:
    #         return None
    #     t = self._min(tree)
    #     return self._delete(tree, t.key)

    # # Delete the maximun node of tree, return root node
    # def _deletemax(self, tree):
    #     if tree is None:
    #         return None
    #     t = self._max(tree)
    #     return self._delete(tree, t.key)

    def size(self) -> int:
        '''Return size of BSTree'''
        return self._size(self.root)

    def empty(self):
        '''Return bool of whether BSTree is empty'''
        return self.size() == 0

    def min(self):
        '''Return the val of minmum TreeNode in BSTree"""'''
        return self._val(self._min(self.root))

    def max(self):
        '''Return the val maximum TreeNode in BSTree'''
        return self._val(self._max(self.root))

    def select(self, kth: int, INCRE=True):
        '''Get the val of kth smallest or largest key

        Args:
            kth (int): The Kth
            INCRE (bool): Whether increment order (Kth smallest)
        Raises:
            IndexError

        Returns:
            target TreeNode.val
        '''
        if kth < 0 or kth >= self.size():
            raise IndexError("Select index OutofRange!")
        if INCRE:
            target = self._select_kthsmallest(self.root, kth)
        else:
            target =  self._select_kthlargest(self.root, kth)
        return self._val(target)

    def get(self, key):
        '''Get val of given key

        Args:
            key (Object): User given key object

        Raises:
            check_validkey(key) raises TypeError

        Returns:
            get: node.val object
        '''
        self.check_validkey(key)
        return self._val(self._get(self.root, key))

    def put(self, key, val=None) -> Optional[BSTreeNode]:
        '''Insert {key: val} into BSTree

        Args:
            key (Object): User given key object
            val (Object): User giver val mapped to key

        Raises:
            check_validkey(key) raises TypeError

        Returns:
            None
        '''
        self.check_validkey(key)
        self.root = self._put(self.root, key, val)

    def delete(self, key):
        '''Insert {key: val} into BSTree

        Args:
            key (Object): User given key object
            val (Object): User giver val mapped to key

        Raises:
            check_validkey(key) raises TypeError

        Returns:
            None
        '''
        self.check_validkey(key)
        self.root = self._delete(self.root, key)
