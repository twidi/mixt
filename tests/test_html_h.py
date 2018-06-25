# coding: mixt

import pytest

from mixt import html
from mixt.exceptions import InvalidPropNameError


def test_normal_h():
    assert str(<h3>foo</h3>) == '<h3>foo</h3>'


def test_normal_h_with_level():
    with pytest.raises(InvalidPropNameError):
        <h3 level=3>foo</h3>

    with pytest.raises(InvalidPropNameError):
        <h3 level=4>foo</h3>


def test_h_tag():
    assert str(<h level=3>foo</h>) == '<h3>foo</h3>'
