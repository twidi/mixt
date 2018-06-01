# coding: mixt

"""Ensure that the space before the ``/`` character is not mandatory"""

from mixt.pyxl import html
from mixt.pyxl.element import Element


def test_normal_tag_without_attributes():
    assert str(<button />) == '<button></button>'
    assert str(<button/>) == '<button></button>'


def test_normal_tag_with_attributes():
    assert str(<button name="foo" />) == '<button name="foo"></button>'
    assert str(<button name="foo"/>) == '<button name="foo"></button>'


def test_nochild_tag_without_attributes():
    assert str(<link />) == '<link />'
    assert str(<link/>) == '<link />'


def test_nochild_tag_with_attributes():
    assert str(<link rel="foo" />) == '<link rel="foo" />'
    assert str(<link rel="foo"/>) == '<link rel="foo" />'


def test_new_element_without_attributes():
    class Foo(Element):

        def render(self):
            return <div data-name="foo"/>

    assert str(<Foo />) == '<div data-name="foo"></div>'
    assert str(<Foo/>) == '<div data-name="foo"></div>'


def test_new_element_with_attributes():
    class Foo(Element):
        class Attrs:
            name: str

        def render(self):
            return <div data-name="{self.name}"/>

    assert str(<Foo name="foo" />) == '<div data-name="foo"></div>'
    assert str(<Foo name="foo"/>) == '<div data-name="foo"></div>'

def test_with_python_value_at_the_end():
    assert str(<button name={"foo"} />) == '<button name="foo"></button>'
    assert str(<button name={"foo"}/>) == '<button name="foo"></button>'
    assert str(<button name={"foo"} ></button>) == '<button name="foo"></button>'
    assert str(<button name={"foo"}></button>) == '<button name="foo"></button>'

def test_with_python_kwargs_at_the_end():
    kwargs = {'name': 'foo'}
    assert str(<button {**kwargs} />) == '<button name="foo"></button>'
    assert str(<button {**kwargs}/>) == '<button name="foo"></button>'
    assert str(<button {**kwargs} ></button>) == '<button name="foo"></button>'
    assert str(<button {**kwargs}></button>) == '<button name="foo"></button>'

