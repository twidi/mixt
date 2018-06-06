# coding: mixt

"""Main entry point of the todolist app example.

To execute it:

    ``python -m mixt.examples.todolist``

"""

from mixt import html

from .components.app import TodoApp
from .data import TODOS


def render_example() -> str:
    """Render the html for this example.

    Returns
    -------
    str
        The final html.

    """
    return str(
        <html>
            <body>
                <TodoApp todos={TODOS} add_url="/todo/add" remove_url={"/todo/{id}/remove"} />
            </body>
        </html>
    )


if __name__ == "__main__":
    print(render_example())
