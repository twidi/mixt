# coding: mixt
import pytest

from mixt.codec.register import pyxl_decode
from mixt.exceptions import ParserError


def test_malformed_if():
    with pytest.raises(ParserError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}">foo</if>
                this is incorrect!
                <else>bar</else>
            </Fragment>""")

def test_invalid_if_prop():
    with pytest.raises(ParserError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}" foo="bar">foo</if>
            </Fragment>""")

def test_missing_if_cond():
    with pytest.raises(ParserError):
        pyxl_decode(b"""
            <Fragment>
                <if>foo</if>
            </Fragment>""")

    with pytest.raises(ParserError):
        pyxl_decode(b"""
            <Fragment>
                <if foo="bar">foo</if>
            </Fragment>""")

def test_multiple_else():
    with pytest.raises(ParserError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}">foo</if>
                <else>bar</else>
                <else>baz</else>
             </Fragment>""")


def test_nested_else():
    with pytest.raises(ParserError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}">foo</if>
                <else><else>bar</else></else>
            </Fragment>""")

def test_else_with_prop():
    with pytest.raises(ParserError):
        pyxl_decode(b"""
            <Fragment>
                <if cond="{true}">foo</if>
                <else foo="bar">bar</else>
            </Fragment>""")
