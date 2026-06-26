"""Ordered multimap backed by a red-black tree."""

from __future__ import annotations

from collections import UserDict
from collections.abc import Callable, Collection, Iterable
from typing import Any

from stl_treemap.insertion_result import InsertionResult
from stl_treemap.iterators import ReverseIterator, TreeIterator
from stl_treemap.js_iterators import JsIterator, JsReverseIterator
from stl_treemap.policies import KeyValuePolicy
from stl_treemap.tree import Tree
from stl_treemap.tree_node import TreeNode


class TreeMultiMap[K, V](Collection[K]):
    """
    Ordered map allowing multiple entries with the same key, backed by a red-black tree.

    Unlike TreeMap, duplicate keys are permitted. Entries with equal keys appear
    in insertion order and are kept in their key's sorted position relative to
    entries with different keys. Lookup, insertion, and deletion are all O(log n).

    Example::

        m = TreeMultiMap()
        m[2] = "b1"
        m[2] = "b2"
        m[1] = "a"
        for key, value in m:
            print(f"{key}: {value}")
        # 1: a
        # 2: b1
        # 2: b2
    """

    def __init__(self, iterable: Iterable[tuple[K, V]] | None = None, **kwargs) -> None:
        """
        Create an empty multimap, or pre-populate it from an iterable of (key, value) pairs.

        Each pair in *iterable* is inserted independently; duplicate keys are kept.

        Args:
            iterable: Optional iterable of (key, value) tuples.
            kwargs: Another way to provide key-value pairs.

        Raises:
            TypeError: When *iterable* is not iterable.

        Example::

            m = TreeMultiMap()
            m = TreeMultiMap([[2, "B"], [1, "A"], [2, "B2"]])
            m = TreeMultiMap({2: "B", 1: "A", 3: "C"})
            m = TreeMultiMap(A=1, B=2)  # {"A": 1, "B": 2}

        """
        self._t: Tree[K, V] = Tree()
        self._t.value_policy = KeyValuePolicy()
        if iterable is not None:
            if isinstance(iterable, (dict, UserDict, TreeMultiMap)):
                for k, v in iterable.items():
                    self.set(k, v)
            elif hasattr(iterable, "__iter__"):
                for k, v in iterable:
                    self.set(k, v)
            else:
                raise TypeError("TreeMultiMap constructor accepts only iterable objects")
        if kwargs:
            for k, v in kwargs.items():
                self.set(k, v)

    # ------------------------------------------------------------------
    # Python dict-compatible methods
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all key-value pairs.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            m.clear()
            len(m)  # 0

        """
        self._t.clear()

    def delete(self, key: K) -> None:
        """
        @private Remove the first entry with *key*; does nothing if the key is absent.

        When multiple entries share the same key, only the first one is removed.
        Call repeatedly or use erase() to remove all of them.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            m.delete(2)  # removes the first entry with key 2
            str(m)  # "{1:A,2:C}"
            m.delete(99)  # no-op

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            self._t.erase(it.node)

    def get(self, key: K, default: V | None = None) -> V | None:
        """
        Return the value of the first entry with *key*, or *default* if absent.

        Args:
            key: Key to look up.
            default: Value returned when *key* is not in the map.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            m.get(2)  # "B"  — first entry with key 2
            m.get(4)  # None
            m.get(4, "Z")  # "Z"

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            return it.value
        return default

    def has(self, key: K) -> bool:
        """
        @private Return True when at least one entry with *key* exists in the map.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            m.has(2)  # True
            m.has(4)  # False

        """
        it = self._t.find(key)
        return not it.equals(self._t.end())

    def set(self, key: K, value: V) -> None:
        """
        @private Add a new *(key, value)* entry, even when *key* already exists.

        This is the defining behaviour of a multimap: duplicate keys are always
        accepted, so calling ``set()`` twice with the same key creates two
        distinct entries.

        Example::

            m = TreeMultiMap()
            m.set(1, "A")
            m.set(1, "B")  # second entry with key 1
            list(m.values())  # ["A", "B"]

        """
        n: TreeNode[K, V] = TreeNode()
        n.key = key
        n.value = value
        self._t.insert_multi(n)

    def items(self) -> JsIterator[tuple[K, V]]:
        """
        Return a forward iterator over (key, value) pairs in ascending key order.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            for key, value in m.items():
                print(f"key: {key}, value: {value}")
            # key: 1, value: A
            # key: 2, value: B
            # key: 2, value: C

        """
        return self._t.items()

    def keys(self) -> JsIterator[K]:
        """
        Return a forward iterator over keys in ascending order (including duplicates).

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            list(m.keys())  # [1, 2, 2]
            list(m.keys().backwards())  # [2, 2, 1]

        """
        return self._t.keys()

    def values(self) -> JsIterator[V]:
        """
        Return a forward iterator over values in ascending key order.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            list(m.values())  # ["A", "B", "C"]
            list(m.values().backwards())  # ["C", "B", "A"]

        """
        return self._t.values()

    @property
    def size(self) -> int:
        """
        @private Total number of entries in the map, counting each duplicate separately.

        Example::

            m = TreeMultiMap([[2, "B"], [2, "C"], [1, "A"]])
            m.size  # 3

        """
        return self._t.size()

    def __getitem__(self, key: K) -> V:
        """
        Return the value of the first entry with *key*.

        Args:
            key: Key to look up.

        Returns:
            Value of the first matching entry.

        Raises:
            KeyError: When *key* is not present.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            m[2]  # "B"  — first entry with key 2
            m[4]  # raises KeyError

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            return it.value
        raise KeyError(f"Key {key} not found")

    def __setitem__(self, key: K, value: V) -> None:
        """
        Add a new *(key, value)* entry (same as set()).

        Unlike a dict, this never replaces an existing entry; it always adds a new one.

        Args:
            key: Key for the new entry.
            value: Value to associate with the key.

        Example::

            m = TreeMultiMap()
            m[1] = "A"
            m[1] = "B"  # adds a second entry, does NOT replace
            list(m.values())  # ["A", "B"]

        """
        self.set(key, value)

    def __contains__(self, key: K) -> bool:
        """
        Return True if at least one entry with *key* exists.

        Args:
            key: Key to check.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            2 in m  # True
            4 in m  # False

        """
        return self.has(key)

    def __iter__(self) -> JsIterator[K]:
        """
        Iterate over (key, value) pairs in ascending key order.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            for key in m:
                print(f"{key}")
            # 1
            # 2
            # 2

        """
        return self._t.keys()

    def __len__(self) -> int:
        """
        Return the total number of entries, counting each duplicate separately.

        Example::

            m = TreeMultiMap([[2, "B"], [2, "C"], [1, "A"]])
            len(m)  # 3

        """
        return self._t.size()

    def __str__(self) -> str:
        """
        Return a string representation in the form {key1:value1,key2:value2,...}.

        Duplicate keys appear multiple times in the output.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            str(m)  # "{1:A,2:B,2:C}"

        """
        return str(self._t)

    def __repr__(self) -> str:
        """
        Return a string representation of the container's contents.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            repr(m)  # "{1:A,2:B,2:C}"

        """
        return self.__str__()

    def __delitem__(self, key: K) -> None:
        """
        Remove **ONLY** the first entry with *key*, or raise KeyError when absent.

        Args:
            key: Key to remove.

        Raises:
            KeyError: When *key* is not present.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            del m[2]  # removes first entry with key 2; m is now {1:A,2:C}
            del m[99]  # raises KeyError

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            self._t.erase(it.node)
        else:
            raise KeyError(f"Key {key} not found")

    def pop(self, key: K, default: V | None = None) -> V | None:
        """
        Remove **ONLY** the first entry with *key* and return its value, or return *default*.

        Args:
            key: Key to remove.
            default: Value to return when *key* is not present.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            m.pop(2)  # "B", m is now {1:A,2:C}
            m.pop(9)  # None, m is unchanged
            m.pop(9, "Z")  # "Z", m is unchanged

        """
        it = self._t.find(key)
        if not it.equals(self._t.end()):
            res = it.value
            self._t.erase(it.node)
            return res
        return default

    # ------------------------------------------------------------------
    # Additional iteration
    # ------------------------------------------------------------------

    def backwards(self) -> JsReverseIterator[K]:
        """
        Return a reverse iterator over keys in descending key order (including duplicates).

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            for key in m.backwards():
                print(key)
            # 2
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
        @private The current 3-way comparison function used to order keys.

        The function must accept two key arguments and return a negative
        integer, zero, or a positive integer when the first key is less
        than, equal to, or greater than the second key.

        Setting this property clears all existing entries because the
        current ordering is no longer valid.

        Example::

            m = TreeMultiMap()
            m.compare_func = lambda a, b: -1 if a < b else (1 if a > b else 0)
            m.set(3, "C")
            m.set(1, "A")
            list(m.keys())  # [1, 3]

        """
        return self._t.compare

    @compare_func.setter
    def compare_func(self, func: Callable[[Any, Any], int]) -> None:
        """@private Replace the comparison function and clear all entries."""
        self.clear()
        self._t.compare = func

    # ------------------------------------------------------------------
    # STL-style iterators
    # ------------------------------------------------------------------

    def begin(self) -> TreeIterator[K, V]:
        """
        Return a forward STL-like iterator to the first entry.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            it = m.begin()
            while not it.equals(m.end()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()
            # key: 1, value: A
            # key: 2, value: B
            # key: 2, value: C

        """
        return self._t.begin()

    def end(self) -> TreeIterator[K, V]:
        """
        Return a forward STL-like iterator past the last entry.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            it = m.begin()
            while not it.equals(m.end()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()

        """
        return self._t.end()

    def find(self, key: K) -> TreeIterator[K, V]:
        """
        Return a forward iterator to the first entry with *key*, or end() if absent.

        When multiple entries share the same key, the iterator points to the first one.
        Use lower_bound() / upper_bound() to iterate over all entries with that key.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            it = m.find(2)
            if not it.equals(m.end()):
                print(f"key: {it.key}, value: {it.value}")  # key: 2, value: B
            m.find(99).equals(m.end())  # True

        """
        return self._t.find(key)

    def insert_unique(self, key: K, value: V) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert *(key, value)* only when *key* is not already present.

        Returns:
            InsertionResult with was_added=True when the key was new;
            was_added=False when any entry with that key already existed.

        Example::

            m = TreeMultiMap()
            res = m.insert_unique(1, "A")
            res.was_added  # True
            res2 = m.insert_unique(1, "B")
            res2.was_added  # False — key 1 already exists

        """
        n: TreeNode[K, V] = TreeNode()
        n.key = key
        n.value = value
        return self._t.insert_unique(n)

    def insert_or_replace(self, key: K, value: V) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert *(key, value)*, replacing the first existing entry when *key* already exists.

        Returns:
            InsertionResult with was_added=True on new insertion, or
            was_replaced=True and the updated iterator on replacement.

        Example::

            m = TreeMultiMap()
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

    def insert_multi(self, key: K, value: V) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert *(key, value)* unconditionally, always creating a new entry.

        This is the multi-key insertion that makes TreeMultiMap distinct from TreeMap.

        Returns:
            InsertionResult with was_added=True and an iterator to the new entry.

        Example::

            m = TreeMultiMap()
            res = m.insert_multi(1, "A")
            res.was_added  # True
            res2 = m.insert_multi(1, "B")
            res2.was_added  # True — second entry with key 1 added
            res2.iterator.prev()
            res2.iterator.value  # "A"

        """
        n: TreeNode[K, V] = TreeNode()
        n.key = key
        n.value = value
        return self._t.insert_multi(n)

    def erase(self, iterator: TreeIterator[K, V]) -> None:
        """
        Remove the entry pointed to by *iterator*.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            it = m.find(2)
            m.erase(it)
            str(m)  # "{1:A,2:C}"

        """
        self._t.erase(iterator.node)

    def lower_bound(self, key: K) -> TreeIterator[K, V]:
        """
        Return an STL-like iterator to the first entry with key >= *key*, or end().

        Combined with upper_bound(), this gives a half-open range over all
        entries that share the same key.

        Example::

            m = TreeMultiMap([[2, "B1"], [2, "B2"], [4, "D"]])
            lo = m.lower_bound(2)
            hi = m.upper_bound(2)
            it = lo
            while not it.equals(hi):
                print(it.value)  # B1, B2
                it.next()

        """
        return self._t.lower_bound(key)

    def rbegin(self) -> ReverseIterator[K, V]:
        """
        Return a reverse STL-like iterator to the entry with the largest key.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            it = m.rbegin()
            while not it.equals(m.rend()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()
            # key: 2, value: C
            # key: 2, value: B
            # key: 1, value: A

        """
        return self._t.rbegin()

    def rend(self) -> ReverseIterator[K, V]:
        """
        Return a reverse STL-like iterator before the entry with the smallest key.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            it = m.rbegin()
            while not it.equals(m.rend()):
                print(f"key: {it.key}, value: {it.value}")
                it.next()

        """
        return self._t.rend()

    def upper_bound(self, key: K) -> TreeIterator[K, V]:
        """
        Return an STL-like iterator to the first entry with key > *key*, or end().

        Combined with lower_bound(), this gives a half-open range over all
        entries that share the same key.

        Example::

            m = TreeMultiMap([[2, "B1"], [2, "B2"], [4, "D"]])
            lo = m.lower_bound(2)
            hi = m.upper_bound(2)
            it = lo
            while not it.equals(hi):
                print(it.value)  # B1, B2
                it.next()

        """
        return self._t.upper_bound(key)

    def first(self) -> tuple[K, V] | None:
        """
        Return the first (key, value) pair, or None when the map is empty.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            key, value = m.first()  # (1, "A")
            TreeMultiMap().first()  # None

        """
        return self._t.first()

    def last(self) -> tuple[K, V] | None:
        """
        Return the last (key, value) pair, or None when the map is empty.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            key, value = m.last()  # (2, "C")
            TreeMultiMap().last()  # None

        """
        return self._t.last()

    def __or__(self, other: Any) -> TreeMultiMap[K, V]:
        """
        Return a new multimap containing all entries from this map followed by all from *other*.

        All entries are added via insert_multi, so duplicates are preserved.

        Example::

            m1 = TreeMultiMap([[1, "A"], [2, "B"]])
            m2 = TreeMultiMap([[2, "X"], [3, "C"]])
            m3 = m1 | m2
            str(m3)  # "{1:A,2:B,2:X,3:C}"

        """
        res = TreeMultiMap[K, V](self.items())
        if isinstance(other, (dict, UserDict, TreeMultiMap)):
            for k, v in other.items():
                res[k] = v
        elif hasattr(other, "__iter__"):
            for k, v in other:
                res[k] = v
        else:
            return NotImplemented
        return res

    def __ror__(self, other: Any) -> TreeMultiMap[K, V]:
        """
        Return a union multimap when this TreeMultiMap is on the right-hand side of ``|``.

        *other*'s entries are inserted first, then this map's entries are appended.

        Example::

            m = TreeMultiMap([[2, "X"], [3, "C"]])
            result = {1: "A", 2: "B"} | m
            str(result)  # "{1:A,2:B,2:X,3:C}"

        """
        if isinstance(other, (dict, UserDict, TreeMultiMap)) or hasattr(other, "__iter__"):
            res = TreeMultiMap[K, V](other)
        else:
            return NotImplemented
        for k, v in self.items():
            res[k] = v
        return res

    def __ior__(self, other: Any) -> TreeMultiMap[K, V]:
        """
        Add all entries from *other* to this multimap in-place.

        Example::

            m = TreeMultiMap([[1, "A"], [2, "B"]])
            m |= {2: "X", 3: "C"}
            str(m)  # "{1:A,2:B,2:X,3:C}"

        """
        if isinstance(other, (dict, UserDict, TreeMultiMap)):
            for k, v in other.items():
                self[k] = v
        elif hasattr(other, "__iter__"):
            for k, v in other:
                self[k] = v
        else:
            return NotImplemented
        return self

    def __copy__(self) -> TreeMultiMap[K, V]:
        """
        Create a shallow copy, preserving all entries including duplicates.

        Example::

            import copy

            m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
            m2 = copy.copy(m)
            m2.set(3, "D")
            str(m)  # "{1:A,2:B,2:C}"      — original unchanged
            str(m2)  # "{1:A,2:B,2:C,3:D}"

        """
        return TreeMultiMap[K, V](self.items())
