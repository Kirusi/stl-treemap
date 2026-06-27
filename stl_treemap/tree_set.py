"""Ordered set backed by a red-black tree."""

from __future__ import annotations

from collections.abc import Callable, Collection, Iterable
from typing import Any

from stl_treemap.insertion_result import InsertionResult
from stl_treemap.iterators import ReverseIterator, TreeIterator
from stl_treemap.js_iterators import JsIterator, JsReverseIterator
from stl_treemap.policies import KeyOnlyPolicy
from stl_treemap.tree import Tree
from stl_treemap.tree_node import TreeNode


class TreeSet[K](Collection[K]):
    """
    Ordered set of unique keys backed by a red-black tree.

    Elements are kept in ascending order at all times. Lookup, insertion,
    and deletion are all O(log n).

    Example::

        s = TreeSet()
        s.add(1)
        s.add(2)
        s.add(1)  # duplicate; ignored
        for key in s:
            print(key)  # 1, 2
    """

    def __init__(self, iterable: Iterable[K] | None = None, *args) -> None:
        """
        Create an empty set, or pre-populate it from an iterable of keys.

        Duplicate keys in *iterable* are silently ignored (set semantics).

        Args:
            iterable: Optional iterable of keys.
            args: another way to provide key-list

        Raises:
            TypeError: When *iterable* is not iterable.

        Example::

            s = TreeSet()
            s = TreeSet([3, 1, 2, 1])  # {1,2,3} — duplicates dropped
            s = TreeSet({3, 1, 2})  # from a Python set
            s = TreeSet(range(1, 4))

        """
        self._t: Tree[K, K] = Tree()
        self._t.value_policy = KeyOnlyPolicy()
        if iterable is not None:
            self.update(iterable)
        if args:
            self.update(args)

    def update(self, *iterables: Iterable[K]) -> None:
        """
        Add all keys to the current set.

        Duplicate keys in *iterable* are silently ignored (set semantics).

        Args:
            iterables: One or more list/tuple/etc

        Raises:
            TypeError: When *iterable* is not iterable.

        Example::

            TreeSet().update(TreeSet({3, 1, 2}))  # from a TreeSet
            TreeSet().update([3, 1, 2, 1])  # {1,2,3} — duplicates dropped
            TreeSet().update({3, 1, 2})  # from a Python set
            TreeSet().update(range(1, 4))

        """
        if iterables is not None:
            for iterable in iterables:
                if not hasattr(iterable, "__iter__"):
                    raise TypeError("TreeSet accepts only iterable objects")
                for k in iterable:
                    self.add(k)

    # ------------------------------------------------------------------
    # Python set-compatible methods
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all elements.

        Example::

            s = TreeSet([1, 2, 3])
            s.clear()
            len(s)  # 0

        """
        self._t.clear()

    def add(self, key: K) -> None:
        """
        Insert *key* if it is not already present.

        Example::

            s = TreeSet()
            s.add(1)
            s.add(1)  # ignored
            len(s)  # 1

        """
        n: TreeNode[K, K] = TreeNode()
        n.key = key
        self._t.insert_unique(n)

    def discard(self, key: K) -> None:
        """
        Remove *key* if present; do nothing when it is absent.

        Example::

            s = TreeSet([1, 2, 3])
            s.discard(2)  # s is now {1,3}
            s.discard(99)  # no-op

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            self._t.erase(it.node)

    def remove(self, key: K) -> None:
        """
        Remove *key*, raising KeyError when it is absent.

        Args:
            key: Key to remove.

        Raises:
            KeyError: When *key* is not present.

        Example::

            s = TreeSet([1, 2, 3])
            s.remove(2)  # s is now {1,3}
            s.remove(99)  # raises KeyError

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            self._t.erase(it.node)
        else:
            raise KeyError(key)

    def delete(self, key: K) -> None:
        """
        @private Remove *key* if present; do nothing when absent. Alias for discard().

        Example::

            s = TreeSet([1, 2, 3])
            s.delete(2)  # s is now {1,3}
            s.delete(99)  # no-op

        """
        self.discard(key)

    def pop(self, key: K | None = None, default: K | None = None) -> K | None:
        """
        Remove *key* and return it, or return *default* when absent.

        When called with no arguments, removes and returns the smallest element.

        Args:
            key: Key to remove. When None, the smallest element is removed.
            default: Value to return when *key* is absent.

        Raises:
            KeyError: When called with no arguments on an empty set.

        Example::

            s = TreeSet([1, 2, 3])
            s.pop(2)  # 2, s is now {1,3}
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

    def has(self, key: K) -> bool:
        """
        @private Return True when *key* exists in the set.

        Example::

            s = TreeSet([1, 2, 3])
            s.has(1)  # True
            s.has(4)  # False

        """
        it = self._t.find(key)
        return not it.equals(self._t.end())

    def keys(self) -> JsIterator[K]:
        """
        @private Return a forward iterator over all keys in ascending order.

        Example::

            s = TreeSet([1, 2, 3])
            list(s.keys())  # [1, 2, 3]
            list(s.keys().backwards())  # [3, 2, 1]

        """
        return self._t.keys()

    @property
    def size(self) -> int:
        """
        @private Number of elements in the set.

        Example::

            s = TreeSet([1, 2, 3])
            s.size  # 3

        """
        return self._t.size()

    def __contains__(self, key: K) -> bool:
        """
        Return True when *key* is in the set.

        Example::

            s = TreeSet([1, 2, 3])
            1 in s  # True
            4 in s  # False

        """
        return self.has(key)

    def __iter__(self) -> JsIterator[K]:
        """
        Iterate over all keys in ascending order.

        Example::

            s = TreeSet([1, 2, 3])
            for key in s:
                print(key)  # 1, 2, 3

        """
        return self._t.keys()

    def __len__(self) -> int:
        """
        Return the number of elements in the set.

        Example::

            s = TreeSet([1, 2, 3])
            len(s)  # 3

        """
        return self._t.size()

    def __str__(self) -> str:
        """
        Return a string representation in the form {key1,key2,...}.

        Example::

            s = TreeSet([1, 2, 3])
            str(s)  # "{1,2,3}"

        """
        return str(self._t)

    def __repr__(self) -> str:
        """
        Return a string representation of the set's contents.

        Example::

            s = TreeSet([1, 2, 3])
            repr(s)  # "{1,2,3}"

        """
        return self.__str__()

    # ------------------------------------------------------------------
    # Set algebra operators
    # ------------------------------------------------------------------

    def __or__(self, other: Iterable[K]) -> TreeSet[K]:
        """
        Return a new set containing all keys from this set and *other*.

        Example::

            s1 = TreeSet([1, 2, 3])
            s2 = TreeSet([2, 3, 4])
            str(s1 | s2)  # "{1,2,3,4}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        res = TreeSet[K](self.keys())
        res.update(other)
        return res

    def __ror__(self, other: Any) -> TreeSet[K]:
        """
        Return a union when this TreeSet is on the right-hand side of ``|``.

        Example::

            s = TreeSet([2, 3, 4])
            str({1, 2, 3} | s)  # "{1,2,3,4}"

        """
        return self.__or__(other)

    def __ior__(self, other: Any) -> TreeSet[K]:
        """
        Add all keys from *other* to this set in-place.

        Example::

            s = TreeSet([1, 2])
            s |= {3, 4}
            str(s)  # "{1,2,3,4}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        self.update(other)
        return self

    def __and__(self, other: Any) -> TreeSet[K]:
        """
        Return a new set containing only keys present in both this set and *other*.

        Example::

            s1 = TreeSet([1, 2, 3])
            s2 = TreeSet([2, 3, 4])
            str(s1 & s2)  # "{2,3}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        res = TreeSet[K]()
        for k in other:
            if k in self:
                res.add(k)
        return res

    def __rand__(self, other: Any) -> TreeSet[K]:
        """
        Return intersection when this TreeSet is on the right-hand side of ``&``.

        Example::

            s = TreeSet([2, 3, 4])
            str({1, 2, 3} & s)  # "{2,3}"

        """
        return self.__and__(other)

    def __iand__(self, other: Any) -> TreeSet[K]:
        """
        Keep only keys also in *other*, in-place.

        Example::

            s = TreeSet([1, 2, 3])
            s &= {2, 3, 4}
            str(s)  # "{2,3}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        other_items = TreeSet[K](other)
        for k in self:
            if k not in other_items:
                self.delete(k)
        return self

    def __sub__(self, other: Any) -> TreeSet[K]:
        """
        Return a new set with keys from this set that are not in *other*.

        Example::

            s1 = TreeSet([1, 2, 3])
            s2 = TreeSet([2, 3, 4])
            str(s1 - s2)  # "{1}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        other_keys = TreeSet(other)
        res = TreeSet[K]()
        for k in self.keys():
            if k not in other_keys:
                res.add(k)
        return res

    def __rsub__(self, other: Any) -> TreeSet[K]:
        """
        Return *other* - this set when this TreeSet is on the right-hand side of ``-``.

        Example::

            s = TreeSet([2, 3, 4])
            str({1, 2, 3} - s)  # "{1}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        res = TreeSet[K](other)
        for k in self.keys():
            res.delete(k)
        return res

    def __isub__(self, other: Any) -> TreeSet[K]:
        """
        Remove all keys in *other* from this set in-place.

        Example::

            s = TreeSet([1, 2, 3])
            s -= {2, 3, 4}
            str(s)  # "{1}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        for k in other:
            self.delete(k)
        return self

    def __xor__(self, other: Any) -> TreeSet[K]:
        """
        Return a new set with keys in exactly one of this set and *other*.

        Example::

            s1 = TreeSet([1, 2, 3])
            s2 = TreeSet([2, 3, 4])
            str(s1 ^ s2)  # "{1,4}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        other_set = TreeSet(other)
        res = TreeSet[K]()
        for k in self.keys():
            if k not in other_set:
                res.add(k)
        for k in other_set:
            if not self.has(k):
                res.add(k)
        return res

    def __rxor__(self, other: Any) -> TreeSet[K]:
        """
        Return symmetric difference when this TreeSet is on the right-hand side of ``^``.

        Example::

            s = TreeSet([2, 3, 4])
            str({1, 2, 3} ^ s)  # "{1,4}"

        """
        return self.__xor__(other)

    def __ixor__(self, other: Any) -> TreeSet[K]:
        """
        Apply symmetric difference with *other* to this set in-place.

        Example::

            s = TreeSet([1, 2, 3])
            s ^= {2, 3, 4}
            str(s)  # "{1,4}"

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        for k in other:
            if self.has(k):
                self.delete(k)
            else:
                self.add(k)
        return self

    def __le__(self, other: Any) -> bool:
        """
        Return True when every element of this set is in *other* (subset or equal).

        Example::

            TreeSet([1, 2]) <= TreeSet([1, 2, 3])  # True
            TreeSet([1, 2]) <= TreeSet([1, 2])  # True

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        other_set = TreeSet(other)
        return all(k in other_set for k in self.keys())

    def __lt__(self, other: Any) -> bool:
        """
        Return True when this set is a proper subset of *other*.

        Example::

            TreeSet([1, 2]) < TreeSet([1, 2, 3])  # True
            TreeSet([1, 2]) < TreeSet([1, 2])  # False

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        other_set = TreeSet(other)
        return len(self) < len(other_set) and all(k in other_set for k in self.keys())

    def __ge__(self, other: Any) -> bool:
        """
        Return True when every element of *other* is in this set (superset or equal).

        Example::

            TreeSet([1, 2, 3]) >= TreeSet([1, 2])  # True
            TreeSet([1, 2]) >= TreeSet([1, 2])  # True

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        return all(self.has(k) for k in other)

    def __gt__(self, other: Any) -> bool:
        """
        Return True when this set is a proper superset of *other*.

        Example::

            TreeSet([1, 2, 3]) > TreeSet([1, 2])  # True
            TreeSet([1, 2]) > TreeSet([1, 2])  # False

        """
        if not hasattr(other, "__iter__"):
            return NotImplemented
        return len(self) > len(other) and all(self.has(k) for k in other)

    def issubset(self, other: Any) -> bool:
        """
        Return True when every element of this set is in *other*.

        Example::

            TreeSet([1, 2]).issubset([1, 2, 3])  # True
            TreeSet([1, 4]).issubset([1, 2, 3])  # False

        """
        return self <= other

    def issuperset(self, other: Any) -> bool:
        """
        Return True when every element of *other* is in this set.

        Example::

            TreeSet([1, 2, 3]).issuperset([1, 2])  # True
            TreeSet([1, 2]).issuperset([1, 3])  # False

        """
        return self >= other

    def isdisjoint(self, other: Any) -> bool:
        """
        Return True when this set and *other* share no common elements.

        Example::

            TreeSet([1, 2]).isdisjoint([3, 4])  # True
            TreeSet([1, 2]).isdisjoint([2, 3])  # False

        """
        if not hasattr(other, "__iter__"):
            raise TypeError(f"Operation is not supported with instance of {type(other)}")
        return all(not self.has(k) for k in other)

    def intersection_update(self, *others: Iterable[K]) -> None:
        """
        Keep only keys present in this set and all of *others*, in-place.

        Example::

            s = TreeSet([1, 2, 3, 4])
            s.intersection_update([2, 3, 5], [3, 6])
            str(s)  # "{3}"

        """
        all_others = TreeSet()
        if len(others) >= 1:
            all_others = TreeSet(others[0])
        for other in others[1:]:
            if not hasattr(other, "__iter__"):
                raise TypeError(f"Operation is not supported with instance of {type(other)}")
            all_others &= other
        for k in self:
            if k not in all_others:
                self.discard(k)

    def difference_update(self, *others: Iterable[K]) -> None:
        """
        Remove all keys found in any of *others* from this set, in-place.

        Example::

            s = TreeSet([1, 2, 3, 4])
            s.difference_update([2, 3], [4])
            str(s)  # "{1}"

        """
        for other in others:
            if not hasattr(other, "__iter__"):
                raise TypeError(f"Operation is not supported with instance of {type(other)}")
            for k in other:
                self.discard(k)

    def symmetric_difference_update(self, other: Iterable[K]) -> None:
        """
        Apply symmetric difference with *other* to this set in-place.

        Example::

            s = TreeSet([1, 2, 3])
            s.symmetric_difference_update([2, 3, 4])
            str(s)  # "{1,4}"

        """
        self ^= other

    def union(self, *others: Iterable[K]) -> TreeSet[K]:
        """
        Return a new set containing all keys from this set and all of *others*.

        Example::

            s = TreeSet([1, 2])
            str(s.union([3, 4], [5]))  # "{1,2,3,4,5}"

        """
        res = TreeSet[K](self.keys())
        for other in others:
            if not hasattr(other, "__iter__"):
                raise TypeError(f"Operation is not supported with instance of {type(other)}")
            for k in other:
                res.add(k)
        return res

    def intersection(self, *others: Iterable[K]) -> TreeSet[K]:
        """
        Return a new set with keys common to this set and all of *others*.

        Example::

            s = TreeSet([1, 2, 3, 4])
            str(s.intersection([2, 3, 5], [3, 6]))  # "{3}"

        """
        combined: set = set(next(iter(others))) if others else set()
        for other in list(others)[1:]:
            combined &= set(other)
        res = TreeSet[K]()
        for k in self.keys():
            if k in combined:
                res.add(k)
        return res

    def difference(self, *others: Iterable[K]) -> TreeSet[K]:
        """
        Return a new set with keys in this set that are not in any of *others*.

        Example::

            s = TreeSet([1, 2, 3, 4])
            str(s.difference([2, 3], [4]))  # "{1}"

        """
        excluded: set = set()
        for other in others:
            excluded |= set(other)
        res = TreeSet[K]()
        for k in self.keys():
            if k not in excluded:
                res.add(k)
        return res

    def symmetric_difference(self, other: Iterable[K]) -> TreeSet[K]:
        """
        Return a new set with keys in exactly one of this set and *other*.

        Example::

            s = TreeSet([1, 2, 3])
            str(s.symmetric_difference([2, 3, 4]))  # "{1,4}"

        """
        return self ^ other

    def __copy__(self) -> TreeSet[K]:
        """
        Create a shallow copy of the set.

        Example::

            import copy

            s = TreeSet([1, 2, 3])
            s2 = copy.copy(s)
            s2.add(4)
            str(s)  # "{1,2,3}"   — original unchanged
            str(s2)  # "{1,2,3,4}"

        """
        return TreeSet[K](self)

    # ------------------------------------------------------------------
    # Additional iteration
    # ------------------------------------------------------------------

    def backwards(self) -> JsReverseIterator[K]:
        """
        Return a reverse iterator over all keys in descending order.

        Example::

            s = TreeSet([1, 2, 3])
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

        Setting this property clears all existing elements because the
        current ordering is no longer valid.

        Example::

            s = TreeSet()
            s.compare_func = lambda a, b: -1 if a < b else (1 if a > b else 0)
            s.add(3)
            s.add(1)
            list(s)  # [1, 3]

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

            s = TreeSet([1, 2, 3])
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

            s = TreeSet([1, 2, 3])
            it = s.begin()
            while not it.equals(s.end()):
                print(it.key)
                it.next()

        """
        return self._t.end()

    def find(self, key: K) -> TreeIterator[K, K]:
        """
        Return an STL-like iterator to the element with *key*, or end() if absent.

        Example::

            s = TreeSet([1, 2, 3])
            it = s.find(2)
            if not it.equals(s.end()):
                print(it.key)  # 2
            s.find(99).equals(s.end())  # True

        """
        return self._t.find(key)

    def insert_unique(self, key: K) -> InsertionResult[TreeIterator[K, K]]:
        """
        Insert *key* only when it is not already present.

        Returns:
            InsertionResult with was_added=True when the key was new;
            was_added=False when the key already existed.

        Example::

            s = TreeSet()
            res = s.insert_unique(1)
            res.was_added  # True
            res2 = s.insert_unique(1)
            res2.was_added  # False

        """
        n: TreeNode[K, K] = TreeNode()
        n.key = key
        return self._t.insert_unique(n)

    def insert_or_replace(self, key: K) -> InsertionResult[TreeIterator[K, K]]:
        """
        Insert *key* if absent; if present, "replace" (update the same node).

        Returns:
            InsertionResult with was_added=True on new insertion, or
            was_replaced=True when the key already existed.

        Example::

            s = TreeSet()
            res = s.insert_or_replace(1)
            res.was_added  # True
            res2 = s.insert_or_replace(1)
            res2.was_replaced  # True

        """
        n: TreeNode[K, K] = TreeNode()
        n.key = key
        return self._t.insert_or_replace(n)

    def erase(self, iterator: TreeIterator[K, K]) -> None:
        """
        Remove the element pointed to by *iterator*.

        Example::

            s = TreeSet([1, 2, 3])
            it = s.find(2)
            s.erase(it)
            str(s)  # "{1,3}"

        """
        self._t.erase(iterator.node)

    def lower_bound(self, key: K) -> TreeIterator[K, K]:
        """
        Return an STL-like iterator to the first element with key >= *key*, or end().

        Example::

            s = TreeSet([2, 4, 6, 8])
            lo = s.lower_bound(3)  # iterator to 4
            hi = s.upper_bound(6)  # iterator to 8
            it = lo
            while not it.equals(hi):
                print(it.key)  # 4, 6
                it.next()

        """
        return self._t.lower_bound(key)

    def rbegin(self) -> ReverseIterator[K, K]:
        """
        Return a reverse STL-like iterator to the element with the largest key.

        Example::

            s = TreeSet([1, 2, 3])
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

            s = TreeSet([1, 2, 3])
            it = s.rbegin()
            while not it.equals(s.rend()):
                print(it.key)
                it.next()

        """
        return self._t.rend()

    def upper_bound(self, key: K) -> TreeIterator[K, K]:
        """
        Return an STL-like iterator to the first element with key > *key*, or end().

        Example::

            s = TreeSet([2, 4, 6, 8])
            lo = s.lower_bound(3)  # iterator to 4
            hi = s.upper_bound(6)  # iterator to 8
            it = lo
            while not it.equals(hi):
                print(it.key)  # 4, 6
                it.next()

        """
        return self._t.upper_bound(key)

    def first(self) -> K | None:
        """
        Return the smallest element, or None when the set is empty.

        Example::

            s = TreeSet([1, 2, 3])
            s.first()  # 1
            TreeSet().first()  # None

        """
        result = self._t.first()
        return result

    def last(self) -> K | None:
        """
        Return the largest element, or None when the set is empty.

        Example::

            s = TreeSet([1, 2, 3])
            s.last()  # 3
            TreeSet().last()  # None

        """
        result = self._t.last()
        return result
