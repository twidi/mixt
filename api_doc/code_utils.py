import inspect
import re
from textwrap import _leading_whitespace_re
from types import FunctionType
from typing import List, Optional, Set, Tuple, Type

from numpydoc.docscrape import NumpyDocString

from mixt import Choices, DefaultChoices, NotProvided
from mixt.internal.proptypes import BasePropTypes

from .types import (
    Class,
    ClassDocString,
    Code,
    Function,
    FunctionDocString,
    Module,
    ModuleDocString,
    NamedValue,
    PropTypes,
    PropTypesDocString,
    SimpleDocString,
    UnnamedValue,
)


def resolve_proptypes(proptypes: BasePropTypes, only: Optional[List[str]] = None) -> PropTypes:
    docstring = load_docstring(proptypes)

    if only is None:
        props = proptypes.__types__.items()
    elif only:
        props = ((name, proptypes.__types__[name]) for name in only)
    else:
        return None

    result = []
    for name, type in props:

        kwargs = {}
        if type in [Choices, DefaultChoices]:
            kwargs['default'] = getattr(proptypes, name)
        else:
            default = proptypes.__default__(name)
            if default is not NotProvided:
                kwargs['default'] = default

        doc = ((docstring.get("Attributes") or {}).get(name) or {}).get("doc") or [[], []]

        prop_type = simplify_type(type)
        if proptypes.__is_required__(name):
            prop_type = f"Required[{prop_type}]"

        result.append(NamedValue(
            name=name,
            type=prop_type,
            doc=SimpleDocString(doc[0], doc[1]),
            **kwargs
        ))

    return PropTypes(
        props=result,
        doc=PropTypesDocString(
            summary=docstring.get("Summary") or "",
            details=docstring.get("Extended Summary") or [],
        ),
        example=Code(code=docstring["Examples"]) if docstring.get("Examples") else None,
    )


def resolve_class(klass: Type, attrs: List[str], methods: List[str], name: str, only_proptypes: Optional[List[str]] = None) -> Class:
    docstring = load_docstring(klass)

    return Class(
        name=name or klass.__name__,
        attrs=[
            resolve_attribute(
                klass,
                name,
                ((docstring.get("Attributes") or {}).get(name) or {}).get("doc") or [[], []],
            )
            for name in attrs
        ],
        functions=[
            resolve_function(name, getattr(klass, name), method_type(klass, name))
            for name in methods
        ],
        doc=ClassDocString(
            summary=docstring.get("Summary") or "",
            details=docstring.get("Extended Summary") or [],
        ),
        example=Code(code=docstring["Examples"]) if docstring.get("Examples") else None,
        proptypes=resolve_proptypes(klass.PropTypes, only=only_proptypes) if hasattr(klass, 'PropTypes') else None
    )


def resolve_module(module: Type, attrs: List[str], functions: List[str], classes: List[str], name: str) -> Module:
    docstring = load_docstring(module)

    return Module(
        name=name or module.__name__,
        attrs=[
            resolve_attribute(
                module,
                name,
                ((docstring.get("Attributes") or {}).get(name) or {}).get("doc") or [[], []],
            )
            for name in attrs
        ],
        functions=[
            resolve_function(name, getattr(module, name), 'function')
            for name in functions
        ],
        doc=ModuleDocString(
            summary=docstring.get("Summary") or "",
            details=docstring.get("Extended Summary") or [],
        ),
        example=Code(code=docstring["Examples"]) if docstring.get("Examples") else None,
        classes=[
            resolve_class(
                klass=getattr(module, class_name),
                attrs=[],
                methods=[],
                name=class_name,
            )
            for class_name in classes
        ]
    )


def resolve_attribute(klass: Type, name: str, doc: List) -> NamedValue:
    kwargs = {}
    try:
        kwargs['default'] = getattr(klass, name)
    except AttributeError:
        pass

    return NamedValue(
        name=name,
        type=get_attribute_type(klass, name),
        doc=SimpleDocString(summary=doc[0], details=doc[1]),
        **kwargs
    )


def resolve_function(name: str, func: FunctionType, kind: str = 'function') -> Function:
    docstring = load_docstring(func)
    arg_types, return_types = get_function_types(func)
    args_info = get_args_info(func) if arg_types else {}

    return Function(
        name=name,
        args=[
            resolve_function_argument(name, arg_type, docstring, args_info)
            for name, arg_type in arg_types.items()
        ],
        ret=resolve_function_return(return_types, docstring),
        doc=FunctionDocString(
            summary=docstring.get("Summary") or [],
            details=docstring.get("Extended Summary") or [],
        ),
        kind=kind,
        example=Code(code=docstring["Examples"]) if docstring.get("Examples") else None,
        raises=[
            NamedValue(
                name=name,
                type='',
                doc=SimpleDocString(
                    summary = doc[0],
                    details = doc[1],
                )
            )
            for name, doc in docstring["Raises"].items()
        ] if docstring.get("Raises") else None,
    )


def resolve_function_argument(name, arg_type, func_docstring, args_info):
    real_name = (args_info.get(name) or {}).get('name') or name

    params_doc = func_docstring.get("Parameters") or {}
    doc = [[], []]
    if params_doc.get(name):
        doc = params_doc[name].get("doc") or doc
    elif params_doc.get(real_name):
        doc = params_doc[real_name].get("doc") or doc

    kwargs = {}
    if (args_info.get(name) or {}).get('default', inspect.Parameter.empty) is not inspect.Parameter.empty:
        kwargs['default'] = args_info[name]['default']

    return NamedValue(
        name=real_name,
        type=arg_type,
        doc=SimpleDocString(summary=doc[0], details=doc[1]),
        **kwargs
    )


def resolve_function_return(return_type, func_docstring):
    if not func_docstring.get("Returns"):
        return [UnnamedValue(type=return_type, doc=SimpleDocString([], []))]

    return [
        UnnamedValue(
            type=ret["type"],
            doc=SimpleDocString(summary=ret["doc"][0], details=ret["doc"][1])
        )
        for ret in func_docstring["Returns"]
    ]


re_new_doc_line = re.compile("[ \-*]|\d+\.")


def enhance_multilines_doc(doc, name):
    if not doc.get(name):
        doc[name] = [[]]
        return

    groups = [[]]
    for line in doc[name]:
        if not line.strip():
            if groups[-1]:
                groups.append([])
            continue
        if re_new_doc_line.match(line):
            groups[-1].append(line)
        else:
            if not groups[-1]:
                groups[-1].append("")
            groups[-1][-1] += f" {line}"

    if len(groups) > 1 and not groups[-1]:
        groups.pop()

    doc[name] = groups


def enhance_attributes(doc, name, types=None):
    if not doc.get(name):
        doc[name] = {}
        return
    if not types:
        types = {}
    result = {}
    for attr_name, attr_type, attr_doc in doc[name]:
        if ":" in attr_name:
            attr_name, attr_type = attr_name.split(":")
        if attr_name in types:
            attr_type = simplify_type(types[attr_name])
        attr_result = {"type": attr_type, "doc": attr_doc}
        enhance_multilines_doc(attr_result, "doc")
        attr_result["doc"] = [attr_result["doc"][0], attr_result["doc"][1:]]
        result[attr_name] = attr_result
    doc[name] = result


def enhance_return(doc, name, types=None):
    if not doc.get(name):
        doc[name] = []
        return
    if not types:
        types = {}

    return_types = []
    if types.get("return"):
        return_type = types["return"]
        if getattr(return_type, "__origin__", None) is Tuple:
            if len(return_type.__args__) == len(doc["Returns"]):
                return_types = [
                    simplify_type(ret_type) for ret_type in return_type.__args__
                ]
        elif len(doc["Returns"]) == 1:
            return_types = [simplify_type(return_type)]
    if not return_types:
        return_types = [simplify_type(ret_type) for ret_type, *__ in doc[name]]
    result = []
    for index, (*__, ret_doc) in enumerate(doc[name]):
        return_result = {"type": return_types[index], "doc": ret_doc}
        enhance_multilines_doc(return_result, "doc")
        return_result["doc"] = [return_result["doc"][0], return_result["doc"][1:]]
        result.append(return_result)
    doc[name] = result


def enhance_raises(doc, name):
    if not doc.get(name):
        doc[name] = {}
        return

    raises = {}
    for exc, __, raise_doc in doc[name]:
        data = {"doc": raise_doc}
        enhance_multilines_doc(data, "doc")
        raises[exc] = [data["doc"][0], data["doc"][1:]]

    doc[name] = raises


def normalize_docstring(docstring):
    lines = docstring.split("\n")
    if lines and lines[0] and not lines[0].startswith(" "):
        # ok we have to reindent this line
        non_empty_lines = [line for line in lines[1:] if line]
        if non_empty_lines:
            indent = _leading_whitespace_re.findall(non_empty_lines[0])[0]
            docstring = indent + docstring
    return docstring


def load_docstring(obj):

    if obj not in load_docstring.cache:

        docstring = normalize_docstring(getattr(obj, "__doc__", None) or "")
        doc = dict(NumpyDocString(docstring))

        enhance_multilines_doc(doc, "Summary")
        enhance_multilines_doc(doc, "Extended Summary")
        if doc["Extended Summary"] == [[]]:
            doc["Extended Summary"] = []
        doc["Summary"], *more_doc = doc["Summary"]
        if more_doc:
            doc["Extended Summary"] = more_doc + doc["Extended Summary"]

        if isinstance(obj, type):
            enhance_attributes(doc, "Attributes", getattr(obj, "__annotations__", {}))
            for base in obj.__mro__[1:-1]:
                base_doc = load_docstring(base)
                for name in base_doc.get("Attributes", {}).keys():
                    if name not in doc["Attributes"]:
                        doc["Attributes"][name] = base_doc["Attributes"][name]
        else:
            annotations = getattr(obj, '__annotations__', {})
            enhance_attributes(doc, "Parameters", annotations)
            klass = get_class_that_defined_method(obj)
            if klass:
                for base in klass.__mro__[:-1]:
                    try:
                        base_obj = getattr(base, obj.__name__)
                    except AttributeError:
                        continue
                    if base_obj is obj:
                        continue
                    try:
                        if base_obj.__func__ is obj.__func__:
                            continue
                    except AttributeError:
                        pass
                    base_doc = load_docstring(base_obj)
                    for name in base_doc["Parameters"].keys():
                        if name not in doc["Parameters"]:
                            doc["Parameters"][name] = base_doc["Parameters"][name]
            enhance_return(doc, "Returns",annotations)
            enhance_raises(doc, "Raises")

        if doc.get("Examples"):
            doc["Examples"] = "\n".join(doc["Examples"])


        load_docstring.cache[obj] = doc

    return load_docstring.cache[obj]


load_docstring.cache = {}


type_simplify_regexps = [
    re.compile("_ForwardRef\('([^']*)'\)"),
    re.compile("<class '([^']*)'>"),
]


def simplify_type(type_):
    result = str(type_)\
        .replace("typing.", "")\
        .replace("NoneType", "None")\
        .replace("mixt.internal.base.", "")\
        .replace("mixt.internal.html.", "")\
        .replace("mixt.element.", "")\
        .replace("mixt.proptypes.", "")
    for regexp in type_simplify_regexps:
        result = regexp.sub("\g<1>", result)
    return result\
        .replace('"', '')\
        .replace("'", '')



def get_function_types(func):
    annotations = getattr(func, '__annotations__', {})
    return (
        {
            name: simplify_type(arg_type)
            for name, arg_type in annotations.items()
            if name != "return"
        },
        simplify_type(annotations.get("return", 'Any')),
    )


def get_attribute_type(klass, name):
    if hasattr(klass, '__mro__'):
        for base in klass.__mro__:
            if name in getattr(base, "__annotations__", {}):
                return simplify_type(base.__annotations__[name])
    return ""


def get_class_that_defined_method(method):
    # https://stackoverflow.com/a/25959545
    if inspect.ismethod(method):
        for cls in inspect.getmro(method.__self__.__class__):
            if cls.__dict__.get(method.__name__) is method:
                return cls
        method = method.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(method):
        cls = getattr(
            inspect.getmodule(method),
            method.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0],
        )
        if isinstance(cls, type):
            return cls
    return getattr(method, "__objclass__", None)  # handle special descriptor objects


def method_type(klass, name):
    from .insect_mate import is_class_method, is_property_method, is_regular_method, is_static_method
    if is_regular_method(klass, name):
        return 'method'
    if is_class_method(klass, name):
        return 'classmethod'
    if is_static_method(klass, name):
        return 'staticmethod'
    if is_property_method(klass, name):
        return 'property'

    return None


def get_args_info(func):
    signature = inspect.signature(func)
    return {
        k: {
            'default': v.default,
            'name': f"*{k}" if v.kind is inspect._ParameterKind.VAR_POSITIONAL
                    else f"**{k}" if v.kind is inspect._ParameterKind.VAR_KEYWORD
                    else k
        }
        for k, v in signature.parameters.items()
    }

