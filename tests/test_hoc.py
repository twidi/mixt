# coding: mixt

from mixt import html, Element, Required


def test_passthrough_element():

    class El(Element):
        class PropTypes:
            foo: Required[str]
            bar: Required[str]

        def render(self, context):
            return <div>{self.foo} - {self.bar}{self.children()}</div>


    def decorate(Wrapped):
        class HOC (Element):
            __display_name__ = f"decorate({Wrapped.__display_name__})"
            class PropTypes(Wrapped.PropTypes):
                 baz: Required[str]

            def render(self, context):
                props = dict(self.props)
                props['foo'] = f"{self.foo} ({props.pop('baz')})"
                return <Wrapped {**props}>{self.children()}</Wrapped>

        return HOC


    assert str(<El foo="FOO" bar="BAR"><span>QUX</span></El>) == '<div>FOO - BAR<span>QUX</span></div>'

    DecoratedEl = decorate(El)
    el = (<DecoratedEl foo="FOO" bar="BAR" baz="BAZ"><span>QUX</span></DecoratedEl>)

    assert el.__display_name__ == "decorate(El)"
    assert str(el) == '<div>FOO (BAZ) - BAR<span>QUX</span></div>'
