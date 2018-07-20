# coding: mixt

from docutils import nodes
from docutils.examples import internals

from slugify import slugify

from mixt import Element, html, h
from mixt.exceptions import InvalidChildrenError

from ..doc import DocPart, DocHeader
from . import H
from .code import SourceCode


CONTAINERS = {
    nodes.paragraph: h.P,
    nodes.bullet_list: h.Ul,
    nodes.enumerated_list: h.Ol,
    nodes.list_item: h.Li,
    nodes.strong: h.Strong,
    nodes.emphasis: h.Em,
    nodes.block_quote: h.Blockquote,
}

def add_section(node, children, id_prefix, h_level):
    title_node = node.children.pop(0)
    title = title_node.astext()
    slug = slugify(title)
    id_prefix += f"_{slug}"
    id_prefix = id_prefix.strip('_')

    container = DocPart(
        id_prefix=id_prefix,
        kind='rst-section',
        open=True,
        level=h_level
    )
    h_level += 1
    children.append(DocHeader(menu=title)(title))
    return container, id_prefix, h_level


def htmlize_node(node, id_prefix='', h_level=2):

    if isinstance(node, str):
        return node

    node_type = type(node)
    children = []

    if node_type in CONTAINERS:
        container = CONTAINERS[node_type]()
    else:
        if node_type is nodes.title_reference:
            return h.Code(_class="reference")(node.astext())

        if node_type is nodes.literal:
            return h.Code()(node.astext())

        if node_type is nodes.doctest_block:
            return SourceCode(language="python")(node.astext())

        if node_type is nodes.literal_block:
            try:
                language = node.attributes['classes'][1]  # 0 is always "code" for code-blocks
            except IndexError:
                language = "text"
            return SourceCode(language=language)(node.astext())

        if node_type is nodes.target:
            text = node.astext()
            if not text:
                try:
                    text = node.attributes['names'][0]
                except (IndexError, KeyError):
                    text = node.attributes['refuri']
            return h.A(href=node.attributes['refuri'])(text)

        if node_type is nodes.title:
            text = node.astext()
            return H(
                id=id_prefix,
                level=h_level,
                menu=text,
                menu_link=f"#{id_prefix}",
            )(text)

        if node_type in (nodes.document, nodes.section):
            if node.children and type(node.children[0]) is nodes.title:
                container, id_prefix, h_level = add_section(node, children, id_prefix, h_level)
            else:
                container = h.Fragment()
        else:
            print(f'RST node not managed: {node_type}')
            return node.astext()

    for index, child in enumerate(node.children):

        # if a reference is followed by a target, assume we can ignore it and
        # only display the link
        if type(child) is nodes.reference:
            try:
                if type(node.children[index+1]) is nodes.target:
                    node.children[index+1].children = [nodes.Text(child.astext())]
                    continue
            except IndexError:
                pass

        children.append(htmlize_node(child, id_prefix=id_prefix, h_level=h_level))

    return container(children) if children else None


def htmlize_rst(text, id_prefix='', h_level=2):
    return htmlize_node(internals(text)[0], id_prefix, h_level) if text else None


class Rst(Element):

    class PropTypes:
        id_prefix: str = ''
        h_level: int = 2

    def append(self, child_or_children):
        if len(self.__children__):
            raise InvalidChildrenError(self.__display_name__, "cannot have more than one child")
        super().append(child_or_children)

    def prepend(self, child_or_children):
        if len(self.__children__):
            raise InvalidChildrenError(self.__display_name__, "cannot have more than one child")
        super().prepend(child_or_children)

    def render(self, context):
        return htmlize_rst(str(self.children()[0]), self.id_prefix, self.h_level)
