# coding: mixt

"""Ensure that dev-mode can be toggled and does not validate data if off."""
from typing import Union

import pytest
from mixt.internal.base import Base
from mixt.exceptions import PyxlException
from mixt.internal.proptypes import BasePropTypes as PropTypes
from mixt.internal.dev_mode import set_dev_mode, unset_dev_mode, override_dev_mode, in_dev_mode
from mixt.proptypes import Choices


class DummyBase(Base):
    def _to_list(self, l):
        pass


def test_proptypes_default_dev_mode_is_true():
    assert PropTypes.__in_dev_mode__()


def test_proptypes_set_dev_mode_toggle():
    assert PropTypes.__in_dev_mode__()
    try:

        PropTypes.__unset_dev_mode__()
        assert not PropTypes.__in_dev_mode__()
        PropTypes.__unset_dev_mode__()
        assert not PropTypes.__in_dev_mode__()

        PropTypes.__set_dev_mode__()
        assert PropTypes.__in_dev_mode__()
        PropTypes.__set_dev_mode__()
        assert PropTypes.__in_dev_mode__()

        PropTypes.__set_dev_mode__(False)
        assert not PropTypes.__in_dev_mode__()
        PropTypes.__set_dev_mode__(False)
        assert not PropTypes.__in_dev_mode__()

        PropTypes.__set_dev_mode__(True)
        assert PropTypes.__in_dev_mode__()
        PropTypes.__set_dev_mode__(True)
        assert PropTypes.__in_dev_mode__()

    finally:
        PropTypes.__dev_mode__ = True  # force restore the normal state


def test_proptypes_context_manager():
    assert PropTypes.__in_dev_mode__()

    try:
        with PropTypes.__override_dev_mode__(False):
            assert not PropTypes.__in_dev_mode__()
        assert PropTypes.__in_dev_mode__()

        PropTypes.__set_dev_mode__(False)

        with PropTypes.__override_dev_mode__(False):
            assert not PropTypes.__in_dev_mode__()
        assert not PropTypes.__in_dev_mode__()

        with PropTypes.__override_dev_mode__(True):
            assert PropTypes.__in_dev_mode__()
        assert not PropTypes.__in_dev_mode__()

        PropTypes.__set_dev_mode__(True)

        with PropTypes.__override_dev_mode__(True):
            assert PropTypes.__in_dev_mode__()
        assert PropTypes.__in_dev_mode__()

    finally:
        PropTypes.__dev_mode__ = True  # force restore the normal state


def test_global_default_dev_mode_is_true():
    assert in_dev_mode()


def test_global_set_dev_mode_toggle():
    assert in_dev_mode()
    try:

        unset_dev_mode()
        assert not in_dev_mode()
        unset_dev_mode()
        assert not in_dev_mode()

        set_dev_mode()
        assert in_dev_mode()
        set_dev_mode()
        assert in_dev_mode()

        set_dev_mode(False)
        assert not in_dev_mode()
        set_dev_mode(False)
        assert not in_dev_mode()

        set_dev_mode(True)
        assert in_dev_mode()
        set_dev_mode(True)
        assert in_dev_mode()

    finally:
        PropTypes.__dev_mode__ = True  # force restore the normal state


def test_global_context_manager():
    assert in_dev_mode()

    try:
        with override_dev_mode(False):
            assert not in_dev_mode()
        assert in_dev_mode()

        set_dev_mode(False)

        with override_dev_mode(False):
            assert not in_dev_mode()
        assert not in_dev_mode()

        with override_dev_mode(True):
            assert in_dev_mode()
        assert not in_dev_mode()

        set_dev_mode(True)

        with override_dev_mode(True):
            assert in_dev_mode()
        assert in_dev_mode()

    finally:
        PropTypes.__dev_mode__ = True  # force restore the normal state


def test_choices_are_not_checked_in_non_dev_mode():
    class Foo(DummyBase):
        class PropTypes:
            value: Choices = ['a', 'b']

    with override_dev_mode(dev_mode=False):
        assert (<Foo value='c' />.value) == 'c'

    with pytest.raises(PyxlException):
        <Foo value='c' />


def test_boolean_is_not_validated_in_non_dev_mode():
    class Foo(DummyBase):
        class PropTypes:
            value: bool

    with override_dev_mode(dev_mode=False):
        # normal behavior still works
        assert (<Foo value='value' />.value) is True
        assert (<Foo value={False} />.value) is False
        assert (<Foo value='false' />.value) is False
        # but this only works in non-dev mode
        assert (<Foo value='fake' />.value) is True
        assert (<Foo value={0} />.value) is False

    with pytest.raises(PyxlException):
        <Foo value='fake' />

    with pytest.raises(PyxlException):
        <Foo value={0} />


def test_normal_value_is_not_validated_in_non_dev_mode():
    class Foo(DummyBase):
        class PropTypes:
            value: int
            complex: Union[int, float]

    with override_dev_mode(dev_mode=False):
        assert (<Foo value='foo' />.value) == 'foo'
        assert (<Foo complex='bar' />.complex) == 'bar'

    with pytest.raises(PyxlException):
        <Foo value='foo' />

    with pytest.raises(PyxlException):
        <Foo complex='bar' />
