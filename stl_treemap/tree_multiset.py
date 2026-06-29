"""Ordered multiset backed by a red-black tree (duplicate keys allowed)."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from stl_treemap.insertion_result import InsertionResult
from stl_treemap.iterators import ReverseIterator, TreeIterator
from stl_treemap.js_iterators import JsIterator, JsReverseIterator
from stl_treemap.policies import KeyOnlyPolicy
from stl_treemap.tree import Tree
from stl_treemap.tree_node import TreeNode


class TreeMultiSet[K]:
    """
    Ordered multiset of keys backed by a red-black tree.

    Unlike TreeSet, multiple equal keys are allowed. Elements are kept in
    ascending order. Lookup, insertion, and deletion are all O(log n).

    Example::

        s = TreeMultiSet()
        s.add(1)
        s.add(2)
        s.add(2)
        for key in s:
            print(key)  # 1, 2, 2
    """

    def __init__(self, iterable: Iterable[K] | None = None, *args) -> None:
        """
        Create an empty multiset, or pre-populate it from an iterable of keys.

        Duplicate keys are preserved (multiset semantics).

        Args:
            iterable: Optional iterable of keys.

        Raises:
            TypeError: When *iterable* is not iterable.

        Example::

            s = TreeMultiSet()
            s = TreeMultiSet([1, 2, 2, 3])  # {1,2,2,3}

        """
        self._t: Tree[K, K] = Tree()
        self._t.value_policy = KeyOnlyPolicy()
        if iterable is not None:
            self.update(iterable)
        if args:
            self.update(args)

    def update(self, *iterables: Iterable[K]) -> None:
        """
        Add contents from all provided iterables to the current set.

        Duplicate keys are preserved (multiset semantics).

        Args:
            iterables: One or more iterables containing keys.

        Raises:
            TypeError: When *iterable* is not iterable.

        Example::

            s = TreeMultiSet()
            s.update([1, 2, 2, 3])  # {1,2,2,3}

        """
        for iterable in iterables:
            if not hasattr(iterable, "__iter__"):
                raise TypeError("TreeMultiSet accepts only iterable objects")
            for k in iterable:
                self.add(k)

    # ------------------------------------------------------------------
    # Core mutation
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all elements.

        Example::

            s = TreeMultiSet([1, 2, 3])
            s.clear()
            len(s)  # 0

        """
        self._t.clear()

    def add(self, key: K) -> None:
        """
        Insert *key*, always adding a new entry even if an equal key exists.

        Example::

            s = TreeMultiSet()
            s.add(1)
            s.add(1)
            len(s)  # 2

        """
        n: TreeNode[K, K] = TreeNode()
        n.key = key
        self._t.insert_multi(n)

    def discard(self, key: K) -> None:
        """
        Remove one occurrence of *key* if present; do nothing when absent.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            s.discard(2)  # s is now {1,2,3}
            s.discard(99)  # no-op

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            self._t.erase(it.node)

    def remove(self, key: K) -> None:
        """
        Remove one occurrence of *key*, raising KeyError when absent.

        Args:
            key: Key to remove.

        Raises:
            KeyError: When *key* is not present.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            s.remove(2)  # s is now {1,2,3}
            s.remove(99)  # raises KeyError

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            self._t.erase(it.node)
        else:
            raise KeyError(key)

    def delete(self, key: K) -> None:
        """
        @private Remove one occurrence of *key* if present; alias for discard().

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            s.delete(2)  # s is now {1,2,3}
            s.delete(99)  # no-op

        """
        self.discard(key)

    def pop(self, key: K | None = None, default: K | None = None) -> K | None:
        """
        Remove one occurrence of *key* and return it, or return *default* when absent.

        When called with no arguments, removes and returns the smallest element.

        Args:
            key: Key to remove. When None, the smallest element is removed.
            default: Value to return when *key* is absent.

        Raises:
            KeyError: When called with no arguments on an empty set.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            s.pop(2)  # 2, s is now {1,2,3}
            s.pop(9)  # None
            s.pop(9, 0)  # 0
            s.pop()  # 1  — removes and returns smallest element

        """
        if self.size == 0:
            raise KeyError("pop from an empty set")
        it = self._t.find(key) if key is not None else self.begin()
        if not it.equals(self._t.end()):
            k = it.key
            self._t.erase(it.node)
            return k
        return default

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def has(self, key: K) -> bool:
        """
        @private Return True when *key* exists in the set.

        Example::

            s = TreeMultiSet([1, 2, 3])
            s.has(1)  # True
            s.has(4)  # False

        """
        it = self._t.find(key)
        return not it.equals(self._t.end())

    def keys(self) -> JsIterator[K]:
        """
        @private Return a forward iterator over all keys in ascending order.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            list(s.keys())  # [1, 2, 2, 3]

        """
        return self._t.keys()

    @property
    def size(self) -> int:
        """
        @private Number of elements (counting duplicates) in the set.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            s.size  # 4

        """
        return self._t.size()

    def __contains__(self, key: K) -> bool:
        """
        Return True when *key* is in the set.

        Example::

            s = TreeMultiSet([1, 2, 3])
            1 in s  # True
            4 not in s  # True

        """
        return self.has(key)

    def __iter__(self) -> JsIterator[K]:
        """
        Iterate over all keys in ascending order (duplicates included).

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            list(s)  # [1, 2, 2, 3]

        """
        return self._t.keys()

    def __len__(self) -> int:
        """
        Return the total number of elements (counting duplicates).

        Example::

            s = TreeMultiSet([1, 2, 2])
            len(s)  # 3

        """
        return self._t.size()

    def __str__(self) -> str:
        """
        Return a string representation in the form {key1,key2,...}.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            str(s)  # "{1,2,2,3}"

        """
        return str(self._t)

    def __repr__(self) -> str:
        """
        Return a string representation in the form {key1,key2,...}.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            str(s)  # "{1,2,2,3}"

        """
        return self.__str__()

    # ------------------------------------------------------------------
    # Additional iteration
    # ------------------------------------------------------------------

    def backwards(self) -> JsReverseIterator[K]:
        """
        Return a reverse iterator over all keys in descending order.

        Example::

            s = TreeMultiSet([1, 2, 3])
            list(s.backwards())  # [3, 2, 1]

        """
        return self._t.keys().backwards()

    # ------------------------------------------------------------------
    # Custom comparator
    # ------------------------------------------------------------------

    @property
    def compare_func(self) -> Callable[[Any, Any], int]:
        """
        @private The current 3-way comparison function used to order keys.

        Setting this property clears all existing elements.

        Example::

            s = TreeMultiSet()
            s.compare_func = lambda a, b: -1 if a < b else (1 if a > b else 0)

        """
        return self._t.compare

    @compare_func.setter
    def compare_func(self, func: Callable[[Any, Any], int]) -> None:
        """@private Replace the comparison function and clear all elements."""
        self.clear()
        self._t.compare = func

    # ------------------------------------------------------------------
    # STL-style iterators
    # ------------------------------------------------------------------

    def begin(self) -> TreeIterator[K, K]:
        """
        Return a forward STL-like iterator to the first element.

        Example::

            s = TreeMultiSet([1, 2, 3])
            it = s.begin()
            while not it.equals(s.end()):
                print(it.key)
                it.next()
            # 1, 2, 3

        """
        return self._t.begin()

    def end(self) -> TreeIterator[K, K]:
        """
        Return a forward STL-like iterator past the last element.

        Example::

            s = TreeMultiSet([1, 2, 3])
            it = s.begin()
            while not it.equals(s.end()):
                print(it.key)
                it.next()

        """
        return self._t.end()

    def find(self, key: K) -> TreeIterator[K, K]:
        """
        Return an STL-like iterator to an element with *key*, or end() if absent.

        Example::

            s = TreeMultiSet([1, 2, 2, 3])
            it = s.find(2)
            if not it.equals(s.end()):
                print(it.key)  # 2

        """
        return self._t.find(key)

    def insert_unique(self, key: K) -> InsertionResult[TreeIterator[K, K]]:
        """
        Insert *key* only when it is not already present.

        Returns:
            InsertionResult with was_added=True when the key was new.

        Example::

            s = TreeMultiSet()
            res = s.insert_unique(1)
            res.was_added  # True
            res2 = s.insert_unique(1)
            res2.was_added  # False
            s.size  # 1

        """
        n: TreeNode[K, K] = TreeNode()
        n.key = key
        return self._t.insert_unique(n)

    def insert_or_replace(self, key: K) -> InsertionResult[TreeIterator[K, K]]:
        """
        Insert *key* if absent; if present, replace in-place.

        Returns:
            InsertionResult with was_added=True on new insertion, or
            was_replaced=True when the key already existed.

        Example::

            s = TreeMultiSet()
            res = s.insert_or_replace(1)
            res.was_added  # True
            res2 = s.insert_or_replace(1)
            res2.was_replaced  # True
            s.size  # 1

        """
        n: TreeNode[K, K] = TreeNode()
        n.key = key
        return self._t.insert_or_replace(n)

    def insert_multi(self, key: K) -> InsertionResult[TreeIterator[K, K]]:
        """
        Insert *key* unconditionally, even when an equal key already exists.

        Returns:
            InsertionResult always with was_added=True.

        Example::

            s = TreeMultiSet()
            s.insert_multi(1)
            s.insert_multi(1)
            s.size  # 2

        """
        n: TreeNode[K, K] = TreeNode()
        n.key = key
        return self._t.insert_multi(n)

    def erase(self, iterator: TreeIterator[K, K]) -> None:
        """
        Remove the element pointed to by *iterator*.

        Example::

            s = TreeMultiSet([1, 2, 3])
            it = s.find(2)
            it.prev()
            s.erase(it)  # removes element with key 1
            str(s)  # "{2,3}"

        """
        self._t.erase(iterator.node)

    def lower_bound(self, key: K) -> TreeIterator[K, K]:
        """
        Return an STL-like iterator to the first element with key >= *key*, or end().

        Example::

            s = TreeMultiSet([2, 4, 4, 6])
            lo = s.lower_bound(3)  # iterator to first 4
            hi = s.upper_bound(4)  # iterator past last 4
            it = lo
            while not it.equals(hi):
                print(it.key)  # 4, 4
                it.next()

        """
        return self._t.lower_bound(key)

    def rbegin(self) -> ReverseIterator[K, K]:
        """
        Return a reverse STL-like iterator to the element with the largest key.

        Example::

            s = TreeMultiSet([1, 2, 3])
            it = s.rbegin()
            while not it.equals(s.rend()):
                print(it.key)  # 3, 2, 1
                it.next()

        """
        return self._t.rbegin()

    def rend(self) -> ReverseIterator[K, K]:
        """
        Return a reverse STL-like iterator before the element with the smallest key.

        Example::

            s = TreeMultiSet([1, 2, 3])
            it = s.rbegin()
            while not it.equals(s.rend()):
                print(it.key)  # 3 2 1
                it.next()

        """
        return self._t.rend()

    def upper_bound(self, key: K) -> TreeIterator[K, K]:
        """
        Return an STL-like iterator to the first element with key > *key*, or end().

        Example::

            s = TreeMultiSet([2, 4, 4, 6])
            lo = s.lower_bound(3)
            hi = s.upper_bound(4)
            it = lo
            while not it.equals(hi):
                print(it.key)  # 4, 4
                it.next()

        """
        return self._t.upper_bound(key)

    def first(self) -> K | None:
        """
        Return the smallest element, or None when the set is empty.

        Example::

            s = TreeMultiSet([1, 1, 2, 3])
            s.first()  # 1
            TreeMultiSet().first()  # None

        """
        return self._t.first()  # type: ignore[return-value]

    def last(self) -> K | None:
        """
        Return the largest element, or None when the set is empty.

        Example::

            s = TreeMultiSet([1, 2, 3, 3])
            s.last()  # 3
            TreeMultiSet().last()  # None

        """
        return self._t.last()  # type: ignore[return-value]
