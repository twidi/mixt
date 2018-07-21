# coding: mixt

from mixt import html, h
from mixt.contrib.css import css_vars, render_css, Modes

from ...code_utils import resolve_class, resolve_function
from ..doc import DocPart, DocHeader
from ..generic import Rst, SourceCode
from ..models import Class, Function
from .base import _Manual


class HtmlUtils(_Manual):

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        return render_css({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
            ".HtmlUtils .function-function > summary > .h:after": merge(
                context.styles.snippets['TAG'],
                context.styles.snippets['HL'],
                {
                    content: str("function"),
                }
            ),
            "/**": f"</{cls.__module__}.{cls.__name__}>",
        })

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

                <Rst>{h.Raw(
# language=RST
"""
Mixt avoids support for logic within the HTML flow, except for one case where we found it especially
useful: conditionally rendering HTML.

That is why Mixt provides the ``<if>`` tag, which takes a prop named ``cond``.

Children of an ``<if>`` tag are only rendered if ``cond`` evaluates to ``True``.

It comes with the ``<else>`` tag, not taking any prop, that is optional but if
used, must come right after the closing ``</if>`` tag.

Children of an ``<else>`` tag are only rendered if the ``cond`` prop of the
``<if>`` tag evaluates to ``False``.
"""
                )}</Rst>

                <DocPart kind="HtmlUtils" subkind="if-else-example" id_prefix="{id_prefix}" level={self.h_level+2} open>
                    <DocHeader menu="Example">Example</DocHeader>
                    <SourceCode language="python">{h.Raw(
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
"""
                    )}</SourceCode>
                </DocPart>
            </DocPart>

            <DocPart kind="HtmlUtils" subkind="comments" id_prefix={id_prefix} level={self.h_level+1}>
                <DocHeader menu="Comments">Comments</DocHeader>

                <p>HTML and python comments are correctly handled but not rendered in the final HTLM.</p>

                <DocPart kind="HtmlUtils" subkind="if-else-example" id_prefix="{id_prefix}" level={self.h_level+2} open>
                    <DocHeader menu="Example">Example</DocHeader>
                    <SourceCode language="python">{h.Raw(
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
""",
                    )}</SourceCode>
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
