# coding: mixt
from mixt import html


def test1():
    assert str(<Fragment><!-- comment here --></Fragment>) == ""


def test2():
    assert str(<Fragment><!-- comment-here --></Fragment>) == ""
