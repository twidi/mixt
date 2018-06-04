# coding: mixt
from mixt import html
def test():
    assert str(<Fragment> {'<img src="{cond}" />'} </Fragment>) == """ &lt;img src=&quot;{cond}&quot; /&gt; """
