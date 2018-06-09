# pylint: disable=missing-docstring
# flake8: noqa: D

from mixt import Element, Required, html


class Hello(Element):
    class PropTypes:
        name: Required[str]

    def render(self, context):
        return html.Div(title="Greeting")("Hello, ", self.name)


def render_example() -> str:
    """Render the html for this example.

    Returns
    -------
    str
        The final html.

    """
    return str(Hello(name="World"))


if __name__ == "__main__":
    print(render_example())
