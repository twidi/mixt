from typing import Any, List, Optional


class DocEntry:
    pass


class SimpleDocString:
    def __init__(self, summary: List[str], details: List[List[str]]) -> None:
        self.summary = summary
        self.details = details

    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.summary[0]}"


class FunctionDocString(SimpleDocString):
    pass


class PropTypesDocString(SimpleDocString):
    pass


class ClassDocString(SimpleDocString):
    pass


class ModuleDocString(ClassDocString):
    pass


class Code:
    def __init__(self, code: str) -> None:
        self.code = code


class UnnamedValue:
    def __init__(self, type: str, doc: SimpleDocString, example: Optional[Code] = None, **kwargs) -> None:
        self.type = type
        self.doc = doc
        self.example = example
        self.has_default = 'default' in kwargs
        if self.has_default:
            self.default = kwargs['default']

    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.type}"


class NamedValue(UnnamedValue):
    def __init__(self, name: str, type: str, doc: SimpleDocString, example: Optional[Code] = None, **kwargs) -> None:
        self.name = name
        super().__init__(type, doc, example, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name} ({self.type})"


class Function(DocEntry):
    def __init__(
        self,
        name: str,
        args: List[NamedValue],
        ret: List[UnnamedValue],
        doc: FunctionDocString,
        kind: str,
        example: Optional[Code] = None,
        raises: Optional[List[NamedValue]] = None,
    ) -> None:
        self.name = name
        self.doc = doc
        self.args = args
        self.ret = ret
        self.kind = kind
        self.example = example
        self.raises = raises

    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"


class PropTypes:
    def __init__(
        self,
        props: List[NamedValue],
        doc: PropTypesDocString,
        example: Optional[Code] = None,
    ) -> None:
        self.props = props
        self.example = example
        self.doc = doc


class _BaseContainer(DocEntry):
    def __init__(
        self,
        name: str,
        attrs: List[NamedValue],
        functions: List[Function],
        doc: ClassDocString,
        example: Optional[Code] = None,
    ) -> None:
        self.name = name
        self.attrs = attrs
        self.functions = functions
        self.doc = doc
        self.example = example

    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"


class Class(_BaseContainer):

    def __init__(
        self, name: str,
        attrs: List[NamedValue],
        functions: List[Function],
        doc: ClassDocString,
        example: Optional[Code] = None,
        proptypes: Optional[PropTypes] = None,
    ) -> None:
        super().__init__(name, attrs, functions, doc, example)
        self.proptypes = proptypes


class Module(_BaseContainer):

    def __init__(
        self, name: str,
        attrs: List[NamedValue],
        functions: List[Function],
        doc: ClassDocString,
        classes: List[Class],
        example: Optional[Code] = None,
    ) -> None:
        super().__init__(name, attrs, functions, doc, example)
        self.classes = classes
