# coding: mixt

import pytest

from mixt.pyxl import html
from mixt.pyxl.base import PyxlException


def test_using_subclass():
    assert str(<itext maxlength={3} />) == '<input type="text" maxlength="3" />'

def test_using_subclass_with_type_fails():
    with pytest.raises(PyxlException):
        <itext type="number" maxlength={3} />

    with pytest.raises(PyxlException):
        <itext type="text" maxlength={3} />

def test_using_subclass_with_invalid_prop_fails():
    with pytest.raises(PyxlException):
        <itext step={3} />

def test_using_normal_input_returns_subclass_instance():
    el = <input type="text" maxlength={3} />
    assert isinstance(el, html.InputText)

def test_using_normal_input_with_invalid_prop_fails():
    with pytest.raises(PyxlException):
        <input type="text" step={3} />
