# coding: mixt

"""Ensure that complex proptypes are correctly validated."""

import pytest
from mixt.pyxl import html
from mixt.pyxl.base import Base, PyxlException, Mandatory, NotProvided

from typing import *


class DummyBase(Base):
    def _to_list(self, l):
        pass


def test_prop_optional_by_default():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    (<Foo />)

def test_prop_mandatory_ok_if_passed():
    class Foo(DummyBase):
        class PropTypes:
            value: Mandatory[str]

    (<Foo value="foo" />)

def test_prop_mandatory_fail_if_not_passed():
    class Foo(DummyBase):
        class PropTypes:
            value: Mandatory[str]

    with pytest.raises(PyxlException):
        <Foo />

def test_complex_prop_mandatory():
    class Foo(DummyBase):
        class PropTypes:
            value: Mandatory[Union[int, float]]

    with pytest.raises(PyxlException):
        <Foo />

    with pytest.raises(PyxlException):
        <Foo value="foo" />

    (<Foo value={1} />)

def test_mandatory_prop_cannot_have_default():
    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Mandatory[str] = "foo"

    class Foo(DummyBase):
        class PropTypes:
            value: Mandatory[str] = NotProvided
