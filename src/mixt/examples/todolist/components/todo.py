# coding: mixt

"""The Todo component for the todolist app example, to display a todo entry."""

from mixt import Element, Required, html
from mixt.internal.base import OptionalContext, OneOrManyElements

from ..data import TODOS, TodoObject


class Todo(Element):
    """Component that render a toto object."""

    class PropTypes:
        todo: Required[TodoObject]
        remove_url: Required[str]

    def render(self, context: OptionalContext) -> OneOrManyElements:  # noqa: D102
        return \
            <li>
                {self.todo.text}
                <form method="post" action={self.remove_url.format(id=self.todo.id)}>
                    <button type="submit">Remove</button>
                </form>
            </li>

if __name__ == "__main__":
    print(<Todo todo={TODOS[0]} remove_url={"/todo/{id}/remove"} />)
