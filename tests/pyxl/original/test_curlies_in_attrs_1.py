# coding: mixt
from mixt import html
def test():
    # kannan thinks this should be different
    assert str(<Fragment><img src="{'foo'}" /></Fragment>) == """<img src="foo" />"""
