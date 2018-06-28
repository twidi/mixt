# coding: mixt

from docutils import nodes
from docutils.examples import internals

from mixt import Element, html, h
from mixt.exceptions import InvalidChildrenError

from .code import SourceCode


CONTAINERS = {
    nodes.document: h.Fragment,
    nodes.paragraph: h.P,
    nodes.bullet_list: h.Ul,
    nodes.enumerated_list: h.Ol,
    nodes.list_item: h.Li,
    nodes.strong: h.Strong,
    nodes.emphasis: h.Em,
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
            return SourceCode(language=language)(node.astext())

        if node_type is nodes.target:
            try:
                text = node.attributes['names'][0]
            except (IndexError, KeyError):
                text = node.attributes['refuri']
            return h.A(href=node.attributes['refuri'])(text)

        return node.astext()

    children = []
    for index, child in enumerate(node.children):

        # if a reference is followed by a target, assume we can ignore it and
        # only display the link
        if type(child) is nodes.reference:
            try:
                if type(node.children[index+1]) is nodes.target:
                    continue
            except IndexError:
                pass

        children.append(htmlize_node(child))

    return container(children) if children else None


def htmlize_rst(text):
    return htmlize_node(internals(text)[0]) if text else None


class Rst(Element):

    def append(self, child_or_children):
        if len(self.__children__):
            raise InvalidChildrenError(self.__display_name__, "cannot have more than one child")
        super().append(child_or_children)

    def prepend(self, child_or_children):
        if len(self.__children__):
            raise InvalidChildrenError(self.__display_name__, "cannot have more than one child")
        super().prepend(child_or_children)

    def render(self, context):
        return htmlize_rst(str(self.children()[0]))
