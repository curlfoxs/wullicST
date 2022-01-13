from bst import InvalidKeyError, NoSuchElementException
from rbt import RBTree
from copy import deepcopy

class STeleTypeError(TypeError):
    pass

class SETeleTypeError(TypeError):
    pass

class ST(RBTree):
    def __init__(self, data=None):
        super().__init__()
        if data is None:
            pass
        elif isinstance(data, list):
            for key in data:
                self.put(key)
        elif isinstance(data, dict) or isinstance(data, ST):
            for key in data.keys():
                self.put(key, data[key])
        else:
            raise STeleTypeError('Unknown type to init ST object')


class SET:
    def __init__(self, keys=None):
        self.st = ST()
        if keys is None:
            pass
        elif isinstance(keys, list) or isinstance(keys, set) or isinstance(keys, SET):
            for key in keys:
                self.add(key)
        else:
            raise SETeleTypeError('Unkown type to init SET object')

    def __repr__(self):
        keys = self.keys()
        if keys is None:
            return 'SET()'
        return '{' + list(keys).__repr__()[1:-1] + '}'

    def __contains__(self, key):
        return self.st.contains(key)

    def __iter__(self):
        keys = self.st.keys()
        if keys is None:
            return iter([])
        return keys

    def __add__(self, others):
        rel = SET(self)
        rel.union(others)
        return rel

        return self.union(others)

    def add(self, key):
        if not self.st.contains(key):
            self.st.put(key)

    def delete(self, key):
        try:
            if self.st.contains(key):
                self.st.delete(key)
        except InvalidKeyError as e:
            print(str(e) + ': Do nothing')

    def empty(self):
        return self.st.empty()

    def size(self):
        return self.st.size()

    def keys(self):
        return self.st.keys()

    def union(self, others):
        if not isinstance(others, SET) and not isinstance(others, set):
            raise TypeError('\'{}\' is not a SET object'.format(others))
        if others is not None:
            for key in others:
                self.add(key)
        return self
