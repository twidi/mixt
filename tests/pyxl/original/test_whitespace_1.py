# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<div class="{'blah'}">
                   blah <a href="%(url)s">blah</a> blah.
               </div>) == """<div class="blah">blah <a href="%(url)s">blah</a> blah.</div>"""
