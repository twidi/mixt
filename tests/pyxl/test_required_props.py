# coding: mixt

"""Ensure that required proptypes are correctly checked."""

import pytest
from mixt import html
from mixt.internal.base import Base
from mixt.exceptions import PyxlException
from mixt.proptypes import NotProvided, Required

from typing import *


class DummyBase(Base):
    def _to_list(self, acc):
        pass


def test_prop_optional_by_default():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    (<Foo />)

def test_prop_required_ok_if_passed():
    class Foo(DummyBase):
        class PropTypes:
            value: Required[str]

    (<Foo value="foo" />)

def test_prop_required_fail_if_not_passed():
    class Foo(DummyBase):
        class PropTypes:
            value: Required[str]

    with pytest.raises(PyxlException):
        <Foo />

def test_complex_prop_required():
    class Foo(DummyBase):
        class PropTypes:
            value: Required[Union[int, float]]

    with pytest.raises(PyxlException):
        <Foo />

    with pytest.raises(PyxlException):
        <Foo value="foo" />

    (<Foo value={1} />)

def test_required_prop_cannot_have_default():
    with pytest.raises(PyxlException):
        class Foo(DummyBase):
            class PropTypes:
                value: Required[str] = "foo"

    class Foo(DummyBase):
        class PropTypes:
            value: Required[str] = NotProvided
