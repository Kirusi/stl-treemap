"""Node data access policies for sets, maps, and value iteration."""

from __future__ import annotations

from abc import ABC, abstractmethod

from stl_treemap.tree_node import TreeNode


class PolicyInterface[K, V](ABC):
    """@private Interface for node data access policies."""

    @abstractmethod
    def fetch(self, n: TreeNode[K, V]) -> K | V | tuple[K, V]:
        """Return data from the specified node."""

    @abstractmethod
    def copy(self, dst: TreeNode[K, V], src: TreeNode[K, V]) -> None:
        """Copy data from one node to another."""

    @abstractmethod
    def to_string(self, node: TreeNode[K, V]) -> str:
        """Return string representation of the node."""


class KeyOnlyPolicy[K, V](PolicyInterface[K, V]):
    """@private Used by sets."""

    def fetch(self, n: TreeNode[K, V]) -> K:
        """
        Return key data from the specified node.

        Args:
            n: Node to inspect.

        Returns:
            Node's key.

        """
        return n.key

    def copy(self, dst: TreeNode[K, V], src: TreeNode[K, V]) -> None:
        """
        Copy key data from one node to another.

        Args:
            dst: Destination node.
            src: Source node.

        """
        dst.key = src.key

    def to_string(self, node: TreeNode[K, V]) -> str:
        """
        Return string representation of the provided node.

        Args:
            node: Node to serialize.

        Returns:
            String representation of the key.

        """
        return str(node.key)


class KeyValuePolicy[K, V](PolicyInterface[K, V]):
    """@private Used by maps."""

    def fetch(self, n: TreeNode[K, V]) -> tuple[K, V]:
        """
        Return key-value data from the specified node.

        Args:
            n: Node to inspect.

        Returns:
            Tuple of key and value.

        """
        return (n.key, n.value)

    def copy(self, dst: TreeNode[K, V], src: TreeNode[K, V]) -> None:
        """
        Copy key-value data from one node to another.

        Args:
            dst: Destination node.
            src: Source node.

        """
        dst.key = src.key
        dst.value = src.value

    def to_string(self, node: TreeNode[K, V]) -> str:
        """
        Generate string representation of the node.

        Args:
            node: Node to serialize.

        Returns:
            String representation of key-value pair.

        """
        return f"{node.key}:{node.value}"


class ValueOnlyPolicy[K, V](PolicyInterface[K, V]):
    """@private Used for iteration through values of a map."""

    def fetch(self, n: TreeNode[K, V]) -> V:
        """
        Return value data from the specified node.

        Args:
            n: Node to inspect.

        Returns:
            Node's value.

        """
        return n.value

    def copy(self, dst: TreeNode[K, V], src: TreeNode[K, V]) -> None:
        """
        Copy value data from one node to another.

        Args:
            dst: Destination node.
            src: Source node.

        """
        dst.value = src.value

    def to_string(self, node: TreeNode[K, V]) -> str:
        """
        Return string representation of the node.

        Args:
            node: Node to serialize.

        Returns:
            String representation of node's value.

        """
        return str(node.value)
