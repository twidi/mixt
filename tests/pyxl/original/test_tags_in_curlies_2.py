# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<frag>{'<img src="foo" />'}</frag>) == """&lt;img src=&quot;foo&quot; /&gt;"""
