"""STL-like forward and reverse iterators for tree containers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from stl_treemap.tree_node import TreeNode


class IterableContainer(Protocol):
    """Protocol for containers that support forward and backward node traversal."""

    def next(self, node: Any) -> Any:
        """Return the node following *node* in forward order."""
        ...

    def prev(self, node: Any) -> Any:
        """Return the node preceding *node* in forward order."""
        ...


class BaseIterator[K, V, C: IterableContainer](ABC):
    """
    Base class for STL-like iterators.

    References a node and a container. Navigation is achieved by calling
    the container's prev() and next() methods.
    """

    def __init__(self, node: TreeNode[K, V], container: C) -> None:
        """
        Create an iterator from a node and a container.

        Args:
            node: Start node.
            container: Container to traverse.

        """
        self._n = node
        self._c = container

    @abstractmethod
    def next(self) -> None:
        """Advance to the next node."""

    @abstractmethod
    def prev(self) -> None:
        """Retreat to the previous node."""

    def equals(self, rhs: object) -> bool:
        """
        Check equality of two iterators.

        Two iterators are equal when they point to the same node of the same container.

        Args:
            rhs: Right-hand side iterator.

        Returns:
            True when both iterators point to the same node of the same container.

        Raises:
            ValueError: When iterators are of different types.
            ValueError: When iterators belong to different containers.

        """
        if not isinstance(rhs, type(self)):
            lhs_class = type(self).__name__
            rhs_class = type(rhs).__name__
            raise ValueError(f"Can't compare an instance of {lhs_class} with an instance of {rhs_class}")
        if self._c is not rhs.container:
            raise ValueError("Iterators belong to different containers")
        return self._n is rhs.node

    @property
    def node(self) -> TreeNode[K, V]:
        """@private Current node."""
        return self._n

    @property
    def key(self) -> K:
        """Key of the current node."""
        return self._n.key

    @property
    def value(self) -> V:
        """Value of the current node."""
        return self._n.value

    @property
    def container(self) -> C:
        """@private Container that holds the current node."""
        return self._c


class TreeIterator[K, V, C: IterableContainer](BaseIterator[K, V, C]):
    """
    STL-like forward iterator.

    More verbose than Python iterators, but allows iteration over any range
    within the container.

    Example::

        m = TreeMap()
        it = m.begin()
        while not it.equals(m.end()):
            print(f"key: {it.key}, value: {it.value}")
            it.next()
    """

    def __init__(self, *args: Any) -> None:
        """
        Create a forward iterator.

        Three construction forms are supported:

        1. From a node and container: ``TreeIterator(node, container)``
        2. Copy of a TreeIterator: ``TreeIterator(other)``
        3. Convert from ReverseIterator: ``TreeIterator(reverse_iter)``

        Args:
            *args: Either ``(node, container)`` or a single iterator to copy/convert.

        Raises:
            ValueError: When arguments are invalid or the source object is unsupported.

        """
        if len(args) == 2:  # noqa: PLR2004
            node, container = args
            super().__init__(node, container)
        elif len(args) == 1:
            obj = args[0]
            if isinstance(obj, TreeIterator):
                super().__init__(obj._n, obj._c)
            elif isinstance(obj, ReverseIterator):
                c = obj._c
                super().__init__(c.next(obj._n), c)
            else:
                raise ValueError(f"Can't create an Iterator from {type(obj).__name__}")
        else:
            raise ValueError("Can't create an Iterator with provided parameters")

    def next(self) -> None:
        """Advance to the next node in the container."""
        self._n = self._c.next(self._n)

    def prev(self) -> None:
        """Retreat to the previous node in the container."""
        self._n = self._c.prev(self._n)


class ReverseIterator[K, V, C: IterableContainer](BaseIterator[K, V, C]):
    """
    STL-like backward iterator.

    Traverses the container in reverse order: next() moves backward,
    prev() moves forward.

    Example::

        m = TreeMap()
        it = m.rbegin()
        while not it.equals(m.rend()):
            print(f"key: {it.key}, value: {it.value}")
            it.next()
    """

    def __init__(self, *args: Any) -> None:
        """
        Create a reverse iterator.

        Three construction forms are supported:

        1. From a node and container: ``ReverseIterator(node, container)``
        2. Copy of a ReverseIterator: ``ReverseIterator(other)``
        3. Convert from TreeIterator: ``ReverseIterator(forward_iter)``

        Args:
            *args: Either ``(node, container)`` or a single iterator to copy/convert.

        Raises:
            ValueError: When arguments are invalid or the source object is unsupported.

        """
        if len(args) == 2:  # noqa: PLR2004
            node, container = args
            super().__init__(node, container)
        elif len(args) == 1:
            obj = args[0]
            if isinstance(obj, ReverseIterator):
                super().__init__(obj._n, obj._c)
            elif isinstance(obj, TreeIterator):
                c = obj._c
                super().__init__(c.prev(obj._n), c)
            else:
                raise ValueError(f"Can't create an ReverseIterator from {type(obj).__name__}")
        else:
            raise ValueError("Can't create a Reverse Iterator with provided parameters")

    def next(self) -> None:
        """Advance to the previous node in the container (reverse order)."""
        self._n = self._c.prev(self._n)

    def prev(self) -> None:
        """Retreat to the next node in the container (reverse order)."""
        self._n = self._c.next(self._n)
