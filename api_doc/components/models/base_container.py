# coding: mixt

from mixt import DefaultChoices, Element, html

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

    @classmethod
    def render_css_global(cls, context):
        if cls is _BaseContainer:
            return ""

        # language=CSS
        return """
/* <components.models.base_container._BaseContainer.%(name)s> */
.%(kind)s > summary > .h:after { 
    %%(TAG)s
    %%(HL)s
    content: "%(kind)s";
}

.%(kind)s:hover,
.%(kind)s:target,
.%(kind)s.focus-within {
    background: %%(BG2)s;
}
.%(kind)s-doc-part:hover,
.%(kind)s-doc-part:focus,
.%(kind)s-doc-part.focus-within {
    background: %%(BG3)s;
}
.%(kind)s-attributes .value:hover,
.%(kind)s-attributes .value:focus, 
.%(kind)s-attributes .value.focus-within, 
.%(kind)s-%(functions_kind)s .function:hover,
.%(kind)s-%(functions_kind)s .function:focus,
.%(kind)s-%(functions_kind)s .function.focus-within {
    background: %%(BG4)s;
}
.%(kind)s-%(functions_kind)s .function-doc-part:hover,
.%(kind)s-%(functions_kind)s .function-doc-part:focus,
.%(kind)s-%(functions_kind)s .function-doc-part:focus-within {
    background: %%(BG5)s;
}
.%(kind)s-%(functions_kind)s .value:hover,
.%(kind)s-%(functions_kind)s .value:focus,
.%(kind)s-%(functions_kind)s .value.focus-within {
    background: %%(BG6)s;
}
/* </components.models.base_container._BaseContainer.%(name)s> */
        """ % {
            'kind': cls.__kind__,
            'functions_kind': cls.__functions_kind__,
            'name': cls.__name__,
        }

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
