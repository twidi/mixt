# pylint: disable=missing-docstring
# flake8: noqa: D

from mixt import html, Element, Required


class Hello(Element):
    class PropTypes:
        name: Required[str]

    def render(self, context):
        return html.Div(title="Greeting")("Hello, ", self.name)


print(Hello(name="World"))
