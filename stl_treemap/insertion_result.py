"""Result type for tree insertion operations."""

from __future__ import annotations


class InsertionResult[I]:
    """
    Reports whether an insert operation was successful.

    If a node was added or an existing one replaced, an iterator is provided.
    Otherwise iterator is None.
    """

    def __init__(self, was_added: bool, was_replaced: bool, iterator: I | None = None) -> None:
        """
        Create an insertion result.

        Args:
            was_added: True when a new value was added to the container.
            was_replaced: True when a new value replaced an existing value in the container.
            iterator: Iterator pointing to the newly added or replaced node, or None.

        """
        self.was_added = was_added  # Boolean flag indicating whether an element was added
        self.was_replaced = was_replaced  # Boolean flag indicating whether an existing node was updated
        self.iterator = iterator  # Iterator instance pointing to the newly added node
