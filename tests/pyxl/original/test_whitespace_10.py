# coding: mixt
from mixt import html
def test():
    assert str(<div class="{'foo'} {'bar'}"></div>) == '<div class="foo bar"></div>'
