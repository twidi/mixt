# coding: mixt

"""Ensure that parents are saved correctly."""

from mixt import Element, NotProvided, Ref, Required, html
from mixt.contrib.css import CssDict, override_default_mode, Modes
from mixt.contrib.css.vars import extend
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
            return <CSSCollector.Collect>{html.Raw(".content { margin: 15px; }")}
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
                'foo': "C1GlobalFoo",
                'bar': "C1GlobalBar",
                'default': "C1GlobalDefault"
            }

        def render_css(self, context):
            return {
                'bar': "C1Local%sBar" % self.id,
                'default': "C1Local%sDefault" % self.id
            }

        def render(self, context):
            return <CSSCollector.Collect namespace="bar">{html.Raw(
                "C1Collect%sBar" % self.id
            )}</CSSCollector.Collect>

    class Component2(Element):
        @classmethod
        def render_css_global(cls, context):
            return "C2GlobalDefault"

        def render_css(self, context):
            return "C2Local%sDefault" % self.id

        def render(self, context):
            return <CSSCollector.Collect>{html.Raw("C2Collect%sDefault" % self.id)}</CSSCollector.Collect>


    class Component3(Element):
        @classmethod
        def render_css_global(cls, context):
            return {
                'foo': "C3GlobalFoo",
                'bar': "C3GlobalBar",
                'default': "C3GlobalDefault"
            }

        def render_css(self, context):
            return {
                'bar': "C3Local%sBar" % self.id,
                'default': "C3Local%sDefault" % self.id
            }

        def render(self, context):
            return <CSSCollector.Collect namespace="bar">{html.Raw(
                "C3Collect%sBar" % self.id
            )}</CSSCollector.Collect>


    class App(Element):
        class PropTypes:
            css_ref: Required[Ref]

        def render(self, context):
            return <CSSCollector ref={self.css_ref}>
                <Component1 id=1 />
                <Component2 id=1 />
                <Component2 id=2 />
                <Component3 id=1 />
                <Component3 id=2 />
                <Component1 id=2 />
            </CSSCollector>

    ref = Ref()
    app = App(css_ref = ref)
    str(app)

    with override_default_mode(Modes.COMPACT):
        assert ref.current.render_collected(with_tag=False) == """\
C1GlobalFoo
C3GlobalFoo
C1GlobalBar
C1Local1Bar
C1Collect1Bar
C3GlobalBar
C3Local1Bar
C3Collect1Bar
C3Local2Bar
C3Collect2Bar
C1Local2Bar
C1Collect2Bar
C1GlobalDefault
C1Local1Default
C2GlobalDefault
C2Local1Default
C2Collect1Default
C2Local2Default
C2Collect2Default
C3GlobalDefault
C3Local1Default
C3Local2Default
C1Local2Default
"""

        assert ref.current.render_collected("foo", "bar", "baz", with_tag=False) == """\
C1GlobalFoo
C3GlobalFoo
C1GlobalBar
C1Local1Bar
C1Collect1Bar
C3GlobalBar
C3Local1Bar
C3Collect1Bar
C3Local2Bar
C3Collect2Bar
C1Local2Bar
C1Collect2Bar
"""
        assert ref.current.render_collected("default", with_tag=False) == """\
C1GlobalDefault
C1Local1Default
C2GlobalDefault
C2Local1Default
C2Collect1Default
C2Local2Default
C2Collect2Default
C3GlobalDefault
C3Local1Default
C3Local2Default
C1Local2Default
"""


def test_reuse():

    class Component1(Element):

        @classmethod
        def render_css_global(cls, context):
            return "Global."

        def render_css(self, context):
            return "Local%(id)s." % {'id': self.id}

    def run_comp1(**kwargs):
        main_collector, ref1, ref2 = CSSCollector(), Ref(), Ref()
        str(<CSSCollector ref={ref1} reuse={main_collector} {**kwargs}><Component1 id=1 /></CSSCollector>)
        str(<CSSCollector ref={ref2} reuse={main_collector} {**kwargs}><Component1 id=2 /></CSSCollector>)
        return main_collector, ref1, ref2

    with override_default_mode(Modes.COMPRESSED):

        main_collector, ref1, ref2 = run_comp1()
        assert ref1.current.reuse_global is True
        assert ref1.current.reuse_non_global is True
        assert main_collector.render_collected(with_tag=False) == "Global.Local1.Local2."
        assert ref1.current.render_collected(with_tag=False) == ""
        assert ref2.current.render_collected(with_tag=False) == ""

        main_collector, ref1, ref2 = run_comp1(reuse_non_global=False)
        assert ref1.current.reuse_global is True
        assert ref1.current.reuse_non_global is False
        assert main_collector.render_collected(with_tag=False) == "Global."
        assert ref1.current.render_collected(with_tag=False) == "Local1."
        assert ref2.current.render_collected(with_tag=False) == "Local2."

        main_collector, ref1, ref2 = run_comp1(reuse_global=False)
        assert ref1.current.reuse_global is False
        assert ref1.current.reuse_non_global is True
        assert main_collector.render_collected(with_tag=False) == "Local1.Local2."
        assert ref1.current.render_collected(with_tag=False) == "Global."
        assert ref2.current.render_collected(with_tag=False) == "Global."

    class Component2(Element):

        @classmethod
        def render_css_global(cls, context):
            return {
                "foo": "GlobalFoo.",
                "bar": "GlobalBar.",
            }

        def render_css(self, context):
            return {
                "foo": "Local%(id)sFoo." % {'id': self.id}
            }

    def run_comp2(**kwargs):
        main_collector, ref1, ref2 = CSSCollector(), Ref(), Ref()
        str(<CSSCollector ref={ref1} reuse={main_collector} {**kwargs}><Component2 id=1 /></CSSCollector>)
        str(<CSSCollector ref={ref2} reuse={main_collector} {**kwargs}><Component2 id=2 /></CSSCollector>)
        return main_collector, ref1, ref2

    with override_default_mode(Modes.COMPRESSED):

        main_collector, ref1, ref2 = run_comp2(reuse_non_global=False)
        assert ref1.current.reuse_namespaces is None
        assert main_collector.render_collected(with_tag=False) == "GlobalFoo.GlobalBar."
        assert ref1.current.render_collected(with_tag=False) == "Local1Foo."
        assert ref2.current.render_collected(with_tag=False) == "Local2Foo."

        main_collector, ref1, ref2 = run_comp2(reuse_namespaces=["foo", "default"])
        assert ref1.current.reuse_namespaces == {"foo", "default"}
        assert main_collector.render_collected(with_tag=False) == "GlobalFoo.Local1Foo.Local2Foo."
        assert ref1.current.render_collected(with_tag=False) == "GlobalBar."
        assert ref2.current.render_collected(with_tag=False) == "GlobalBar."

        main_collector, ref1, ref2 = run_comp2(reuse_namespaces=["foo", "default"], reuse_non_global=False)
        assert main_collector.render_collected(with_tag=False) == "GlobalFoo."
        assert ref1.current.render_collected(with_tag=False) == "GlobalBar.Local1Foo."
        assert ref2.current.render_collected(with_tag=False) == "GlobalBar.Local2Foo."

        main_collector, ref1, ref2 = run_comp2(reuse_namespaces=["foo", "default"], reuse_global=False)
        assert main_collector.render_collected(with_tag=False) == "Local1Foo.Local2Foo."
        assert ref1.current.render_collected(with_tag=False) == "GlobalFoo.GlobalBar."
        assert ref2.current.render_collected(with_tag=False) == "GlobalFoo.GlobalBar."


def test_all_css_render_at_once():

    class CssLib(Element):
        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                "%ext": {"ext": "end"}
            })

    class Foo(Element):

        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                ".foo": extend("ext", css={
                    "color": "FOO",
                })
            })

    class Bar(Element):

        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                ".bar": extend("ext", css={
                    "color": "BAR",
                })
            })


    class App(Element):
        def render(self, context):
            return <CSSCollector render_position="before">
                <CssLib />
                <Foo />
                <Bar />
            </CSSCollector>

    with override_default_mode(Modes.NORMAL):
        assert str(App()) == """\
<style type="text/css">
.foo, .bar {
  ext: end;
}
.foo {
  color: FOO;
}
.bar {
  color: BAR;
}
</style>"""
