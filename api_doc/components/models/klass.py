# coding: mixt

from mixt import Required, html
from mixt.contrib.css import css_vars, CssDict

from ... import datatypes
from . import PropTypes
from .base_container import _BaseContainer


class Class(_BaseContainer):
    __kind__ = 'class'
    __functions_kind__ = 'methods'
    __functions_kind_title__ = 'Methods'

    class PropTypes:
        _class: str = "doc-part class"
        obj: Required[datatypes.Class]

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        return merge({
            "/***": f"<{cls.__module__}.{cls.__name__}>",
        }, super().render_css_global(context), {
            "/****": f"</{cls.__module__}.{cls.__name__}>",
        })

    def render_content(self, id_prefix, context):
        children_before, content, children_after = super().render_content(id_prefix, context)

        doc_proptypes = None
        obj = self.obj
        if obj.proptypes:
            doc_proptypes = <PropTypes obj={obj.proptypes} id_prefix={id_prefix} h_level={self.h_level+1} />

        return children_before, doc_proptypes, content, children_after



