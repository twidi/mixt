# coding: mixt

"""Ensure that parents are saved correctly."""

from mixt import Element, html
from mixt.internal.collector import Collector, CSSCollector


def test_collector():

    class Child(Element):
        def render(self, context):
            return [
                <Collector.Collect>
                    CHILD
                </Collector.Collect>,
                self.children(),
                <div>child-div</div>,
            ]

    class Parent(Element):
        def render(self, context):
            return [
                <Collector.Collect>
                    PARENT
                    <div />
                </Collector.Collect>,
                self.children(),
                <Child><div>parent-child-children</div></Child>,
                <div>parent-div</div>,
            ]

    collector = <Collector>
        <Parent>
            <Child><div>child-children</div></Child>
            <div>parent-children</div>
        </Parent>
        <Collector.Collect>{"""
            MAIN
            MAIN
        """}</Collector.Collect>
        <Child><div>child-children</div></Child>
    </Collector>

    str_collector = str(collector)
    assert 'CHILD' not in str_collector
    assert 'PARENT' not in str_collector
    assert 'MAIN' not in str_collector


    assert len(collector.__collected__) == 5

    assert len(collector.__collected__[0].__children__) == 2
    assert collector.__collected__[0].__children__[0].prop("text") == "PARENT"
    assert isinstance(collector.__collected__[0].__children__[1], html.Div)

    for index, text in [(1, "CHILD"), (2, "CHILD"), (4, "CHILD")]:
        assert len(collector.__collected__[index].__children__) == 1
        assert collector.__collected__[index].__children__[0].prop("text") == text

    assert len(collector.__collected__[3].__children__) == 1
    assert collector.__collected__[3].__children__[0] == """
            MAIN
            MAIN
        """

    assert collector.render_collected() == """\
PARENT<div></div>CHILDCHILD
            MAIN
            MAIN
        CHILD"""


def test_css_collector():

    class Content(Element):

        def render_css(self, context):
            return <CSSCollector.Collect>{"""
.content { margin: 15px; }
"""}
            </CSSCollector.Collect>

        def render(self, context):
            return <Fragment>
                {self.render_css(context)}
                <div class="content">{self.children()}</div>
            </Fragment>

    collector = <CSSCollector><Content><p>Hello</p></Content></CSSCollector>
    str(collector)

    assert str(collector.render_collected()) == """\
<style type="text/css">
.content { margin: 15px; }
</style>"""
