# coding: mixt

"""Ensure that elements work correctly."""

from mixt import html
from mixt.element import Element


def test_auto_display_name():
    assert html.Div.__display_name__ == "div"
    assert (<div />).__display_name__ == "div"

    class Foo(Element):
        pass

    assert Foo.__display_name__ == "Foo"
    assert (<Foo />).__display_name__ == "Foo"


def test_force_display_name():
    class Foo(Element):
        __display_name__ = "TheFoo"

    assert Foo.__display_name__ == "TheFoo"
    assert (<Foo />).__display_name__ == "TheFoo"


def test_display_name_is_not_inherited():
    class Foo(Element):
        __display_name__ = "TheFoo"


    class Bar(Foo):
        pass

    assert Foo.__display_name__ == "TheFoo"
    assert (<Foo />).__display_name__ == "TheFoo"

    assert Bar.__display_name__ == "Bar"
    assert (<Bar />).__display_name__ == "Bar"


def test_class_names_are_inherited_for_single_child():
    class Child(Element):
        def render(self, context):
            return <div class="div" />

    class Parent(Element):
        def render(self, context):
            return <Child class="child" />

    assert str(<Parent class="parent" />) == '<div class="div child parent"></div>'


def test_class_names_are_not_inherited_to_html_grand_children():
    class Parent(Element):
        def render(self, context):
            return <div class="level0"><div class="level1">{self.children()}</div></div>

    assert str(<Parent class="parent"><div class="level2"/></Parent>) == (
        '<div class="level0 parent"><div class="level1"><div class="level2"></div></div></div>')


def test_class_names_are_not_inherited_for_many_children():

    class Child(Element):
        def render(self, context):
            return <Fragment><div class="div1" /><div class="div2" /></Fragment>

    class Parent(Element):
        def render(self, context):
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

    assert get_ids(el.children(Element)) == ['4']
    assert get_ids(el.children(Child)) == ['4']
    assert get_ids(el.children(Element, exclude=True)) == ['0', '1', '2', '3']
    assert get_ids(el.children(Child, exclude=True)) == ['0', '1', '2', '3']


def test_pre_post_render():

    class Node(Element):
        def render(self, context):
            return <div class="node"/>

        def prerender(self, context):
            self.add_class('keep remove')

        def postrender(self, element, context):
            self.remove_class('remove')

    assert str(<Node class="render"/>) == '<div class="node render keep"></div>'


def test_cached_rendering():
    class Node(Element):
        class PropTypes:
            number: int = 0

        def render(self, context):
            return <div data-number={self.number}/>

    el = <Node />
    assert str(el) == '<div data-number="0"></div>'

    el.set_prop('number', 1)
    assert str(el) == '<div data-number="0"></div>'


def test_auto_fragment():
    class Node(Element):
        def render(self, context):
            return (
                <div id=1/>,
                <div id=2/>,
            )

    assert str(<Node class="ignored" />) == '<div id="1"></div><div id="2"></div>'


def test_classes_can_be_changed():
    class Node(Element):
        def render(self, context):
            return <div class="div divremoved" />

        def prerender(self, context):
            self.prepend_class('prepended removed')

        def postrender(self, element, context):
            self.append_class('appended')
            self.remove_class('removed')
            element.append_class('divappended')
            element.remove_class('divremoved')

    assert str(<Node class="node" />) == '<div class="div divappended prepended node appended"></div>'


def test_element_can_be_simple_function():

    def Bolding():
        # use lambda to manage children
        return lambda *children: <b>{children}</b>

    def Hello():
        # no html at all
        return 'Hello'

    def Greeting(first_name, last_name, title):
        # accept props (but no proptypes checks)
        return <div title={title}><Hello /> <Bolding>{first_name} {last_name}</Bolding></div>

    assert str(
           <Greeting title="Greetings" first_name="John" last_name="Smith" />
    ) == '<div title="Greetings">Hello <b>John Smith</b></div>'
