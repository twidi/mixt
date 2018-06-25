# coding: mixt

"""Ensure that parents are saved correctly."""

from mixt import Element, html


def test_simple_parent():
    div = <div>
        <span><br /></span>
        <span />
    </div>

    assert div.__parent__ is None
    span1, span2 = div.__children__
    assert span1.__parent__ is div
    assert span2.__parent__ is div
    br, = span1.__children__
    assert br.__parent__ is span1
    assert len(span2.__children__) == 0


def test_parent_via_fragment():
    div = <div>
        <Fragment>
            <span><br /></span>
            <span />
        </Fragment>
    </div>

    assert div.__parent__ is None
    span1, span2 = div.__children__
    assert span1.__parent__ is div
    assert span2.__parent__ is div
    br, = span1.__children__
    assert br.__parent__ is span1
    assert len(span2.__children__) == 0


def test_parent_via_encapsulated_fragments():
    div = <div>
        <Fragment>
            <Fragment>
                <Fragment>
                    <span><br /></span>
                    <span />
                </Fragment>
            </Fragment>
        </Fragment>
    </div>

    assert div.__parent__ is None
    span1, span2 = div.__children__
    assert span1.__parent__ is div
    assert span2.__parent__ is div
    br, = span1.__children__
    assert br.__parent__ is span1
    assert len(span2.__children__) == 0


def test_parent_via_encapsulated_fragments_and_siblings():
    div = <div>
        <Fragment>
            <Fragment>
                <Fragment>
                    <span><br /></span>
                    <span />
                </Fragment>
                <div />
            </Fragment>
        </Fragment>
    </div>

    assert div.__parent__ is None
    span1, span2, div2 = div.__children__
    assert span1.__parent__ is div
    assert span2.__parent__ is div
    assert div2.__parent__ is div
    br, = span1.__children__
    assert br.__parent__ is span1
    assert len(span2.__children__) == 0


def test_append_one_el_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child = <span />
    assert parent.__children__ == []
    parent.append(child)
    assert parent.__children__ == [child]
    assert parent_children is parent.__children__
    assert child.__parent__ is parent
    assert str(parent) == '<div><span></span></div>'


def test_append_one_string_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child = "foo"
    parent.append(child)
    assert parent.__children__ == [child]
    assert parent_children is parent.__children__
    assert str(parent) == '<div>foo</div>'


def test_prepend_one_el_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child = <span />
    parent.prepend(child)
    assert parent.__children__ == [child]
    assert parent_children is parent.__children__
    assert child.__parent__ is parent
    assert str(parent) == '<div><span></span></div>'


def test_prepend_one_string_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child = "foo"
    parent.prepend(child)
    assert parent.__children__ == [child]
    assert parent_children is parent.__children__
    assert str(parent) == '<div>foo</div>'


def test_remove_one_el_from_empty():
    parent = <div />
    parent_children = parent.__children__
    child = <span />
    parent.remove(child)
    assert parent.__children__ == []
    assert parent_children is parent.__children__
    assert child.__parent__ is None
    assert str(parent) == '<div></div>'


def test_remove_one_string_from_empty():
    parent = <div />
    parent_children = parent.__children__
    child = "foo"
    parent.remove(child)
    assert parent.__children__ == []
    assert parent_children is parent.__children__
    assert str(parent) == '<div></div>'


def test_append_many_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    parent.append([child1, child2])
    assert parent.__children__ == [child1, child2]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert str(parent) == '<div><span></span>foo</div>'


def test_prepend_many_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    parent.prepend([child1, child2])
    assert parent.__children__ == [child1, child2]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert str(parent) == '<div><span></span>foo</div>'


def test_remove_many_from_empty():
    parent = <div />
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    parent.remove([child1, child2])
    assert parent.__children__ == []
    assert parent_children is parent.__children__
    assert child1.__parent__ is None
    assert str(parent) == '<div></div>'


def test_append_many_levels_list_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    child3 = <br />
    parent.append([child1, [child2, child3]])
    assert parent.__children__ == [child1, child2, child3]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert child3.__parent__ is parent
    assert str(parent) == '<div><span></span>foo<br /></div>'


def test_prepend_many_levels_list_to_empty():
    parent = <div />
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    child3 = <br />
    parent.prepend([child1, [child2, child3]])
    assert parent.__children__ == [child1, child2, child3]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert child3.__parent__ is parent
    assert str(parent) == '<div><span></span>foo<br /></div>'


def test_remove_many_levels_list_from_empty():
    parent = <div />
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    child3 = <br />
    parent.remove([child1, [child2, child3]])
    assert parent.__children__ == []
    assert parent_children is parent.__children__
    assert child1.__parent__ is None
    assert str(parent) == '<div></div>'


def test_append_one_el_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child = <span />
    assert parent.__children__ == [first_child]
    parent.append(child)
    assert parent.__children__ == [first_child, child]
    assert parent_children is parent.__children__
    assert child.__parent__ is parent
    assert str(parent) == '<div><div></div><span></span></div>'


def test_append_one_string_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child = "foo"
    parent.append(child)
    assert parent.__children__ == [first_child, child]
    assert parent_children is parent.__children__
    assert str(parent) == '<div><div></div>foo</div>'


def test_prepend_one_el_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child = <span />
    parent.prepend(child)
    assert parent.__children__ == [child, first_child]
    assert parent_children is parent.__children__
    assert child.__parent__ is parent
    assert str(parent) == '<div><span></span><div></div></div>'


def test_prepend_one_string_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child = "foo"
    parent.prepend(child)
    assert parent.__children__ == [child, first_child]
    assert parent_children is parent.__children__
    assert str(parent) == '<div>foo<div></div></div>'


def test_remove_one_absent_el_from_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child = <span />
    assert parent.__children__ == [first_child]
    parent.remove(child)
    assert parent.__children__ == [first_child]
    assert parent_children is parent.__children__
    assert child.__parent__ is None
    assert str(parent) == '<div><div></div></div>'


def test_remove_one_absent_string_from_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child = "foo"
    assert parent.__children__ == [first_child]
    parent.remove(child)
    assert parent.__children__ == [first_child]
    assert parent_children is parent.__children__
    assert str(parent) == '<div><div></div></div>'


def test_remove_only_present_el_from_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    assert first_child.__parent__ is parent
    parent_children = parent.__children__
    assert parent.__children__ == [first_child]
    parent.remove(first_child)
    assert parent.__children__ == []
    assert parent_children is parent.__children__
    assert first_child.__parent__ is None
    assert str(parent) == '<div></div>'


def test_remove_only_present_string_from_non_empty():
    first_child = "foo"
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    assert parent.__children__ == [first_child]
    parent.remove(first_child)
    assert parent.__children__ == []
    assert parent_children is parent.__children__
    assert str(parent) == '<div></div>'


def test_remove_one_present_el_from_non_empty():
    first_child = <div />
    second_child = <span />
    parent = <div>{first_child}{second_child}</div>
    assert first_child.__parent__ is parent
    assert second_child.__parent__ is parent
    parent_children = parent.__children__
    assert parent.__children__ == [first_child, second_child]
    parent.remove(first_child)
    assert parent.__children__ == [second_child]
    assert parent_children is parent.__children__
    assert first_child.__parent__ is None
    assert second_child.__parent__ is parent
    assert str(parent) == '<div><span></span></div>'


def test_remove_one_present_string_from_non_empty():
    first_child = "foo"
    second_child = <span />
    parent = <div>{first_child}{second_child}</div>
    assert second_child.__parent__ is parent
    parent_children = parent.__children__
    assert parent.__children__ == [first_child, second_child]
    parent.remove(first_child)
    assert parent.__children__ == [second_child]
    assert parent_children is parent.__children__
    assert second_child.__parent__ is parent
    assert str(parent) == '<div><span></span></div>'


def test_append_many_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    parent.append([child1, child2])
    assert parent.__children__ == [first_child, child1, child2]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert str(parent) == '<div><div></div><span></span>foo</div>'


def test_prepend_many_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    parent.prepend([child1, child2])
    assert parent.__children__ == [child1, child2, first_child]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert str(parent) == '<div><span></span>foo<div></div></div>'


def test_append_many_levels_list_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    child3 = <br />
    parent.append([child1, [child2, child3]])
    assert parent.__children__ == [first_child, child1, child2, child3]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert child3.__parent__ is parent
    assert str(parent) == '<div><div></div><span></span>foo<br /></div>'


def test_prepend_many_levels_list_to_non_empty():
    first_child = <div />
    parent = <div>{first_child}</div>
    parent_children = parent.__children__
    child1 = <span />
    child2 = "foo"
    child3 = <br />
    parent.prepend([child1, [child2, child3]])
    assert parent.__children__ == [child1, child2, child3, first_child]
    assert parent_children is parent.__children__
    assert child1.__parent__ is parent
    assert child3.__parent__ is parent
    assert str(parent) == '<div><span></span>foo<br /><div></div></div>'


def test_remove_many_levels_list_from_non_empty():
    first_child = <div />
    second_child = <span />
    third_child = "foo"
    parent = <div>{first_child}{second_child}{third_child}</div>
    assert parent.__children__ == [first_child, second_child, third_child]
    parent_children = parent.__children__
    child1 = first_child
    child2 = "bar"
    child3 = <span/>
    child4 = "foo"
    parent.remove([child1, [child2, child3, [child4]]])
    assert parent.__children__ == [second_child]
    assert first_child.__parent__ is None
    assert second_child.__parent__ is parent
    assert parent_children is parent.__children__
    assert str(parent) == '<div><span></span></div>'


def test_postrender_child_element():

    class Collect(Element):
        def render(self, context):
            pass

    class Child(Element):
        def render(self, context):
            return [
                <Collect id="collect-child-{self.id}"/>,
                <div id="child-{self.id}">{self.children()}</div>
            ]

    class Parent(Element):
        def render(self, context):
            return [
                <Collect id="collect-parent-{self.id}"/>,
                <div id="parent-{self.id}">
                    {self.children()}
                    <Child id="fromparent-{self.id}">
                        <span id="fromparent-{self.id}" />
                    </Child>
                </div>,
            ]

    elements = [
        <Parent id=1>,
            <span id=span1><Child id=1 /></span>,
        </Parent>,
        <Child id=2><span id=span2 /></Child>,
        <span id=span3><span id=span4>Foo</span></span>,
    ]

    # start with a simple usage of prerender_child that collect all for testing
    class Root(Element):
        def __init__(self, **kwargs) -> None:
            self.__postrendered_children__ = []
            super().__init__(**kwargs)

        def postrender_child_element(self, child, child_element, context):
            self.__postrendered_children__.append(child)

    root = <Root>{elements}</Root>
    str(root)

    assert [(el.__class__, el.prop('id')) for el in root.__postrendered_children__] == [
        # In Root render we have only children
        # In Root children with start by a Parent instance
        (Parent, '1'),
        # In Parent render we start with a Collect instance
        (Collect, 'collect-parent-1'),
        # In Parent render we continue with children
        # In Parent children we have a Child instance
        (Child, '1'),
        # In a Child render we have a Collect instance
        (Collect, 'collect-child-1'),
        # Next in Parent render we have a Child instance
        (Child, 'fromparent-1'),
        # In a Child render we have a Collect instance
        (Collect, 'collect-child-fromparent-1'),
        # Next in Root children we have a Child instance
        (Child, '2'),
        # In a Child render we have a Collect instance
        (Collect, 'collect-child-2'),
    ]

    # Now we can test a collector collecting only ``Collect`` instances
    class Collector(Element):
        def __init__(self, **kwargs) -> None:
            self.__collected__ = []
            super().__init__(**kwargs)

        def postrender_child_element(self, child, child_element, context):
            if isinstance(child, Collect):
                self.__collected__.append(child)

    collector = <Collector>{elements}</Collector>
    str(collector)

    assert [(el.__class__, el.prop('id')) for el in collector.__collected__] == [
        (Collect, 'collect-parent-1'),
        (Collect, 'collect-child-1'),
        (Collect, 'collect-child-fromparent-1'),
        (Collect, 'collect-child-2'),
    ]
