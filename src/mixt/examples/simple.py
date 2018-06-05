# coding: mixt
# pylint: disable=missing-docstring
# flake8: noqa: D

from mixt import Element, Required, html


class Hello(Element):
    class PropTypes:
        name: Required[str]

    def render(self, context):
        return <div title="Greeting">Hello, {self.name}</div>


print(<Hello name="World"/>)
