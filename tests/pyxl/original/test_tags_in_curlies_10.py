# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<Fragment>{<br /> if False else <div></div>}</Fragment>) == '''<div></div>'''
