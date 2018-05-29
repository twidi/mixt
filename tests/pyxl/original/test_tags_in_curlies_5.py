# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<frag> {'<img src="{cond}" />'} </frag>) == """ &lt;img src=&quot;{cond}&quot; /&gt; """
