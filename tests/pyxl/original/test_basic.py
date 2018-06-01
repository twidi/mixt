# coding: mixt

import pytest

from mixt.pyxl import html
from mixt.pyxl.base import PyxlException, Base, Choices

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

def test_decl():
    assert (str(<script><![CDATA[<div><div>]]></script>)
        == '<script><![CDATA[<div><div>]]></script>')

def test_enum_attrs():
    class Foo(Base):
        class Attrs:
            value: Choices = ['a', 'b']

        def _to_list(self, l):
            pass

    assert (<Foo />.attr('value')) == 'a'
    assert (<Foo />.value) == 'a'
    assert (<Foo value="b" />.attr('value')) == 'b'
    assert (<Foo value="b" />.value) == 'b'

    with pytest.raises(PyxlException):
        <Foo value="c" />

    class Bar(Base):
        class Attrs:
            value: Choices = ['a', None, 'b']

        def _to_list(self, l):
            pass

    with pytest.raises(PyxlException):
        <Bar />.attr('value')

    with pytest.raises(PyxlException):
        <Bar />.value

    class Baz(Base):
        class Attrs:
            value: Choices = [None, 'a', 'b']

        def _to_list(self, l):
            pass

    assert (<Baz />.value) == None


def test_special_attributes():
    class Foo(html.HtmlElement):
        class Attrs:
            _def: str
            foo_bar__baz: str

    # using "html" type attribute names
    tag = <Foo def='fed' foo-bar:baz='qux' />
    assert str(tag) == '<foo def="fed" foo-bar:baz="qux"></foo>'
    assert tag._def == 'fed'
    assert tag.foo_bar__baz == 'qux'

    # using "python" type attributes names
    tag = <Foo _def='fed' foo_bar__baz='qux' />
    assert str(tag) == '<foo def="fed" foo-bar:baz="qux"></foo>'
    assert tag._def == 'fed'
    assert tag.foo_bar__baz == 'qux'
