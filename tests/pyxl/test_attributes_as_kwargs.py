# coding: mixt

"""Ensure we can pass attributes to tags as kwargs."""

import pytest
from mixt.pyxl import html
from mixt.pyxl.codec.parser import ParseError
from mixt.pyxl.codec.register import pyxl_decode


def test_single_valid_kwargs():
    kwargs = {'type': 'checkbox', 'value': 'on'}

    # alone
    assert str(<input {**kwargs}/>) == '<input type="checkbox" value="on" />'

    # after attribute without value
    assert str(<input required {**kwargs}/>) == '<input required type="checkbox" value="on" />'
    # after attribute with value
    assert str(<input name="foo" {**kwargs}/>) == '<input name="foo" type="checkbox" value="on" />'
    # after attribute with python value
    assert str(<input name={"foo"} {**kwargs}/>) == '<input name="foo" type="checkbox" value="on" />'

    # before attribute without value
    assert str(<input {**kwargs} required/>) == '<input required type="checkbox" value="on" />'
    # before attribute with value
    assert str(<input {**kwargs} name="foo"/>) == '<input name="foo" type="checkbox" value="on" />'
    # before attribute with python value
    assert str(<input {**kwargs} name={"foo"} />) == '<input name="foo" type="checkbox" value="on" />'

def test_many_valid_kwargs():
    kwargs1 = {'type': 'checkbox'}
    kwargs2 = {'value': 'on'}
    assert str(<input
        name={"foo"}
        {**kwargs1}
        required="required"
        {**kwargs2}
        placeholder="bar"
    />) == '<input name="foo" required placeholder="bar" type="checkbox" value="on" />'

def test_invalid_duplicate_arguments():
    kwargs = {'type': 'checkbox', 'value': 'on'}

    with pytest.raises(TypeError):
        <input {**kwargs} value="off" />


def test_invalid_python():
    with pytest.raises(ParseError):
        pyxl_decode(b'<input {"foo"} />')
