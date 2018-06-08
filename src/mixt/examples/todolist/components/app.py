# coding: mixt

"""App component for the todolist app example."""

from typing import List

from mixt import Element, Required, html
from mixt.internal.base import OptionalContext, OneOrManyElements

from ..data import TODOS, TodoObject
from .form import TodoForm
from .list import TodoList


class TodoApp(Element):
    """Component that render a todo app."""

    class PropTypes:
        todos: Required[List[TodoObject]]
        add_url: Required[str]
        remove_url: Required[str]

    def render(self, context: OptionalContext) -> OneOrManyElements:  # noqa: D102
        return \
            <main class="app">
                <h1>The todo list</h1>
                <TodoForm add_url={self.add_url} />
                <TodoList todos={self.todos}  remove_url={self.remove_url} />
            </main>

if __name__ == "__main__":
    print(<TodoApp todos={TODOS} add_url="/todo/add" remove_url={"/todo/{id}/remove"} />)
