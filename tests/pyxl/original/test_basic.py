# coding: mixt
import pytest

from mixt.pyxl import html
from mixt.pyxl.base import PyxlException, Base

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
        __attrs__ = {
            'value': ['a', 'b'],
        }

        def _to_list(self, l):
            pass

    assert (<Foo />.attr('value')) == 'a'
    assert (<Foo />.value) == 'a'
    assert (<Foo value="b" />.attr('value')) == 'b'
    assert (<Foo value="b" />.value) == 'b'

    with pytest.raises(PyxlException):
        <Foo value="c" />

    class Bar(Base):
        __attrs__ = {
            'value': ['a', None, 'b'],
        }

        def _to_list(self, l):
            pass

    with pytest.raises(PyxlException):
        <Bar />.attr('value')

    with pytest.raises(PyxlException):
        <Bar />.value

    class Baz(Base):
        __attrs__ = {
            'value': [None, 'a', 'b'],
        }

        def _to_list(self, l):
            pass

    assert (<Baz />.value) == None
