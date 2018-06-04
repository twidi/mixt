# coding: mixt
from mixt import html
def test():
    assert str(<div class="{ 'foo' }">foo</div>) == '<div class="foo">foo</div>'
