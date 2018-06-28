# coding: mixt

from mixt import Element, Required

from ... import types
from ..generic import SourceCode


class Code(Element):
    class PropTypes:
        code: Required[types.Code]

    def render(self, context):
        return <SourceCode language={self.code.language}>{self.code.code}</SourceCode>
