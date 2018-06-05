# coding: mixt
from mixt import html


def test():
    assert str(<div cLaSs="foo"></div>) == '<div class="foo"></div>'
