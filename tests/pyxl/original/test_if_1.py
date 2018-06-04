# coding: mixt
from mixt import html

def test():
    assert str(<Fragment><if cond="{True}">true</if><else>false</else></Fragment>) == "true"
    assert str(<Fragment><if cond="{False}">true</if><else>false</else></Fragment>) == "false"
