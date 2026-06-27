import copy

import pytest

from stl_treemap.tree_set import TreeSet

# ------------------------------------------------------------------
# Constructor
# ------------------------------------------------------------------


def test_constructor_empty():
    s: TreeSet[int] = TreeSet()
    assert s.size == 0


def test_constructor_list():
    s = TreeSet([1, 2, 3])
    assert s.size == 3
    assert list(s) == [1, 2, 3]


def test_constructor_deduplication():
    s = TreeSet([3, 1, 2, 1, 3])
    assert s.size == 3
    assert list(s) == [1, 2, 3]


def test_constructor_python_set():
    s = TreeSet({2, 1, 3})
    assert s.size == 3
    assert list(s) == [1, 2, 3]


def test_constructor_generator():
    def gen():
        yield from range(1, 4)

    s = TreeSet(gen())
    assert s.size == 3
    assert list(s) == [1, 2, 3]


def test_constructor_args():
    s = TreeSet(None, 1, 2, 3)
    assert s.size == 3
    assert list(s) == [1, 2, 3]


def test_constructor_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet(35)  # type: ignore[arg-type]
    assert "iterable objects" in str(ex.value)


def test_constructor_none():
    s = TreeSet(None)
    assert s.size == 0


def test_constructor_no_arg():
    s = TreeSet()
    assert s.size == 0


def test_constructor_range():
    s = TreeSet(range(1, 4))
    assert list(s) == [1, 2, 3]


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

    s: TreeSet[Id] = TreeSet()
    s.compare_func = compare_ids
    s.add(Id("B", 8))
    s.add(Id("A", 340))
    s.add(Id("A", 12))
    s.add(Id("AA", 147))

    actual = [(k.alpha, k.num) for k in s]
    assert actual == [("A", 12), ("A", 340), ("AA", 147), ("B", 8)]


def test_compare_func_property_get():
    s: TreeSet[int] = TreeSet([1, 2, 3])
    assert callable(s.compare_func)
    assert s.compare_func(1, 2) == -1
    assert s.compare_func(2, 1) == 1
    assert s.compare_func(1, 1) == 0


# ------------------------------------------------------------------
# Core mutation
# ------------------------------------------------------------------


def test_clear():
    s = TreeSet([1, 2, 3])
    s.clear()
    assert s.size == 0


def test_add_unique():
    s: TreeSet[int] = TreeSet()
    s.add(1)
    s.add(1)
    assert s.size == 1


def test_discard_existing():
    s = TreeSet([1, 2, 3])
    s.discard(2)
    assert str(s) == "{1,3}"


def test_discard_missing():
    s = TreeSet([1, 2, 3])
    s.discard(99)
    assert str(s) == "{1,2,3}"


def test_delete_existing():
    s = TreeSet([1, 2, 3])
    s.delete(2)
    assert str(s) == "{1,3}"
    s.delete(4)
    assert str(s) == "{1,3}"


def test_delete_rightmost_and_root():
    s = TreeSet([1, 5, 3])
    s.delete(5)
    s.delete(3)
    s.add(4)
    assert str(s) == "{1,4}"


def test_delete_leftmost_and_root():
    s = TreeSet([1, 5, 3])
    s.delete(1)
    s.delete(3)
    s.add(2)
    assert str(s) == "{2,5}"


def test_remove_existing():
    s = TreeSet([1, 2, 3])
    s.remove(2)
    assert str(s) == "{1,3}"


def test_remove_missing():
    s = TreeSet([1, 2, 3])
    with pytest.raises(KeyError):
        s.remove(99)


def test_pop_specific_key():
    s = TreeSet([1, 2, 3])
    v = s.pop(2)
    assert v == 2
    assert str(s) == "{1,3}"


def test_pop_missing_returns_default():
    s = TreeSet([1, 2, 3])
    assert s.pop(99) is None
    assert s.pop(99, 0) == 0


def test_pop_no_args_removes_smallest():
    s = TreeSet([3, 1, 2])
    v = s.pop()
    assert v == 1
    assert list(s) == [2, 3]


def test_pop_no_args_empty_raises():
    s: TreeSet[int] = TreeSet()
    with pytest.raises(KeyError) as ex:
        s.pop()
    msg = str(ex)
    assert "pop from an empty set" in msg


# ------------------------------------------------------------------
# Queries
# ------------------------------------------------------------------


def test_has():
    s = TreeSet([1, 2, 3])
    assert s.has(1) is True
    assert s.has(4) is False


def test_contains():
    s = TreeSet([1, 2, 3])
    assert 1 in s
    assert 4 not in s


def test_size():
    s = TreeSet([1, 2, 3])
    assert s.size == 3


def test_len():
    s = TreeSet([1, 2, 3])
    assert len(s) == 3


# ------------------------------------------------------------------
# Iteration
# ------------------------------------------------------------------


def test_iter():
    s = TreeSet([3, 1, 2])
    assert list(s) == [1, 2, 3]


def test_keys():
    s = TreeSet([1, 2, 3])
    assert list(s.keys()) == [1, 2, 3]


def test_keys_backwards():
    s = TreeSet([1, 2, 3])
    assert list(s.keys().backwards()) == [3, 2, 1]


def test_backwards():
    s = TreeSet([1, 2, 3])
    assert list(s.backwards()) == [3, 2, 1]


# ------------------------------------------------------------------
# String representation
# ------------------------------------------------------------------


def test_str():
    s = TreeSet([1, 2, 3])
    assert str(s) == "{1,2,3}"


def test_str_empty():
    s: TreeSet[int] = TreeSet()
    assert str(s) == "{}"


def test_repr():
    s = TreeSet([1, 2, 3])
    assert repr(s) == "{1,2,3}"


# ------------------------------------------------------------------
# Set algebra operators
# ------------------------------------------------------------------


def test_or_tree_sets():
    s1 = TreeSet([1, 2, 3])
    s2 = TreeSet([2, 3, 4])
    assert str(s1 | s2) == "{1,2,3,4}"
    assert str(s1) == "{1,2,3}"  # original unchanged
    assert str(s2) == "{2,3,4}"


def test_or_list():
    s = TreeSet([1, 2, 3])
    assert str(s | [2, 3, 4]) == "{1,2,3,4}"


def test_or_python_set():
    s = TreeSet([1, 2, 3])
    assert str(s | {2, 3, 4}) == "{1,2,3,4}"


def test_or_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s | 25
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_ror_with_set():
    s = TreeSet([2, 3, 4])
    result = {1, 2, 3} | s
    assert str(result) == "{1,2,3,4}"


def test_ror_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        25 | s
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_ior_operator():
    s = TreeSet([1, 2])
    s |= {3, 4}
    assert str(s) == "{1,2,3,4}"


def test_ior_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s |= 25
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_and_tree_sets():
    s1 = TreeSet([1, 2, 3])
    s2 = TreeSet([2, 3, 4])
    assert str(s1 & s2) == "{2,3}"


def test_and_list():
    s = TreeSet([1, 2, 3])
    assert str(s & [2, 3, 4]) == "{2,3}"


def test_and_python_set():
    s = TreeSet([1, 2, 3])
    assert str(s & {2, 3, 4}) == "{2,3}"


def test_and_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s & 25
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_rand_set():
    s = TreeSet([2, 3, 4])
    result = {1, 2, 3} & s
    assert str(result) == "{2,3}"


def test_rand_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        25 & s
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_iand_tree_set():
    s = TreeSet([1, 2, 3])
    s &= TreeSet({2, 3, 4})
    assert str(s) == "{2,3}"


def test_iand_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s &= 25
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_sub_tree_sets():
    s1 = TreeSet([1, 2, 3])
    s2 = TreeSet([2, 3, 4])
    assert str(s1 - s2) == "{1}"


def test_sub_list():
    s1 = TreeSet([1, 2, 3])
    s2 = [2, 3, 4]
    assert str(s1 - s2) == "{1}"


def test_sub_python_set():
    s1 = TreeSet([1, 2, 3])
    s2 = {2, 3, 4}
    assert str(s1 - s2) == "{1}"


def test_sub_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s - 25
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_rsub():
    s = TreeSet([2, 3, 4])
    result = {1, 2, 3} - s
    assert str(result) == "{1}"


def test_rsub_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        25 - s
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_isub():
    s = TreeSet([1, 2, 3])
    s -= {2, 3, 4}
    assert str(s) == "{1}"


def test_isub_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s -= 25
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_xor():
    s1 = TreeSet([1, 2, 3])
    s2 = TreeSet([2, 3, 4])
    assert str(s1 ^ s2) == "{1,4}"


def test_xor_python_set():
    s = TreeSet([2, 3, 4])
    result = s ^ {1, 2, 3}
    assert str(result) == "{1,4}"


def test_xor_list():
    s = TreeSet([2, 3, 4])
    result = s ^ [1, 2, 3]
    assert str(result) == "{1,4}"


def test_xor_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s ^ 25
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_rxor():
    s = TreeSet([2, 3, 4])
    result = {1, 2, 3} ^ s
    assert str(result) == "{1,4}"


def test_rxor_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        25 ^ s
    msg = str(ex)
    assert "unsupported operand type" in msg


def test_ixor():
    s = TreeSet([1, 2, 3])
    s ^= {2, 3, 4}
    assert str(s) == "{1,4}"


def test_ixor_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s ^= 25
    msg = str(ex)
    assert "unsupported operand type" in msg


# ------------------------------------------------------------------
# Comparison operators
# ------------------------------------------------------------------


def test_le_subset():
    assert TreeSet([1, 2]) <= TreeSet([1, 2, 3])


def test_le_equal():
    assert TreeSet([1, 2]) <= TreeSet([1, 2])


def test_le_false():
    assert not (TreeSet([1, 2]) <= TreeSet([1, 3]))


def test_le_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s <= 25  # noqa: B015
    msg = str(ex)
    assert "not supported between instances" in msg


def test_lt_proper_subset():
    assert TreeSet([1, 2]) < TreeSet([1, 2, 3])


def test_lt_equal_is_false():
    assert not (TreeSet([1, 2]) < TreeSet([1, 2]))


def test_lt_greater_is_false():
    assert not (TreeSet([1, 4]) < TreeSet([1, 2]))


def test_lt_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s < 25  # noqa: B015
    msg = str(ex)
    assert "not supported between instances" in msg


def test_ge_superset():
    assert TreeSet([1, 2, 3]) >= TreeSet([1, 2])


def test_ge_equal():
    assert TreeSet([1, 2]) >= TreeSet([1, 2])


def test_ge_superset_is_false():
    assert not TreeSet([1, 2]) >= TreeSet([1, 2, 3])


def test_ge_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s >= 25  # noqa: B015
    msg = str(ex)
    assert "not supported between instances" in msg


def test_gt_proper_superset():
    assert TreeSet([1, 2, 3]) > TreeSet([1, 2])


def test_gt_equal_is_false():
    assert not (TreeSet([1, 2]) > TreeSet([1, 2]))


def test_gt_superset_is_false():
    assert not (TreeSet([1, 2]) > TreeSet([1, 2, 3]))


def test_gt_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s > 25  # noqa: B015
    msg = str(ex)
    assert "not supported between instances" in msg


# ------------------------------------------------------------------
# Set relationship methods
# ------------------------------------------------------------------


def test_issubset_true():
    assert TreeSet([1, 2]).issubset([1, 2, 3])


def test_issubset_equal_true():
    assert TreeSet([1, 2, 3]).issubset([1, 2, 3])


def test_issubset_false():
    assert not TreeSet([1, 4]).issubset([1, 2, 3])


def test_issubset_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s.issubset(25)
    msg = str(ex)
    assert "not supported between instances" in msg


def test_issuperset_true():
    assert TreeSet([1, 2, 3]).issuperset([1, 2])


def test_issuperset_equal_true():
    assert TreeSet([1, 2, 3]).issuperset([1, 2, 3])


def test_issuperset_false():
    assert not TreeSet([1, 2]).issuperset([1, 3])


def test_issuperset_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s.issuperset(25)
    msg = str(ex)
    assert "not supported between instances" in msg


def test_isdisjoint_true():
    assert TreeSet([1, 2]).isdisjoint([3, 4])


def test_isdisjoint_false():
    assert not TreeSet([1, 2]).isdisjoint([2, 3])


def test_isdisjoint_invalid():
    s = TreeSet([1, 2])
    with pytest.raises(TypeError) as ex:
        s.isdisjoint(25)
    msg = str(ex)
    assert "is not supported with instance" in msg
    assert "'int'" in msg


# ------------------------------------------------------------------
# Multi-operand set methods
# ------------------------------------------------------------------


def test_update():
    s = TreeSet[int]([1, 2])
    s.update(TreeSet([2, 3, 4]))
    assert (list(s)) == [1, 2, 3, 4]


def test_update_multiple_iterables():
    s = TreeSet([1, 2])
    s.update(TreeSet([3, 4]), [5], {6, 7})
    assert str(s) == "{1,2,3,4,5,6,7}"


def test_update_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet().update(35)
    assert "only iterable objects" in str(ex.value)


def test_intersection_update():
    s = TreeSet([1, 2, 3, 4])
    s.intersection_update(TreeSet([2, 3, 5]))
    assert str(s) == "{2,3}"


def test_intersection_update_two_sets():
    s = TreeSet([1, 2, 3, 4])
    s.intersection_update([2, 3, 5], {3, 6})
    assert str(s) == "{3}"


def test_intersection_update_invalid1():
    with pytest.raises(TypeError) as ex:
        TreeSet().intersection_update(25, {3, 6})
    assert "only iterable objects" in str(ex.value)


def test_intersection_update_invalid2():
    with pytest.raises(TypeError) as ex:
        TreeSet().intersection_update([2, 3, 5], 25)
    assert "not supported with instance" in str(ex.value)


def test_difference_update():
    s = TreeSet([1, 2, 3, 4])
    s.difference_update(TreeSet([2, 4]), [2, 3], [4])
    assert str(s) == "{1}"


def test_difference_update_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet().difference_update(35)
    assert "not supported with instance" in str(ex.value)


def test_symmetric_difference_update():
    s = TreeSet([1, 2, 3])
    s.symmetric_difference_update([2, 2, 3, 4])
    assert str(s) == "{1,2,4}"


def test_symmetric_difference_update_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet().symmetric_difference_update(35)
    assert "unsupported operand type" in str(ex.value)


def test_union():
    s = TreeSet([1, 2])
    assert str(s.union([3, 4], {5})) == "{1,2,3,4,5}"


def test_union_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet().union(35)
    assert "not supported with instance" in str(ex.value)


def test_intersection():
    s = TreeSet([1, 2, 3, 4])
    assert str(s.intersection([2, 3, 5], {3, 6})) == "{3}"


def test_intersection_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet().intersection(35)
    assert "object is not iterable" in str(ex.value)


def test_difference():
    s = TreeSet([1, 2, 3, 4])
    assert str(s.difference([2, 3], {4})) == "{1}"


def test_difference_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet().difference(35)
    assert "object is not iterable" in str(ex.value)


def test_symmetric_difference():
    s = TreeSet([1, 2, 3])
    assert str(s.symmetric_difference([2, 3, 4])) == "{1,4}"


def test_symmetric_difference_invalid():
    with pytest.raises(TypeError) as ex:
        TreeSet().symmetric_difference(35)
    assert "unsupported operand type" in str(ex.value)


# ------------------------------------------------------------------
# Copy
# ------------------------------------------------------------------


def test_copy():
    s = TreeSet([1, 2, 3])
    s2 = copy.copy(s)
    s2.add(4)
    assert str(s) == "{1,2,3}"
    assert str(s2) == "{1,2,3,4}"


# ------------------------------------------------------------------
# STL-style iterators
# ------------------------------------------------------------------


def test_begin_end():
    s = TreeSet([1, 2, 3])
    actual = []
    it = s.begin()
    while not it.equals(s.end()):
        actual.append(it.key)
        it.next()
    assert actual == [1, 2, 3]


def test_rbegin_rend():
    s = TreeSet([1, 2, 3])
    actual = []
    it = s.rbegin()
    while not it.equals(s.rend()):
        actual.append(it.key)
        it.next()
    assert actual == [3, 2, 1]


def test_find_existing():
    s = TreeSet([1, 2, 3])
    it = s.find(2)
    assert it.key == 2
    assert not it.equals(s.end())


def test_find_missing():
    s = TreeSet([1, 2, 3])
    assert s.find(99).equals(s.end())


def test_lower_bound_upper_bound():
    s: TreeSet[int] = TreeSet()
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
    s: TreeSet[int] = TreeSet()
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
    s: TreeSet[int] = TreeSet()
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


def test_erase():
    s = TreeSet([1, 2, 3])
    it = s.find(2)
    it.prev()
    s.erase(it)
    assert str(s) == "{2,3}"
    s.delete(4)
    assert str(s) == "{2,3}"


def test_first_last():
    s = TreeSet([1, 2, 3])
    assert s.first() == 1
    assert s.last() == 3


def test_first_last_empty():
    s: TreeSet[int] = TreeSet([])
    assert s.first() is None
    assert s.last() is None
