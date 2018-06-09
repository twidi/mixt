# coding: mixt

"""Ensure that boolean attributes are correctly managed."""

import pytest
from mixt import html
from mixt.exceptions import InvalidPropBoolError


def test_without_value():
    assert str(<textarea readonly />) == '<textarea readonly></textarea>'
    assert str(<textarea readonly/>) == '<textarea readonly></textarea>'

def test_with_empty_value():
    assert str(<textarea readonly="" />) == '<textarea readonly></textarea>'

def test_with_name_as_value():
    assert str(<textarea readonly="readonly" />) == '<textarea readonly></textarea>'

def test_with_boolean_true_as_value():
    assert str(<textarea readonly={True} />) == '<textarea readonly></textarea>'

def test_with_string_true_as_value():
    assert str(<textarea readonly="true" />) == '<textarea readonly></textarea>'

def test_with_boolean_false_as_value():
    assert str(<textarea readonly={False} />) == '<textarea></textarea>'

def test_with_string_false_as_value():
    assert str(<textarea readonly="false" />) == '<textarea></textarea>'

def test_with_other_thing_as_value():
    with pytest.raises(InvalidPropBoolError):
        <textarea readonly="other" />

    with pytest.raises(InvalidPropBoolError):
        <textarea readonly=123 />

    with pytest.raises(InvalidPropBoolError):
        <textarea readonly={"other"} />

    with pytest.raises(InvalidPropBoolError):
        <textarea readonly={123} />
