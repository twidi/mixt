# coding: mixt
from mixt.pyxl import html
def test():
    # kannan thinks this should be different
    assert str(<Fragment><img src="{'foo'}" /></Fragment>) == """<img src="foo" />"""
