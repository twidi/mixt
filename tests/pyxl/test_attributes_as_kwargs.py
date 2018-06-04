# coding: mixt

"""Ensure we can pass attributes to tags as kwargs."""

import pytest
from mixt.pyxl import html
from mixt.pyxl.codec.parser import ParseError
from mixt.pyxl.codec.register import pyxl_decode


def test_single_valid_kwargs():
    kwargs = {'title': 'bar', 'autocomplete': 'on'}

    # alone
    assert str(<textarea {**kwargs}/>) == '<textarea title="bar" autocomplete="on"></textarea>'

    # after attribute without value
    assert str(<textarea required {**kwargs}/>) == '<textarea required title="bar" autocomplete="on"></textarea>'
    # after attribute with value
    assert str(<textarea name="foo" {**kwargs}/>) == '<textarea name="foo" title="bar" autocomplete="on"></textarea>'
    # after attribute with python value
    assert str(<textarea name={"foo"} {**kwargs}/>) == '<textarea name="foo" title="bar" autocomplete="on"></textarea>'

    # before attribute without value
    assert str(<textarea {**kwargs} required/>) == '<textarea required title="bar" autocomplete="on"></textarea>'
    # before attribute with value
    assert str(<textarea {**kwargs} name="foo"/>) == '<textarea name="foo" title="bar" autocomplete="on"></textarea>'
    # before attribute with python value
    assert str(<textarea {**kwargs} name={"foo"} />) == '<textarea name="foo" title="bar" autocomplete="on"></textarea>'

def test_many_valid_kwargs():
    kwargs1 = {'title': 'bar'}
    kwargs2 = {'autocomplete': 'on'}
    assert str(<textarea
        name={"foo"}
        {**kwargs1}
        required="required"
        {**kwargs2}
        placeholder="baz"
    />) == '<textarea name="foo" required placeholder="baz" title="bar" autocomplete="on"></textarea>'

def test_invalid_duplicate_arguments():
    kwargs = {'title': 'bar', 'autocomplete': 'on'}

    with pytest.raises(TypeError):
        <textarea {**kwargs} autocomplete="off" />


def test_invalid_python():
    with pytest.raises(ParseError):
        pyxl_decode(b'<textarea {"foo"} />')
