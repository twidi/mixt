# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<div class="{'foo'} {'bar'}"></div>) == '<div class="foo bar"></div>'
