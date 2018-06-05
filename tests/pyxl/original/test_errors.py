# coding: mixt
import pytest

from mixt.codec.register import pyxl_decode
from mixt.codec.parser import ParseError


def test_malformed_if():
    with pytest.raises(ParseError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}">foo</if>
                this is incorrect!
                <else>bar</else>
            </Fragment>""")


def test_multiple_else():
    with pytest.raises(ParseError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}">foo</if>
                <else>bar</else>
                <else>baz</else>
             </Fragment>""")


def test_nested_else():
    with pytest.raises(ParseError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}">foo</if>
                <else><else>bar</else></else>
            </Fragment>""")
