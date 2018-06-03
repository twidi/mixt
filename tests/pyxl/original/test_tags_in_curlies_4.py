# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<Fragment>{'<div class="foo"> foobar </div>'}</Fragment>) == """&lt;div class=&quot;foo&quot;&gt; foobar &lt;/div&gt;"""
