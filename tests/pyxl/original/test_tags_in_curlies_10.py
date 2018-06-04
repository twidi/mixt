# coding: mixt
from mixt import html
def test():
    assert str(<Fragment>{<br /> if False else <div></div>}</Fragment>) == '''<div></div>'''
