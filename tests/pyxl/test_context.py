# coding: mixt

"""Ensure that context props are passed to all elements."""

from mixt.pyxl import html
from mixt.pyxl.base import BaseContext
from mixt.pyxl.element import Element


def test_context_propagation():
    class Context(BaseContext):
        class PropTypes:
            value: str

    class GrandChild(Element):
        def render(self, context):
            return (
                <div>
                    <span data-value={context.value} />
                </div>,
                <br />,
                self.children(),
            )

    class Child(Element):
        def render(self, context):
            return \
                <main>
                    <article>
                        <GrandChild>
                            <div data-other={context.value} />
                        </GrandChild>
                    </article>
                </main>

    class Parent(Element):
        def render(self, context):
            return <html><Child /></html>

    class GrandParent(Element):
        def render(self, context):
            return <Parent />

    assert str(<Context value="foo"><GrandParent /></Context>) == (
        '<html>'
            '<main>'
                '<article>'
                    '<div>'
                        '<span data-value="foo"></span>'
                    '</div>'
                    '<br />'
                    '<div data-other="foo"></div>'
                '</article>'
            '</main>'
        '</html>'
    )


def test_context_via_functions():
    class Context(BaseContext):
        class PropTypes:
            title: str

    class Child(Element):
        def render(self, context):
            return <span title={context.title} />

    def Parent():
        return <div><Child /></div>

    assert str(<Context title="foo"><Parent /></Context>) == '<div><span title="foo"></span></div>'


def test_merge_context():
    class ParentContext(BaseContext):
        class PropTypes:
            val1: str
            val2: str

    class ChildContext(BaseContext):
        class PropTypes:
            val2: str
            val3: str

    class GrandChild(Element):
        def render(self, context):
            return <div data-val1={context.val1} data-val2={context.val2} data-val3={context.val3} />

    class Child(Element):
        def render(self, context):
            return <GrandChild />

    class Parent(Element):
        def render(self, context):
            return <ChildContext val2="baz" val3="qux"><Child /></ChildContext>

    assert str(
        <ParentContext val1="foo" val2="bar"><Parent /></ParentContext>
    ) == '<div data-val1="foo" data-val2="baz" data-val3="qux"></div>'
