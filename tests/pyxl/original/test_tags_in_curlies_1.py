# coding: mixt
from mixt import html
def test():
    assert str(<Fragment>{'<br />'}</Fragment>) == """&lt;br /&gt;"""
