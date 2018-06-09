"""Main entry point of the user-guide app example.

To execute it:

    ``python -m mixt.examples.user_guide``

"""

from .pure_python import ThingApp, UserContext


def render_example():
    """Render the html for this example."""
    return str(UserContext(authenticated_user_id=1)(ThingApp()))


if __name__ == "__main__":
    print(render_example())
