from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from mixt import Element, Required, html as h

from ... import types


class Code(Element):
    class PropTypes:
        code: Required[types.Code]

    @classmethod
    def render_css_global(cls, context):
        # fmt: off

        # language=CSS
        return """
/* <components.models.code.Code> */
        """ + HtmlFormatter().get_style_defs(".code") + """
.code {
    display: inline-block;
    background: transparent;
    margin-top: 5px;
}
.code > pre {
    display: inline-block;
    margin: 0;
    overflow: auto;
}
/* </components.models.code.Code> */
        """
        # fmt: on

    def render(self, context):
        return h.Raw(
            highlight(self.code.code, PythonLexer(), HtmlFormatter(cssclass="code"))
        )
