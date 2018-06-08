# coding: mixt

"""The Form component for the todolist app example, to add a todo entry."""

from mixt import Element, Required, html
from mixt.internal.base import OptionalContext, OneOrManyElements


class TodoForm(Element):
    """Component that render a form to add a todo."""

    class PropTypes:
        add_url: Required[str]

    def render(self, context: OptionalContext) -> OneOrManyElements:  # noqa: D102
        return \
            <form method="post" action={self.add_url}>
                <label>New Todo: </label><itext name="todo" />
                <button type="submit">Add</button>
            </form>

if __name__ == "__main__":
    print(<TodoForm add_url="/todo/add" />)
