"""Provides data for the todolist app."""
from typing import List


class TodoObject:
    """Will store a todo with a text and auto-incremented id."""

    last_id: int = 0

    def __init__(self, text: str) -> None:
        """Create the todo object with a text and force its id.

        Parameters
        ----------
        text: str
            The text of the todo line.

        """
        TodoObject.last_id += 1
        self.id: int = TodoObject.last_id
        self.text: str = text


TODOS: List[TodoObject] = [TodoObject("foo"), TodoObject("bar"), TodoObject("baz")]
