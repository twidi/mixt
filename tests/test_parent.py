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
