# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<frag><img src="barbaz{'foo'}" /></frag>) == """<img src="barbazfoo" />"""
