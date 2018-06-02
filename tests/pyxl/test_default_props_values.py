# coding: mixt

"""Ensure that complex proptypes are correctly validated."""

import pytest
from mixt.pyxl import html
from mixt.pyxl.base import Base, PyxlException, Choices, NotProvided, Mandatory

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

def test_default_are_returned():
    class Foo(DummyBase):
        class PropTypes:
            value1: int
            value2: str = "foo"
            value3: Choices = [1, 2, 3]
            value4: str = NotProvided

    assert (<Foo />.props) == {'value2': 'foo', 'value3': 1}
    assert (<Foo value1={123} />.props) == {'value1': 123, 'value2': 'foo', 'value3': 1}
    assert (<Foo value1={123} value2="bar" />.props) == {'value1': 123, 'value2': 'bar', 'value3': 1}
    assert (<Foo value1={123} value2="bar" value3={2} />.props) == {'value1': 123, 'value2': 'bar', 'value3': 2}
    assert (<Foo value1={123} value2="bar" value3={2} value4="baz" />.props) == {'value1': 123, 'value2': 'bar', 'value3': 2, 'value4': 'baz'}

def test_default_cannot_be_mandatory():
    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Mandatory[str] = "foo"

    class Foo(DummyBase):
        class PropTypes:
            value: Mandatory[str] = NotProvided
