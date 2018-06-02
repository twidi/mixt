# coding: mixt

"""Ensure that complex proptypes are correctly validated."""

import pytest
from mixt.pyxl import html
from mixt.pyxl.base import Base, PyxlException

from typing import *


class DummyBase(Base):
    def _to_list(self, l):
        pass


def test_no_default_value():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    with pytest.raises(AttributeError):
        <Foo />.value

def test_valid_default_value_simple_type():
    class Foo(DummyBase):
        class PropTypes:
            value: str = "foo"

    assert((<Foo />.value) == "foo")

def test_invalid_default_value_simple_type():
    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: str = 123

def test_valid_default_value_complex_type():
    class Foo(DummyBase):
        class PropTypes:
            value: Union[int, float] = 123

    assert (<Foo />.value) == 123

def test_invalid_default_value_complex_type():
    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Union[int, float] = "foo"
