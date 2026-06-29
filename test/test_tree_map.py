import copy

import pytest

from stl_treemap.tree_map import TreeMap


def test_constructor_empty():
    m: TreeMap[int, str] = TreeMap()
    assert m.size == 0


def test_constructor_list():
    m = TreeMap([[2, "B"], [1, "A"], [3, "C"]])
    assert m.size == 3
    assert list(m.items()) == [(1, "A"), (2, "B"), (3, "C")]


def test_constructor_dict_items():
    d = {2: "B", 1: "A", 3: "C"}
    m: TreeMap[int, str] = TreeMap(d.items())
    assert m.size == 3
    assert list(m.items()) == [(1, "A"), (2, "B"), (3, "C")]


def test_constructor_dict():
    d = {2: "B", 1: "A", 3: "C"}
    m: TreeMap[int, str] = TreeMap(d)
    assert m.size == 3
    assert list(m.items()) == [(1, "A"), (2, "B"), (3, "C")]


def test_constructor_kwargs():
    m = TreeMap(A=1, B=2, C=3)
    assert m.size == 3
    assert list(m.items()) == [("A", 1), ("B", 2), ("C", 3)]


def test_constructor_generator():
    def gen():
        for i in range(1, 4):
            yield (i, f"N{i * 2}")

    m = TreeMap(gen())
    assert m.size == 3
    assert list(m.items()) == [(1, "N2"), (2, "N4"), (3, "N6")]


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

    m: TreeMap[Id, str] = TreeMap()
    m.compare_func = compare_ids
    m.set(Id("B", 8), "Book with id B8")
    m.set(Id("A", 340), "Book with id A340")
    m.set(Id("A", 12), "Book with id A12")
    m.set(Id("AA", 147), "Book with id AA147")

    actual = [(k.alpha, k.num, v) for k, v in m.items()]
    expected = [
        ("A", 12, "Book with id A12"),
        ("A", 340, "Book with id A340"),
        ("AA", 147, "Book with id AA147"),
        ("B", 8, "Book with id B8"),
    ]
    assert actual == expected


def test_constructor_invalid_literal():
    with pytest.raises(TypeError) as ex:
        TreeMap(35)  # type: ignore[arg-type]
    assert "iterable objects" in str(ex)


def test_constructor_none():
    m = TreeMap(None)
    assert m.size == 0


def test_constructor_no_arg():
    m = TreeMap()
    assert m.size == 0


def test_clear():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    m.clear()
    assert m.size == 0


def test_delete():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    m.delete(2)
    assert str(m) == "{1:A,3:C}"
    m.delete(4)
    assert str(m) == "{1:A,3:C}"


def test_items():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert list(m.items()) == [(1, "A"), (2, "B"), (3, "C")]


def test_get():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert m.get(1) == "A"
    assert m.get(4) is None


def test_get_default():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert m.get(4, "Q") == "Q"


def test_getitem():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert m[1] == "A"


def test_setitem():
    m = TreeMap[int, str]()
    m[1] = "A"
    m[2] = "B"
    m[3] = "C"
    assert list(m.items()) == [(1, "A"), (2, "B"), (3, "C")]


def test_contains():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert 1 in m


def test_contains_nonexisting():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert 4 not in m


def test_getitem_nonexisting():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    with pytest.raises(KeyError) as ex:
        _ = m[4]
    msg = str(ex)
    assert "Key 4 not found" in msg


def test_has():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert m.has(1) is True
    assert m.has(4) is False


def test_keys():
    m: TreeMap[int, str] = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert list(m.keys()) == [1, 2, 3]


def test_values():
    m: TreeMap[int, str] = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert list(m.values()) == ["A", "B", "C"]


def test_backwards():
    m: TreeMap[int, str] = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert list(m.backwards()) == [3, 2, 1]


def test_begin_end():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    actual = []
    it = m.begin()
    while not it.equals(m.end()):
        actual.append((it.key, it.value))
        it.next()
    assert actual == [(1, "A"), (2, "B"), (3, "C")]


def test_rbegin_rend():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    actual = []
    it = m.rbegin()
    while not it.equals(m.rend()):
        actual.append((it.key, it.value))
        it.next()
    assert actual == [(3, "C"), (2, "B"), (1, "A")]


def test_find():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    it = m.find(2)
    assert it.key == 2
    assert it.value == "B"
    it = m.find(4)
    assert it.equals(m.end())


def test_lower_bound_upper_bound():
    m: TreeMap[int, str] = TreeMap()
    for i in range(1, 17):
        m.set(i * 2, f"N{i}")
    actual = []
    it = m.upper_bound(50)
    lo = m.lower_bound(0)
    while not it.equals(lo):
        it.prev()
        actual.append(it.key)
    assert actual == [32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]


def test_insert_unique():
    m: TreeMap[int, str] = TreeMap()
    for i in range(1, 4):
        res = m.insert_unique(1, f"N{i}")
        if i == 1:
            assert res.was_added
            assert not res.was_replaced
            assert res.iterator is not None
            assert res.iterator.key == 1
            assert res.iterator.value == "N1"
        else:
            assert not res.was_added
            assert not res.was_replaced
    assert m.size == 1


def test_insert_or_replace():
    m: TreeMap[int, str] = TreeMap()
    for i in range(1, 4):
        res = m.insert_or_replace(1, f"N{i}")
        if i == 1:
            assert res.was_added
            assert not res.was_replaced
            assert res.iterator is not None
            assert res.iterator.key == 1
            assert res.iterator.value == f"N{i}"
        else:
            assert not res.was_added
            assert res.was_replaced
            assert res.iterator is not None
            assert res.iterator.key == 1
            assert res.iterator.value == f"N{i}"
    assert m.size == 1


def test_erase():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    it = m.find(2)
    it.prev()
    m.erase(it)
    assert str(m) == "{2:B,3:C}"
    m.delete(4)
    assert str(m) == "{2:B,3:C}"


def test_first_last():
    m: TreeMap[int, str] = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert m.first() is not None
    assert m.first()[1] == "A"
    assert m.last() is not None
    assert m.last()[1] == "C"


def test_first_last_empty():
    m: TreeMap[int, str] = TreeMap([])
    assert m.first() is None
    assert m.last() is None


def test_str():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert f"{m}" == "{1:A,2:B,3:C}"


def test_str_empty():
    m = TreeMap()
    assert f"{m}" == "{}"


def test_repr():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert repr(m) == "{1:A,2:B,3:C}"


def test_compare_property():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    compare_func = m.compare_func
    assert compare_func(1, 0) == 1


def test_delitem():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    del m[2]
    assert str(m) == "{1:A,3:C}"
    with pytest.raises(KeyError) as ex:
        del m[4]
    msg = str(ex)
    assert "Key 4 not found" in msg


def test_pop():
    m = TreeMap([[1, "A"], [2, "B"], [3, "C"]])
    assert m.pop(2) == "B"
    assert str(m) == "{1:A,3:C}"
    assert m.pop(9) is None
    assert m.pop(9, "Z") == "Z"
    assert str(m) == "{1:A,3:C}"


def test_or_maps():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    m2 = TreeMap({4: "D", 5: "E"})
    res = m1 | m2
    assert str(res) == "{1:A,2:B,3:C,4:D,5:E}"
    assert isinstance(res, TreeMap)


def test_or_dict():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    d = {4: "D", 5: "E"}
    res = m1 | d
    assert str(res) == "{1:A,2:B,3:C,4:D,5:E}"
    assert isinstance(res, TreeMap)


def test_or_list():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    l = [[4, "D"], [5, "E"]]  # noqa: E741
    res = m1 | l
    assert str(res) == "{1:A,2:B,3:C,4:D,5:E}"
    assert isinstance(res, TreeMap)


def test_or_items():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    d = {4: "D", 5: "E"}
    res = m1 | d.items()
    assert str(res) == "{1:A,2:B,3:C,4:D,5:E}"
    assert isinstance(res, TreeMap)


def test_or_not_implemented():
    m = TreeMap({1: "A", 2: "B", 3: "C"})
    with pytest.raises(TypeError) as ex:
        m | 25
    msg = str(ex)
    assert "unsupported operand type" in msg
    assert "TreeMap" in msg
    assert "int" in msg


def test_ror_dict():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    d = {4: "D", 5: "E"}
    res = d | m1
    assert str(res) == "{1:A,2:B,3:C,4:D,5:E}"
    assert isinstance(res, TreeMap)


def test_ror_list():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    l = [[4, "D"], [5, "E"]]  # noqa: E741
    res = l | m1
    assert str(res) == "{1:A,2:B,3:C,4:D,5:E}"
    assert isinstance(res, TreeMap)


def test_ror_items():
    # This form is not very usable in practice, because it produces a set of tuples
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    d = {4: "D", 5: "E"}
    res = d.items() | m1
    assert isinstance(res, set)


def test_ror_not_implemented():
    m = TreeMap({1: "A", 2: "B", 3: "C"})
    with pytest.raises(TypeError) as ex:
        25 | m
    msg = str(ex)
    assert "unsupported operand type" in msg
    assert "TreeMap" in msg
    assert "int" in msg


def test_ior_maps():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    m2 = TreeMap({4: "D", 5: "E"})
    m1 |= m2
    assert str(m1) == "{1:A,2:B,3:C,4:D,5:E}"


def test_ior_dict():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    d = {4: "D", 5: "E"}
    m1 |= d
    assert str(m1) == "{1:A,2:B,3:C,4:D,5:E}"


def test_ior_list():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    l = [[4, "D"], [5, "E"]]  # noqa: E741
    m1 |= l
    assert str(m1) == "{1:A,2:B,3:C,4:D,5:E}"


def test_ior_items():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    d = {4: "D", 5: "E"}
    m1 |= d.items()
    assert str(m1) == "{1:A,2:B,3:C,4:D,5:E}"


def test_ior_not_implemented():
    m = TreeMap({1: "A", 2: "B", 3: "C"})
    with pytest.raises(TypeError) as ex:
        m |= 25
    msg = str(ex)
    assert "unsupported operand type" in msg
    assert "TreeMap" in msg
    assert "int" in msg


def test_copy():
    m1 = TreeMap({1: "A", 2: "B", 3: "C"})
    m2 = copy.copy(m1)
    m2[4] = "D"
    assert str(m1) == "{1:A,2:B,3:C}"
    assert str(m2) == "{1:A,2:B,3:C,4:D}"
    assert m1 is not m2


def test_len():
    m = TreeMap({1: "A", 2: "B", 3: "C"})
    assert len(m) == 3


def test_len_empty():
    m = TreeMap()
    assert len(m) == 0
