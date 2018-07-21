# coding: mixt

from mixt import DefaultChoices, Element, html
from mixt.contrib.css import css_vars, CssDict

from ..doc import DocPart, DocHeader

from . import Code, DocString, Function, NamedValue


class _BaseContainer(Element):

    __kind__ = None
    __functions_kind__ = None
    __functions_kind_title__ = None

    class PropTypes:
        id_prefix: str = ''
        h_level: int = 2
        open: bool = False
        open_doc_details: bool = True
        children_position: DefaultChoices = ['end', 'start']

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        if cls is _BaseContainer:
            return None

        colors = context.styles.colors

        _kind = cls.__kind__
        _functions_kind = cls.__functions_kind__
        _target = "&:hover, &:target, &.focus-within"
        _focus = "&:hover, &:focus, &.focus-within"

        return CssDict({
            "/*": f"<{cls.__module__}.BaseContainer.{cls.__name__}>",
            f".{_kind}": {
                "> summary > .h:after": merge(
                    context.styles.snippets['TAG'],
                    context.styles.snippets['HL'],
                    {
                        content: str(_kind),
                    }
                ),
                _target: {
                    background: colors[2],
                },
                "&-doc-part": {
                    _focus: {
                        background: colors[3],
                    }
                },
                f"&-attributes .value, &-{_functions_kind} .function": {
                    _focus: {
                        background: colors[4],
                    }
                },
                f"&-{_functions_kind} .function-doc-part": {
                    _focus: {
                        background: colors[5],
                    }
                },
                f"&-{_functions_kind} .value": {
                    _focus: {
                        background: colors[6],
                    }
                },
            },
            "/**": f"</{cls.__module__}.BaseContainer.{cls.__name__}>",
        })

    def render_content(self, id_prefix, context):
        obj = self.obj

        doc_example = doc_attributes = doc_functions = None

        if obj.example:
            doc_example = <DocPart kind={self.__kind__} subkind="example" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Example">Example</DocHeader>
                <Code code={obj.example} />
            </DocPart>

        if obj.attrs:
            doc_attributes = <DocPart kind={self.__kind__} subkind="attributes" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Attributes">Attributes</DocHeader>
                {[
                    <NamedValue value={attr} h_level={self.h_level+2} id_prefix="{id_prefix}-attributes-"/>
                    for attr in obj.attrs
                ]}
            </DocPart>

        if obj.functions:
            doc_functions = <DocPart kind={self.__kind__} subkind={self.__functions_kind__} id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu={self.__functions_kind_title__}>{self.__functions_kind_title__}</DocHeader>
                {[
                    <Function obj={function} h_level={self.h_level+2} id_prefix="{id_prefix}-{self.__functions_kind__}-"/>
                    for function in obj.functions
                ]}
            </DocPart>

        children = self.children()

        return [
            children if self.children_position == 'start' else None,
            [
                doc_example,
                doc_attributes,
                doc_functions,
            ],
            children if self.children_position == 'end' else None,
        ]

    def render(self, context):
        obj = self.obj
        id_prefix = f'{self.id_prefix}{self.__kind__}-{self.obj.name}'


        return <DocPart kind={self.__kind__} id_prefix={id_prefix} level={self.h_level} open={self.open}>
            <DocHeader menu={obj.name}>{obj.name}</DocHeader>

            <DocString doc={obj.doc} open={self.open_doc_details} />

            {self.render_content(id_prefix, context)}

        </DocPart>
