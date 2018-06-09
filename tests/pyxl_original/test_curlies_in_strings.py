# coding: mixt
from mixt import html


def test1():
    assert str(<Fragment> '{'foobar'}' </Fragment>) == """ 'foobar' """


def test2():
    assert str(<Fragment> "{' "foobar'} </Fragment>) == ''' " &quot;foobar '''


def test3():
    assert str(<Fragment> "{' "foobar" '}" </Fragment>) == ''' " &quot;foobar&quot; " '''


def test4():
    assert str(<Fragment>"</Fragment>) + '{}' == '''"{}'''
