# coding: mixt

from mixt import Element, Required

from ... import datatypes
from ..generic import SourceCode


class Code(Element):
    class PropTypes:
        code: Required[datatypes.Code]

    def render(self, context):
        return <SourceCode language={self.code.language}>{self.code.code}</SourceCode>
