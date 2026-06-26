"""@private A node for a red-black tree."""

from __future__ import annotations


class NodeColors:
    """@private Node colors."""

    RED = 1
    BLACK = 2


class TreeNode[K, V]:
    """@private A node for a red-black tree."""

    def __init__(self) -> None:
        """Default constructor."""
        self.left: SomeNode[K, V] = None  # left child
        self.right: SomeNode[K, V] = None  # right child
        self.parent: SomeNode[K, V] = None  # parent node
        self.key: K | None = None  # key object (additional 'value' data member is added in map-like classes)
        self.value: V | None = None  # value associated with the key
        self.color: int = NodeColors.RED  # by default new node is red

    def grandparent(self) -> TreeNode[K, V] | None:
        """
        Parent of parent node.

        Returns:
            Parent node of parent node.

        """
        p = self.parent
        if not isinstance(p, TreeNode):
            return None
        gp = p.parent
        return gp if isinstance(gp, TreeNode) else None

    def sibling(self) -> TreeNode[K, V] | None:
        """
        Next sibling in the forward iteration order or None.

        Returns:
            The other child of the same parent.

        """
        p = self.parent
        if not isinstance(p, TreeNode):
            return None
        other = p.right if self is p.left else p.left
        return other if isinstance(other, TreeNode) else None

    def uncle(self) -> TreeNode[K, V] | None:
        """
        Parent's sibling (in the forward iteration order).

        Returns:
            Another child of the grandparent.

        """
        p = self.parent
        if not isinstance(p, TreeNode):
            return None
        if not isinstance(p.parent, TreeNode):
            return None
        return p.sibling()


class Head[K, V]:
    """@private Special node in a tree is created for performance reasons."""

    def __init__(self) -> None:
        """Default constructor."""
        self.leftmost: SomeNode[K, V] = self  # node with the smallest key
        self.rightmost: SomeNode[K, V] = self  # node with the largest key
        self.root: SomeNode[K, V] = self  # root node of the tree
        self.size: int = 0  # number of nodes in the tree
        self.id: str = "HEAD"  # extra tag used in debugging of unit tests


type SomeNode[K, V] = Head[K, V] | TreeNode[K, V] | None
