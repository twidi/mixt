# coding: mixt

from mixt import html

from ... import types
from ...code_utils import resolve_class, resolve_function
from ..doc import DocPart, DocHeader
from ..models import Class, Code, Function
from .base import _Manual


class HtmlUtils(_Manual):

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
.HtmlUtils .function-function > summary > .h:after { 
    %(TAG)s
    %(HL)s
    content: "function";
}

        """

    def render(self, context):
        id_prefix = f'{self.id_prefix}HtmlUtils'

        return <DocPart kind="HtmlUtils" id_prefix={id_prefix} level={self.h_level}>
            <DocHeader menu="HTML utils">HTML utils</DocHeader>

            <Class h_level={self.h_level+1} id_prefix="{id_prefix}-" obj={resolve_class(
                klass=html.RawHtml,
                attrs=[],
                methods=[],
                name='RawHtml',
                only_proptypes=['text'],
            )} />

            <Function h_level={self.h_level+1} id_prefix="{id_prefix}-" open=False open_details obj={resolve_function(
                func=html.Raw,
                name='Raw',
            )} />


            <Class h_level={self.h_level+1} id_prefix="{id_prefix}-" obj={resolve_class(
                klass=html.Fragment,
                attrs=[],
                methods=[],
                name='Fragment',
                only_proptypes=[],
            )} />

            <DocPart kind="HtmlUtils" subkind="if-else" id_prefix={id_prefix} level={self.h_level+1}>
                <DocHeader menu="if / else tags">if / else tags</DocHeader>

                <p>
                    Mixt avoids support for logic within the HTML flow, except for one case where we found it especially
                    useful: conditionally rendering HTML.
                </p>
                <p>
                    That is why Mixt provides the <code>&lt;if&gt;</code> tag, which takes a prop named
                    <code>cond</code>.
                </p>
                <p>
                    Children of an <code>&lt;if&gt;</code> tag are only rendered if <code>cond</code> evaluates
                    to <code>True</code>.
                </p>
                <p>
                    It comes with the <code>&lt;else&gt;</code> tag, not taking any prop, that is optional but if
                    used, must come right after the closing <code>&lt;/if&gt;</code> tag.
                </p>
                <p>
                    Children of an <code>&lt;else&gt;</code> tag are only rendered if the <code>cond</code> prop of the
                    <code>&lt;if&gt;</code> tag evaluates to <code>False</code>.
                </p>

                <DocPart kind="HtmlUtils" subkind="if-else-example" id_prefix="{id_prefix}" level={self.h_level+2} open>
                    <DocHeader menu="Example">Example</DocHeader>
                    <Code code={types.Code(
# language=Python
"""
>>> class Component(Element):
...     class PropTypes:
...         flag: Required[bool]
...
...     def render(self, context):
...         return <div>
...             <if cond={self.flag}>
...                 <span>It's TRUE</span>
...             </if>
...             <else>
...                 <p>It's FALSE</p>
...             </else>
...         </div>

>>> print(<Component flag=True />)
<div><span>It's TRUE</span></div>

>>> print(<Component flag=True />)
<div><p>It's FALSE</p></div>

# A more pythonic way to do this without using these if/else tags:

>>> class Component(Element):
>>>     def render(self, context):
... 
...         if self.flag:
...             conditional_render =  <span>It's TRUE</span>
...         else:
...             conditional_render =  <p>It's FALSE</p>
...
...         return <div>
...             {conditional_render}
...         </div>

# Or using the fact that ``None`` is not rendered:

>>>     def render(self, context):
...
...         part_if_true = part_if_false = None
...
...         if self.flag:
...             part_if_true =  <span>It's TRUE</span>
...         else:
...             part_if_false =  <p>It's FALSE</p>
...
...         return <div>
...             {part_if_true}
...             {part_if_false}
...         </div>
""", language="python"
                    )} />
                </DocPart>
            </DocPart>

            <DocPart kind="HtmlUtils" subkind="comments" id_prefix={id_prefix} level={self.h_level+1}>
                <DocHeader menu="Comments">Comments</DocHeader>

                <p>HTML and python comments are correctly handled but not rendered in the final HTLM.</p>

                <DocPart kind="HtmlUtils" subkind="if-else-example" id_prefix="{id_prefix}" level={self.h_level+2} open>
                    <DocHeader menu="Example">Example</DocHeader>
                    <Code code={types.Code(
# language=Python
"""
>>> class Component(Element):
...     def render(self, context):
...         return <div>
...             <!-- inside the div -->
...             Foo  # bar?
...         </div>

>>> print(<Component />)
<div>Foo</div>
""", language="python"
                    )} />
                </DocPart>
            </DocPart>

            <Class h_level={self.h_level+1} id_prefix="{id_prefix}-" obj={resolve_class(
                klass=html.Doctype,
                attrs=[],
                methods=[],
                name='Doctype',
                only_proptypes=['doctype'],
            )} />

        </DocPart>
