import copy

import pytest

from stl_treemap.tree_multimap import TreeMultiMap


def test_constructor_empty():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    assert m.size == 0


def test_constructor_list():
    m = TreeMultiMap([[2, "B"], [1, "A"], [2, "B2"]])
    assert m.size == 3
    assert list(m.items()) == [(1, "A"), (2, "B"), (2, "B2")]


def test_constructor_dict():
    d = {2: "B", 1: "A", 3: "C"}
    m: TreeMultiMap[int, str] = TreeMultiMap(d)
    assert m.size == 3
    assert list(m.items()) == [(1, "A"), (2, "B"), (3, "C")]


def test_constructor_dict_items():
    d = {2: "B", 1: "A", 3: "C"}
    m: TreeMultiMap[int, str] = TreeMultiMap(d.items())
    assert m.size == 3
    assert list(m.items()) == [(1, "A"), (2, "B"), (3, "C")]


def test_constructor_kwargs():
    m = TreeMultiMap(A=1, B=2, C=3)
    assert m.size == 3
    assert list(m.items()) == [("A", 1), ("B", 2), ("C", 3)]


def test_constructor_generator():
    def gen():
        yield (1, "A")
        yield (2, "B")
        yield (2, "C")

    m = TreeMultiMap(gen())
    assert m.size == 3
    assert list(m.items()) == [(1, "A"), (2, "B"), (2, "C")]


def test_constructor_invalid():
    with pytest.raises(TypeError) as exc_info:
        TreeMultiMap(42)  # type: ignore[arg-type]
    assert "iterable objects" in str(exc_info.value)


def test_constructor_none():
    m = TreeMultiMap(None)
    assert m.size == 0


def test_set_allows_duplicate_keys():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    m.set(1, "A")
    m.set(1, "B")
    m.set(2, "C")
    assert m.size == 3
    assert list(m.values()) == ["A", "B", "C"]


def test_clear():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    m.clear()
    assert m.size == 0


def test_delete_removes_first_occurrence():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    m.delete(2)
    assert str(m) == "{1:A,2:C}"
    m.delete(99)
    assert str(m) == "{1:A,2:C}"


def test_get():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert m.get(1) == "A"
    assert m.get(2) == "B"
    assert m.get(4) is None
    assert m.get(4, "Z") == "Z"


def test_has():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert m.has(2) is True
    assert m.has(4) is False


def test_items():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert list(m.items()) == [(1, "A"), (2, "B"), (2, "C")]


def test_keys_with_duplicates():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert list(m.keys()) == [1, 2, 2]


def test_keys_backwards():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert list(m.keys().backwards()) == [2, 2, 1]


def test_values():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert list(m.values()) == ["A", "B", "C"]


def test_values_backwards():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert list(m.values().backwards()) == ["C", "B", "A"]


def test_size():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert m.size == 3


def test_len():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert len(m) == 3


def test_iter():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert list(m.items()) == [(1, "A"), (2, "B"), (2, "C")]


def test_getitem():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert m[1] == "A"
    assert m[2] == "B"


def test_getitem_missing():
    m = TreeMultiMap([[1, "A"]])
    with pytest.raises(KeyError) as exc_info:
        _ = m[99]
    assert "99" in str(exc_info.value)


def test_setitem_adds_duplicate():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    m[1] = "A"
    m[1] = "B"
    assert list(m.values()) == ["A", "B"]


def test_contains():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert 2 in m
    assert 4 not in m


def test_str():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert str(m) == "{1:A,2:B,2:C}"


def test_str_empty():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    assert str(m) == "{}"


def test_repr():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert repr(m) == "{1:A,2:B,2:C}"


def test_delitem():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    del m[2]
    assert str(m) == "{1:A,2:C}"


def test_delitem_missing():
    m = TreeMultiMap([[1, "A"]])
    with pytest.raises(KeyError):
        del m[99]


def test_pop():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    v = m.pop(2)
    assert v == "B"
    assert str(m) == "{1:A,2:C}"


def test_pop_missing():
    m = TreeMultiMap([[1, "A"]])
    assert m.pop(99) is None
    assert m.pop(99, "Z") == "Z"


def test_popitem():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert m.popitem(2) == (2, "B")
    assert str(m) == "{1:A,2:C}"
    with pytest.raises(KeyError) as ex:
        m.popitem(9)
    msg = str(ex)
    assert "Key 9 not found" in msg


def test_backwards():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert list(m.backwards()) == [2, 2, 1]


def test_compare_func():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    m.compare_func = lambda a, b: -1 if a < b else (1 if a > b else 0)
    m.set(3, "C")
    m.set(1, "A")
    m.set(1, "A2")
    assert list(m.keys()) == [1, 1, 3]


def test_compare_func_property_get():
    m = TreeMultiMap([[1, "A"]])
    assert callable(m.compare_func)
    assert m.compare_func(1, 2) == -1
    assert m.compare_func(2, 1) == 1
    assert m.compare_func(1, 1) == 0


def test_begin_end():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    actual = []
    it = m.begin()
    while not it.equals(m.end()):
        actual.append((it.key, it.value))
        it.next()
    assert actual == [(1, "A"), (2, "B"), (2, "C")]


def test_rbegin_rend():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    actual = []
    it = m.rbegin()
    while not it.equals(m.rend()):
        actual.append((it.key, it.value))
        it.next()
    assert actual == [(2, "C"), (2, "B"), (1, "A")]


def test_find():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    it = m.find(2)
    assert it.key == 2
    assert it.value == "B"
    assert m.find(99).equals(m.end())


def test_lower_bound_upper_bound_range():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    for i in range(1, 5):
        m.set(i * 2, f"N{i}a")
        m.set(i * 2, f"N{i}b")
    lo = m.lower_bound(4)
    hi = m.upper_bound(6)
    actual = []
    it = lo
    while not it.equals(hi):
        actual.append((it.key, it.value))
        it.next()
    assert actual == [(4, "N2a"), (4, "N2b"), (6, "N3a"), (6, "N3b")]


def test_insert_unique():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    res = m.insert_unique(1, "A")
    assert res.was_added
    assert res.iterator is not None
    assert res.iterator.value == "A"
    res2 = m.insert_unique(1, "B")
    assert not res2.was_added
    assert m.size == 1


def test_insert_or_replace():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    res = m.insert_or_replace(1, "A")
    assert res.was_added
    res2 = m.insert_or_replace(1, "B")
    assert res2.was_replaced
    assert res2.iterator is not None
    assert res2.iterator.value == "B"
    assert m.size == 1


def test_insert_multi():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    res1 = m.insert_multi(1, "A")
    assert res1.was_added
    res2 = m.insert_multi(1, "B")
    assert res2.was_added
    assert m.size == 2
    res2.iterator.prev()
    assert res2.iterator.value == "A"


def test_erase():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    it = m.find(2)
    m.erase(it)
    assert str(m) == "{1:A,2:C}"


def test_first_last():
    m: TreeMultiMap[int, str] = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    assert m.first() == (1, "A")
    assert m.last() == (2, "C")


def test_first_last_empty():
    m: TreeMultiMap[int, str] = TreeMultiMap()
    assert m.first() is None
    assert m.last() is None


def test_or_maps():
    m1 = TreeMultiMap([[1, "A"], [2, "B"]])
    m2 = TreeMultiMap([[2, "X"], [3, "C"]])
    result = m1 | m2
    assert str(result) == "{1:A,2:B,2:X,3:C}"
    assert str(m1) == "{1:A,2:B}"
    assert str(m2) == "{2:X,3:C}"
    assert isinstance(result, TreeMultiMap)


def test_or_dict():
    m = TreeMultiMap([[1, "A"], [2, "B"]])
    result = m | {2: "X", 3: "C"}
    assert str(result) == "{1:A,2:B,2:X,3:C}"
    assert isinstance(result, TreeMultiMap)


def test_or_list():
    m = TreeMultiMap([[1, "A"], [2, "B"]])
    result = m | [[2, "X"], [3, "C"]]
    assert str(result) == "{1:A,2:B,2:X,3:C}"
    assert isinstance(result, TreeMultiMap)


def test_or_items():
    m = TreeMultiMap([[1, "A"], [2, "B"]])
    result = m | {2: "X", 3: "C"}.items()
    assert str(result) == "{1:A,2:B,2:X,3:C}"
    assert isinstance(result, TreeMultiMap)


def test_or_not_implemented():
    m = TreeMultiMap({1: "A", 2: "B", 3: "C"})
    with pytest.raises(TypeError) as ex:
        m | 25
    msg = str(ex)
    assert "unsupported operand type" in msg
    assert "TreeMultiMap" in msg
    assert "int" in msg


def test_ror_dict():
    m = TreeMultiMap([[2, "X"], [3, "C"]])
    res = {1: "A", 2: "B"} | m
    assert str(res) == "{1:A,2:B,2:X,3:C}"
    assert isinstance(res, TreeMultiMap)


def test_ror_list():
    m = TreeMultiMap([[2, "X"], [3, "C"]])
    res = [[1, "A"], [2, "B"]] | m
    assert str(res) == "{1:A,2:B,2:X,3:C}"
    assert isinstance(res, TreeMultiMap)


def test_ror_items():
    # This form is not very usable in practice, because it produces a set of tuples
    m = TreeMultiMap([[2, "X"], [3, "C"]])
    res = {1: "A", 2: "B"}.items() | m
    assert isinstance(res, set)


def test_ror_not_implemented():
    m = TreeMultiMap({1: "A", 2: "B", 3: "C"})
    with pytest.raises(TypeError) as ex:
        25 | m
    msg = str(ex)
    assert "unsupported operand type" in msg
    assert "TreeMultiMap" in msg
    assert "int" in msg


def test_ior_maps():
    m1 = TreeMultiMap([[1, "A"], [2, "B"]])
    m2 = TreeMultiMap({2: "X", 3: "C"})
    m1 |= m2
    assert str(m1) == "{1:A,2:B,2:X,3:C}"


def test_ior_dict():
    m1 = TreeMultiMap([[1, "A"], [2, "B"]])
    m2 = {2: "X", 3: "C"}
    m1 |= m2
    assert str(m1) == "{1:A,2:B,2:X,3:C}"


def test_ior_list():
    m1 = TreeMultiMap([[1, "A"], [2, "B"]])
    m2 = [[2, "X"], [3, "C"]]
    m1 |= m2
    assert str(m1) == "{1:A,2:B,2:X,3:C}"


def test_ior_items():
    m1 = TreeMultiMap([[1, "A"], [2, "B"]])
    m2 = {2: "X", 3: "C"}
    m1 |= m2.items()
    assert str(m1) == "{1:A,2:B,2:X,3:C}"


def test_ior_not_implemented():
    m = TreeMultiMap({1: "A", 2: "B", 3: "C"})
    with pytest.raises(TypeError) as ex:
        m |= 25
    msg = str(ex)
    assert "unsupported operand type" in msg
    assert "TreeMultiMap" in msg
    assert "int" in msg


def test_copy():
    m = TreeMultiMap([[1, "A"], [2, "B"], [2, "C"]])
    m2 = copy.copy(m)
    m2.set(3, "D")
    assert str(m) == "{1:A,2:B,2:C}"
    assert str(m2) == "{1:A,2:B,2:C,3:D}"
    assert m is not m2
