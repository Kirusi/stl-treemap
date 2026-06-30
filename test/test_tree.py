import random

import pytest

from stl_treemap.iterators import ReverseIterator
from stl_treemap.policies import KeyOnlyPolicy, KeyValuePolicy, ValueOnlyPolicy
from stl_treemap.tree import Tree
from stl_treemap.tree_node import Head, NodeColors, TreeNode


class NodeHelper(TreeNode):
    def __init__(self, node_id: str) -> None:
        super().__init__()
        self.id = node_id


def create_node(node_id: str) -> NodeHelper:
    return NodeHelper(node_id)


def set_pointers(node, p, l, r, c=None):  # noqa: E741
    node.parent = p
    node.left = l
    node.right = r
    if c is not None:
        node.color = c


def _node_id(n):
    return n.id if hasattr(n, "id") else "head"


def validate_pointers(node, p, l, r, k=None, c=None):  # noqa: E741
    assert node.parent is p, (
        f"Node '{_node_id(node)}': wrong parent. Expected '{_node_id(p) if p else None}',"
        " got '{_node_id(node.parent) if node.parent else None}'"
    )
    assert node.left is l, (
        f"Node '{_node_id(node)}': wrong left. Expected '{_node_id(l) if l else None}',"
        " got '{_node_id(node.left) if node.left else None}'"
    )
    assert node.right is r, (
        f"Node '{_node_id(node)}': wrong right. Expected '{_node_id(r) if r else None}',"
        " got '{_node_id(node.right) if node.right else None}'"
    )
    if k is not None:
        assert node.key == k, f"Node '{_node_id(node)}': wrong key. Expected '{k}', got '{node.key}'"
    if c is not None:
        assert node.color == c, f"Node '{_node_id(node)}': wrong color. Expected '{c}', got '{node.color}'"


def validate_head(head: Head, root, leftmost, rightmost, size: int):
    assert head.root is root, "head: wrong root"
    assert head.leftmost is leftmost, "head: wrong leftmost"
    assert head.rightmost is rightmost, "head: wrong rightmost"
    assert head.size == size, f"head: wrong size. Expected {size}, got {head.size}"


def add_nodes(t: Tree, *keys) -> list:
    nodes = []
    for k in keys:
        n = NodeHelper(str(k))
        n.key = k
        t.insert_node(n)
        nodes.append(n)
    return nodes


def build_tree(*keys):
    t = Tree()
    nodes = add_nodes(t, *keys)
    return [t, *nodes]


class TestCompare:
    def test_numbers(self):
        assert Tree.default_compare(5, 6) == -1
        assert Tree.default_compare(-2, -2) == 0
        assert Tree.default_compare(6, -5) == 1

    def test_strings(self):
        assert Tree.default_compare("A", "a") == -1
        assert Tree.default_compare("abc", "abc") == 0
        assert Tree.default_compare("Abcd", "Abc") == 1


class TestTree:
    def test_constructor(self):
        t = Tree()
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_size(self):
        t = Tree()
        t.head.size = 5
        assert t.size() == 5

    def test_replace_node_root(self):
        p = NodeHelper("1")
        n = NodeHelper("2")
        t = Tree()
        t.head.root = p
        t.head.leftmost = p
        t.head.rightmost = p
        t.head.size = 1
        t.replace_node(p, n)
        validate_head(t.head, n, p, p, 1)
        validate_pointers(p, None, None, None)
        validate_pointers(n, None, None, None)

    def test_replace_node_left_child(self):
        p, l, r, n = create_node("p"), create_node("l"), create_node("r"), create_node("n")  # noqa: E741
        set_pointers(p, None, l, r)
        set_pointers(l, p, None, None)
        set_pointers(r, p, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = l
        t.head.rightmost = r
        t.head.size = 3
        t.replace_node(l, n)
        validate_head(t.head, p, l, r, 3)
        validate_pointers(p, None, n, r)
        validate_pointers(l, p, None, None)
        validate_pointers(r, p, None, None)
        validate_pointers(n, p, None, None)

    def test_replace_node_right_child(self):
        p, l, r, n = create_node("p"), create_node("l"), create_node("r"), create_node("n")  # noqa: E741
        set_pointers(p, None, l, r)
        set_pointers(l, p, None, None)
        set_pointers(r, p, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = l
        t.head.rightmost = r
        t.head.size = 3
        t.replace_node(r, n)
        validate_head(t.head, p, l, r, 3)
        validate_pointers(p, None, l, n)
        validate_pointers(l, p, None, None)
        validate_pointers(r, p, None, None)
        validate_pointers(n, p, None, None)

    def test_replace_node_itself(self):
        p, l, r = create_node("p"), create_node("l"), create_node("r")  # noqa: E741
        set_pointers(p, None, l, r)
        set_pointers(l, p, None, None)
        set_pointers(r, p, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = l
        t.head.rightmost = r
        t.head.size = 3
        t.replace_node(r, r)
        validate_head(t.head, p, l, r, 3)
        validate_pointers(p, None, l, r)
        validate_pointers(l, p, None, None)
        validate_pointers(r, p, None, None)

    def test_replace_node_none(self):
        p, l, r = create_node("p"), create_node("l"), create_node("r")  # noqa: E741
        set_pointers(p, None, l, r)
        set_pointers(l, p, None, None)
        set_pointers(r, p, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = l
        t.head.rightmost = r
        t.head.size = 3
        t.replace_node(r, None)
        validate_head(t.head, p, l, r, 3)
        validate_pointers(p, None, l, None)
        validate_pointers(l, p, None, None)
        validate_pointers(r, p, None, None)

    def test_rotate_left_all_nodes(self):
        p, n, X, Y, a, b, c = (create_node(x) for x in ["p", "n", "X", "Y", "a", "b", "c"])
        set_pointers(p, None, Y, n)
        set_pointers(n, p, None, None)
        set_pointers(X, Y, b, c)
        set_pointers(Y, p, a, X)
        set_pointers(a, Y, None, None)
        set_pointers(b, X, None, None)
        set_pointers(c, X, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = a
        t.head.rightmost = n
        t.head.size = 7
        t.rotate_left(Y)
        validate_head(t.head, p, a, n, 7)
        validate_pointers(p, None, X, n)
        validate_pointers(n, p, None, None)
        validate_pointers(X, p, Y, c)
        validate_pointers(Y, X, a, b)
        validate_pointers(a, Y, None, None)
        validate_pointers(b, Y, None, None)
        validate_pointers(c, X, None, None)

    def test_rotate_left_all_nodes_2(self):
        p, n, X, Y, a, b, c = (create_node(x) for x in ["p", "n", "X", "Y", "a", "b", "c"])
        set_pointers(p, None, n, Y)
        set_pointers(n, p, None, None)
        set_pointers(X, Y, b, c)
        set_pointers(Y, p, a, X)
        set_pointers(a, Y, None, None)
        set_pointers(b, X, None, None)
        set_pointers(c, X, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = n
        t.head.rightmost = c
        t.head.size = 7
        t.rotate_left(Y)
        validate_head(t.head, p, n, c, 7)
        validate_pointers(p, None, n, X)
        validate_pointers(n, p, None, None)
        validate_pointers(X, p, Y, c)
        validate_pointers(Y, X, a, b)
        validate_pointers(a, Y, None, None)
        validate_pointers(b, Y, None, None)
        validate_pointers(c, X, None, None)

    def test_rotate_left_two_nodes(self):
        X, Y = create_node("X"), create_node("Y")
        set_pointers(X, Y, None, None)
        set_pointers(Y, None, None, X)
        t = Tree()
        t.head.root = Y
        t.head.leftmost = Y
        t.head.rightmost = X
        t.head.size = 2
        t.rotate_left(Y)
        validate_head(t.head, X, Y, X, 2)
        validate_pointers(X, None, Y, None)
        validate_pointers(Y, X, None, None)

    def test_rotate_left_single_node(self):
        X = create_node("X")
        set_pointers(X, None, None, None)
        t = Tree()
        t.head.root = X
        t.head.leftmost = X
        t.head.rightmost = X
        t.head.size = 1
        with pytest.raises(ValueError) as exc_info:
            t.rotate_left(X)
        msg = str(exc_info.value)
        assert "rotateLeft" in msg
        assert "corrupted" in msg

    def test_rotate_right_all_nodes(self):
        p, n, X, Y, a, b, c = (create_node(x) for x in ["p", "n", "X", "Y", "a", "b", "c"])
        set_pointers(p, None, X, n)
        set_pointers(n, p, None, None)
        set_pointers(X, p, Y, c)
        set_pointers(Y, X, a, b)
        set_pointers(a, Y, None, None)
        set_pointers(b, Y, None, None)
        set_pointers(c, X, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = a
        t.head.rightmost = n
        t.head.size = 7
        t.rotate_right(X)
        validate_head(t.head, p, a, n, 7)
        validate_pointers(p, None, Y, n)
        validate_pointers(n, p, None, None)
        validate_pointers(X, Y, b, c)
        validate_pointers(Y, p, a, X)
        validate_pointers(a, Y, None, None)
        validate_pointers(b, X, None, None)
        validate_pointers(c, X, None, None)

    def test_rotate_right_all_nodes_2(self):
        p, n, X, Y, a, b, c = (create_node(x) for x in ["p", "n", "X", "Y", "a", "b", "c"])
        set_pointers(p, None, n, X)
        set_pointers(n, p, None, None)
        set_pointers(X, p, Y, c)
        set_pointers(Y, X, a, b)
        set_pointers(a, Y, None, None)
        set_pointers(b, Y, None, None)
        set_pointers(c, X, None, None)
        t = Tree()
        t.head.root = p
        t.head.leftmost = n
        t.head.rightmost = c
        t.head.size = 7
        t.rotate_right(X)
        validate_head(t.head, p, n, c, 7)
        validate_pointers(p, None, n, Y)
        validate_pointers(n, p, None, None)
        validate_pointers(X, Y, b, c)
        validate_pointers(Y, p, a, X)
        validate_pointers(a, Y, None, None)
        validate_pointers(b, X, None, None)
        validate_pointers(c, X, None, None)

    def test_rotate_right_two_nodes(self):
        X, Y = create_node("X"), create_node("Y")
        set_pointers(X, None, Y, None)
        set_pointers(Y, X, None, None)
        t = Tree()
        t.head.root = X
        t.head.leftmost = Y
        t.head.rightmost = X
        t.head.size = 2
        t.rotate_right(X)
        validate_head(t.head, Y, Y, X, 2)
        validate_pointers(X, Y, None, None)
        validate_pointers(Y, None, None, X)

    def test_rotate_right_single_node(self):
        X = create_node("X")
        set_pointers(X, None, None, None)
        t = Tree()
        t.head.root = X
        t.head.leftmost = X
        t.head.rightmost = X
        t.head.size = 1
        with pytest.raises(ValueError) as exc_info:
            t.rotate_right(X)
        msg = str(exc_info.value)
        assert "rotateRight" in msg
        assert "corrupted" in msg

    def test_is_leaf(self):
        X = create_node("X")
        set_pointers(X, None, None, None, NodeColors.BLACK)
        t = Tree()
        t.head.root = X
        t.head.leftmost = X
        t.head.rightmost = X
        t.head.size = 1
        assert not t.is_leaf(X)
        assert t.is_leaf(t.head)
        assert t.is_leaf(None)

    def test_fetch_color(self):
        X, Y = create_node("X"), create_node("Y")
        set_pointers(X, None, Y, None, NodeColors.BLACK)
        set_pointers(Y, X, None, None, NodeColors.RED)
        t = Tree()
        t.head.root = X
        t.head.leftmost = Y
        t.head.rightmost = X
        t.head.size = 2
        assert t.fetch_color(X) == NodeColors.BLACK
        assert t.fetch_color(t.head) == NodeColors.BLACK
        assert t.fetch_color(None) == NodeColors.BLACK
        assert t.fetch_color(Y) == NodeColors.RED
        assert t.is_black(X)
        assert t.is_red(Y)

    def test_insert_node_root_case1(self):
        t, n = build_tree(2)
        validate_head(t.head, n, n, n, 1)
        validate_pointers(n, None, t.head, t.head, 2, NodeColors.BLACK)

    def test_insert_node_root_left_child_case2(self):
        t, n2, n1 = build_tree(2, 1)
        validate_head(t.head, n2, n1, n2, 2)
        validate_pointers(n2, None, n1, t.head, 2, NodeColors.BLACK)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.RED)

    def test_insert_node_root_right_child_case2(self):
        t, n2, n3 = build_tree(2, 3)
        validate_head(t.head, n2, n2, n3, 2)
        validate_pointers(n2, None, t.head, n3, 2, NodeColors.BLACK)
        validate_pointers(n3, n2, None, t.head, 3, NodeColors.RED)

    def test_insert_node_2_3_1_4_case3(self):
        t, n2, n3, n1, n4 = build_tree(2, 3, 1, 4)
        validate_head(t.head, n2, n1, n4, 4)
        validate_pointers(n2, None, n1, n3, 2, NodeColors.BLACK)
        validate_pointers(n3, n2, None, n4, 3, NodeColors.BLACK)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.BLACK)
        validate_pointers(n4, n3, None, t.head, 4, NodeColors.RED)

    def test_insert_node_1_2_3_case4(self):
        t, n1, n2, n3 = build_tree(1, 2, 3)
        validate_head(t.head, n2, n1, n3, 3)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.RED)
        validate_pointers(n2, None, n1, n3, 2, NodeColors.BLACK)
        validate_pointers(n3, n2, None, t.head, 3, NodeColors.RED)

    def test_insert_node_1_3_2_case4(self):
        t, n1, n3, n2 = build_tree(1, 3, 2)
        validate_head(t.head, n2, n1, n3, 3)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.RED)
        validate_pointers(n2, None, n1, n3, 2, NodeColors.BLACK)
        validate_pointers(n3, n2, None, t.head, 3, NodeColors.RED)

    def test_insert_node_6_4_5_case4(self):
        t, n6, n4, n5 = build_tree(6, 4, 5)
        validate_head(t.head, n5, n4, n6, 3)
        validate_pointers(n4, n5, t.head, None, 4, NodeColors.RED)
        validate_pointers(n5, None, n4, n6, 5, NodeColors.BLACK)
        validate_pointers(n6, n5, None, t.head, 6, NodeColors.RED)

    def test_insert_node_1_2_3_4_case4(self):
        t, n1, n2, n3, n4 = build_tree(1, 2, 3, 4)
        validate_head(t.head, n2, n1, n4, 4)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.BLACK)
        validate_pointers(n2, None, n1, n3, 2, NodeColors.BLACK)
        validate_pointers(n3, n2, None, n4, 3, NodeColors.BLACK)
        validate_pointers(n4, n3, None, t.head, 4, NodeColors.RED)

    def test_insert_node_1_2_3_4_5_case4(self):
        t, n1, n2, n3, n4, n5 = build_tree(1, 2, 3, 4, 5)
        validate_head(t.head, n2, n1, n5, 5)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.BLACK)
        validate_pointers(n2, None, n1, n4, 2, NodeColors.BLACK)
        validate_pointers(n3, n4, None, None, 3, NodeColors.RED)
        validate_pointers(n4, n2, n3, n5, 4, NodeColors.BLACK)
        validate_pointers(n5, n4, None, t.head, 5, NodeColors.RED)

    def test_insert_node_1_2_3_4_5_6_case4(self):
        t, n1, n2, n3, n4, n5, n6 = build_tree(1, 2, 3, 4, 5, 6)
        validate_head(t.head, n2, n1, n6, 6)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.BLACK)
        validate_pointers(n2, None, n1, n4, 2, NodeColors.BLACK)
        validate_pointers(n3, n4, None, None, 3, NodeColors.BLACK)
        validate_pointers(n4, n2, n3, n5, 4, NodeColors.RED)
        validate_pointers(n5, n4, None, n6, 5, NodeColors.BLACK)
        validate_pointers(n6, n5, None, t.head, 6, NodeColors.RED)

    def test_insert_node_6_5_4_3_2_1_case4(self):
        t, n6, n5, n4, n3, n2, n1 = build_tree(6, 5, 4, 3, 2, 1)
        validate_head(t.head, n5, n1, n6, 6)
        validate_pointers(n6, n5, None, t.head, 6, NodeColors.BLACK)
        validate_pointers(n5, None, n3, n6, 5, NodeColors.BLACK)
        validate_pointers(n4, n3, None, None, 4, NodeColors.BLACK)
        validate_pointers(n3, n5, n2, n4, 3, NodeColors.RED)
        validate_pointers(n2, n3, n1, None, 2, NodeColors.BLACK)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.RED)

    def test_fetch_maximum(self):
        t, n20, _n10, _n30, n15, n40, n17 = build_tree(20, 10, 30, 15, 40, 17)
        assert t.fetch_maximum(n20) is n40
        assert t.fetch_maximum(n15) is n17

    def test_fetch_minimum(self):
        t, n20, _n10, n30, n5, _n15, n25, _n35, _n27 = build_tree(20, 10, 30, 5, 15, 25, 35, 27)
        assert t.fetch_minimum(n20) is n5
        assert t.fetch_minimum(n30) is n25

    def test_clear(self):
        t, *_ = build_tree(1, 2, 3)
        t.clear()
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_none(self):
        t = Tree()
        t.erase(None)
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_head(self):
        t = Tree()
        t.erase(t.head)
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_case1(self):
        t, n2 = build_tree(2)
        t.erase(n2)
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_replaced_by_leftmost_child(self):
        t, n2, _n1, n3 = build_tree(2, 1, 3)
        t.erase(n2)
        validate_head(t.head, n2, n2, n3, 2)
        validate_pointers(n2, None, t.head, n3, 1, NodeColors.BLACK)
        validate_pointers(n3, n2, None, t.head, 3, NodeColors.RED)

    def test_erase_delete_leftmost_child(self):
        t, n2, n1, n3 = build_tree(2, 1, 3)
        t.erase(n1)
        validate_head(t.head, n2, n2, n3, 2)
        validate_pointers(n2, None, t.head, n3, 2, NodeColors.BLACK)
        validate_pointers(n3, n2, None, t.head, 3, NodeColors.RED)

    def test_erase_delete_leftmost_child_2(self):
        t, n10, n8, n12, n6, n14 = build_tree(10, 8, 12, 6, 14)
        t.erase(n6)
        validate_head(t.head, n10, n8, n14, 4)
        validate_pointers(n8, n10, t.head, None, 8, NodeColors.BLACK)
        validate_pointers(n10, None, n8, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, n14, 12, NodeColors.BLACK)
        validate_pointers(n14, n12, None, t.head, 14, NodeColors.RED)

    def test_erase_delete_leftmost_and_root_then_root_again(self):
        t, n2, n1, n3 = build_tree(2, 1, 3)
        t.erase(n1)
        t.erase(n2)
        validate_head(t.head, n3, n3, n3, 1)
        validate_pointers(n3, None, t.head, t.head, 3, NodeColors.BLACK)
        t.erase(n3)
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_delete_2_nodes_order1(self):
        t, n1, n3 = build_tree(1, 3)
        t.erase(n1)
        t.erase(n3)
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_delete_2_nodes_order2(self):
        t, n1, n3 = build_tree(1, 3)
        t.erase(n3)
        t.erase(n1)
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_delete_rightmost_child(self):
        t, n2, n1, n3 = build_tree(2, 1, 3)
        t.erase(n3)
        validate_head(t.head, n2, n1, n2, 2)
        validate_pointers(n1, n2, t.head, None, 1, NodeColors.RED)
        validate_pointers(n2, None, n1, t.head, 2, NodeColors.BLACK)

    def test_erase_delete_rightmost_child_2(self):
        t, n10, n8, n12, n6, n14 = build_tree(10, 8, 12, 6, 14)
        t.erase(n14)
        validate_head(t.head, n10, n6, n12, 4)
        validate_pointers(n6, n8, t.head, None, 6, NodeColors.RED)
        validate_pointers(n8, n10, n6, None, 8, NodeColors.BLACK)
        validate_pointers(n10, None, n8, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, t.head, 12, NodeColors.BLACK)

    def test_erase_delete_rightmost_and_root(self):
        t, n2, n1, n3 = build_tree(2, 1, 3)
        t.erase(n3)
        t.erase(n2)
        validate_head(t.head, n1, n1, n1, 1)
        validate_pointers(n1, None, t.head, t.head, 1, NodeColors.BLACK)
        t.erase(n1)
        validate_head(t.head, t.head, t.head, t.head, 0)

    def test_erase_delete_node_with_single_left_child(self):
        t, n20, n10, n30, n25, n35, n22 = build_tree(20, 10, 30, 25, 35, 22)
        t.erase(n25)
        validate_head(t.head, n20, n10, n35, 5)
        validate_pointers(n10, n20, t.head, None, 10, NodeColors.BLACK)
        validate_pointers(n20, None, n10, n30, 20, NodeColors.BLACK)
        validate_pointers(n22, n30, None, None, 22, NodeColors.RED)
        validate_pointers(n30, n20, n22, n35, 30, NodeColors.BLACK)
        validate_pointers(n35, n30, None, t.head, 35, NodeColors.RED)

    def test_erase_delete_node_with_single_right_child(self):
        t, n20, n10, n30, n25, n35, n27 = build_tree(20, 10, 30, 25, 35, 27)
        t.erase(n25)
        validate_head(t.head, n20, n10, n35, 5)
        validate_pointers(n10, n20, t.head, None, 10, NodeColors.BLACK)
        validate_pointers(n20, None, n10, n30, 20, NodeColors.BLACK)
        validate_pointers(n27, n30, None, None, 27, NodeColors.RED)
        validate_pointers(n30, n20, n27, n35, 30, NodeColors.BLACK)
        validate_pointers(n35, n30, None, t.head, 35, NodeColors.RED)

    def test_erase_cases_2_4_left_child(self):
        t, n20, n10, n30, n5, n25, n35, n40 = build_tree(20, 10, 30, 5, 25, 35, 40)
        t.erase(n5)
        t.erase(n40)
        validate_head(t.head, n20, n10, n35, 5)
        validate_pointers(n10, n20, t.head, None, 10, NodeColors.BLACK)
        validate_pointers(n20, None, n10, n30, 20, NodeColors.BLACK)
        validate_pointers(n25, n30, None, None, 25, NodeColors.BLACK)
        validate_pointers(n30, n20, n25, n35, 30, NodeColors.RED)
        validate_pointers(n35, n30, None, t.head, 35, NodeColors.BLACK)
        t.erase(n10)
        validate_head(t.head, n30, n20, n35, 4)
        validate_pointers(n20, n30, t.head, n25, 20, NodeColors.BLACK)
        validate_pointers(n25, n20, None, None, 25, NodeColors.RED)
        validate_pointers(n30, None, n20, n35, 30, NodeColors.BLACK)
        validate_pointers(n35, n30, None, t.head, 35, NodeColors.BLACK)

    def test_erase_cases_2_4_right_child(self):
        t, n20, n10, n30, n5, n15, n18 = build_tree(20, 10, 30, 5, 15, 18)
        t.erase(n18)
        validate_head(t.head, n20, n5, n30, 5)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n20, n5, n15, 10, NodeColors.RED)
        validate_pointers(n15, n10, None, None, 15, NodeColors.BLACK)
        validate_pointers(n20, None, n10, n30, 20, NodeColors.BLACK)
        validate_pointers(n30, n20, None, t.head, 30, NodeColors.BLACK)
        t.erase(n30)
        validate_head(t.head, n10, n5, n20, 4)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, None, n5, n20, 10, NodeColors.BLACK)
        validate_pointers(n15, n20, None, None, 15, NodeColors.RED)
        validate_pointers(n20, n10, n15, t.head, 20, NodeColors.BLACK)

    def test_erase_cases_3_5_6_left_child(self):
        t, n20, n10, n30, n5, n15, n25, n35, n40 = build_tree(20, 10, 30, 5, 15, 25, 35, 40)
        t.erase(n40)
        n12, n17, n16 = add_nodes(t, 12, 17, 16)
        validate_head(t.head, n20, n5, n35, 10)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n20, n5, n15, 10, NodeColors.BLACK)
        validate_pointers(n12, n15, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, n10, n12, n17, 15, NodeColors.RED)
        validate_pointers(n16, n17, None, None, 16, NodeColors.RED)
        validate_pointers(n17, n15, n16, None, 17, NodeColors.BLACK)
        validate_pointers(n20, None, n10, n30, 20, NodeColors.BLACK)
        validate_pointers(n25, n30, None, None, 25, NodeColors.BLACK)
        validate_pointers(n30, n20, n25, n35, 30, NodeColors.BLACK)
        validate_pointers(n35, n30, None, t.head, 35, NodeColors.BLACK)
        t.erase(n25)
        validate_head(t.head, n15, n5, n35, 9)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n15, n5, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, None, n10, n20, 15, NodeColors.BLACK)
        validate_pointers(n16, n17, None, None, 16, NodeColors.RED)
        validate_pointers(n17, n20, n16, None, 17, NodeColors.BLACK)
        validate_pointers(n20, n15, n17, n30, 20, NodeColors.BLACK)
        validate_pointers(n30, n20, None, n35, 30, NodeColors.BLACK)
        validate_pointers(n35, n30, None, t.head, 35, NodeColors.RED)

    def test_erase_cases_3_5_6_right_child(self):
        t, n20, n10, n30, n5, n15, n25, n35, n40 = build_tree(20, 10, 30, 5, 15, 25, 35, 40)
        t.erase(n40)
        n12, n17, n16 = add_nodes(t, 12, 17, 16)
        validate_head(t.head, n20, n5, n35, 10)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n20, n5, n15, 10, NodeColors.BLACK)
        validate_pointers(n12, n15, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, n10, n12, n17, 15, NodeColors.RED)
        validate_pointers(n16, n17, None, None, 16, NodeColors.RED)
        validate_pointers(n17, n15, n16, None, 17, NodeColors.BLACK)
        validate_pointers(n20, None, n10, n30, 20, NodeColors.BLACK)
        validate_pointers(n25, n30, None, None, 25, NodeColors.BLACK)
        validate_pointers(n30, n20, n25, n35, 30, NodeColors.BLACK)
        validate_pointers(n35, n30, None, t.head, 35, NodeColors.BLACK)
        t.erase(n35)
        validate_head(t.head, n15, n5, n30, 9)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n15, n5, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, None, n10, n20, 15, NodeColors.BLACK)
        validate_pointers(n16, n17, None, None, 16, NodeColors.RED)
        validate_pointers(n17, n20, n16, None, 17, NodeColors.BLACK)
        validate_pointers(n20, n15, n17, n30, 20, NodeColors.BLACK)
        validate_pointers(n25, n30, None, None, 25, NodeColors.RED)
        validate_pointers(n30, n20, n25, t.head, 30, NodeColors.BLACK)

    def test_erase_cases_5_6_left_child_red(self):
        t, n20, n10, n30, n5, n15, n25, n35, n40 = build_tree(20, 10, 30, 5, 15, 25, 35, 40)
        t.erase(n40)
        n12, n17, n16 = add_nodes(t, 12, 17, 16)
        t.erase(n35)
        t.erase(n16)
        validate_head(t.head, n15, n5, n30, 8)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n15, n5, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, None, n10, n20, 15, NodeColors.BLACK)
        validate_pointers(n17, n20, None, None, 17, NodeColors.BLACK)
        validate_pointers(n20, n15, n17, n30, 20, NodeColors.BLACK)
        validate_pointers(n25, n30, None, None, 25, NodeColors.RED)
        validate_pointers(n30, n20, n25, t.head, 30, NodeColors.BLACK)
        t.erase(n17)
        validate_head(t.head, n15, n5, n30, 7)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n15, n5, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, None, n10, n25, 15, NodeColors.BLACK)
        validate_pointers(n20, n25, None, None, 20, NodeColors.BLACK)
        validate_pointers(n25, n15, n20, n30, 25, NodeColors.BLACK)
        validate_pointers(n30, n25, None, t.head, 30, NodeColors.BLACK)

    def test_erase_cases_5_6_left_child_red_2(self):
        t, n20, n10, n30, n5, n15, n25, n35, n40 = build_tree(20, 10, 30, 5, 15, 25, 35, 40)
        t.erase(n40)
        n12, n17, n16 = add_nodes(t, 12, 17, 16)
        t.erase(n35)
        t.erase(n25)
        validate_head(t.head, n15, n5, n30, 8)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n15, n5, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, None, n10, n20, 15, NodeColors.BLACK)
        validate_pointers(n16, n17, None, None, 16, NodeColors.RED)
        validate_pointers(n17, n20, n16, None, 17, NodeColors.BLACK)
        validate_pointers(n20, n15, n17, n30, 20, NodeColors.BLACK)
        validate_pointers(n30, n20, None, t.head, 30, NodeColors.BLACK)
        t.erase(n30)
        validate_head(t.head, n15, n5, n20, 7)
        validate_pointers(n5, n10, t.head, None, 5, NodeColors.BLACK)
        validate_pointers(n10, n15, n5, n12, 10, NodeColors.BLACK)
        validate_pointers(n12, n10, None, None, 12, NodeColors.BLACK)
        validate_pointers(n15, None, n10, n17, 15, NodeColors.BLACK)
        validate_pointers(n16, n17, None, None, 16, NodeColors.BLACK)
        validate_pointers(n17, n15, n16, n20, 17, NodeColors.BLACK)
        validate_pointers(n20, n17, None, t.head, 20, NodeColors.BLACK)

    def test_insert_erase_random(self):
        max_key_value = 1000
        max_size = 10
        max_iterations = 10

        class ValidationResult:
            def __init__(self):
                self.is_valid = True
                self.height = 0
                self.size = 0
                self.error_message = ""

        def is_valid_subtree(t, n, res):
            if t.is_leaf(n):
                return
            if not t.is_leaf(n.left) and n.left.parent is not n:
                res.is_valid = False
                res.error_message = f"Invalid left child node {n.left.key}. It must point to parent {n.key}."
                return
            if not t.is_leaf(n.right) and n.right.parent is not n:
                res.is_valid = False
                res.error_message = f"Invalid right child node {n.right.key}. It must point to parent {n.key}."
                return
            if n.left is n.right and not t.is_leaf(n.left):
                res.is_valid = False
                res.error_message = f"Invalid node {n.key}. Both children are {n.right.key}."
                return
            if t.is_red(n):
                if not t.is_black(n.left):
                    res.is_valid = False
                    res.error_message = f"Node {n.left.key} must be BLACK because parent {n.key} is RED."
                    return
                if not t.is_black(n.right):
                    res.is_valid = False
                    res.error_message = f"Node {n.right.key} must be BLACK because parent {n.key} is RED."
                    return
            res_left = ValidationResult()
            is_valid_subtree(t, n.left, res_left)
            if not res_left.is_valid:
                res.is_valid = False
                res.error_message = res_left.error_message
                return
            res_right = ValidationResult()
            is_valid_subtree(t, n.right, res_right)
            if not res_right.is_valid:
                res.is_valid = False
                res.error_message = res_right.error_message
                return
            if res_left.height != res_right.height:
                res.is_valid = False
                res.error_message = (
                    f"Invalid node {n.key}. BLACK height left={res_left.height} right={res_right.height}"
                )
                return
            res.is_valid = True
            res.height = res_left.height + (1 if t.is_black(n) else 0)
            res.size = res_left.size + res_right.size + 1

        def is_valid_tree(t):
            res = ValidationResult()
            h = t.head
            if h.root is h:
                res.is_valid = True
                return res
            if h.root.parent is not None:
                res.is_valid = False
                res.error_message = "Root parent must be None"
                return res
            if not t.is_black(h.root):
                res.is_valid = False
                res.error_message = "Root must be BLACK"
                return res
            if h.leftmost.left is not h:
                res.is_valid = False
                res.error_message = f"Invalid leftmost node {h.leftmost.key}. Left child must be head."
                return res
            if h.rightmost.right is not h:
                res.is_valid = False
                res.error_message = f"Invalid rightmost node {h.rightmost.key}. Right child must be head."
                return res
            is_valid_subtree(t, h.root, res)
            if res.size != h.size:
                res.is_valid = False
                res.error_message = f"Invalid size. Head size: {h.size}. Actual size: {res.size}"
            return res

        rng = random.Random(42)
        t = Tree()
        keys = []
        for _ in range(max_size):
            k = rng.randint(0, max_key_value - 1)
            keys.append(k)
            add_nodes(t, k)
            res = is_valid_tree(t)
            assert res.is_valid, res.error_message

        for _ in range(max_iterations):
            i = rng.randint(0, max_size - 1)
            k = keys[i]
            it = t.find(k)
            t.erase(it.node)
            res = is_valid_tree(t)
            assert res.is_valid, res.error_message
            k = rng.randint(0, max_key_value - 1)
            keys[i] = k
            add_nodes(t, k)
            res = is_valid_tree(t)
            assert res.is_valid, res.error_message

    def test_lower_bound(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        assert t.lower_bound(8).node.key == 8
        assert t.lower_bound(22).node.key == 22
        assert t.lower_bound(12).node.key == 12
        assert t.lower_bound(21).node.key == 22
        assert t.lower_bound(2).node.key == 2
        assert t.lower_bound(-1).node.key == 2
        assert t.lower_bound(100).node is t.head

    def test_lower_bound_empty(self):
        t = Tree()
        assert t.lower_bound(22).node is t.head

    def test_upper_bound(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        assert t.upper_bound(7).node.key == 8
        assert t.upper_bound(20).node.key == 22
        assert t.upper_bound(10).node.key == 12
        assert t.upper_bound(21).node.key == 22
        assert t.upper_bound(-1).node.key == 2
        assert t.upper_bound(32).node is t.head
        assert t.upper_bound(100).node is t.head

    def test_upper_bound_empty(self):
        t = Tree()
        assert t.upper_bound(22).node is t.head

    def test_find(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        assert t.find(8).key == 8
        assert t.find(22).key == 22
        assert t.find(12).key == 12
        assert t.find(23).node is t.head
        assert t.find(-1).node is t.head
        assert t.find(100).node is t.head

    def test_find_empty(self):
        t = Tree()
        assert t.find(22).node is t.head

    def test_next(self):
        t, *_ = build_tree(32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2)
        n = t.head.leftmost
        for i in range(1, 17):
            assert n.key == 2 * i
            n = t.next(n)
        assert n is t.head

    def test_prev(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        n = t.head.rightmost
        for i in range(16, 0, -1):
            assert n.key == 2 * i
            n = t.prev(n)
        assert n is t.head

    def test_iter(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        actual = []
        for k in t:
            actual.append(k)
        assert actual == [2, 4, 6, 8, 10]

    def test_items(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        actual = []
        for k, v in t.items():
            actual.append(f"{k}|{v}")
        assert actual == ["2|N1", "4|N2", "6|N3", "8|N4", "10|N5"]

    def test_backwards(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        actual = []
        for k in t.backwards():
            actual.append(k)
        assert actual == [10, 8, 6, 4, 2]

    def test_iter_empty(self):
        t = Tree()
        assert list(t) == []

    def test_iter_as_list(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        assert list(t) == [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]

    def test_iter_backward(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        actual = []
        it = t.rbegin()
        while not it.equals(t.rend()):
            actual.append(it.node.key)
            it.next()
        assert actual == [32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]

    def test_iter_keys(self):
        t = Tree()
        t.value_policy = KeyOnlyPolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert list(t) == [2, 4, 6, 8, 10]

    def test_iter_values(self):
        t = Tree()
        t.value_policy = ValueOnlyPolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert list(t.values()) == ["N1", "N2", "N3", "N4", "N5"]

    def test_iter_items(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert list(t.items()) == [(2, "N1"), (4, "N2"), (6, "N3"), (8, "N4"), (10, "N5")]

    def test_forward_stl_iterator(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        actual = []
        it = t.begin()
        while not it.equals(t.end()):
            actual.append(it.node.key)
            it.next()
        assert actual == [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]

    def test_forward_stl_iterator_empty(self):
        t = Tree()
        actual = []
        it = t.begin()
        while not it.equals(t.end()):
            actual.append(it.node.key)
            it.next()
        assert actual == []

    def test_backward_stl_iterator(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        actual = []
        it = t.rbegin()
        while not it.equals(t.rend()):
            actual.append(it.node.key)
            it.next()
        assert actual == [32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]

    def test_backward_stl_iterator_empty(self):
        t = Tree()
        actual = []
        it = t.rbegin()
        while not it.equals(t.rend()):
            actual.append(it.node.key)
            it.next()
        assert actual == []

    def test_key_value_policy(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert list(t.items()) == [(2, "N1"), (4, "N2"), (6, "N3"), (8, "N4"), (10, "N5")]

    def test_insert_unique(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 4):
            n = TreeNode()
            n.key = 1
            n.value = f"N{i}"
            res = t.insert_unique(n)
            if i == 1:
                assert res.was_added
                assert not res.was_replaced
                assert res.iterator.key == 1
                assert res.iterator.value == "N1"
            else:
                assert not res.was_added
                assert not res.was_replaced
        assert t.size() == 1

    def test_insert_or_replace(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 4):
            n = TreeNode()
            n.key = 1
            n.value = f"N{i}"
            res = t.insert_or_replace(n)
            if i == 1:
                assert res.was_added
                assert not res.was_replaced
                assert res.iterator.key == 1
                assert res.iterator.value == f"N{i}"
            else:
                assert not res.was_added
                assert res.was_replaced
                assert res.iterator.key == 1
                assert res.iterator.value == f"N{i}"
        assert t.size() == 1

    def test_insert_multi(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 4):
            n = TreeNode()
            n.key = 1
            n.value = f"N{i}"
            res = t.insert_multi(n)
            assert res.was_added
            assert not res.was_replaced
            assert res.iterator.key == 1
            assert res.iterator.value == f"N{i}"
        assert t.size() == 3

    def test_insert_multi_lower_upper_bound_same_values(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = 12
            n.value = f"N{i}"
            t.insert_multi(n)
        actual = []
        it = t.lower_bound(12)
        to = t.upper_bound(12)
        while not it.equals(to):
            actual.append(it.value)
            it.next()
        assert actual == ["N1", "N2", "N3", "N4", "N5"]

    def test_insert_unique_lower_upper_bound_same_values(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = 12
            n.value = f"N{i}"
            t.insert_unique(n)
        actual = []
        it = t.lower_bound(12)
        to = t.upper_bound(12)
        while not it.equals(to):
            actual.append(it.value)
            it.next()
        assert actual == ["N1"]
        assert t.size() == 1

    def test_insert_or_replace_lower_upper_bound_same_values(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = 12
            n.value = f"N{i}"
            t.insert_or_replace(n)
        actual = []
        it = t.lower_bound(12)
        to = t.upper_bound(12)
        while not it.equals(to):
            actual.append(it.value)
            it.next()
        assert actual == ["N5"]
        assert t.size() == 1

    def test_lower_upper_bound_forward_iteration(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        actual = []
        it = t.lower_bound(0)
        to = t.upper_bound(50)
        while not it.equals(to):
            actual.append(it.node.key)
            it.next()
        assert actual == [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]

    def test_lower_upper_bound_reverse_forward_iteration(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        actual = []
        it = t.lower_bound(0)
        to = t.upper_bound(50)
        while not to.equals(it):
            to.prev()
            actual.append(to.node.key)
        assert actual == [32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]

    def test_lower_upper_bound_backward_iteration(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        actual = []
        rev_from = ReverseIterator(t.upper_bound(50))
        rev_to = ReverseIterator(t.lower_bound(0))
        it = rev_from
        while not it.equals(rev_to):
            actual.append(it.node.key)
            it.next()
        assert actual == [32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2]

    def test_lower_upper_bound_reverse_backward_iteration(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        actual = []
        rev_from = ReverseIterator(t.upper_bound(50))
        rev_to = ReverseIterator(t.lower_bound(0))
        it = rev_to
        while not it.equals(rev_from):
            it.prev()
            actual.append(it.node.key)
        assert actual == [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]

    def test_first(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        assert t.first() == 2

    def test_first_empty(self):
        t = Tree()
        assert t.first() is None

    def test_last(self):
        t, *_ = build_tree(2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
        assert t.last() == 32

    def test_last_empty(self):
        t = Tree()
        assert t.last() is None

    def test_custom_compare(self):
        class Id:
            def __init__(self, alpha: str, num: int):
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

        t = Tree()
        t.compare = compare_ids
        add_nodes(t, Id("B", 8), Id("A", 340), Id("A", 12), Id("AA", 147))
        actual = [(k.alpha, k.num) for k in t]
        assert actual == [("A", 12), ("A", 340), ("AA", 147), ("B", 8)]

    def test_str_key_value(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_or_replace(n)
        assert str(t) == "{2:N1,4:N2,6:N3,8:N4,10:N5}"

    def test_str_keys_only(self):
        t, *_ = build_tree(2, 4, 6)
        assert f"{t}" == "{2,4,6}"

    def test_repr_key_value(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_or_replace(n)
        assert repr(t) == "{2:N1,4:N2,6:N3,8:N4,10:N5}"

    def test_repr_keys_only(self):
        t, *_ = build_tree(2, 4, 6)
        assert repr(t) == "{2,4,6}"

    def test_getitem(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert t[2] == "N1"
        assert t[6] == "N3"
        assert t[10] == "N5"

    def test_getitem_missing_key(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        n = TreeNode()
        n.key = 1
        n.value = "A"
        t.insert_unique(n)
        with pytest.raises(KeyError) as ex:
            _ = t[99]
        msg = f"{ex}"
        assert "KeyError(99)" in msg

    def test_setitem(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        t[1] = "one"
        t[2] = "two"
        t[3] = "three"
        assert t.size() == 3
        assert t[1] == "one"
        assert t[2] == "two"
        assert t[3] == "three"

    def test_setitem_replace(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        t[1] = "one"
        assert t[1] == "one"
        t[1] = "ONE"
        assert t[1] == "ONE"
        assert t.size() == 1

    def test_keys(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        res = []
        for n in t.keys():  # noqa: SIM118
            res.append(n)
        assert res == [2, 4, 6, 8, 10]

    def test_keys_backwards(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        res = []
        for n in t.keys().backwards():  # noqa: SIM118
            res.append(n)
        assert res == [10, 8, 6, 4, 2]

    def test_values(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        res = []
        for n in t.values():
            res.append(n)
        assert res == ["N1", "N2", "N3", "N4", "N5"]

    def test_values_backwards(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        res = []
        for n in t.values().backwards():
            res.append(n)
        assert res == ["N5", "N4", "N3", "N2", "N1"]

    def test_contains(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert (2 in t) is True
        assert (12 in t) is False

    def test_len(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert len(t) == 5

    def test_delitem(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        assert len(t) == 5
        assert 4 in t
        del t[4]
        assert len(t) == 4
        assert 4 not in t

    def test_delitem_nonexisting(self):
        t = Tree()
        t.value_policy = KeyValuePolicy()
        for i in range(1, 6):
            n = TreeNode()
            n.key = i * 2
            n.value = f"N{i}"
            t.insert_unique(n)
        with pytest.raises(KeyError) as ex:
            del t[12]
        msg = str(ex.value)
        assert "Key 12 not found" in msg
