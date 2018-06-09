# coding: mixt

"""The TodoList component for the todolist app example, to display a list of todo entries."""

from typing import List

from mixt import Element, Required, html
from mixt.internal.base import OptionalContext, OneOrManyElements

from ..data import TODOS, TodoObject
from .todo import Todo


class TodoList(Element):
    """Component to render a list of todos."""

    class PropTypes:
        todos: Required[List[TodoObject]]
        remove_url: Required[str]

    def render(self, context: OptionalContext) -> OneOrManyElements:  # noqa: D102
        return (
            <ul>
                {
                    [
                        <Todo todo={todo} remove_url={self.remove_url} />
                        for todo
                        in self.todos
                    ]
                }
            </ul>
        )

if __name__ == "__main__":
    print(<TodoList todos={TODOS} remove_url={"/todo/{id}/remove"} />)
