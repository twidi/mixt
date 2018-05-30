# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<Fragment><img src="barbaz{'foo'}" /></Fragment>) == """<img src="barbazfoo" />"""
