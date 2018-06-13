# coding: mixt

from typing import Any

from mixt import Element, html



def test_refs():

    class Foo(Element):

        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)

            self.div_ref = self.add_ref()
            self.span_ref = self.add_ref()

        def render(self, context):
            return <div ref={self.div_ref}><span ref={self.span_ref}></span></div>

        def postrender(self, element, context):
            self.div_ref.current.add_class('pr_div')
            self.span_ref.current.add_class('pr_span')

    assert str(<Foo />) == '<div class="pr_div"><span class="pr_span"></span></div>'



