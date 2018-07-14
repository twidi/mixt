# coding: mixt

from mixt import Element, Required, html

from ... import datatypes
from ..doc import DocPart, DocHeader
from . import Code, DocString, NamedValue


class PropTypes(Element):

    class PropTypes:
        id_prefix: str = ''
        h_level: int = 3
        obj: Required[datatypes.PropTypes]

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
/* <components.models.proptypes.PropTypes> */
.prop_types:hover,
.prop_types:target,
.prop_types.focus-within {
    background: %(BG3)s;
}
.prop_types-doc-part:hover,
.prop_types-doc-part:focus,
.prop_types-doc-part.focus-within,
.prop_types-props .value:hover,
.prop_types-props .value:focus, 
.prop_types-props .value.focus-within {
    background: %(BG4)s;
}
.prop_types-props.doc-part .value:hover,
.prop_types-props.doc-part .value:focus, 
.prop_types-props.doc-part .value.focus-within {
    background: %(BG5)s;
}
/* </components.models.proptypes.PropTypes> */
        """

    def render(self, context):
        proptypes = self.obj
        id_prefix = f'{self.id_prefix}-prop_types'

        doc_example = None
        if proptypes.example:
            doc_example = <DocPart kind="prop_types" subkind="example" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Example">Example</DocHeader>
                <Code code={proptypes.example} />
            </DocPart>

        doc_props = lambda h_level: [
            <NamedValue value={proptype} h_level={h_level} id_prefix="{id_prefix}-props-"/>
            for proptype in proptypes.props
        ]

        if doc_example:
            doc_props = <DocPart kind="prop_types" subkind="props" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Props">Props</DocHeader>
                {doc_props(self.h_level+2)}
            </DocPart>
        else:
            doc_props = <div class="prop_types-props">
                {doc_props(self.h_level+1)}
            </div>

        return <DocPart kind="prop_types" id_prefix={id_prefix} level={self.h_level} open>
            <DocHeader menu="PropTypes">PropTypes</DocHeader>
            <DocString doc={proptypes.doc} open=True />

            {doc_props}
            {doc_example}
        </DocPart>
