import pytest

from stl_treemap.tree_multiset import TreeMultiSet

# ------------------------------------------------------------------
# Constructor
# ------------------------------------------------------------------


def test_constructor_empty():
    s: TreeMultiSet[int] = TreeMultiSet()
    assert s.size == 0


def test_constructor_list():
    s = TreeMultiSet([1, 2, 3, 1])
    assert s.size == 4
    assert list(s) == [1, 1, 2, 3]


def test_constructor_python_set():
    s = TreeMultiSet({2, 1, 3})
    assert s.size == 3
    assert list(s) == [1, 2, 3]


def test_constructor_generator():
    def gen():
        for i in range(1, 4):
            yield i
            yield i

    s = TreeMultiSet(gen())
    assert s.size == 6
    assert list(s) == [1, 1, 2, 2, 3, 3]


def test_constructor_invalid():
    with pytest.raises(TypeError) as ex:
        TreeMultiSet(35)  # type: ignore[arg-type]
    assert "iterable objects" in str(ex.value)


def test_constructor_none():
    s = TreeMultiSet(None)
    assert s.size == 0


def test_constructor_arg():
    s = TreeMultiSet(
        None,
        1,
        2,
        3,
        1,
    )
    assert s.size == 4
    assert list(s) == [1, 1, 2, 3]


def test_constructor_set_and_arg():
    s = TreeMultiSet(
        {1, 2},
        2,
        3,
    )
    assert s.size == 4
    assert list(s) == [1, 2, 2, 3]


def test_compare_func():
    class Id:
        def __init__(self, alpha: str, num: int) -> None:
            self.alpha = alpha
            self.num = num

    def compare_ids(lhs: Id, rhs: Id) -> int:
        if lhs.alpha < rhs.alpha:
            return -1
        if lhs.alpha > rhs.alpha:
            return 1
        if lhs.num < rhs.num:
            return -1
        if lhs.num > rhs.num:
            return 1
        return 0

    s: TreeMultiSet[Id] = TreeMultiSet()
    s.compare_func = compare_ids
    s.add(Id("B", 8))
    s.add(Id("A", 340))
    s.add(Id("A", 340))
    s.add(Id("A", 12))
    s.add(Id("AA", 147))

    actual = [(k.alpha, k.num) for k in s]
    assert actual == [("A", 12), ("A", 340), ("A", 340), ("AA", 147), ("B", 8)]


def test_compare_func_property_get():
    s: TreeMultiSet[int] = TreeMultiSet([1, 2, 3])
    assert callable(s.compare_func)
    assert s.compare_func(1, 2) == -1
    assert s.compare_func(2, 1) == 1
    assert s.compare_func(1, 1) == 0


# ------------------------------------------------------------------
# Core mutation
# ------------------------------------------------------------------


def test_clear():
    s = TreeMultiSet([1, 2, 3])
    s.clear()
    assert s.size == 0


def test_add_allows_duplicates():
    s: TreeMultiSet[int] = TreeMultiSet()
    s.add(1)
    s.add(1)
    assert s.size == 2
    assert list(s) == [1, 1]


def test_discard_removes_one_occurrence():
    s = TreeMultiSet([1, 2, 2, 3])
    s.discard(2)
    assert str(s) == "{1,2,3}"


def test_discard_missing():
    s = TreeMultiSet([1, 2, 3])
    s.discard(99)
    assert str(s) == "{1,2,3}"


def test_delete_existing():
    s = TreeMultiSet([1, 2, 2, 3])
    s.delete(2)
    assert str(s) == "{1,2,3}"
    s.delete(4)
    assert str(s) == "{1,2,3}"


def test_delete_removes_only_one():
    s = TreeMultiSet([2, 2, 2])
    s.delete(2)
    assert s.size == 2
    assert list(s) == [2, 2]


def test_remove_existing():
    s = TreeMultiSet([1, 2, 2, 3])
    s.remove(2)
    assert str(s) == "{1,2,3}"


def test_remove_missing():
    s = TreeMultiSet([1, 2, 3])
    with pytest.raises(KeyError):
        s.remove(99)


def test_pop_specific_key():
    s = TreeMultiSet([1, 2, 2, 3])
    v = s.pop(2)
    assert v == 2
    assert str(s) == "{1,2,3}"


def test_pop_missing_returns_default():
    s = TreeMultiSet([1, 2, 3])
    assert s.pop(99) is None
    assert s.pop(99, 0) == 0


def test_pop_no_args_removes_smallest():
    s = TreeMultiSet([3, 1, 2, 1])
    v = s.pop()
    assert v == 1
    assert list(s) == [1, 2, 3]


def test_pop_no_args_empty_raises():
    s: TreeMultiSet[int] = TreeMultiSet()
    with pytest.raises(KeyError) as ex:
        s.pop()
    assert "pop from an empty set" in str(ex)


# ------------------------------------------------------------------
# Queries
# ------------------------------------------------------------------


def test_has():
    s = TreeMultiSet([1, 2, 3])
    assert s.has(1) is True
    assert s.has(4) is False


def test_contains():
    s = TreeMultiSet([1, 2, 3])
    assert 1 in s
    assert 4 not in s


def test_size():
    s = TreeMultiSet([1, 2, 2, 3])
    assert s.size == 4


def test_len():
    s = TreeMultiSet([1, 2, 2, 3])
    assert len(s) == 4


# ------------------------------------------------------------------
# Iteration
# ------------------------------------------------------------------


def test_iter():
    s = TreeMultiSet([3, 1, 2, 1])
    assert list(s) == [1, 1, 2, 3]


def test_keys():
    s = TreeMultiSet([1, 2, 2, 3])
    assert list(s.keys()) == [1, 2, 2, 3]


def test_keys_backwards():
    s = TreeMultiSet([1, 2, 2, 3])
    assert list(s.keys().backwards()) == [3, 2, 2, 1]


def test_backwards():
    s = TreeMultiSet([1, 2, 3])
    assert list(s.backwards()) == [3, 2, 1]


# ------------------------------------------------------------------
# String representation
# ------------------------------------------------------------------


def test_str():
    s = TreeMultiSet([1, 2, 2, 3])
    assert str(s) == "{1,2,2,3}"


def test_str_empty():
    s: TreeMultiSet[int] = TreeMultiSet()
    assert str(s) == "{}"


def test_repr():
    s = TreeMultiSet([1, 2, 2, 3])
    assert repr(s) == "{1,2,2,3}"


# ------------------------------------------------------------------
# STL-style iterators
# ------------------------------------------------------------------


def test_begin_end():
    s = TreeMultiSet([1, 2, 2, 3])
    actual = []
    it = s.begin()
    while not it.equals(s.end()):
        actual.append(it.key)
        it.next()
    assert actual == [1, 2, 2, 3]


def test_rbegin_rend():
    s = TreeMultiSet([1, 2, 3])
    actual = []
    it = s.rbegin()
    while not it.equals(s.rend()):
        actual.append(it.key)
        it.next()
    assert actual == [3, 2, 1]


def test_find_existing():
    s = TreeMultiSet([1, 2, 2, 3])
    it = s.find(2)
    assert it.key == 2
    assert not it.equals(s.end())


def test_find_missing():
    s = TreeMultiSet([1, 2, 3])
    assert s.find(99).equals(s.end())


def test_lower_bound_upper_bound():
    s: TreeMultiSet[int] = TreeMultiSet()
    for i in range(1, 17):
        s.add(i * 2)
    actual = []
    it = s.upper_bound(50)
    lo = s.lower_bound(0)
    while not it.equals(lo):
        it.prev()
        actual.append(it.key)
    assert actual == [32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]


def test_insert_unique():
    s: TreeMultiSet[int] = TreeMultiSet()
    for i in range(1, 4):
        res = s.insert_unique(1)
        if i == 1:
            assert res.was_added
            assert not res.was_replaced
            assert res.iterator is not None
            assert res.iterator.key == 1
        else:
            assert not res.was_added
            assert not res.was_replaced
    assert s.size == 1


def test_insert_or_replace():
    s: TreeMultiSet[int] = TreeMultiSet()
    for i in range(1, 4):
        res = s.insert_or_replace(1)
        if i == 1:
            assert res.was_added
            assert not res.was_replaced
            assert res.iterator is not None
            assert res.iterator.key == 1
        else:
            assert not res.was_added
            assert res.was_replaced
            assert res.iterator.key == 1
    assert s.size == 1


def test_insert_multi():
    s: TreeMultiSet[int] = TreeMultiSet()
    for _ in range(1, 4):
        res = s.insert_multi(1)
        assert res.was_added
        assert not res.was_replaced
        assert res.iterator is not None
        assert res.iterator.key == 1
    assert s.size == 3


def test_erase():
    s = TreeMultiSet([1, 2, 3])
    it = s.find(2)
    it.prev()
    s.erase(it)
    assert str(s) == "{2,3}"
    s.delete(4)
    assert str(s) == "{2,3}"


def test_first_last():
    s = TreeMultiSet([1, 1, 2, 3, 3])
    assert s.first() == 1
    assert s.last() == 3


def test_first_last_empty():
    s: TreeMultiSet[int] = TreeMultiSet([])
    assert s.first() is None
    assert s.last() is None
