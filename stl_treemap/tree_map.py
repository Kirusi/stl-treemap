"""Ordered map backed by a red-black tree."""

from __future__ import annotations

from collections import UserDict
from collections.abc import Callable, Collection, Iterable
from typing import Any

from stl_treemap.insertion_result import InsertionResult
from stl_treemap.iterators import ReverseIterator, TreeIterator
from stl_treemap.policies import KeyValuePolicy
from stl_treemap.py_iterators import PyIterator, PyReverseIterator
from stl_treemap.tree import Tree
from stl_treemap.tree_node import TreeNode


class TreeMap[K, V](Collection[K]):
    """
    Ordered map associating unique keys with values, backed by a red-black tree.

    Keys are kept in ascending order at all times. Lookup, insertion, and
    deletion are all O(log n).

    Example::

        m = TreeMap()
        m[1] = "a"
        m[2] = "b"
        v = m[1]  # 'a'
        for key, value in m:
            print(f"key: {key}, value: {value}")
    """

    def __init__(self, iterable: Iterable[tuple[K, V]] | None = None, **kwargs) -> None:
        """
        Create an empty map, or pre-populate it from an iterable of (key, value) pairs.

        Args:
            iterable: Optional iterable of (key, value) tuples.
            kwargs: another way to provide key-value pairs

        Raises:
            TypeError: When *iterable* is not iterable.

        Example::

            m = TreeMap()
            m = TreeMap({2: "B", 1: "A", 3: "C"})
            m = TreeMap({2: "B", 1: "A", 3: "C"}.items())
            m = TreeMap([[2, "B"], [1, "A"], [3, "C"]])
            m = TreeMap(A=1, B=2, C=3)

        """
        self._t: Tree[K, V] = Tree()
        self._t.value_policy = KeyValuePolicy()
        if iterable is not None:
            self.update(iterable)
        if kwargs:
            self.update(kwargs.items())

    def update(self, iterable: Iterable[tuple[K, V]]) -> None:
        """
        Add all contents from the iterable of (key, value) pairs.

        Args:
            iterable: Optional iterable of (key, value) tuples.

        Raises:
            TypeError: When *iterable* is not iterable.

        Example::

            TreeMap().update(TreeMap({2: "B", 1: "A", 3: "C"}))
            TreeMap().update({2: "B", 1: "A", 3: "C"})
            TreeMap().update({2: "B", 1: "A", 3: "C"}.items())
            TreeMap().update([[2, "B"], [1, "A"], [3, "C"]])

        """
        if isinstance(iterable, (dict, UserDict, TreeMap)):
            for k, v in iterable.items():
                self.set(k, v)
        elif hasattr(iterable, "__iter__"):
            for k, v in iterable:
                self.set(k, v)
        else:
            raise TypeError("TreeMap accepts only iterable objects")

    # ------------------------------------------------------------------
    # Python dict-compatible methods
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all key-value pairs.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            m.clear()
            len(m)  # 0

        """
        self._t.clear()

    def delete(self, key: K) -> None:
        """
        @private Remove the entry with *key*; does nothing if the key is absent.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            m.delete(2)  # m is now {1:A,3:C}
            m.delete(99)  # no-op

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            self._t.erase(it.node)

    def get(self, key: K, default: V = None) -> V | None:
        """
        Return the value for *key*, or *default* if the key is absent.

        Args:
            key: Key to look up.
            default: Value returned when *key* is not in the map.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            m.get(1)  # "A"
            m.get(4)  # None
            m.get(4, "Z")  # "Z"

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            return it.value
        return default

    def has(self, key: K) -> bool:
        """
        @private Return True when *key* exists in the map.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            m.has(1)  # True
            m.has(4)  # False

        """
        it = self._t.find(key)
        return not it.equals(self._t.end())

    def set(self, key: K, value: V) -> None:
        """
        @private Insert *key*/*value*, or update the value if *key* already exists.

        Example::

            m = TreeMap()
            m.set(1, "A")
            m.set(1, "B")  # updates existing entry; m is now {1:B}

        """
        n: TreeNode[K, V] = TreeNode()
        n.key = key
        n.value = value
        self._t.insert_or_replace(n)

    def items(self) -> PyIterator[tuple[K, V]]:
        """
        Return a forward iterator over (key, value) pairs in ascending key order.

        Example:
            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            for key, value in m.items():
                print(f"key: {key}, value: {value}")
            # key: 1, value: A
            # key: 2, value: B
            # key: 3, value: C

        """
        return self._t.items()

    def keys(self) -> PyIterator[K]:
        """
        Return a forward iterator over keys in ascending order.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            list(m.keys())  # [1, 2, 3]
            list(m.keys().backwards())  # [3, 2, 1]

        """
        return self._t.keys()

    def values(self) -> PyIterator[V]:
        """
        Return a forward iterator over values in ascending key order.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            list(m.values())  # ["A", "B", "C"]
            list(m.values().backwards())  # ["C", "B", "A"]

        """
        return self._t.values()

    @property
    def size(self) -> int:
        """
        @private Number of entries in the map.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            len(m)  # 3

        """
        return self._t.size()

    def __getitem__(self, key: K) -> V | None:
        """
        @public Return the value associated with key.

        Args:
            key: Key to look up.

        Returns:
            Value stored at key.

        Raises:
            KeyError: When key is not present in the tree.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            m[1]  # "A"
            m[4]  # raises KeyError

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            return it.value
        raise KeyError(f"Key {key} not found")

    def __setitem__(self, key: K, value: V) -> None:
        """
        @public Insert or replace the value for key.

        Args:
            key: Key to insert or update.
            value: Value to associate with the key.

        Example::

            m = TreeMap()
            m[1] = "A"
            m[1] = "B"  # updates existing entry

        """
        self.set(key, value)

    def __contains__(self, key: K) -> bool:
        """
        @public Return true if tree contains provided key.

        Args:
            key: Key to check.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            1 in m  # True
            4 in m  # False

        """
        it = self.find(key)
        return not it.equals(self.end())

    def __iter__(self) -> PyIterator[K]:
        """
        @public Iterate over keys in ascending key order.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            for key in m:
                print(f"{key}")

        """
        return self._t.keys()

    def __len__(self) -> int:
        """
        @public Return the number of entries in the map.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            len(m)  # 3

        """
        return self._t.size()

    def __str__(self) -> str:
        """
        @public Return a string representation in the form {key1:value1,key2:value2,...}.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            str(m)  # "{1:A,2:B,3:C}"

        """
        return str(self._t)

    def __repr__(self) -> str:
        """
        @public Return a string representation of the container's contents.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            repr(m)  # "{1:A,2:B,3:C}"

        """
        return self.__str__()

    def __delitem__(self, key: K):
        """
        @public Delete item by key or raise KeyError.

        Args:
            key: Key to remove.

        Raises:
            KeyError: When key is not present in the map.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            del m[2]  # m is now {1:A,3:C}
            del m[99]  # raises KeyError

        """
        del self._t[key]

    def popitem(self, key: K) -> tuple[K, V]:
        """
        Remove *key* and return its key-value tuple or raise KeyError.

        Args:
            key: Key to remove.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            m.popitem(2)  # "(2,B)", m is now {1:A,3:C}
            m.popitem(9)  # raises KeyError

        """
        it = self.find(key)
        if not it.equals(self.end()):
            k = it.key
            v = it.value
            self.erase(it)
            return (k, v)
        raise KeyError(f"Key {key} not found")

    def pop(self, key: K, default: K | None = None) -> V:
        """
        Remove *key* and return its value, or return *default* if absent.

        Args:
            key: Key to remove.
            default: Value to return when *key* is not present.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            m.pop(2)  # "B", m is now {1:A,3:C}
            m.pop(9)  # None, m is unchanged
            m.pop(9, "Z")  # "Z", m is unchanged

        """
        it = self.find(key)
        if not it.equals(self.end()):
            res = it.value
            self.erase(it)
            return res
        return default

    # ------------------------------------------------------------------
    # Additional iteration
    # ------------------------------------------------------------------

    def backwards(self) -> PyReverseIterator[K]:
        """
        Return a reverse iterator over keys in descending key order.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            for key in m.backwards():
                print(f"{key}")
            # 3
            # 2
            # 1

        """
        return self._t.keys().backwards()

    # ------------------------------------------------------------------
    # Custom comparator
    # ------------------------------------------------------------------

    @property
    def compare_func(self) -> Callable[[Any, Any], int]:
        """
        @private The current 3-way comparison function is used to order keys.

        The function must accept two key arguments and return a negative
        integer, zero, or a positive integer when the first key is less
        than, equal to, or greater than the second key.

        Example::

            m = TreeMap([[3, "C"], [1, "A"], [2, "B"]])
            m.compare_func = lambda a, b: -1 if a < b else (1 if a > b else 0)
            m.set(4, "D")
            list(m.keys())  # [1, 2, 3, 4]

        """
        return self._t.compare

    @compare_func.setter
    def compare_func(self, func: Callable[[Any, Any], int]) -> None:
        """@private Replace the comparison function. Clears the map because existing order is invalid."""
        self.clear()
        self._t.compare = func

    # ------------------------------------------------------------------
    # STL-style iterators
    # ------------------------------------------------------------------

    def begin(self) -> TreeIterator[K, V]:
        """
        Return a forward STL-like iterator to the first entry.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            it = m.begin()
            while not it.equals(m.end()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()

        """
        return self._t.begin()

    def end(self) -> TreeIterator[K, V]:
        """
        Return a forward STL-like iterator past the last entry.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            it = m.begin()
            while not it.equals(m.end()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()

        """
        return self._t.end()

    def find(self, key: K) -> TreeIterator[K, V]:
        """
        Return an STL-like iterator to the entry with *key*, or end() if not found.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            it = m.find(2)
            if not it.equals(m.end()):
                print(f"key: {it.key}, value: {it.value}")  # key: 2, value: B
            it = m.find(99)
            it.equals(m.end())  # True

        """
        return self._t.find(key)

    def insert_unique(self, key: K, value: V) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert *(key, value)* only when *key* is not already present.

        Returns:
            InsertionResult with was_added=True and an iterator when the key
            was new; was_added=False and iterator=None when the key existed.

        Example::

            m = TreeMap()
            res = m.insert_unique(1, "A")
            res.was_added  # True
            res.iterator.value  # "A"
            res2 = m.insert_unique(1, "B")
            res2.was_added  # False — key already exists, no change made

        """
        n: TreeNode[K, V] = TreeNode()
        n.key = key
        n.value = value
        return self._t.insert_unique(n)

    def insert_or_replace(self, key: K, value: V) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert *(key, value)*, replacing the existing value when *key* already exists.

        Returns:
            InsertionResult with was_added=True on new insertion, or
            was_replaced=True and the updated iterator on replacement.

        Example::

            m = TreeMap()
            res = m.insert_or_replace(1, "A")
            res.was_added  # True
            res2 = m.insert_or_replace(1, "B")
            res2.was_replaced  # True
            res2.iterator.value  # "B"

        """
        n: TreeNode[K, V] = TreeNode()
        n.key = key
        n.value = value
        return self._t.insert_or_replace(n)

    def erase(self, iterator: TreeIterator[K, V]) -> None:
        """
        Remove the entry pointed to by *iterator*.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            it = m.find(2)
            m.erase(it)
            str(m)  # "{1:A,3:C}"

        """
        self._t.erase(iterator.node)

    def lower_bound(self, key: K) -> TreeIterator[K, V]:
        """
        Return an STL-like iterator to the first entry with key >= *key*, or end().

        Example::

            m = TreeMap([[2, "B"], [4, "D"], [6, "F"], [8, "H"]])
            lo = m.lower_bound(3)  # iterator to key 4
            hi = m.upper_bound(6)  # iterator to key 8
            it = lo
            while not it.equals(hi):
                print(it.key)  # 4, 6
                it.next()

        """
        return self._t.lower_bound(key)

    def rbegin(self) -> ReverseIterator[K, V]:
        """
        Return a reverse STL-like iterator to the entry with largest key.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            it = m.rbegin()
            while not it.equals(m.rend()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()
            # key: 3, value: C
            # key: 2, value: B
            # key: 1, value: A

        """
        return self._t.rbegin()

    def rend(self) -> ReverseIterator[K, V]:
        """
        Return a reverse STL-like iterator before the entry with the smallest key.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            it = m.rbegin()
            while not it.equals(m.rend()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()

        """
        return self._t.rend()

    def upper_bound(self, key: K) -> TreeIterator[K, V]:
        """
        Return an STL-like iterator to the first entry with key larger than *key*, or end().

        Example::

            m = TreeMap([[2, "B"], [4, "D"], [6, "F"], [8, "H"]])
            lo = m.lower_bound(3)  # iterator to key 4
            hi = m.upper_bound(6)  # iterator to key 8
            it = lo
            while not it.equals(hi):
                print(it.key)  # 4, 6
                it.next()

        """
        return self._t.upper_bound(key)

    def first(self) -> tuple[K, V] | None:
        """
        Return the first (key, value) pair, or None when the map is empty.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            key, value = m.first()  # (1, "A")
            TreeMap().first()  # None

        """
        return self._t.first()

    def last(self) -> tuple[K, V] | None:
        """
        Return the last (key, value) pair, or None when the map is empty.

        Example::

            m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
            key, value = m.last()  # (3, "C")
            TreeMap().last()  # None

        """
        return self._t.last()

    def __or__(self, other: Any) -> TreeMap[K, V]:
        """
        @public Return a new map that is the union of this map and *other*.

        Values from *other* override values in this map for shared keys.

        Example::

            m1 = TreeMap([[1, "A"], [2, "B"]])
            m2 = TreeMap([[2, "X"], [3, "C"]])
            m3 = m1 | m2
            str(m3)  # "{1:A,2:X,3:C}"

        """
        res = TreeMap[K, V](self.items())
        if isinstance(other, (UserDict, dict, TreeMap)) or hasattr(other, "__iter__"):
            res.update(other)
        else:
            return NotImplemented
        return res

    def __ror__(self, other):
        """
        @public Return a union map when this TreeMap is on the right-hand side of ``|``.

        Example::

            m = TreeMap([[2, "X"], [3, "C"]])
            result = {1: "A", 2: "B"} | m
            str(result)  # "{1:A,2:X,3:C}"

        """
        res = TreeMap[K, V]()
        if isinstance(other, (UserDict, dict, TreeMap)) or hasattr(other, "__iter__"):
            res.update(other)
        else:
            return NotImplemented
        res.update(self)
        return res

    def __ior__(self, other: Any) -> TreeMap[K, V]:
        """
        @public Update this map in-place with key-value pairs from *other*.

        Example::

            m = TreeMap([[1, "A"], [2, "B"]])
            m |= {2: "X", 3: "C"}
            str(m)  # "{1:A,2:X,3:C}"

        """
        if isinstance(other, (UserDict, dict, TreeMap)) or hasattr(other, "__iter__"):
            self.update(other)
        else:
            return NotImplemented
        return self

    def __copy__(self):
        """
        @public Create a shallow copy of the map.

        Example::

            import copy

            m = TreeMap([[1, "A"], [2, "B"]])
            m2 = copy.copy(m)
            m2[3] = "C"
            str(m)  # "{1:A,2:B}"      — original unchanged
            str(m2)  # "{1:A,2:B,3:C}"

        """
        res = TreeMap[K, V](self.items())
        return res
