# coding: mixt

from mixt import Required, html

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

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        css = """
/* <components.models.module.Module> */
.module .class:hover,
.module .class:target,
.module .class.focus-within {
    background: %(BG4)s;
}
.module .class-doc-part:hover,
.module .class-doc-part:focus,
.module .class-doc-part.focus-within,
.module .prop_types:hover,
.module .prop_types:target,
.module .prop_types.focus-within {
    background: %(BG5)s;
}
.module .prop_types-doc-part:hover,
.module .prop_types-doc-part:focus,
.module .prop_types-doc-part.focus-within,
.module .prop_types-props .value:hover,
.module .prop_types-props .value:focus, 
.module .prop_types-props .value.focus-within {
    background: %(BG6)s;
}
.module .prop_types-props.doc-part .value:hover,
.module .prop_types-props.doc-part .value:focus, 
.module .prop_types-props.doc-part .value.focus-within {
    background: %(BG7)s;
}
/* </components.models.module.Module> */
        """
        return super().render_css_global(context) + css

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
