# coding: mixt
from mixt import html


def test1():
    # kannan thinks this should be different
    assert str(<Fragment><img src="{'foo'}" /></Fragment>) == """<img src="foo" />"""


def test2():
    assert str(<Fragment><img src="barbaz{'foo'}" /></Fragment>) == """<img src="barbazfoo" />"""
