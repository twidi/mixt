# coding: mixt

import pytest

from mixt import html
from mixt.internal.html import HtmlElement
from mixt.pyxl.base import PyxlException, Base, Choices, DefaultChoices, NotProvided


class DummyBase(Base):
    def _to_list(self, l):
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

    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices

    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices = []

    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices = 'foo'

    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Choices = 123

    class Foo(DummyBase):
        class PropTypes:
            value: Choices = ['a', 'b']

    with pytest.raises(AttributeError):
        <Foo />.prop('value')

    with pytest.raises(AttributeError):
        <Foo />.value

    assert (<Foo value="b" />.prop('value')) == 'b'
    assert (<Foo value="b" />.value) == 'b'

    with pytest.raises(PyxlException):
        <Foo value="c" />

    with pytest.raises(PyxlException):
        <Foo value={None} />

    with pytest.raises(AttributeError):
        <Foo value={NotProvided} />.value

    class Bar(DummyBase):
        class PropTypes:
            value: DefaultChoices = ['a', 'b']

    assert (<Bar />.prop('value')) == 'a'
    assert (<Bar />.value) == 'a'
    assert (<Bar value="b" />.prop('value')) == 'b'
    assert (<Bar value="b" />.value) == 'b'

    with pytest.raises(PyxlException):
        <Bar value="c" />

    with pytest.raises(PyxlException):
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
    assert tag._def == 'fed'
    assert tag.foo_bar__baz == 'qux'

    # using "python" type props names
    tag = <Foo _def='fed' foo_bar__baz='qux' />
    assert str(tag) == '<foo def="fed" foo-bar:baz="qux"></foo>'
    assert tag._def == 'fed'
    assert tag.foo_bar__baz == 'qux'


def test_doctype():
    assert str(<!DOCTYPE html>) == '<!DOCTYPE html>'
    assert str(<Doctype doctype=html/>) == '<!DOCTYPE html>'

def test_cdata():
    assert str(<div><![CDATA[Testing Data here]]></div>) == '<div><![CDATA[Testing Data here]]></div>'
    assert str(<div><CData cdata="Testing Data here"/></div>) == '<div><![CDATA[Testing Data here]]></div>'
