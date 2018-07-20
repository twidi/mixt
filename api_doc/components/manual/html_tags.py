# coding: mixt

from itertools import chain
from typing import Any, List

from mixt import html, h
from mixt.internal.html import __tags__, HtmlBaseElement

from ...code_utils import load_docstring, resolve_proptypes
from ... import datatypes
from ..doc import DocPart, DocHeader
from ..models import Class, DocString
from .base import _Manual


def add_separator(input: List, separator: Any):
    """Return the `input` list with `separator` inserted between each entry."""
    output = input[:]
    for counter in range(0, len(input) - 1):
        output.insert(counter * 2 + 1, separator)
    return output


def get_proptypes(tag):
    ignore_props = set(chain.from_iterable([base.PropTypes.__types__.keys() for base in tag.__mro__[1:-4]]))
    self_props = tag.PropTypes.__types__.keys()
    only_props = [prop for prop in self_props if prop not in ignore_props]
    return resolve_proptypes(tag.PropTypes, only=only_props) if only_props else None


def prepare_tag(name, tag):
    docstring = load_docstring(tag)

    klass = datatypes.Class(
        name=name,
        attrs=[],
        functions=[],
        doc=datatypes.ClassDocString(
            summary=docstring.get("Summary") or "",
            details=docstring.get("Extended Summary") or [],
        ),
        example=None,
        proptypes=get_proptypes(tag)

    )
    return {
        'bases': tag.__mro__[1:-5],
        'class': klass,
        'accept_children': issubclass(tag, html.HtmlElement),
    }


class HtmlTags(_Manual):

    def render(self, context):
        id_prefix = f'{self.id_prefix}HtmlTags'

        base_tag = prepare_tag('_Base', HtmlBaseElement)

        tags = [base_tag] + [
            prepare_tag(name, getattr(html, name))
            for name
            in __tags__.values()
            if hasattr(html, name)
                and name not in [
                    'HtmlElement',
                    'HtmlElementNoChild',
                    '_H',
                    'RawHtml',
                ]
        ]

        html_docstring = load_docstring(html)
        docstring = datatypes.SimpleDocString(
            summary=html_docstring.get("Summary") or "",
            details=html_docstring.get("Extended Summary") or [],
        )

        return <DocPart kind="HtmlTags" id_prefix={id_prefix} level={self.h_level}>
            <DocHeader menu="HTML tags">HTML tags</DocHeader>

            <DocString doc={docstring} open />

            {[
                <Class obj={tag['class']} h_level={self.h_level+1} id_prefix="{id_prefix}-tags-" children_position=start>
                    <if cond={tag['bases']}>
                        <p><strong>Bases</strong>: {add_separator([h.Code()(base.__name__) for base in tag['bases']], ', ')}</p>
                    </if>
                    <p><strong>Accept children</strong>: {'yes' if tag['accept_children'] else 'no'}</p>
                </Class>
                for tag in tags
            ]}
        </DocPart>
