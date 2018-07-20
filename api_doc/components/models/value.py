# coding: mixt

from typing import Optional

from mixt import Element, Required, html
from mixt.contrib.css import css_vars, render_css, Modes

from ... import datatypes
from ..doc import DocHeader, DocPart
from ..generic import H
from . import Code, DocString


class _Value(Element):
    class PropTypes:
        id_prefix: str = ""
        h_level: int = 3
        value: Required[datatypes.UnnamedValue]
        open_doc_details: bool = False
        open_example: bool = False

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_pycss_global(cls, context):
        return {
            ".value": {
                "&:not(:last-child) p:last-child": {
                    margin-bottom: 0,
                },
                "&:not(:first-child)": {
                    margin-top: 1*em,
                },
                ".docstring": {
                    margin-left: 1*em,
                },
            }
        }

    @classmethod
    def render_css_global(cls, context):
        css = render_css((cls.render_pycss_global(context)))
        return f"""
/* <{cls.__module__}.{cls.__name__}> */
{css}
/* </{cls.__module__}.{cls.__name__}> */
"""

    def render_example(self, context, id_prefix):
        doc_example = None
        example = self.value.example
        if example:
            doc_example = <DocPart kind="value" subkind="example" id_prefix={id_prefix} level={self.h_level+1} open={self.open_example}>
                <DocHeader menu="Example">Example</DocHeader>
                <Code code={example} />
            </DocPart>

        return doc_example


class UnnamedValue(_Value):
    class PropTypes:
        _class: str = "doc-part value value-unnamed"
        index: Optional[int] = None

    def render(self, context):
        value = self.value
        index = self.index

        id_prefix = f"{self.id_prefix}{index or 0}"

        output_type = None
        if value.type:
            output_type = [': ' if index else '', <code>{value.type}</code>]

        return <div id={id_prefix} tabindex=0>
            <H
                level={self.h_level}
                menu={index}
                menu_link="#{id_prefix}"
                menu_class="menu-value menu-value-unnamed"
            >
                {index or None}{output_type}
            </H>

            <DocString doc={value.doc} open={self.open_doc_details}/>
            {self.render_example(context, id_prefix)}
        </div>


class NamedValue(_Value):
    class PropTypes:
        _class: str = "doc-part value value-named"
        value: Required[datatypes.NamedValue]

    def render(self, context):
        value = self.value

        id_prefix = f"{self.id_prefix}{value.name.replace('*', '')}"

        output_type = output_default = None
        if value.type:
            output_type = [': ', <code>{value.type}</code>]
        if value.has_default:
            default = getattr(value.default, "__name__", value.default)
            output_default = [' = ', <code>{repr(default)}</code>]

        return <div id={id_prefix} tabindex=0>
            <H
                level={self.h_level}
                menu={value.name}
                menu_link="#{id_prefix}"
                menu_class="menu-value menu-value-named"
            >
                {value.name}<span class="attr-details">{output_type}{output_default}</span>
            </H>

            <DocString doc={value.doc} open={self.open_doc_details}/>
            {self.render_example(context, id_prefix)}
        </div>
