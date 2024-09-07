from typing import List
import io, sys, re, random

import pkuseg  # Chinese word segmentation

from bst import BSTree
from avl import AVLTree
from rbt import RBTree
from st import ST, SET
from spider5 import PageDB

# This test code is so simple that could meet our need
class KthLargest:
    def __init__(self, k: int, nums: List[int]):
        self.kth = k
        self.BST = RBTree()
        for num in nums:
            self.BST.put(num, num)

    def add(self, val: int) -> int:
        self.BST.put(val, val)
        return self.BST.select(self.kth - 1, False)

    def show(self):
        for i in range(self.BST.size()):
            node = self.BST.get_tmp( self.BST.select(i))
        # print(node.val)
            print("{0} height : {1}, facotr: {2}".format(node.val,  node.H, self.BST._cal_factor(node)))


class PageIndex:
    def __init__(self):
        self.db = PageDB('test')
        self.st = ST()

    def build_index(self):
        keys = self.db.fetch_allkeys()
        print(len(keys))
        for key in keys:
            item = self.db.fetch_oneitem(key)
            url = item[1]
            text = item[2]
            print(url)
            for line in io.StringIO(text).readlines():
                for word in re.findall(r'[\u4e00-\u9fff]+', line):
                    if not self.st.contains(word):
                        self.st.put(word, SET())
                    file_set = self.st.get(word)
                    file_set.add(url)

    def query_index(self):
        while True:
            query = input()
            if self.st.contains(query):
                for url in self.st.get(query):
                    print(url)




pi = PageIndex()
pi.build_index()
# That's our goal:
# Use a pytest - And using CI development enviroment
# Reference and study algorithm website code style
# Test a ST's correctness
# Test a ST's performance
# Visualizaion ST

# Your KthLargest object will be instantiated and called as such:
# obj = KthLargest(k, nums)
# param_1 = obj.add(val)
