# coding: mixt
from mixt import html
def test():
    assert str(<Fragment>{<br /> if True else <div></div>}</Fragment>) == '''<br />'''
