# coding: mixt

from mixt import Element, Required, html
from mixt.contrib.css import css_vars, CssDict

from ... import datatypes
from ..doc import DocPart, DocHeader
from . import Code, DocString, NamedValue


class PropTypes(Element):

    class PropTypes:
        id_prefix: str = ''
        h_level: int = 3
        obj: Required[datatypes.PropTypes]

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        colors = context.styles.colors

        _target = "&:hover, &:target, &.focus-within"
        _focus = "&:hover, &:focus, &.focus-within"

        return CssDict({
            comment(): f"<{cls.__module__}.{cls.__name__}>",
            ".prop_types": {
                _target: {
                    background: colors[3],
                },
                "&-doc-part, &-props .value": {
                    _focus: {
                        background: colors[4],
                    },
                },
                "&-props-doc-part .value": {
                    _focus: {
                        background: colors[5],
                    }
                }
            },
            comment(): f"</{cls.__module__}.{cls.__name__}>",
        })

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
