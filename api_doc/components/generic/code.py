from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, get_lexer_by_name

from mixt import Element, Required, h
from mixt.exceptions import InvalidChildrenError


class SourceCode(Element):
    class PropTypes:
        language: str = "text"

    @classmethod
    def render_css_global(cls, context):
        # fmt: off

        # language=CSS
        return """
/* <components.generic.code.SourceCode> */
        """ + HtmlFormatter().get_style_defs(".code") + """
.code {
    display: block;
    background: transparent;
    margin-top: 5px;
}
.code > pre {
    display: inline-block;
    margin: 0;
    overflow: auto;
    white-space: pre;
}
/* </components.generic.code.SourceCode> */
        """
        # fmt: on

    def append(self, child_or_children):
        if len(self.__children__):
            raise InvalidChildrenError(self.__display_name__, "cannot have more than one child")
        super().append(child_or_children)

    def prepend(self, child_or_children):
        if len(self.__children__):
            raise InvalidChildrenError(self.__display_name__, "cannot have more than one child")
        super().prepend(child_or_children)

    def render(self, context):
        lexer = get_lexer_by_name(self.language, stripall=True)
        return h.Raw(
            highlight(str(self.children()[0]), lexer, HtmlFormatter(cssclass="code"))
        )
