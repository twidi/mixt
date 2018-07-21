from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, get_lexer_by_name

from mixt import Element, Required, h
from mixt.contrib.css import css_vars, render_css, Modes
from mixt.exceptions import InvalidChildrenError


class SourceCode(Element):
    class PropTypes:
        language: str = "text"

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        return render_css({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
        }) + HtmlFormatter().get_style_defs(".code") + "\n" + render_css({
            ".code": {
                display: block,
                background: transparent,
                margin-top: 5*px,
                "> pre": {
                    display: inline-block,
                    margin: 0,
                    overflow: auto,
                    white-space: pre,
                }
            },
            "/**": f"</{cls.__module__}.{cls.__name__}>",
        })

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
