# coding: mixt
from mixt import html


def test1():
    assert str(<Fragment>Im cool # lol
</Fragment>) == """Im cool """


def test2():
    assert str(<div style="background-color: #1f75cc;"></div>) == """<div style="background-color: #1f75cc;"></div>"""


def test3():
    assert str(<div #style="display: none;"
               ></div>) == "<div></div>"
