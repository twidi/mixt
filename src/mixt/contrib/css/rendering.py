"""Tools to render a "dict" representing some CSS into a CSS string."""

from types import GeneratorType
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple, Union

from .modes import Modes, get_default_mode
from .units import QuantifiedUnit
from .utils import dict_hash
from .vars import Combine, Comment, Extend, Override, Raw, combine, join, many


def render_css(css: Union[Dict, Combine], mode: Optional[Modes] = None) -> str:
    """Convert some CSS given as a dict, to a string.

    Parameters
    ----------
    css : Union[Dict, Combine]
        The CSS, as a dict or an instance of ``Combine``, to render.
    mode : Modes
        The rendering mode to use. When not set/set to ``None``, the "default mode" will be used.
        See ``set_default_mode`` and ``override_default_mode`` to change it.

    Returns
    -------
    str
        The CSS as a string.

    """
    if mode is None:
        mode = get_default_mode()

    return _render_css("", css, mode.value)


_RAW_KEY: str = "::RAW::"

_SELECTOR_TEMPLATE: str = "".join(
    """
%(indent)s %(SELECTOR)s %(space)s
{
    %(opening_endline)s

    %(DECLARATIONS)s

    %(closing_endline)s
    %(indent_end)s
}
%(sel_after_endline)s
""".split()
)
_RAW_TEMPLATE: str = "".join(
    """
%(DECLARATIONS)s
%(sel_after_endline)s
""".split()
)

_NO__SELECTOR_TEMPLATE: str = "".join(
    """
%(DECLARATIONS)s
%(closing_endline)s
""".split()
)

_DECLARATION_TEMPLATE: str = "".join(
    """
%(indent)s
%(KEY)s : %(space)s %(VALUE)s
%(semicolon)s
""".split()
)

_DECLARATION_NO_VALUE_TEMPLATE: str = "".join(
    """
%(indent)s
%(KEY)s
%(semicolon)s
""".split()
)
_RAW_DECLARATION_TEMPLATE: str = "".join(
    """
%(indent)s
%(VALUE)s
""".split()
)


def _render_selector(
    selector: str,
    declarations: List[Tuple[str, Union[str, None]]],
    conf: Dict,
    level: int,
    force_indent: str,
) -> str:
    """Render a selector with its list of declarations.

    Parameters
    ----------
    selector : str
        The selector to render
    declarations : List[Tuple[str, Union[str, None]]]
        The list of declarations to render for this selector.
        Each declaration is a tuple with key and value.
        The value can be ``None``. In this case, only the part before the ``:`` is rendered.
    conf : Dict
        Configuration on how to render the selector.
    level : int
        In indent mode, the indentation level to use.
    force_indent : str
        Indentation to force use if not in indent mode.
        Use for @ rules to indent their children in some mode.s

    Returns
    -------
    str
        The CSS for this selector as a string.

    """
    if not declarations:
        return ""

    selector = selector.strip()

    last_decl_index: int = len(declarations) - 1

    if not selector or (selector == _RAW_KEY and not conf["indent_children"]):
        level = level - 1

    css_declarations: str = conf["decl_endline"].join(
        (
            _DECLARATION_NO_VALUE_TEMPLATE
            if value is None
            else _RAW_DECLARATION_TEMPLATE
            if key == _RAW_KEY
            else _DECLARATION_TEMPLATE
        )
        % {
            "KEY": key,
            "VALUE": value,
            "indent": (
                (force_indent if index else "")
                + conf["indent"] * (level + conf["decl_incr"])
            )
            if "\n" in conf["decl_endline"] or not index
            else "",
            "space": conf["space"],
            "semicolon": ";" if index != last_decl_index or conf["last_semi"] else "",
        }
        for index, (key, value) in enumerate(declarations)
    )

    if (
        declarations
        and declarations[-1][0] == _RAW_KEY
        and conf["closing_endline"] == " "
    ):
        conf = dict(conf, closing_endline="\n")

    if selector == _RAW_KEY:
        stack_result = _RAW_TEMPLATE % {
            "DECLARATIONS": css_declarations,
            "sel_after_endline": conf["sel_after_endline"],
        }
    elif selector:
        stack_result = _SELECTOR_TEMPLATE % {
            "SELECTOR": selector,
            "DECLARATIONS": css_declarations,
            "indent": force_indent + conf["indent"] * level,
            "indent_end": (conf["indent"] * (level + conf["indent_closing_incr"]))
            if "\n" in conf["closing_endline"]
            else "",
            "endline": conf["endline"],
            "space": conf["space"],
            "sel_after_endline": conf["sel_after_endline"],
            "opening_endline": conf["opening_endline"],
            "closing_endline": conf["closing_endline"],
        }
    else:
        stack_result = _NO__SELECTOR_TEMPLATE % {
            "DECLARATIONS": css_declarations,
            "closing_endline": conf["closing_endline"],
        }

    declarations.clear()
    return stack_result


def _compose_selector(parent_key: str, child_key: Union[str, Sequence[str]]) -> str:
    """Compose the final selector for a `parent_key` and a `child_key`.

    - Both keys will be split on comma (except for `child_key` if already a sequence)
    - child keys not containing "&" will be prefixed with "& "
    - the product of both list will be generated

    Parameters
    ----------
    parent_key : str
        The parent keys. The left part(s) of the list of the final selectors.
    child_key : str
        The child keys. The right part(s) of the list of the final selectors.

    Returns
    -------
    str
        The final selector.

    Examples
    --------
    >>> _compose_selector('p, div', 'em, strong, &:after')
    'p em, p strong, p:after, div em, div strong, div:after'

    """
    if isinstance(child_key, str):
        child_key = child_key.split(",")

    if parent_key:
        parent_parts = [sel_part.strip() for sel_part in parent_key.split(",")]
        if child_key:
            child_parts = [
                child_part
                if "&" in child_part
                else (f"& {child_part}" if child_part else "&")
                for child_part in [child_part.strip() for child_part in child_key]
            ]
        else:
            child_parts = ["&"]

        return ", ".join(
            child_part.replace("&", parent_part)
            for parent_part in parent_parts
            for child_part in child_parts
        )

    return ", ".join(key_part.strip().replace("&", "") for key_part in child_key)


def _contains_properties(css: Union[Dict[str, Any], Combine]) -> bool:
    """Check if the css has some properties or only other selectors.

    Parameters
    ----------
    css : Union[Dict[str, Any], Combine]
        The css to check for properties

    Returns
    -------
    bool
        ``True`` if the given CSS has some properties, or ``False`` if it
        only contains dicts for sub-selectors.

    """
    for value in css.values():
        if not isinstance(value, (dict, Extend)):
            return True

    return False


class RenderingExtend(NamedTuple):
    """Data structure to save an extend during the rendering process."""

    name: str
    css: Union[Dict[str, Any], Combine]
    selectors: List[str]


def _render_css(  # noqa: 37  # pylint: disable=too-many-branches,too-many-locals
    selector: str,
    css: Union[Dict, Combine],
    conf: Dict,
    level: int = -1,
    force_indent: str = "",
    no_indent_min_level: int = 0,
    extends: Optional[Dict[str, RenderingExtend]] = None,
) -> str:
    """Convert some CSS given as a dict, to a string, recursively.

    Parameters
    ----------
    selector : str
        The base selector. Will be present before the opening ``{``.
    css : Dict
        The CSS, as a dict or an instance of ``Combine``, to render.
    conf : Dict
        Configuration on how to render the css.
    level : int
        In indent mode, the indentation level to use.
    force_indent : str
        Indentation to force use if not in indent mode.
        Use for @ rules to indent their children in some modes.
    no_indent_min_level : int
        Level to force use if not in indent mode.
        Use for @ rules to indent their children in some modes.
    extends : Dict[str, RenderingExtend]
        The already defined extends that can be used. Default to ``None``.

    Returns
    -------
    str
        The CSS as a string.

    Raises
    ------
    ValueError
        If a tuple is used for a property or a @ rule.

    """
    declarations: List[Tuple[str, Union[str, None]]] = []
    comments: List[Tuple[str, Union[str, None]]] = []
    result: str = ""

    selector = selector.strip()

    next_level: int = level + 1 if conf["indent_children"] else no_indent_min_level

    _extends: Dict[str, RenderingExtend] = extends or {}

    new_extends: List[str] = []

    render_selector_level: int = level if conf[
        "indent_children"
    ] else no_indent_min_level

    stack: List[Tuple[str, Union[Dict, str]]] = list(css.items())

    def register_extend(
        dct: Union[Dict[str, Any], Combine], name: Optional[str] = None
    ) -> str:
        """Register a new extend.

        A registered extend can then by used by the hash of the dict (obtained by calling
        ``dict_hash(dct)``), or, if given, by the name.

        Parameters
        ----------
        dct : Union[Dict[str, Any], Combine]
            The dict, or an instance of ``Combine``, to use as a new extend.
        name : str
            If given, this extend can be used by this name.

        Returns
        -------
        str
            The hash of ``dtc`.

        Raises
        ------
        ValueError
            If the name is invalid or already defined for another extend.

        """
        if name is not None:
            name = name.strip()
            if not name[1:]:
                raise ValueError("An extend must have a name: it cannot be `%` alone")
            if name in _extends:
                raise ValueError(f"The extend `{name}` already exists")

        dct_hash = str(dict_hash(dct) if isinstance(dct, dict) else hash(dct))
        if dct_hash not in _extends:
            _extends[dct_hash] = RenderingExtend("", dct, [])

            # put string in result that will be replaced at the end
            nonlocal result
            result += f"<extend:{dct_hash}>"  # pylint: disable=undefined-variable
            new_extends.append(dct_hash)

        if name:
            _extends[name] = _extends[dct_hash] = RenderingExtend(
                name, dct, _extends[dct_hash][2]
            )

        return dct_hash

    def use_extend(
        selector: str, extend: Union[str, Dict[str, Any], Combine, Extend]
    ) -> None:
        """Use the `extend` for the given `selector`.

        Parameters
        ----------
        selector : str
            The selector for which to use the given `extend`.
        extend : Union[str, Dict[str, Any], Combine, Extend]
            The extend to use.

        Raises
        ------
        ValueError
            If `extend` is given as a name and there is no extend with this name.

        """
        if isinstance(extend, (dict, Combine)):
            key = register_extend(extend)

        elif isinstance(extend, Extend):
            for sub_extend in extend.extends:
                use_extend(selector, sub_extend)
            if extend.css:
                use_extend(selector, extend.css)
            return

        else:
            key = f"%{extend}"
            if key not in _extends:
                raise ValueError(
                    f"Cannot extend `{selector}` with undefined/not yet defined `{key}`"
                )

        _extends[key][2].append(selector)

    def render_current_stack(merge_comments: bool) -> None:
        """Render and clean the current stack.

        Parameters
        ----------
        merge_comments : bool
            If ``True``, the comments in the stack will be rendered in the same selector
            as the declarations. If ``False``, the default, they will be rendered after.

        """
        nonlocal result
        if declarations:
            if merge_comments:
                if comments:
                    declarations.extend(comments)
                comments.clear()
            result += _render_selector(
                selector, declarations, conf, render_selector_level, force_indent
            )
        if comments:
            result += _render_selector(
                _RAW_KEY, comments, dict(conf, decl_incr=1), render_selector_level, ""
            )

    while stack:  # pylint: disable=too-many-nested-blocks
        key: Union[str, Sequence[str]]
        value: Any

        key, value = stack.pop(0)

        if isinstance(value, (dict, Combine)):
            render_current_stack(merge_comments=False)

            if isinstance(key, GeneratorType):
                key = tuple(key)
            if isinstance(key, QuantifiedUnit):
                # keys of keyframes can be "75%" for example
                key = str(key)

            if isinstance(key, str) and key.startswith("%"):
                register_extend(value, key)

            elif isinstance(key, str) and key.startswith("@"):
                if _extends:
                    value = combine(
                        {
                            ext.name or f"%{ext_key}": ext.css
                            for ext_key, ext in _extends.items()
                            if not ext_key.startswith("%")
                        },
                        value,
                    )

                at_rule_declarations: str = _render_css(
                    selector,
                    value,
                    conf,
                    next_level,
                    force_indent=force_indent + conf["force_indent_rule_children"],
                    no_indent_min_level=no_indent_min_level + 1,
                ).rstrip(conf["endline"])

                result += _SELECTOR_TEMPLATE % {
                    "SELECTOR": key,
                    "DECLARATIONS": at_rule_declarations,
                    "indent": conf["indent"] * next_level,
                    "indent_end": conf["indent"]
                    * (next_level + conf["indent_closing_incr"]),
                    "endline": conf["endline"],
                    "space": conf["space"],
                    "sel_after_endline": conf["sel_after_endline"],
                    "opening_endline": conf["sel_after_endline"],  # on purpose
                    "closing_endline": conf["closing_endline"],
                }

            elif not isinstance(key, str) and [k for k in key if k.startswith("@")]:
                raise ValueError(
                    f"A CSS @ rule must be a string, not a {type(key).__name__}: {key}"
                )

            elif not isinstance(key, str) and [k for k in key if k.startswith("%")]:
                raise ValueError(
                    f"An extend must be a string, not a {type(key).__name__}: {key}"
                )

            else:

                if _contains_properties(value):
                    sub_level = next_level
                else:
                    sub_level = (
                        level if conf["indent_children"] else no_indent_min_level
                    )

                result += _render_css(
                    _compose_selector(selector, key),
                    value,
                    conf,
                    sub_level,
                    force_indent,
                    no_indent_min_level,
                    _extends,
                )

        elif isinstance(value, Extend):

            child_selector = _compose_selector(selector, key)
            for extend in value.extends:
                use_extend(child_selector, extend)

            stack.insert(0, (key, value.css or {}))

        else:
            if not isinstance(key, str):
                raise ValueError(
                    f"A CSS property must be a string, not a {type(key).__name__}: {key}"
                )

            if key.startswith("%"):
                raise ValueError(f"A CSS property cannot start with %: {key}")

            if key.startswith(Comment.prefix):
                if conf["display_comments"]:
                    lines = value.split("\n")
                    for index, line in enumerate(lines):
                        declaration = line.strip()
                        if index == 0:
                            declaration = f"/* {declaration}"
                        else:
                            declaration = f"   {declaration}"
                        if index == len(lines) - 1:
                            declaration = f"{declaration} */"
                        comments.append((_RAW_KEY, declaration))
                continue

            if comments:
                declarations += comments
                comments = []

            if key.startswith(Raw.prefix):
                render_current_stack(merge_comments=True)

                content: str
                for content in [value] if isinstance(value, str) else value:
                    declarations.extend(
                        (_RAW_KEY, line.strip()) for line in content.split("\n")
                    )
                result += _render_selector(
                    _RAW_KEY,
                    declarations,
                    dict(
                        conf,
                        decl_incr=1,
                        # closing_endline="\n"
                        # if conf["closing_endline"] == " "
                        # else conf["closing_endline"],
                    ),
                    render_selector_level,
                    "",
                )
                continue

            if value is None:
                declarations.append((key, None))

            else:
                values: List[Union[str, tuple, list]] = list(
                    value.declarations
                ) if isinstance(value, Override) else [value]

                for one_value in values:
                    if isinstance(one_value, tuple):
                        one_value = join(*one_value)
                    elif isinstance(one_value, list):
                        one_value = many(*one_value)

                    declarations.append((key, one_value))

    render_current_stack(merge_comments=True)

    def get_ext_selectors(ext_selectors: List[str]) -> List[str]:
        """Get the final list of selectors for an extend.

        All selectors in `ext_selectors` will be added, and the ones starting with a ``%``
        will be replaced by another call to this function with the selectors from the extend
        defined by this name.

        Parameters
        ----------
        ext_selectors : List[str]
            The list of selectors to resolve.

        Returns
        -------
        List[str]
            The final list of selectors.

        """
        result_selectors: List[str] = []
        for ext_selector in ext_selectors:
            if not ext_selector.startswith("%"):
                result_selectors.append(ext_selector)
                continue
            result_selectors += get_ext_selectors(_extends[ext_selector].selectors)
        return result_selectors

    for extend_key in new_extends:
        # extract by the dict hash
        new_extend = _extends.pop(extend_key)
        # remove if we also have the name
        if new_extend.name:
            del _extends[new_extend.name]

        extend_css = (
            _render_css(
                ", ".join(get_ext_selectors(new_extend.selectors)),
                new_extend.css,
                conf,
                next_level,
                force_indent,
                no_indent_min_level,
                _extends,
            )
            if new_extend.css and new_extend.selectors
            else ""
        )

        replace_key = f"<extend:{extend_key}>"
        result = result.replace(replace_key, extend_css, 1).replace(replace_key, "")

    return result
