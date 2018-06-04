# coding: mixt
from mixt import html
def test():
    assert str(<Fragment>{'<div> foobar </div>'}</Fragment>) == """&lt;div&gt; foobar &lt;/div&gt;"""
