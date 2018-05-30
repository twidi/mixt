# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<frag>{<br /> if True else <div></div>}</frag>) == '''<br />'''
