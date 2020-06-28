# coding: mixt

import pytest

from mixt import Element, html, Ref,  ElementProxy
from mixt.exceptions import ElementError


def test_base_proxy():
    assert ElementProxy.__proxy_base__ is ElementProxy
    assert ElementProxy.proxied is None
    assert ElementProxy.__name__ == 'ElementProxy'
    assert ElementProxy.__tag__ == 'ElementProxy'
    assert ElementProxy.__display_name__ == 'ElementProxy'


def test_for_on_base_proxy():
    ProxyDiv = ElementProxy.For(html.Div)

    assert ProxyDiv.__proxy_base__ is ElementProxy
    assert ProxyDiv.proxied is html.Div
    assert ProxyDiv.__name__ == 'ElementProxyForDiv'
    assert ProxyDiv.__tag__ == 'ElementProxyForDiv'
    assert ProxyDiv.__display_name__ == 'ElementProxyForDiv'


def test_proxied_must_be_base():
    with pytest.raises(ElementError) as raised:
        ElementProxy.For('foo')

    assert str(raised.value) == "<ElementProxy>.For: the argument must be a subclass of `Base`"


def test_inherit_from_base_proxy():
    class Comp(ElementProxy):
        pass

    assert Comp.__proxy_base__ is Comp
    assert Comp.proxied is None
    assert Comp.__name__ == 'Comp'
    assert Comp.__tag__ == 'Comp'
    assert Comp.__display_name__ == 'Comp'


def test_inherit_from_for_on_base_proxy():
    class Comp(ElementProxy.For(html.Div)):
        pass

    assert Comp.__proxy_base__.proxied is None
    assert Comp.__proxy_base__.__name__ == 'Comp'
    assert Comp.__proxy_base__.__tag__ == 'Comp'
    assert Comp.__proxy_base__.__display_name__ == 'Comp'

    assert Comp.proxied is html.Div
    assert Comp.__name__ == 'Comp'
    assert Comp.__tag__ == 'Comp'
    assert Comp.__display_name__ == 'Comp'


def test_for_on_proxy():
    class Comp(ElementProxy):
        pass

    CompDiv = Comp.For(html.Div)

    assert CompDiv.__proxy_base__ is Comp
    assert CompDiv.proxied is html.Div
    assert CompDiv.__name__ == 'CompForDiv'
    assert CompDiv.__tag__ == 'CompForDiv'
    assert CompDiv.__display_name__ == 'CompForDiv'


def test_for_on_for_on_proxy():
    class Comp(ElementProxy):
        pass

    CompDiv = Comp.For(html.Div)
    CompSpan = CompDiv.For(html.Span)

    assert CompSpan.__proxy_base__ is Comp
    assert CompSpan.proxied is html.Span
    assert CompSpan.__name__ == 'CompForSpan'
    assert CompSpan.__tag__ == 'CompForSpan'
    assert CompSpan.__display_name__ == 'CompForSpan'


def test_inherit_from_proxy():
    class Comp(ElementProxy):
        pass

    class Comp2(Comp):
        pass

    assert Comp2.__proxy_base__ is Comp2
    assert Comp2.proxied is None
    assert Comp2.__name__ == 'Comp2'
    assert Comp2.__tag__ == 'Comp2'
    assert Comp2.__display_name__ == 'Comp2'


def test_for_on_inherit_from_proxy():
    class Comp(ElementProxy):
        pass

    class Comp2(Comp):
        pass

    Comp2Div = Comp2.For(html.Div)

    assert Comp2Div.__proxy_base__ is Comp2
    assert Comp2Div.proxied is html.Div
    assert Comp2Div.__name__ == 'Comp2ForDiv'
    assert Comp2Div.__tag__ == 'Comp2ForDiv'
    assert Comp2Div.__display_name__ == 'Comp2ForDiv'


def test_inherit_from_for_on_proxy():
    class Comp(ElementProxy):
        pass

    class Comp2(Comp.For(html.Div)):
        pass

    assert Comp2.__proxy_base__.proxied is None
    assert Comp2.__proxy_base__.__name__ == 'Comp2'
    assert Comp2.__proxy_base__.__tag__ == 'Comp2'
    assert Comp2.__proxy_base__.__display_name__ == 'Comp2'

    assert Comp2.proxied is html.Div
    assert Comp2.__name__ == 'Comp2'
    assert Comp2.__tag__ == 'Comp2'
    assert Comp2.__display_name__ == 'Comp2'


def test_for_on_inherit_from_for_on_proxy():
    class Comp(ElementProxy):
        pass

    class Comp2(Comp.For(html.Div)):
        pass

    Comp2Span = Comp2.For(html.Span)

    assert Comp2Span.__proxy_base__ is Comp2.__proxy_base__
    assert Comp2Span.proxied is html.Span
    assert Comp2Span.__name__ == 'Comp2ForSpan'
    assert Comp2Span.__tag__ == 'Comp2ForSpan'
    assert Comp2Span.__display_name__ == 'Comp2ForSpan'


def test_components_are_cached():
    class Comp(ElementProxy):
        pass

    CompDiv = Comp.For(html.Div)
    CompSpan = CompDiv.For(html.Span)

    assert Comp.For(html.Div) is CompDiv
    assert CompDiv.For(html.Div) is CompDiv
    assert CompSpan.For(html.Div) is CompDiv


    class Comp2(ElementProxy.For(html.Div)):
        pass

    assert Comp2.For(html.Div) is Comp2


def test_cannot_init_without_proxy():
    class Comp(ElementProxy):
        pass

    with pytest.raises(ElementError) as raised:
        Comp()

    assert str(raised.value) == "<Comp> has nothing to proxy. `Comp.For(...)` must be used"


def test_proxy_proptypes():

    class Comp1(Element):
        class PropTypes:
            foo: str = "FOO"
            bar: str = "BAR"
            baz: str = "BAZ"

    class Comp2(ElementProxy.For(Comp1)):
        class PropTypes:
            foo: str = "FOOFOO"
            baz: int = 1
            qux: str = "QUX"

    assert Comp2.PropTypes.__types__ == {
        "_class": str,
        "id": str,
        "ref": Ref,

        "foo": str,
        "bar": str,
        "baz": int,
        "qux": str,
    }

    assert Comp2.PropTypes.__default_props__ == {
        "foo": "FOOFOO",
        "bar": "BAR",
        "baz": 1,
        "qux": "QUX",
    }

    # props from comp1 and comp2 should be allowed
    obj = Comp2(foo="foo", bar='bar', baz=2, qux="qux", data_x="x", aria_y="y")
    assert obj.foo == "foo"
    assert obj.bar == "bar"
    assert obj.baz == 2
    assert obj.qux == "qux"
    assert obj.data_x == "x"
    assert obj.aria_y == "y"

    obj = Comp2(foo="foo", qux="qux", data_x="x", aria_y="y")
    assert obj.proxied_props == {
        "foo": "foo",
        "bar": "BAR",
        "baz": 1,
        "data_x": "x",
        "aria_y": "y",
    }
    assert obj.own_props == {
        "foo": "foo",
        "baz": 1,
        "qux": "qux",
    }
    assert obj.declared_props == {
        "foo": "foo",
        "bar": "BAR",
        "baz": 1,
        "qux": "qux",
    }
    assert obj.non_declared_props == {
        "data_x": "x",
        "aria_y": "y",
    }
    assert obj.props_for(Comp1) == {
        "foo": "foo",
        "bar": "BAR",
        "baz": 1,
    }
    assert obj.props_for(Comp2) == {
        "foo": "foo",
        "bar": "BAR",
        "baz": 1,
        "qux": "qux",
    }

    # replace Comp1 by Canvas
    Comp3 = Comp2.For(html.Canvas)

    obj = Comp3(foo="foo", qux="qux", height=300)

    assert obj.proxied_props == {
        "height": 300
    }
    assert obj.own_props == {
        "foo": "foo",
        "baz": 1,
        "qux": "qux",
    }
    assert obj.props_for(Comp1) == {
        "foo": "foo",
        "baz": 1,
    }
    assert obj.props_for(Comp2) == {
        "foo": "foo",
        "baz": 1,
        "qux": "qux",
    }
    assert obj.props_for(Comp3) == {
        "foo": "foo",
        "baz": 1,
        "qux": "qux",
        "height": 300,
    }
    assert obj.props_for(html.Canvas) == {
        "height": 300,
    }

    assert obj.props_for(html.Div) == {
    }

    with pytest.raises(ElementError):
        obj.props_for("foo")

    with pytest.raises(ElementError):
        class Foo: pass
        obj.props_for(Foo)


def test_render():

    class Button(ElementProxy.For(html.Button)):
        class PropTypes:
            label: str = "button"
        def render(self, context):
            return self.proxied(**self.proxied_props)(
                <span>{self.label}</span>
            )

    assert str(<Button autofocus />) == "<button autofocus><span>button</span></button>"

    ButtonDiv = Button.For(html.Div)

    assert str(<ButtonDiv label="ok" />) == "<div><span>ok</span></div>"

    # div does not accept autofocus
    with pytest.raises(Exception):
        <ButtonDiv autofocus />
