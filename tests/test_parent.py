# coding: mixt

"""Ensure that parents are saved correctly."""

from mixt import html


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
    frag, = div.__children__
    assert frag.__parent__ is div
    span1, span2 = frag.__children__
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
    frag1, = div.__children__
    assert frag1.__parent__ is div
    frag2, = frag1.__children__
    assert frag2.__parent__ is div
    frag3, = frag2.__children__
    assert frag3.__parent__ is div
    span1, span2 = frag3.__children__
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
    frag1, = div.__children__
    assert frag1.__parent__ is div
    frag2, = frag1.__children__
    assert frag2.__parent__ is div
    frag3, div2 = frag2.__children__
    assert frag3.__parent__ is div
    assert div2.__parent__ is div
    span1, span2 = frag3.__children__
    assert span1.__parent__ is div
    assert span2.__parent__ is div
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
