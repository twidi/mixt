# coding: mixt

from docutils import nodes
from docutils.examples import internals
from typing import List

from mixt import Element, Required, html, h

from ... import types
from ..generic import Details
from . import Code


CONTAINERS = {
    nodes.document: h.Fragment,
    nodes.paragraph: h.P,
    nodes.bullet_list: h.Ul,
    nodes.enumerated_list: h.Ol,
    nodes.list_item: h.Li,
}

def htmlize_node(node):

    if isinstance(node, str):
        return node

    node_type = type(node)

    if node_type in CONTAINERS:
        container = CONTAINERS[node_type]()
    else:

        if node_type is nodes.title_reference:
            return h.Code(_class="reference")(node.astext())

        if node_type is nodes.literal:
            return h.Code()(node.astext())

        if node_type is nodes.literal_block:
            try:
                language = node.attributes['classes'][1]  # 0 is always "code" for code-blocks
            except IndexError:
                language = "text"
            return Code(code=types.Code(code=node.astext(), language=language))

        return node.astext()

    children = [htmlize_node(child) for child in node.children]
    return container(children) if children else None


def htmlize_summary(lines: List[str]):
    text = "\n".join(lines).strip()
    return htmlize_node(internals(text)[0]) if text else None


def htmlize_details(parts: List[List[str]]):
    text = "\n\n".join(["\n".join(para) for para in parts]).strip()
    return htmlize_node(internals(text)[0]) if text else None


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
            summary = htmlize_summary(doc.summary)

        if not self.hide_details:
            details = htmlize_details(doc.details)

        if summary and details:
            return <Details open={self.open}>
                <summary>{summary}</summary>
                {details}
            </Details>

        if summary:
            return <div>{summary}</div>

        if details:
            return <div>{details}</div>
