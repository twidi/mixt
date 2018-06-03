# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<Fragment>{'<img src="foo" />'}</Fragment>) == """&lt;img src=&quot;foo&quot; /&gt;"""
