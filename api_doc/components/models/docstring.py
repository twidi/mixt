# coding: mixt

import re
from typing import Any, List, Union

from mixt import Element, Required, html, h
from mixt.internal.base import Base, escape, AnElement

from ... import types
from ..generic import Details


FIND_CODE = re.compile("(`+)(.+?)\\1")
CODE_DELIM = {"``", "`"}


def htmlize_line(text: str) -> List[Union[str, Base]]:
    parts = FIND_CODE.split(text)
    result = []
    next_is_code = False
    for part in parts:
        if next_is_code:
            result.append(h.Code()(part))
            next_is_code = False
            continue
        if part in CODE_DELIM:
            next_is_code = True
            continue
        result.append(part)

    return result


def add_separator(input: List, separator: Any):
    """Return the `input` list with `separator` inserted between each entry."""
    output = input[:]
    for counter in range(0, len(input) - 1):
        output.insert(counter * 2 + 1, separator)
    return output


class DocString(Element):
    class PropTypes:
        _class: str = "docstring"
        doc: Required[types.SimpleDocString]
        hide_summary: bool = False
        hide_details: bool = False
        open: bool = False

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
/* <components.models.docstring> */
details.docstring {
    margin-top: 1em;
}
details.docstring > summary > p {
    margin-top: 0;
    white-space: normal;
    display: inline;
}
details.docstring > div.content > p:first-child {
    margin-top: 1em;
}
/* </components.models.docstring> */
        """

    def render(self, context):
        doc = self.doc

        summary = None
        details = None

        if not self.hide_summary:
            summary = h.P()(add_separator(
                [htmlize_line(line) for line in doc.summary], h.Br()
            ))

        if not self.hide_details:
            details = [
                h.P()(add_separator([htmlize_line(line) for line in detail], h.Br()))
                for detail in doc.details
            ]

        if summary and details:
            return <Details open={self.open}>
                <summary>{summary}</summary>
                {details}
            </Details>

        if summary:
            return <div>{summary}</div>

        if details:
            return <div>{details}</div>
