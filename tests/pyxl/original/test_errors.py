# coding: mixt
import pytest

from mixt.pyxl.codec.register import pyxl_decode
from mixt.pyxl.codec.parser import ParseError

def test_malformed_if():
    with pytest.raises(ParseError):
        pyxl_decode(b"""
            <frag>
                <if cond="{true}">foo</if>
                this is incorrect!
                <else>bar</else>
            </frag>""")

def test_multiple_else():
    with pytest.raises(ParseError):
        pyxl_decode(b"""
            <frag>
                <if cond="{true}">foo</if>
                <else>bar</else>
                <else>baz</else>
             </frag>""")

def test_nested_else():
    with pytest.raises(ParseError):
        pyxl_decode(b"""
            <frag>
                <if cond="{true}">foo</if>
                <else><else>bar</else></else>
            </frag>""")
