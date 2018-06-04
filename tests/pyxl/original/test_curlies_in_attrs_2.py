# coding: mixt
from mixt import html
def test():
    assert str(<Fragment><img src="barbaz{'foo'}" /></Fragment>) == """<img src="barbazfoo" />"""
