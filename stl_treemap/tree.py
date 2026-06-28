"""Red-black tree implementation."""

from __future__ import annotations

from collections.abc import Callable, Collection
from typing import Any

from stl_treemap.insertion_result import InsertionResult
from stl_treemap.iterators import ReverseIterator, TreeIterator
from stl_treemap.policies import KeyOnlyPolicy, PolicyInterface, ValueOnlyPolicy
from stl_treemap.py_iterators import PyIterator, PyReverseIterator
from stl_treemap.tree_node import Head, NodeColors, TreeNode

_INSERT_MULTI = 1
_INSERT_UNIQUE = 2
_INSERT_REPLACE = 3


class Tree[K, V](Collection[K]):
    """@private Red-black tree."""

    def __init__(self) -> None:
        """Construct an empty tree."""
        self.head: Head[K, V] = Head()
        self.compare: Callable[[Any, Any], int] = Tree.compare
        self.value_policy: PolicyInterface[K, V] = KeyOnlyPolicy()

    @staticmethod
    def compare(lhs: Any, rhs: Any) -> int:
        """
        3-way comparison, similar to strcmp in C.

        Args:
            lhs: Left-hand side value.
            rhs: Right-hand side value.

        Returns:
            -1 if lhs < rhs, 0 if equal, 1 if lhs > rhs.

        """
        if lhs < rhs:
            return -1
        if lhs == rhs:
            return 0
        return 1

    def clear(self) -> None:
        """Delete all nodes in the tree."""
        self.head = Head()

    def size(self) -> int:
        """@private Return the number of nodes in the tree."""
        return self.head.size

    def compare_nodes(self, lhs: TreeNode[K, V], rhs: TreeNode[K, V]) -> int:
        """@private Call 3-way comparison on node keys."""
        return self.compare(lhs.key, rhs.key)

    def replace_node(self, old_node: TreeNode[K, V], new_node: TreeNode[K, V] | None) -> None:
        """@private Update parent and child pointers when swapping nodes during rotations."""
        if old_node is new_node:
            return
        if old_node.parent is None:
            self.head.root = new_node
        elif old_node is old_node.parent.left:
            old_node.parent.left = new_node
        else:
            old_node.parent.right = new_node
        if not self.is_leaf(new_node):
            new_node.parent = old_node.parent

    def rotate_left(self, node: TreeNode[K, V]) -> None:
        r"""
        Rebalance the tree with a left rotation.

        ::

            X                 Y
           / \    rotate     / \
          Y   c  ------->  a   X
         / \                  / \
        a   b                b   c

        Args:
            node: Root of the sub-tree to rotate.

        Raises:
            ValueError: When the node has no right child (tree is corrupted).

        """
        right = node.right
        if self.is_leaf(right):
            raise ValueError("rotateLeft can't be performed. The tree is corrupted")
        self.replace_node(node, right)
        node.right = right.left
        if right.left is not None:
            right.left.parent = node
        right.left = node
        node.parent = right

    def rotate_right(self, node: TreeNode[K, V]) -> None:
        """
        Rebalance the tree with a right rotation (mirror of rotate_left).

        Args:
            node: Root of the sub-tree to rotate.

        Raises:
            ValueError: When the node has no left child (tree is corrupted).

        """
        left = node.left
        if self.is_leaf(left):
            raise ValueError("rotateRight can't be performed. The tree is corrupted")
        self.replace_node(node, left)
        node.left = left.right
        if left.right is not None:
            left.right.parent = node
        left.right = node
        node.parent = left

    def is_leaf(self, node: Any) -> bool:
        """
        Return True for nodes that should not be traversed.

        Args:
            node: Node to inspect.

        Returns:
            True for None and the head sentinel; False for all real nodes.

        """
        return node is None or node is self.head

    def fetch_color(self, node: Any) -> int:
        """
        Return the color of a node, treating leaves as BLACK.

        Args:
            node: Node to inspect.

        Returns:
            NodeColors.BLACK for leaf nodes; the node's stored color otherwise.

        """
        if self.is_leaf(node):
            return NodeColors.BLACK
        return node.color

    def is_black(self, node: Any) -> bool:
        """Return True when the node color is BLACK."""
        return self.fetch_color(node) == NodeColors.BLACK

    def is_red(self, node: Any) -> bool:
        """Return True when the node color is RED."""
        return self.fetch_color(node) == NodeColors.RED

    # === INSERT ===

    def insert_multi(self, node: TreeNode[K, V]) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert a node, allowing duplicate keys.

        Args:
            node: Node to insert.

        Returns:
            InsertionResult indicating whether the node was added and an iterator to it.

        """
        return self.insert_node(node, _INSERT_MULTI)

    def insert_unique(self, node: TreeNode[K, V]) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert a node only if no node with the same key exists.

        Args:
            node: Node to insert.

        Returns:
            InsertionResult indicating whether the node was added and an iterator to it.

        """
        return self.insert_node(node, _INSERT_UNIQUE)

    def insert_or_replace(self, node: TreeNode[K, V]) -> InsertionResult[TreeIterator[K, V]]:
        """
        Insert a node, replacing the value of any existing node with the same key.

        Args:
            node: Node to insert.

        Returns:
            InsertionResult indicating whether the node was added or replaced and an iterator to it.

        """
        return self.insert_node(node, _INSERT_REPLACE)

    def insert_node(self, n: TreeNode[K, V], mode: int = _INSERT_MULTI) -> InsertionResult[TreeIterator[K, V]]:
        """
        @private Insert a node, update the head sentinel, and rebalance the tree.

        Args:
            n: Node to insert.
            mode: One of _INSERT_MULTI, _INSERT_UNIQUE, or _INSERT_REPLACE.

        Returns:
            InsertionResult indicating outcome and providing an iterator to the node.

        """
        res = self.insert_node_internal(self.head.root, n, mode)
        if res.was_added:
            if self.head.size == 0:
                self.head.root = n
                self.head.leftmost = n
                self.head.rightmost = n
                n.left = self.head
                n.right = self.head
            elif self.head.leftmost.left is n:
                self.head.leftmost = n
                n.left = self.head
            elif self.head.rightmost.right is n:
                self.head.rightmost = n
                n.right = self.head
            self.insert_repair_tree(n)
            self.head.size += 1
        return res

    def insert_node_internal(self, root: Any, n: TreeNode[K, V], mode: int) -> InsertionResult[TreeIterator[K, V]]:
        """
        @private Descend the tree and place the node according to mode.

        Args:
            root: Root node of the tree.
            n: Node to insert.
            mode: One of _INSERT_MULTI, _INSERT_UNIQUE, or _INSERT_REPLACE.

        Returns:
            InsertionResult indicating outcome and providing an iterator to the node.

        """
        x = root
        y = None
        rc = -1
        while not self.is_leaf(x):
            y = x
            rc = self.compare_nodes(n, y)
            if rc < 0:
                x = y.left
            elif rc > 0:
                x = y.right
            else:
                if mode == _INSERT_UNIQUE:
                    return InsertionResult(False, False, None)
                if mode == _INSERT_REPLACE:
                    self.value_policy.copy(y, n)
                    return InsertionResult(False, True, TreeIterator(y, self))
                x = y.right  # _INSERT_MULTI: continue right to allow duplicates
        if self.is_leaf(y):
            n.parent = None
            n.left = self.head
            n.right = self.head
        else:
            n.parent = y
            if rc < 0:
                y.left = n
            else:
                y.right = n
        return InsertionResult(True, False, TreeIterator(n, self))

    def insert_repair_tree(self, n: TreeNode[K, V]) -> None:
        """
        @private Restore red-black invariants after insertion.

        See https://en.wikipedia.org/wiki/Red-black_tree#Insertion

        Args:
            n: Newly inserted node.

        """
        if n.parent is None:
            self.repair_case1(n)
        elif self.is_black(n.parent):
            pass  # case 2: parent is black — no fix needed
        elif self.is_red(n.uncle()):
            self.repair_case3(n)
        else:
            self.repair_case4(n)

    def repair_case1(self, n: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Insertion."""
        n.color = NodeColors.BLACK

    def repair_case3(self, n: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Insertion."""
        n.parent.color = NodeColors.BLACK
        n.uncle().color = NodeColors.BLACK
        n.grandparent().color = NodeColors.RED
        self.insert_repair_tree(n.grandparent())

    def repair_case4(self, node: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Insertion."""
        n = node
        p = n.parent
        g = n.grandparent()
        if not self.is_leaf(g.left) and n is g.left.right:
            self.rotate_left(p)
            n = n.left
        elif not self.is_leaf(g.right) and n is g.right.left:
            self.rotate_right(p)
            n = n.right
        p = n.parent
        g = n.grandparent()
        if n is p.left:
            self.rotate_right(g)
        else:
            self.rotate_left(g)
        p.color = NodeColors.BLACK
        g.color = NodeColors.RED

    # === FETCH MAX / MIN ===

    def fetch_maximum(self, node: TreeNode[K, V]) -> TreeNode[K, V]:
        """
        Return the node with the largest key in the subtree.

        Args:
            node: Root of the subtree to search.

        Returns:
            Node with the highest key.

        """
        res = node
        while not self.is_leaf(res.right):
            res = res.right
        return res

    def fetch_minimum(self, node: TreeNode[K, V]) -> TreeNode[K, V]:
        """
        Return the node with the smallest key in the subtree.

        Args:
            node: Root of the subtree to search.

        Returns:
            Node with the lowest key.

        """
        res = node
        while not self.is_leaf(res.left):
            res = res.left
        return res

    # === ERASE ===

    def erase(self, node: TreeNode[K, V]) -> None:
        """
        Remove a node from the tree.

        Args:
            node: Node to remove; ignored if it is a leaf.

        """
        if self.is_leaf(node):
            return
        self.erase_internal(node)
        self.head.size -= 1

    def erase_internal(self, node_param: TreeNode[K, V]) -> None:
        """
        @private https://en.wikipedia.org/wiki/Red-black_tree#Removal.

        Args:
            node_param: Node to remove.

        """
        node = node_param
        if not self.is_leaf(node.left) and not self.is_leaf(node.right):
            pred = self.fetch_maximum(node.left)
            self.value_policy.copy(node, pred)
            node = pred

        child = node.left if self.is_leaf(node.right) else node.right

        if self.is_black(node):
            self.erase_case1(node)
        self.replace_node(node, child)
        if not self.is_leaf(child) and child.parent is None:
            # child becomes root
            child.color = NodeColors.BLACK

        h = self.head
        if self.is_leaf(child):
            if h.leftmost is node:
                p = node.parent
                if p is None:
                    h.leftmost = h
                else:
                    h.leftmost = p
                    p.left = h
            if h.rightmost is node:
                p = node.parent
                if p is None:
                    h.rightmost = h
                else:
                    h.rightmost = p
                    p.right = h
        else:
            if h.leftmost is node:
                h.leftmost = child
                child.left = h
            if h.rightmost is node:
                h.rightmost = child
                child.right = h

    def erase_case1(self, node: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Removal."""
        if node.parent is not None:
            self.erase_case2(node)

    def erase_case2(self, node: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Removal."""
        s = node.sibling()
        if self.is_red(s):
            node.parent.color = NodeColors.RED
            s.color = NodeColors.BLACK
            if node is node.parent.left:
                self.rotate_left(node.parent)
            else:
                self.rotate_right(node.parent)
        self.erase_case3(node)

    def erase_case3(self, node: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Removal."""
        s = node.sibling()
        p = node.parent
        if self.is_black(p) and self.is_black(s) and self.is_black(s.left) and self.is_black(s.right):
            s.color = NodeColors.RED
            self.erase_case1(p)
        else:
            self.erase_case4(node)

    def erase_case4(self, node: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Removal."""
        s = node.sibling()
        p = node.parent
        if self.is_red(p) and self.is_black(s) and self.is_black(s.left) and self.is_black(s.right):
            s.color = NodeColors.RED
            p.color = NodeColors.BLACK
        else:
            self.erase_case5(node)

    def erase_case5(self, node: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Removal."""
        s = node.sibling()
        p = node.parent
        if node is p.left and self.is_red(s.left) and self.is_black(s.right):
            s.color = NodeColors.RED
            s.left.color = NodeColors.BLACK
            self.rotate_right(s)
        elif node is p.right and self.is_black(s.left) and self.is_red(s.right):
            s.color = NodeColors.RED
            s.right.color = NodeColors.BLACK
            self.rotate_left(s)
        self.erase_case6(node)

    def erase_case6(self, node: TreeNode[K, V]) -> None:
        """@private https://en.wikipedia.org/wiki/Red-black_tree#Removal."""
        s = node.sibling()
        p = node.parent
        s.color = self.fetch_color(p)
        p.color = NodeColors.BLACK
        if node is p.left:
            s.right.color = NodeColors.BLACK
            self.rotate_left(p)
        else:
            s.left.color = NodeColors.BLACK
            self.rotate_right(p)

    # === SEARCH ===

    def find(self, k: K) -> TreeIterator[K, V]:
        """
        Return an iterator for the node with the given key.

        Args:
            k: Key to search for.

        Returns:
            Iterator pointing to the matching node, or end() if not found.

        """
        x = self.head.root
        while not self.is_leaf(x):
            rc = self.compare(x.key, k)
            if rc > 0:
                x = x.left
            elif rc < 0:
                x = x.right
            else:
                return TreeIterator(x, self)
        return TreeIterator(self.head, self)

    def lower_bound(self, k: K) -> TreeIterator[K, V]:
        """
        Return an iterator to the first node with key >= k.

        Args:
            k: Key to search for.

        Returns:
            Iterator to the first node not less than k, or end() if none exists.

        """
        y: Any = self.head
        x = y.root
        while not self.is_leaf(x):
            rc = self.compare(x.key, k)
            if rc >= 0:
                y = x
                x = x.left
            else:
                x = x.right
        return TreeIterator(y, self)

    def upper_bound(self, k: K) -> TreeIterator[K, V]:
        """
        Return an iterator to the first node with key > k.

        Args:
            k: Key to search for.

        Returns:
            Iterator to the first node greater than k, or end() if none exists.

        """
        y: Any = self.head
        x = y.root
        while not self.is_leaf(x):
            rc = self.compare(x.key, k)
            if rc > 0:
                y = x
                x = x.left
            else:
                x = x.right
        return TreeIterator(y, self)

    # === STL ITERATORS ===

    def begin(self) -> TreeIterator[K, V]:
        """Return an iterator to the node with the lowest key."""
        return TreeIterator(self.head.leftmost, self)

    def end(self) -> TreeIterator[K, V]:
        """Return an iterator to the position past the last node."""
        return TreeIterator(self.head, self)

    def rbegin(self) -> ReverseIterator[K, V]:
        """Return a reverse iterator to the node with the highest key."""
        return ReverseIterator(self.head.rightmost, self)

    def rend(self) -> ReverseIterator[K, V]:
        """Return a reverse iterator to the position before the first node."""
        return ReverseIterator(self.head, self)

    # === PYTHON ITERATORS ===

    def py_begin(self) -> TreeNode[K, V]:
        """@private Provide support for regular Python forward iteration."""
        return self.head.leftmost

    def py_end(self) -> TreeNode[K, V]:
        """@private Provide support for regular Python forward iteration."""
        return self.head

    def py_rbegin(self) -> TreeNode[K, V]:
        """@private Provide support for  Python backward iteration."""
        return self.head.rightmost

    def py_rend(self) -> TreeNode[K, V]:
        """@private Provide support for  Python backward iteration."""
        return self.head

    def next(self, node: Any) -> Any:
        """
        Return the next node in ascending key order.

        Args:
            node: Node to advance from.

        Returns:
            Successor node, or the head sentinel when past the last node.

        """
        n = node
        if n is self.head:
            return self.head.leftmost
        if n.right is self.head:
            return self.head
        if n.right is not None:
            return self.fetch_minimum(n.right)
        while n.parent.left is not n:
            n = n.parent
        return n.parent

    def prev(self, node: Any) -> Any:
        """
        Return the previous node in ascending key order.

        Args:
            node: Node to retreat from.

        Returns:
            Predecessor node, or the head sentinel when before the first node.

        """
        n = node
        if n is self.head:
            return self.head.rightmost
        if n.left is self.head:
            return self.head
        if n.left is not None:
            return self.fetch_maximum(n.left)
        while n.parent.right is not n:
            n = n.parent
        return n.parent

    def items(self) -> PyIterator[tuple[K, V]]:
        """
        Python forward iterator.

        Returns:
            Iterator for all elements in the tree in the order of keys

        """
        return PyIterator(self, self.value_policy)

    def backwards(self) -> PyReverseIterator[K]:
        """
        Python reverse iterator.

        Returns:
            Iterator for all keys in the tree in the reverse order of keys

        """
        return self.keys().backwards()

    def first(self) -> K | V | tuple[K, V] | None:
        """
        Return the first element, or None if the tree is empty.

        Returns:
            Value fetched by value_policy from the first node, or None.

        """
        if self.size() == 0:
            return None
        return self.value_policy.fetch(self.begin().node)

    def last(self) -> K | V | tuple[K, V] | None:
        """
        Return the last element, or None if the tree is empty.

        Returns:
            Value fetched by value_policy from the last node, or None.

        """
        if self.size() == 0:
            return None
        return self.value_policy.fetch(self.rbegin().node)

    def __str__(self) -> str:
        """Return a string representation of the container's contents."""
        parts = []
        it = self.begin()
        end = self.end()
        while not it.equals(end):
            parts.append(self.value_policy.to_string(it.node))
            it.next()
        return "{" + ",".join(parts) + "}"

    def __repr__(self) -> str:
        """Return a string representation of the container's contents."""
        return self.__str__()

    def __iter__(self) -> PyIterator[K | V | tuple[K, V]]:
        """Return forward key iterator."""
        return self.keys()

    def __getitem__(self, key: K) -> V:
        """
        Return the value associated with key.

        Args:
            key: Key to look up.

        Returns:
            Value stored at key.

        Raises:
            KeyError: When key is not present in the tree.

        """
        it = self.find(key)
        if self.is_leaf(it.node):
            raise KeyError(key)
        return it.node.value

    def __setitem__(self, key: K, value: V) -> None:
        """
        Insert or replace the value for key.

        Args:
            key: Key to insert or update.
            value: Value to associate with the key.

        """
        n: TreeNode[K, V] = TreeNode()
        n.key = key
        n.value = value
        self.insert_or_replace(n)

    def __contains__(self, k: K) -> bool:
        """Return true if tree contains provided key."""
        iter = self.find(k)
        return not iter.equals(self.end())

    def __delitem__(self, k: K):
        """Delete item by key or raise KeyError."""
        iter = self.find(k)
        if not iter.equals(self.end()):
            self.erase(iter.node)
        else:
            raise KeyError(f"Key {k} not found")

    def __len__(self) -> int:
        """Return number of elements in the tree."""
        return self.head.size

    def keys(self) -> PyIterator[K]:
        """Yield keys for each node in ascending key order."""
        return PyIterator(self, KeyOnlyPolicy())

    def values(self) -> PyIterator[V]:
        """Yield values for each node in ascending key order."""
        return PyIterator(self, ValueOnlyPolicy())
