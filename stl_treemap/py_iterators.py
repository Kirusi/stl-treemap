"""Python-style forward and backward iterators wrapping tree containers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


class PyIterator[T](Iterator):
    """
    Forward iterator for tree containers.

    Implements the Python iterator protocol so it can be used directly in
    ``for`` loops.  The container must provide ``py_begin()``, ``py_end()``,
    ``next(node)``, ``prev(node)``, and a ``value_policy`` attribute.

    Example::

        m = TreeMap()
        for key, value in m:
            print(f"key: {key}, value: {value}")

        for value in m.values():
            print(f"value: {value}")

    """

    def __init__(self, container: Any, value_policy: Any = None) -> None:
        """
        Construct a forward iterator for container.

        Args:
            container: Container to traverse.
            value_policy: Policy controlling what each element yields; defaults
                to ``container.value_policy``.

        """
        self.container = container
        self.value_policy = container.value_policy if value_policy is None else value_policy
        self.node = container.py_begin()

    def __iter__(self) -> PyIterator[T]:
        """Return self to satisfy the iterator protocol."""
        return self

    def __next__(self) -> T:
        """Return the next value and advance, or raise StopIteration when exhausted."""
        if self.node == self.container.py_end():
            raise StopIteration
        value: T = self.value_policy.fetch(self.node)
        self.node = self.container.next(self.node)
        return value

    def backwards(self) -> PyReverseIterator[T]:
        """Return a reverse iterator for the same container and value policy."""
        return PyReverseIterator(self.container, self.value_policy)


class PyReverseIterator[T](Iterator):
    """
    Backward iterator for tree containers.

    Implements the Python iterator protocol so it can be used directly in
    ``for`` loops.  The container must provide ``py_rbegin()``, ``py_rend()``,
    ``next(node)``, ``prev(node)``, and a ``value_policy`` attribute.

    Example::

        m = TreeMap()
        for key, value in m.backwards():
            print(f"key: {key}, value: {value}")

        for key in m.keys().backwards():
            print(f"key: {key}")

    """

    def __init__(self, container: Any, value_policy: Any = None) -> None:
        """
        Construct a backward iterator for container.

        Args:
            container: Container to traverse.
            value_policy: Policy controlling what each element yields; defaults
                to ``container.value_policy``.

        """
        self.container = container
        self.value_policy = container.value_policy if value_policy is None else value_policy
        self.node = container.py_rbegin()

    def __iter__(self) -> PyReverseIterator[T]:
        """Return self to satisfy the iterator protocol."""
        return self

    def __next__(self) -> T:
        """Return the next value (in reverse order) and advance, or raise StopIteration."""
        if self.node == self.container.py_rend():
            raise StopIteration
        value: T = self.value_policy.fetch(self.node)
        self.node = self.container.prev(self.node)
        return value

    def backwards(self) -> PyIterator[T]:
        """Return a forward iterator for the same container and value policy."""
        return PyIterator(self.container, self.value_policy)
