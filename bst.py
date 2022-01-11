from typing import Optional
from random import randint
from copy import deepcopy


class BSTreeNode:
    def __init__(self, key=None, val=None, left=None, right=None):
        self.key = key
        self.val = val
        self.left = left
        self.right = right
        self.N = 1

class WullicBST:
    def __init__(self):
        self.root = None

    def is_comparable(self, obj) -> bool:
         cls = obj.__class__
         return cls.__lt__ != object.__lt__ or \
             cls.__gt__ != object.__gt__

    def check_validkey(self, key):
        # if key is None:
            # raise TypeError
        if self.size() > 0:
            nodeType = self.select(0).__class__
            if not isinstance(key, nodeType):
                raise TypeError("{} is not instance of {}".format(key, nodeType))
        else:
            if not self.is_comparable(key):
                raise TypeError("{} is not comparable".format(key))

    def copytree_tmp(self, tree, keyname, valname):
        # For basic testing
        if tree:
            self.put(getattr(tree, keyname), getattr(tree, valname))
            self.copytree(tree.left, keyname, valname)
            self.copytree(tree.right, keyname, valname)

    def get_tmp(self, key) -> Optional[BSTreeNode]:
        # For basic testing
        self.check_validkey(key)
        return self._get(self.root, key)

    def _key(self, tree: Optional[BSTreeNode]):
        return tree.key if tree else None

    def _val(self, tree: Optional[BSTreeNode]):
        return tree.val if tree else None

    def size(self) -> int:
        return self._size(self.root)

    def _size(self, tree: Optional[BSTreeNode]) -> int:
        return tree.N if tree else 0

    def _cal_size(self,  tree: Optional[BSTreeNode]) -> int:
        return 0 if not tree else self._size(tree.left) + self._size(tree.right) + 1

    def min(self):
        return self._val(self._min(self.root))

    def _min(self, tree):
        # Find the minimum of tree
        if tree is None:
            return None
        elif tree.left is None:
            return tree
        else:
            return self._min(tree.left)

    def max(self):
        return self._val(self._max(self.root))

    def _max(self, tree):
        # Find the maximum of tree
        if tree is None:
            return None
        elif tree.right is None:
            return tree
        else:
            return self._max(tree.right)

    def get(self, key) -> Optional[BSTreeNode]:
        self.check_validkey(key)
        return self._val(self._get(self.root, key))

    def _get(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        if tree is None:
            return None
        if key < tree.key:
            return self._get(tree.left, key)
        elif tree.key < key:
            return self._get(tree.right, key)
        else:
            return tree

    def put(self, key, val=None) -> Optional[BSTreeNode]:
        self.check_validkey(key)
        self.root = self._put(self.root, key, val)

    def _put(self, tree: Optional[BSTreeNode], key, val) -> Optional[BSTreeNode]:
        if tree is None:
            return BSTreeNode(key, val)
        if key < tree.key:
            tree.left = self._put(tree.left, key, val)
        elif tree.key < key:
            tree.right = self._put(tree.right, key, val)
        else:
            tree.val = val
        tree.N = self._cal_size(tree)
        return tree

    def select(self, kth: int, INCRE=True):
        if kth < 0 or kth >= self.size():
            return None
        if INCRE:
            target = self.select_kthsmallest(self.root, kth)
        else:
            target =  self.select_kthlargest(self.root, kth)
        return self._val(target)


    def select_kthlargest(self, tree: Optional[BSTreeNode], kth: int) -> Optional[BSTreeNode]:
        return self.select_kthsmallest(tree, self._size(tree) - kth - 1)

    def select_kthsmallest(self, tree: Optional[BSTreeNode], kth: int) -> Optional[BSTreeNode]:
        if tree is None:
            return None
        t = self._size(tree.left)
        if t < kth:
            return self.select_kthsmallest(tree.right, kth - t - 1)
        elif kth < t:
            return self.select_kthsmallest(tree.left, kth)
        else:
            return tree

    def delete(self, key: int):
        self.root = self._delete(self.root, key)


    def _delete(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        if tree is None:
            return None
        # Find the node to be deleted
        # Avoid getting parent node, just find the node in one recurrsion, fantastic.
        if key < tree.key:
            tree.left = self._delete(tree.left, key)
        elif key > tree.key:
            tree.right = self._delete(tree.right, key)
        else:
            # Simplify the problem to delete the root node ~
            if tree.left is None:
                return tree.right
            elif tree.right is None:
                return tree.left
            # Simpplify the problem to delete the Min of right tree or the Max of left tree ~
            r = randint(0, 1)
            if r == 0:
                t = self._min(tree.right)
                tree.right = self._delete(tree.right, t.key)
            else:
                t = self._max(tree.left)
                tree.left = self._delete(tree.left, t.key)
            tree.key  = deepcopy(t.key)
            tree.val = deepcopy(t.val)
        tree.N = self._cal_size(tree)
        return tree

    # def _deletemin(self, tree: Optional[BSTreeNode]) -> Optional[BSTreeNode]:
    #     # Delete the minimun node of tree, return root node
    #     if tree is None:
    #         return None
    #     t = self._min(tree)
    #     return self._delete(tree, t.key)

    # def _deletemax(self, tree: Optional[BSTreeNode]) -> Optional[BSTreeNode]:
    #     # Delete the maximun node of tree, return root node
    #     if tree is None:
    #         return None
    #     t = self._max(tree)
    #     return self._delete(tree, t.key)

    def _rotateRight(self, tree: Optional[BSTreeNode]) -> Optional[BSTreeNode]:
        leftTree = tree.left
        tree.left = leftTree.right
        leftTree.right = tree
        leftTree.N = tree.N
        tree.N = self._cal_size(tree)
        self._recal_info_afterRotateRight(leftTree, tree)
        return leftTree

    def _rotateLeft(self, tree: Optional[BSTreeNode]) -> Optional[BSTreeNode]:
        rightTree  = tree.right
        tree.right = rightTree.left
        rightTree.left = tree
        rightTree.N = tree.N
        tree.N = self._cal_size(tree)
        self._recal_info_afterRotateLeft(rightTree, tree)
        return rightTree

    def _recal_info_afterRotateRight(self, preLeft, preRoot):
        # Basic BST would not use rotation
        raise NotImplementedError

    def _recal_info_afterRotateLeft(self, preRight, preRoot):
        # Basic BST would not use rotation
        raise NotImplementedError
