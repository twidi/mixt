# coding: mixt

from mixt import html, Element, Required

def test_rendering():

    class Hello(Element):
        class PropTypes:
            name: Required[str]

        def render(self, context):
            return <div>Hello, {self.name}</div>

    assert str(<Hello name="World"/>) == '<div>Hello, World</div>'
