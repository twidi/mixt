# coding: mixt

"""Ensure that parents are saved correctly."""

from mixt import Element, NotProvided, Ref, Required, html
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


    assert len(collector.__collected__["default"]) == 5

    assert len(collector.__collected__["default"][0].__children__) == 2
    assert collector.__collected__["default"][0].__children__[0].prop("text") == "PARENT"
    assert isinstance(collector.__collected__["default"][0].__children__[1], html.Div)

    for index, text in [(1, "CHILD"), (2, "CHILD"), (4, "CHILD")]:
        assert len(collector.__collected__["default"][index].__children__) == 1
        assert collector.__collected__["default"][index].__children__[0].prop("text") == text

    assert len(collector.__collected__["default"][3].__children__) == 1
    assert collector.__collected__["default"][3].__children__[0] == """
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
            return <CSSCollector.Collect>{html.Raw("""
.content { margin: 15px; }
""")}
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


def test_no_children():
    def get(position=NotProvided, ref=NotProvided):
        return <Collector render_position={position} ref={ref}>
            <Collector.Collect>
                foo
            </Collector.Collect>
        </Collector>

    assert str(get(position="before")) == "foo"
    assert str(get(position="after")) == "foo"

    ref =  Ref()
    assert str(<Fragment>{get(ref=ref)}{ref.current.render_collected}</Fragment>) == "foo"
    ref =  Ref()
    assert str(<Fragment>{lambda: ref.current.render_collected()}{get(ref=ref)}</Fragment>) == "foo"


def test_namespaces():

    class Component1(Element):
        @classmethod
        def render_css_global(cls, context):
            return {
                'file': """
Component1.render_css_global.file
""",
                'outside': """
Component1.render_css_global.outside
""",
                'default': """
Component1.render_css_global.default
"""
            }

        def render_css(self, context):
            return {
                'outside': """
Component1#%s.render_css.outside
""" % self.id,
                'default': """
Component1#%s.render_css.default
""" % self.id
            }

        def render(self, context):
            return <CSSCollector.Collect namespace="outside">{html.Raw("""
Component1#%s.render.collect.outside
""" % self.id)}</CSSCollector.Collect>

    class Component2(Element):
        @classmethod
        def render_css_global(cls, context):
            return """
Component2.render_css_global.default
"""

        def render_css(self, context):
            return """
Component2#%s.render_css.default
""" % self.id

        def render(self, context):
            return <CSSCollector.Collect>{html.Raw("""
Component2#%s.render.collect.default
""" % self.id)}</CSSCollector.Collect>


    class Component3(Element):
        @classmethod
        def render_css_global(cls, context):
            return {
                'file': """
Component3.render_css_global.file
""",
                'outside': """
Component3.render_css_global.outside
""",
                'default': """
Component3.render_css_global.default
"""
            }

        def render_css(self, context):
            return {
                'outside': """
Component3#%s.render_css.outside
""" % self.id,
                'default': """
Component3#%s.render_css.default
""" % self.id
            }

        def render(self, context):
            return <CSSCollector.Collect namespace="outside">{html.Raw("""
Component3#%s.render.collect.outside
""" % self.id)}</CSSCollector.Collect>


    class App(Element):
        class PropTypes:
            css_ref: Required[Ref]

        def render(self, context):
            return <CSSCollector ref={self.css_ref}>
                <Component1 id="id1-1" />
                <Component2 id="id2-1" />
                <Component2 id="id2-2" />
                <Component3 id="id3-1" />
                <Component3 id="id3-2" />
                <Component1 id="id1-2" />
            </CSSCollector>

    ref = Ref()
    app = App(css_ref = ref)
    str(app)

    print(ref.current.render_collected(with_tag=False))

    assert ref.current.render_collected(with_tag=False) == """
Component1.render_css_global.file

Component3.render_css_global.file

Component1.render_css_global.outside

Component1#id1-1.render_css.outside

Component1#id1-1.render.collect.outside

Component3.render_css_global.outside

Component3#id3-1.render_css.outside

Component3#id3-1.render.collect.outside

Component3#id3-2.render_css.outside

Component3#id3-2.render.collect.outside

Component1#id1-2.render_css.outside

Component1#id1-2.render.collect.outside

Component1.render_css_global.default

Component1#id1-1.render_css.default

Component2.render_css_global.default

Component2#id2-1.render_css.default

Component2#id2-1.render.collect.default

Component2#id2-2.render_css.default

Component2#id2-2.render.collect.default

Component3.render_css_global.default

Component3#id3-1.render_css.default

Component3#id3-2.render_css.default

Component1#id1-2.render_css.default
"""

    assert ref.current.render_collected("file", "outside", with_tag=False) == """
Component1.render_css_global.file

Component3.render_css_global.file

Component1.render_css_global.outside

Component1#id1-1.render_css.outside

Component1#id1-1.render.collect.outside

Component3.render_css_global.outside

Component3#id3-1.render_css.outside

Component3#id3-1.render.collect.outside

Component3#id3-2.render_css.outside

Component3#id3-2.render.collect.outside

Component1#id1-2.render_css.outside

Component1#id1-2.render.collect.outside
"""
    assert ref.current.render_collected("default", with_tag=False) == """
Component1.render_css_global.default

Component1#id1-1.render_css.default

Component2.render_css_global.default

Component2#id2-1.render_css.default

Component2#id2-1.render.collect.default

Component2#id2-2.render_css.default

Component2#id2-2.render.collect.default

Component3.render_css_global.default

Component3#id3-1.render_css.default

Component3#id3-2.render_css.default

Component1#id1-2.render_css.default
"""
