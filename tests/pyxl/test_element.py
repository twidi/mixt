# coding: mixt

"""Ensure that elements work correctly."""

import pytest
from mixt.pyxl import html
from mixt.pyxl.element import Element


def test_class_names_are_inherited_for_single_child():
    class Child(Element):
        def render(self):
            return <div class="div" />

    class Parent(Element):
        def render(self):
            return <Child class="child" />

    assert str(<Parent class="parent" />) == '<div class="div child parent"></div>'


def test_class_names_are_not_inherited_to_html_grand_children():
    class Parent(Element):
        def render(self):
            return <div class="level0"><div class="level1">{self.children()}</div></div>

    assert str(<Parent class="parent"><div class="level2"/></Parent>) == (
        '<div class="level0 parent"><div class="level1"><div class="level2"></div></div></div>')


def test_class_names_are_not_inherited_for_many_children():

    class Child(Element):
        def render(self):
            return <Fragment><div class="div1" /><div class="div2" /></Fragment>

    class Parent(Element):
        def render(self):
            return <Child class="child" />

    assert str(<Parent class="parent" />) == '<div class="div1"></div><div class="div2"></div>'
