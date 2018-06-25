# coding: mixt

"""Ensure that parents are saved correctly."""

from mixt import Element, html
from mixt.internal.collectors import Collector, CSSCollector, JSCollector


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


def test_css_collector_via_collect():

    class Content(Element):

        def render_style(self, context):
            return <CSSCollector.Collect>{"""
.content { margin: 15px; }
"""}
            </CSSCollector.Collect>

        def render(self, context):
            return <Fragment>
                {self.render_style(context)}
                <div class="content">{self.children()}</div>
            </Fragment>

    collector = <CSSCollector><Content><p>Hello</p></Content></CSSCollector>
    str(collector)

    assert str(collector.render_collected()) == """\
<style type="text/css">
.content { margin: 15px; }
</style>"""

    class App(Element):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.css_ref = self.add_ref()

        def render(self, context):
            return \
                <html>
                    <head>
                    {lambda: self.css_ref.current.render_collected()}
                    </head>
                    <body>
                        <CSSCollector ref={self.css_ref}>
                            <Content><p>Hello</p></Content>
                        </CSSCollector>
                    </body>
                </html>

    assert str(<App />) == """\
<html><head><style type="text/css">
.content { margin: 15px; }
</style></head><body><div class="content"><p>Hello</p></div></body></html>"""


def test_js_collector_via_render_js():

    class Content(Element):
        def render_js(self, context):
            return """
alert(1);
"""

        def render(self, context):
            return <div>{self.children()}</div>

    class App(Element):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.js_ref = self.add_ref()

        def render(self, context):
            return \
                <html>
                    <head>
                    {lambda: self.js_ref.current.render_collected()}
                    </head>
                    <body>
                        <JSCollector ref={self.js_ref}>
                            <Content><p>Hello</p></Content>
                        </JSCollector>
                    </body>
                </html>

    assert str(<App />) == """\
<html><head><script type="text/javascript">
alert(1);
</script></head><body><div><p>Hello</p></div></body></html>"""
