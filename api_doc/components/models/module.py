# coding: mixt

from mixt import Required, html
from mixt.contrib.css import css_vars, render_css, Modes

from ... import datatypes

from ..doc import DocPart, DocHeader
from .base_container import _BaseContainer
from . import Class


class Module(_BaseContainer):
    __kind__ = 'module'
    __functions_kind__ = 'functions'
    __functions_kind_title__ = 'Functions'

    class PropTypes:
        _class: str = "doc-part module"
        obj: Required[datatypes.Module]

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        colors = context.styles.colors

        _target = "&:hover, &:target, &.focus-within"
        _focus = "&:hover, &:focus, &.focus-within"

        return super().render_css_global(context) + render_css({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
            ".module": {
                ".class": {
                    _target: {
                        background: colors[4],
                    },
                },
                ".class-doc-part":{
                    _focus: {
                        background: colors[5],
                    }
                },
                ".prop-types": {
                    _target: {
                        background: colors[5],
                    },
                    "&-doc-part": {
                        _focus: {
                            background: colors[6],
                        },
                    },
                    "&-props .value": {
                        _focus: {
                            background: colors[6],
                        }
                    },
                    "&-props.doc-part .value": {
                        background: colors[7],
                    }
                }
            },
            "/**": f"</{cls.__module__}.{cls.__name__}>",
        })

    def render_content(self, id_prefix, context):
        children_before, content, children_after = super().render_content(id_prefix, context)

        doc_classes = None
        obj = self.obj
        if obj.classes:
            doc_classes = <DocPart kind={self.__kind__} subkind="classes" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Classes">Classes</DocHeader>
                {[
                    <Class obj={klass} h_level={self.h_level+2} id_prefix="{id_prefix}-classes-" open open_doc_details=False/>
                    for klass in obj.classes
                ]}
            </DocPart>

        return children_before, content, doc_classes, children_after
