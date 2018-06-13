# coding: mixt

import pytest

from mixt import html
from mixt.internal.html import HtmlElement
from mixt.internal.base import Base
from mixt.exceptions import (
    InvalidPropChoiceError,
    InvalidPropNameError,
    PropTypeChoicesError,
    UnsetPropError,
)
from mixt.proptypes import NotProvided, DefaultChoices, Choices


class DummyBase(Base):
    def _to_list(self, acc):
        pass


def test_basics():
    assert str(<div />) == '<div></div>'
    assert str(<img src="blah" />) == '<img src="blah" />'
    assert str(<div class="c"></div>) == '<div class="c"></div>'
    assert str(<div><span></span></div>) == '<div><span></span></div>'
    assert str(<Fragment><span /><span /></Fragment>) == '<span></span><span></span>'


def test_escaping():
    assert str(<div class="&">&{'&'}</div>) == '<div class="&amp;">&&amp;</div>'
    assert str(<div>{html.Raw('&')}</div>) == '<div>&</div>'


def test_comments():
    pyxl = (
        <div
            class="blah" # attr comment
            >  # comment1
            <!-- comment2 -->
            text# comment3
            # comment4
        </div>)
    assert str(pyxl) == '<div class="blah">text</div>'


def test_conditional_comment():
    s = 'blahblah'
    assert (str(<ConditionalComment cond="lt IE 8"><div class=">">{s}</div></ConditionalComment>)
        == '<!--[if lt IE 8]><div class="&gt;">blahblah</div><![endif]-->')
    assert (str(<ConditionalComment cond="(lt IE 8) & (gt IE 5)"><div>{s}</div></ConditionalComment>)
        == '<!--[if (lt IE 8) & (gt IE 5)]><div>blahblah</div><![endif]-->')


def test_conditional_non_comment():
    s = 'blahblah'
    assert (str(<ConditionalNonComment cond="lt IE 8"><div class=">">{s}</div></ConditionalNonComment>)
        == '<!--[if lt IE 8]><!--><div class="&gt;">blahblah</div><!--<![endif]-->')
    assert (str(<ConditionalNonComment cond="(lt IE 8) & (gt IE 5)"><div>{s}</div></ConditionalNonComment>)
        == '<!--[if (lt IE 8) & (gt IE 5)]><!--><div>blahblah</div><!--<![endif]-->')


def test_decl():
    assert (str(<script><![CDATA[<div><div>]]></script>)
        == '<script><![CDATA[<div><div>]]></script>')

def test_enum_prop():

    with pytest.raises(PropTypeChoicesError):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices

    with pytest.raises(PropTypeChoicesError):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices = []

    with pytest.raises(PropTypeChoicesError):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices = 'foo'

    with pytest.raises(PropTypeChoicesError):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices = 123

    class Foo(DummyBase):
        class PropTypes:
            value: Choices = ['a', 'b']

    with pytest.raises(UnsetPropError):
        <Foo />.prop('value')

    with pytest.raises(UnsetPropError):
        <Foo />.value

    assert (<Foo value="b" />.prop('value')) == 'b'
    assert (<Foo value="b" />.value) == 'b'

    with pytest.raises(InvalidPropChoiceError):
        <Foo value="c" />

    with pytest.raises(InvalidPropChoiceError):
        <Foo value={None} />

    with pytest.raises(UnsetPropError):
        <Foo value={NotProvided} />.value

    class Bar(DummyBase):
        class PropTypes:
            value: DefaultChoices = ['a', 'b']

    assert (<Bar />.prop('value')) == 'a'
    assert (<Bar />.value) == 'a'
    assert (<Bar value="b" />.prop('value')) == 'b'
    assert (<Bar value="b" />.value) == 'b'

    with pytest.raises(InvalidPropChoiceError):
        <Bar value="c" />

    with pytest.raises(InvalidPropChoiceError):
        <Bar value={None} />

    assert (<Bar value={NotProvided} />.value) == 'a'

    class Baz(DummyBase):
        class PropTypes:
            value: DefaultChoices = [None, 'a', 'b']

    assert (<Baz />.prop('value')) is None
    assert (<Baz />.value) is None

    class Qux(DummyBase):
        class PropTypes:
            value: DefaultChoices = [NotProvided, 'a', 'b']

    with pytest.raises(AttributeError):
        <Qux />.prop('value')

    with pytest.raises(AttributeError):
        <Qux />.value


def test_special_prop_names():
    class Foo(HtmlElement):
        class PropTypes:
            _def: str
            foo_bar__baz: str

    # using "html" type props names
    tag = <Foo def='fed' foo-bar:baz='qux' />
    assert str(tag) == '<foo def="fed" foo-bar:baz="qux"></foo>'
    assert tag.prop_name("def") == "_def"
    assert tag._def == 'fed'
    assert tag.prop("def") == "fed"
    assert tag.prop_name("foo-bar:baz") == "foo_bar__baz"
    assert tag.foo_bar__baz == 'qux'
    assert tag.prop("foo-bar:baz") == "qux"

    # using "python" type props names
    tag = <Foo _def='fed' foo_bar__baz='qux' />
    assert str(tag) == '<foo def="fed" foo-bar:baz="qux"></foo>'
    assert tag.prop_name("_def") == "_def"
    assert tag._def == 'fed'
    assert tag.prop("_def") == "fed"
    assert tag.prop_name("foo_bar__baz") == "foo_bar__baz"
    assert tag.foo_bar__baz == 'qux'
    assert tag.prop("foo_bar__baz") == "qux"


def test_props_methods():
    class Foo(Base):
        class PropTypes:
            foo: str
            bar: str
            baz: str = "BAZ"

    el = <Foo foo="FOO" />

    assert el.prop_name("foo") == "foo"
    assert el.prop("foo") == "FOO"
    assert el.foo == "FOO"
    assert el.props["foo"] == "FOO"
    assert el.has_prop("foo")
    assert el.has_prop("foo", allow_invalid=False)
    assert el.prop_default("foo") is NotProvided
    assert not el.is_prop_default("foo")
    assert not el.is_prop_default("foo", "bar")
    assert el.prop_type("foo") is str

    assert el.prop_name("bar") == "bar"
    with pytest.raises(UnsetPropError):
        el.prop("bar")
    with pytest.raises(UnsetPropError):
        el.bar
    with pytest.raises(KeyError):
        el.props["bar"]
    assert not el.has_prop("bar")
    assert not el.has_prop("bar", allow_invalid=False)
    assert el.prop_default("bar") is NotProvided
    with pytest.raises(UnsetPropError):
        el.is_prop_default("bar")

    assert el.prop_name("baz") == "baz"
    assert el.prop("baz") == "BAZ"
    assert el.baz == "BAZ"
    assert el.props["baz"] == "BAZ"
    assert el.has_prop("baz")
    assert el.has_prop("baz", allow_invalid=False)
    assert el.prop_default("baz") == "BAZ"
    assert el.is_prop_default("baz")
    assert not el.is_prop_default("baz", "ZAB")

    with pytest.raises(InvalidPropNameError):
        el.prop_name("qux")
    with pytest.raises(InvalidPropNameError):
        el.prop("qux")
    with pytest.raises(InvalidPropNameError):
        el.qux
    with pytest.raises(KeyError):
        el.props["qux"]
    assert not el.has_prop("qux")
    with pytest.raises(InvalidPropNameError):
        el.has_prop("qux", allow_invalid=False)
    with pytest.raises(InvalidPropNameError):
        el.prop_default("qux")
    with pytest.raises(InvalidPropNameError):
        el.is_prop_default("qux")
    with pytest.raises(InvalidPropNameError):
        el.prop_type("qux")

    el.set_prop("bar", "BAR")
    assert el.prop("bar") == "BAR"
    assert el.bar == "BAR"
    assert el.has_prop("bar")
    assert el.props["bar"] == "BAR"

    el.set_prop("bar", NotProvided)
    with pytest.raises(UnsetPropError):
        el.prop("bar")
    with pytest.raises(UnsetPropError):
        el.bar
    assert not el.has_prop("bar")

    el.set_prop("baz", "ZAB")
    assert el.prop("baz") == "ZAB"
    assert el.baz == "ZAB"
    assert el.has_prop("baz")
    assert el.props["baz"] == "ZAB"
    assert el.prop_default("baz") == "BAZ"
    assert not el.is_prop_default("baz")
    assert el.is_prop_default("baz", "BAZ")

    el.unset_prop("baz")
    assert el.prop("baz") == "BAZ"
    assert el.baz == "BAZ"
    assert el.props["baz"] == "BAZ"
    assert el.has_prop("baz")
    assert el.prop_default("baz") == "BAZ"
    assert el.is_prop_default("baz")



def test_doctype():
    assert str(<!DOCTYPE html>) == '<!DOCTYPE html>'
    assert str(<Doctype doctype=html/>) == '<!DOCTYPE html>'


def test_cdata():
    assert str(<div><![CDATA[Testing Data here]]></div>) == '<div><![CDATA[Testing Data here]]></div>'
    assert str(<div><CData cdata="Testing Data here"/></div>) == '<div><![CDATA[Testing Data here]]></div>'


def test_callable_to_string():

    class Foo(Base):

        def render_qux(self):
            return "qux"

        def _to_list(self, acc):
            self._render_children_to_list(acc)
            acc.append(self.render_qux)

    def render_bar():
        return 'bar'

    assert str(<Foo>foo{render_bar}baz</Foo>) == "foobarbazqux"
