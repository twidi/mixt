# coding: mixt

"""Ensure that complex proptypes are correctly validated."""

import pytest
from mixt import html
from mixt.internal.base import Base
from mixt.exceptions import InvalidPropNameError, InvalidPropValueError, UnsetPropError
from mixt.proptypes import NotProvided

from typing import *


class DummyBase(Base):
    def _to_list(self, acc):
        pass


def test_simple_union():

    class Foo(DummyBase):
        class PropTypes:
            value: Union[float, int]

    assert (<Foo value={1} />.value) == 1
    assert (<Foo value={1.1} />.value) == 1.1
    assert (<Foo value="1" />.value) == 1
    assert (<Foo value="1.1" />.value) == 1.1
    assert (<Foo value=1 />.value) == 1
    assert (<Foo value=1.1 />.value) == 1.1

    with pytest.raises(InvalidPropValueError):
        <Foo value={"foo"} />

    with pytest.raises(InvalidPropValueError):
        <Foo value="foo" />

    with pytest.raises(InvalidPropValueError):
        <Foo value={None} />

    with pytest.raises(AttributeError):
        <Foo value={NotProvided} />.value

    with pytest.raises(UnsetPropError):
        <Foo value={NotProvided} />.value


def test_user_class():

    class User: ...

    class Hero(User): ...

    class Animal: ...

    class Foo(DummyBase):
        class PropTypes:
            user: User

    user = User()
    hero = Hero()
    animal = Animal()

    assert (<Foo user={user} />.user) == user
    assert (<Foo user={hero} />.user) == hero

    with pytest.raises(InvalidPropValueError):
        <Foo user={animal} />

    with pytest.raises(InvalidPropValueError):
        <Foo user={None} />

    with pytest.raises(AttributeError):
        <Foo user={NotProvided} />.user

    with pytest.raises(InvalidPropValueError):
        <Foo user="john" />



def test_complex_union():

    class User: ...

    class Hero(User): ...

    class Animal: ...


    class Foo(DummyBase):
        class PropTypes:
            user: Union[User, str]

    user = User()
    hero = Hero()
    animal = Animal()

    assert (<Foo user={user} />.user) == user
    assert (<Foo user="john" />.user) == "john"
    assert (<Foo user={"john"} />.user) == "john"

    with pytest.raises(InvalidPropValueError):
        <Foo user={animal} />

    with pytest.raises(InvalidPropValueError):
        <Foo user={None} />

    with pytest.raises(UnsetPropError):
        <Foo user={NotProvided} />.user

    with pytest.raises(InvalidPropValueError):
        <Foo user={123} />


def test_data_and_aria_are_not_validated():
    el = <div data-string="foo" aria-number={123} data-complex={{'foo': 123}} />
    assert el.data_string == 'foo'
    assert el.aria_number == 123
    assert el.data_complex == {'foo': 123}

    assert str(el) == '<div data-string="foo" aria-number="123" data-complex="{\'foo\': 123}"></div>'


def test_ints_can_be_passed_unquoted_for_string_props():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    assert (<Foo value=1 />.value) == '1'
    assert (<Foo value={1} />.value) == '1'

def test_bools_cannot_be_passed_unquoted_for_string_props():
    # important because bools are ints
    class Foo(DummyBase):
        class PropTypes:
            value: str

    with pytest.raises(InvalidPropValueError):
        <Foo value=True />
    with pytest.raises(InvalidPropValueError):
        <Foo value={True} />


def test_floats_can_be_passed_unquoted_for_string_props():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    assert (<Foo value=1.1 />.value) == '1.1'
    assert (<Foo value={1.1} />.value) == '1.1'


def test_int_props_can_be_passed_unquoted_():
    class Foo(DummyBase):
        class PropTypes:
            value: int

    assert (<Foo value=1 />.value) == 1
    assert (<Foo value={1} />.value) == 1


def test_float_props_can_be_passed_unquoted():
    class Foo(DummyBase):
        class PropTypes:
            value: float

    assert (<Foo value=1.1 />.value) == 1.1
    assert (<Foo value={1.1} />.value) == 1.1


def test_none_can_be_passed_unquoted():
    class Foo(DummyBase):
        class PropTypes:
            value: Union[int, None]

    assert (<Foo value=None />.value) is None


def test_none_can_be_passed_quoted():
    class Foo(DummyBase):
        class PropTypes:
            value: Union[int, None]

    assert (<Foo value="None" />.value) is None


def test_none_can_only_be_used_as_strings_via_python():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    with pytest.raises(InvalidPropValueError):
        <Foo value=None />
    with pytest.raises(InvalidPropValueError):
        <Foo value="None" />
    with pytest.raises(InvalidPropValueError):
        <Foo value={None} />

    assert (<Foo value={"None"} />.value) == 'None'


def test_bools_can_be_passed_unquoted():
    class Foo(DummyBase):
        class PropTypes:
            value: bool

    assert (<Foo value=False />.value) is False
    assert (<Foo value=True />.value) is True


def test_bools_can_be_passed_quoted():
    class Foo(DummyBase):
        class PropTypes:
            value: bool

    assert (<Foo value="False" />.value) is False
    assert (<Foo value="True" />.value) is True


def test_notprovided_can_be_passed_unquoted():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    with pytest.raises(UnsetPropError):
        <Foo value=NotProvided />.value


def test_bools_can_only_be_used_as_strings_via_python():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    with pytest.raises(InvalidPropValueError):
        <Foo value=True />
    with pytest.raises(InvalidPropValueError):
        <Foo value="True" />
    with pytest.raises(InvalidPropValueError):
        <Foo value={True} />

    assert (<Foo value={"True"} />.value) == 'True'


def test_notprovided_can_be_passed_quoted():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    with pytest.raises(UnsetPropError):
        <Foo value="NotProvided" />.value


def test_notprovided_can_only_be_used_as_strings_via_python():
    class Foo(DummyBase):
        class PropTypes:
            value: str

    with pytest.raises(UnsetPropError):
        <Foo value=NotProvided />.value
    with pytest.raises(UnsetPropError):
        <Foo value="NotProvided" />.value
    with pytest.raises(UnsetPropError):
        <Foo value={NotProvided} />.value

    assert (<Foo value={"NotProvided"} />.value) == 'NotProvided'


def test_exclude():
    class Foo(DummyBase):
        class PropTypes:
            val1: str
            val2: str

    class Bar(DummyBase):
        class PropTypes(Foo.PropTypes):
            __exclude__ = {'val1'}

    with pytest.raises(InvalidPropNameError):
        <Bar val1="bar" />

    (<Bar val2="bar" />)
