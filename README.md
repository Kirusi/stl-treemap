# stl-treemap

[![License Badge](https://img.shields.io/github/license/kirusi/stl-treemap)](https://github.com/Kirusi/stl-treemap/blob/master/README.md)

A Python library of ordered, tree-based associative containers. All containers are backed by a red-black tree and keep their elements in ascending key order at all times. Insertion, deletion, and lookup are all O(log n)

The following containers are provided:

* [**TreeMap**](https://kirusi.github.io/stl-treemap/stl_treemap/tree_map.html) — an ordered map associating unique keys with values. Behaves like a Python `dict` with sorted keys.
* [**TreeSet**](https://kirusi.github.io/stl-treemap/stl_treemap/tree_set.html) — an ordered set of unique keys. Behaves like a Python `set` with sorted elements.
* [**TreeMultiMap**](https://kirusi.github.io/stl-treemap/stl_treemap/tree_multimap.html) — an ordered map that allows multiple entries with the same key.
* [**TreeMultiSet**](https://kirusi.github.io/stl-treemap/stl_treemap/tree_multiset.html) — an ordered set that allows duplicate keys.

## Installation

```shell
pip install stl-treemap
```

Or with [uv](https://docs.astral.sh/uv/):

```shell
uv add stl-treemap
```

## Quick start

### TreeMap

```python
from stl_treemap import TreeMap

# Create and populate
m: TreeMap[int, str] = TreeMap()
m[2] = "B"
m[1] = "A"
m[3] = "C"

# Iterate in ascending key order
for key, value in m:
    print(f"key: {key}, value: {value}")
# key: 1, value: A
# key: 2, value: B
# key: 3, value: C

# Reverse iteration
for key, value in m.backwards():
    print(f"key: {key}, value: {value}")
# key: 3, value: C
# key: 2, value: B
# key: 1, value: A

# Initialize from a dict or list of pairs
m2 = TreeMap({2: "B", 1: "A", 3: "C"})
m3 = TreeMap([[2, "B"], [1, "A"], [3, "C"]])
```

### TreeSet

```python
from stl_treemap import TreeSet

s = TreeSet([3, 1, 2, 1])  # duplicates dropped → {1,2,3}
s.add(4)
s.discard(2)
print(list(s))  # [1, 3, 4]

# Set algebra — same operators as Python's built-in set
s1 = TreeSet([1, 2, 3])
s2 = TreeSet([2, 3, 4])
print(s1 | s2)  # {1,2,3,4}
print(s1 & s2)  # {2,3}
print(s1 - s2)  # {1}
print(s1 ^ s2)  # {1,4}
```

### TreeMultiMap

```python
from stl_treemap import TreeMultiMap

m: TreeMultiMap[int, str] = TreeMultiMap()
m[2] = "b1"
m[2] = "b2"   # second entry for the same key
m[1] = "a"

for key, value in m:
    print(f"key: {key}, value: {value}")
# key: 1, value: a
# key: 2, value: b1
# key: 2, value: b2
```

### TreeMultiSet

```python
from stl_treemap import TreeMultiSet

s = TreeMultiSet([1, 2, 2, 3])
s.add(2)           # another duplicate
print(list(s))     # [1, 2, 2, 2, 3]
s.discard(2)       # removes one occurrence
print(list(s))     # [1, 2, 2, 3]
```

## Iteration

All containers support Python's standard iteration protocol as well as STL-style explicit iterators for range-based traversal.

### Python-style

```python
# Forward
for key in s:
    print(key)

# Reverse
for key in s.backwards():
    print(key)
```

### STL-style iterators

Use `begin()` / `end()` for forward iteration and `rbegin()` / `rend()` for reverse. `lower_bound` and `upper_bound` let you iterate over a key range.

```python
# Iterate a specific key range [10, 20]
it = m.lower_bound(10)
stop = m.upper_bound(20)
while not it.equals(stop):
    print(f"key: {it.key}, value: {it.value}")
    it.next()

# Erase elements while iterating (erase a different iterator than the current one)
prev = None
it = m.lower_bound(10)
stop = m.upper_bound(20)
while not it.equals(stop):
    if prev is not None and prev.key == 15:
        m.erase(prev)
    from stl_treemap.iterators import TreeIterator
    prev = TreeIterator(it)   # copy current iterator
    it.next()
```

## Custom comparator

When keys are not natively comparable, supply a 3-way comparison function. It must return a negative int, zero, or positive int when `lhs < rhs`, `lhs == rhs`, or `lhs > rhs` respectively.

```python
from stl_treemap import TreeMap

def compare_str_len(a: str, b: str) -> int:
    return (len(a) > len(b)) - (len(a) < len(b))

m: TreeMap[str, int] = TreeMap()
m.compare_func = compare_str_len
m["bb"] = 2
m["aaa"] = 3
m["c"] = 1

print(list(m.keys()))  # ['c', 'bb', 'aaa']
```

The same `compare_func` property is available on `TreeSet`, `TreeMultiMap`, and `TreeMultiSet`. Setting it clears all existing elements because the current ordering is no longer valid.

## Why stl-treemap?

Python's built-in `dict` and `set` are hash-based and unordered. `sortedcontainers` provides sorted sequences, but this library's red-black tree gives true O(log n) worst-case complexity for all operations and exposes STL-style iterators for precise range manipulation — useful when you need to iterate, modify, or erase entries in a specific key range without rebuilding the container.
