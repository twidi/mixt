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


def test_children_filtering():
    class Parent(Element): ...
    class Child(Element): ...

    el = <Parent>
        <div id=0></div>
        <div class="foo" id=1/>
        <span class="foo" id=2/>
        <div class="bar" id=3><div class="foo" id=3.1/></div>
        <Child class="bar" id=4 />
    </Parent>

    assert [child.__tag__ for child in el.children()] == ['div', 'div', 'span', 'div', 'Child']

    def get_ids(children):
        return [child.get_id() for child in children]

    assert get_ids(el.children('.foo')) == ['1', '2']
    assert get_ids(el.children('.bar')) == ['3', '4']
    assert get_ids(el.children('.baz')) == []

    assert get_ids(el.children('.foo', exclude=True)) == ['0', '3', '4']
    assert get_ids(el.children('.bar', exclude=True)) == ['0', '1', '2']
    assert get_ids(el.children('.baz', exclude=True)) == ['0', '1', '2', '3', '4']

    assert get_ids(el.children('#1')) == ['1']
    assert get_ids(el.children('#4')) == ['4']
    assert get_ids(el.children('#1000')) == []

    assert get_ids(el.children('#1', exclude=True)) == ['0', '2', '3', '4']
    assert get_ids(el.children('#1000', exclude=True)) == ['0', '1', '2', '3', '4']

    assert get_ids(el.children('span')) == ['2']
    assert get_ids(el.children('Child')) == ['4']

    assert get_ids(el.children('span', exclude=True)) == ['0', '1', '3', '4']
    assert get_ids(el.children('Child', exclude=True)) == ['0', '1', '2', '3']


def test_pre_post_render():

    class Node(Element):
        def render(self):
            return <div class="node"/>

        def prerender(self):
            self.add_class('keep remove')

        def postrender(self, element):
            self.set_prop('class', ' '.join([c for c in self.get_class().split() if c != 'remove']))

    assert str(<Node class="render"/>) == '<div class="node render keep"></div>'


def test_cached_rendering():
    class Node(Element):
        class PropTypes:
            number: int = 0

        def render(self):
            return <div data-number={self.number}/>

    el = <Node />
    assert str(el) == '<div data-number="0"></div>'

    el.set_prop('number', 1)
    assert str(el) == '<div data-number="0"></div>'
