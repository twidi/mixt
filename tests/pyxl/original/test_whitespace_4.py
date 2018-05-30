# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<div class="{ 'foo' }">foo</div>) == '<div class="foo">foo</div>'
