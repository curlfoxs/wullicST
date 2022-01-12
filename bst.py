from typing import Optional, Generator
from queue import LifoQueue
from random import randint

from bst_func import _display_aux
# from bst_func import *
class InvalidKeyError(KeyError):
    pass


class NoSuchElementException(Exception):
    pass


class TreeNode:
    def __init__(self, key=None, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right


class BSTreeNode(TreeNode):
    def __init__(self, key=None, val=None, left=None, right=None):
        super().__init__(key, left, right)
        self.val = val
        self.N = 1


class BSTree:
    ''' A Binary Search Tree reasonable implementation '''
    def __init__(self, num=None):
        self.root = None
        if num:
            for _ in range(num):
                self.put(randint(0, 10000))

    def __len__(self):
        return self.size()

    def __bool__(self):
        return False if self.empty() else True

    def __index__(self):
        raise NotImplementedError

    def __contains__(self, key):
        return self.contains(key)

    def __getitem__(self, key):
        item = self.get(key)
        if item:
            return item
        raise BSTKeyError

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def check_validkey(self, key):
        '''We should check the key object whether valid
        If BST is empty, key object must be comparable
        If BST is not empty, key object must be instance of existed key object's __class__
        '''
        if key is None:
            raise InvalidKeyError("Invalid key: None!")
        if not self.empty():
            keyType = self._key(self._min(self.root)).__class__
            if not isinstance(key, keyType):
                raise InvalidKeyError("Existed key is instance of {1}. But \'{0}\' is not!".format(key, keyType))
        elif not self._is_comparable(key):
            raise InvalidKeyError("{} is not comparable key!".format(key))

    def validKey(func):
        def wrap(self, key, *args, **kwargs):
            self.check_validkey(key)
            return func(self, key, *args, **kwargs)
        return wrap

    def validRet(func):
        def wrap(*args, **kwargs):
            x =  func(*args, **kwargs)
            if x:
                return x
            raise NoSuchElementException("calls {}() with None result".format(func.__name__))
        return wrap

    def size(self) -> int:
        '''Return size of BSTree'''
        return self._size(self.root)

    def empty(self):
        '''Return bool of whether BSTree is empty'''
        return self.size() == 0

    @validRet
    def min(self):
        '''Return the minimum key in BSTree"""'''
        return self._key(self._min(self.root))

    @validRet
    def max(self):
        '''Return the  maximum key in BSTree'''
        return self._key(self._max(self.root))

    @validKey
    def contains(self, key) -> bool:
        return True if self._get(self.root, key) else False

    @validKey
    @validRet
    def get(self, key):
        '''Get val of given key

        Args:
            key (Object): User given key object

        Raises:
            check_validkey(key) raises TypeError

        Returns:
            if exist: TreeNode.val
            else: None
        '''
        return self._val(self._get(self.root, key))


    @validKey
    def put(self, key, val=None):
        '''Insert {key: val} into BSTree

        Args:
            key (Object): User given key object
            val (Object): User giver val mapped to key

        Raises:
            check_validkey(key) raises TypeError

        Returns:
            None
        '''
        # val = val if val else key  # For only-key BST
        self.root = self._put(self.root, key, val)

    @validKey
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
        self.root = self._delete(self.root, key)

    @validKey
    @validRet
    def floor(self, key):
        return self._key(self._floor(self.root, key))


    @validKey
    @validRet
    def ceil(self, key):
        return self._key(self._ceil(self.root, key))

    @validRet
    def select(self, kth: int, INCRE=True):
        '''Get the kth smallest or largest key

        Args:
            kth (int): The Kth
            INCRE (bool): Whether increment order (Kth smallest)
        Raises:
            IndexError

        Returns:
            TreeNode.key of target node
        '''
        if kth < 0 or kth >= self.size():
            raise IndexError("Select index OutofRange!")
        if INCRE:
            target = self._select_kthsmallest(self.root, kth)
        else:
            target =  self._select_kthlargest(self.root, kth)
        return self._key(target)

    @validKey
    def rank(self, key) -> int:
        return self._rank(self.root, key)


    # # tmp code
    # def copytree_tmp(self, tree, keyname, valname):
    #     # For basic testing
    #     if tree:
    #         self.put(getattr(tree, keyname), getattr(tree, valname))
    #         self.copytree(tree.left, keyname, valname)
    #         self.copytree(tree.right, keyname, valname)

    # tmp code
    @validKey
    def get_tmp(self, key) -> Optional[BSTreeNode]:
        # For basic testing
        return self._get(self.root, key)

    def keys(self, low=None, high=None, INCRE=True) -> Generator:
        low = low if low else self.min()
        high = high if high else self.max()
        self.check_validkey(low)
        self.check_validkey(high)
        if low > high:
            raise InvalidKeyError("low should not larger than high!")
        if INCRE:
            return self._keysIncre(self.root, low, high)
        return self._keysDecre(self.root, low, high)

    def _keysIncre(self, tree: Optional[BSTreeNode], lo, hi):
        st = LifoQueue()
        while tree or not st.empty():
            while tree:
                st.put(tree)
                tree = tree.left if lo < tree.key else None
            tree = st.get()
            if lo <= tree.key and tree.key <= hi:
                yield tree.key
            tree = tree.right if tree.key < hi  else None

    def _keysDecre(self, tree: Optional[BSTreeNode], lo, hi):
        st = LifoQueue()
        while tree or not st.empty():
            while tree:
                st.put(tree)
                tree = tree.right if tree.key < hi else None
            tree = st.get()
            if lo <= tree.key and tree.key <= hi:
                yield tree.key
            tree = tree.left if lo < tree.key else None

    # Check the key object whether comparable
    def _is_comparable(self, obj) -> bool:
         cls = obj.__class__
         return cls.__lt__ != object.__lt__ or \
             cls.__gt__ != object.__gt__

    # Get TreeNode.key
    def _key(self, tree: Optional[BSTreeNode]):
        return tree.key if tree else None

    # Get TreeNode.val
    def _val(self, tree: Optional[BSTreeNode]):
        return tree.val if tree else None

    # Common method to get the minimum TreeNode of tree
    def _min(self, tree: Optional[BSTreeNode]) -> BSTreeNode:
        if tree is None or tree.left is None:
            return tree
        return self._min(tree.left)

    # Common method to get the maximum TreeNode of tree
    def _max(self, tree: Optional[BSTreeNode]) -> BSTreeNode:
        if tree is None or tree.right is None:
            return tree
        return self._max(tree.right)

    # Common method to get size of tree
    def _size(self, tree: Optional[BSTreeNode]) -> int:
        return tree.N if tree else 0

    # Common method to calcute size(node counts) of tree
    def _cal_size(self,  tree: Optional[BSTreeNode]) -> int:
        return 0 if not tree else self._size(tree.left) + self._size(tree.right) + 1

    # Common method to get the TreeNode of given key
    def _get(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        if tree is None:
            return None
        if key < tree.key:
            return self._get(tree.left, key)
        elif tree.key < key:
            return self._get(tree.right, key)
        else:
            return tree

    def _treeNodeType(self, key, val):
        '''Build a new TreeNode(key, val)

        Args:
            key (Object): key of TreeNode to build
            val (Object): val of TreeNode to build

        Returns:
            BSTreeNode
        '''
        return BSTreeNode(key, val)

    def _put_maintain(self, tree: Optional[BSTreeNode], key, val) ->  Optional[BSTreeNode]:
        '''Maintian good features of BSTree in insertion procedure

        Args:
            tree (BSTreeNode): The BSTreeNode in insertion recursion

        Returns:
            RootNode that complete insertion and maintains good features that we want
        '''
        return tree

    # Common method to put the TreeNode(key, val) to tree and return the root node
    def _put(self, tree: Optional[BSTreeNode], key, val) -> Optional[BSTreeNode]:
        '''Insert a new TreeNode(key, val) to BSTree

        Args:
            tree (BSTreeNode): The root of BSTree to insert
            key (Object): key of TreeNode to insert
            val (Object): val of TreeNode to insert
            args: Other arguments to build new TreeNode

        Raises:
            RuntimeError

        Returns:
            RootNode of tree that has completed insertion
        '''
        if tree is None:
            return self._treeNodeType(key, val)
        if key < tree.key:
            tree.left = self._put(tree.left, key, val)
        elif tree.key < key:
            tree.right = self._put(tree.right, key, val)
        else:
            tree.val = val
        tree.N = self._cal_size(tree)
        # Call _put_maintain method which could be overwrited by derived class
        return self._put_maintain(tree, key, val)

    def _delete_maintain(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        '''Maintian good features of BSTree in deletion procedure

        Args:
            tree (BSTreeNode): The BSTreeNode in deletion recursion

        Returns:
            RootNode that coomplete deletion and maintains good features that we want
        '''
        return tree

    def _delete(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        '''Delete the TreeNode of given key

        Args:
            tree (BSTreeNode): The root of BSTree
            key (Object): key of TreeNode to delete

        Returns:
            RootNode of tree that has completed deletion
        '''
        if tree is None:
            return None
        if key < tree.key:
            tree.left = self._delete(tree.left, key)
        elif key > tree.key:
            tree.right = self._delete(tree.right, key)
        else:
            if tree.left is None:
                return tree.right
            elif tree.right is None:
                return tree.left
            t = tree
            r = randint(0, 1)
            if r == 0:
                tree = self._min(t.right)
                tree.right = self._delete(t.right, tree.key)
                tree.left = t.left
            else:
                tree = self._max(t.left)
                tree.left = self._delete(t.left, tree.key)
                tree.right = t.right
        tree.N = self._cal_size(tree)
        return self._delete_maintain(tree, key)

    def _updateAfterRotate(self, preChild: Optional[BSTreeNode], preRoot: Optional[BSTreeNode]) -> None:
        '''Update BSTreeNode attribution after rotation

        Args:
            preChild (BSTreeNode): The child node before rotation
            preRoot (BSTreeNode): The root node before rotation

        Returns:
            None: Just update attribution of BSTreeNode
        '''
        preChild.N = preRoot.N
        preRoot.N = self._cal_size(preRoot)

    def _rotateRight(self, tree: Optional[BSTreeNode]) -> Optional[BSTreeNode]:
        x = tree.left
        tree.left = x.right
        x.right = tree
        self._updateAfterRotate(x, tree)
        return x

    def _rotateLeft(self, tree: Optional[BSTreeNode]) -> Optional[BSTreeNode]:
        x  = tree.right
        tree.right = x.left
        x.left = tree
        self._updateAfterRotate(x, tree)
        return x

    def _floor(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        if tree is None:
            return None
        elif tree.key == key:
            return tree
        elif key < tree.key:
            return self._floor(tree.left, key)
        else:
            t = self._floor(tree.right, key)
            return t if t else tree

    def _ceil(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        if tree is None:
            return None
        elif tree.key == key:
            return tree
        elif tree.key < key:
            return self._ceil(tree.right, key)
        else:
            t = self._ceil(tree.left, key)
            return t if t else tree

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

    def _rank(self, tree: Optional[BSTreeNode], key) -> Optional[BSTreeNode]:
        if tree is None:
            return 0
        elif tree.key == key:
            return self._size(tree.left)
        elif key < tree.key:
            return self._rank(tree.left, key)
        else:
            return self._rank(tree.right, key) + self._size(tree.left) + 1

    def display(self):
        lines, *_ = _display_aux(self.root)
        for line in lines:
            print(line)
