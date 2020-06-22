"""Manages CSS keywords as python vars.

The idea of these vars is to have a string that can be joined with others via classical operations.

For example ``margin-bottom`` are two vars, ``margin`` and ``bottom`` and using subtract, we have
the string ``margin-bottom``.
"""

from collections import defaultdict
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from .utils import CssDict, _dict_merge, builtins, dict_hash, isbuiltin, iskeyword


class Var(str):
    """A subclass of string that does magic with operators.

    The main idea is to compose other strings (in fact, other ``Var``) when there is an operation
    on a ``Var``.

    Examples
    --------
    >>> margin = Var("margin")
    >>> bottom = Var("bottom")
    >>> margin-bottom
    'margin-bottom'

    """

    @classmethod
    def many(cls: Type["Var"], *names: str) -> List["Var"]:
        """Create many ``Var`` at once.

        Parameters
        ----------
        names : Union[str, Tuples[str, ...]]
            The names of the ``Var`` to create. If a single string, it will be splitted.

        Returns
        -------
        List[Var]
            The ``Var`` just created.

        """
        if len(names) == 1:
            names = tuple(names[0].split())
        return [cls(name) for name in names]

    def __neg__(self) -> "Var":
        """Generate a new ``Var`` by prefixing `self` with a dash.

        Returns
        -------
        Var
            The new composed ``Var``.

        Example
        -------
        >>> moz = Var("moz")
        >>> -moz
        '-moz'

        >>> border, radius = Var.many("border radius")
        >>> -moz-border-radius
        '-moz-border-radius'

        """
        if not self:
            return self
        return self.__class__(f"-{self}")

    def __sub__(self, other: Union["Var", str]) -> "Var":
        """Generate a new ``Var`` by joining `self` with `other` with a dash.

        Parameters
        ----------
        other : Union[Var, str]
            The string to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Example
        -------
        >>> margin, bottom = Var.many("margin bottom")
        >>> margin-bottom
        'margin-bottom'
        >>> top = "top"
        >>> margin-top
        'margin-top'

        """
        if not other:
            return self
        return self.__class__(f"{self}-{other}")

    def __rsub__(self, other: Any) -> "Var":
        """Generate a new ``Var`` by joining `other` with `self` with a dash.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.


        Example
        -------
        >>> top = Var("top")
        >>> margin = "margin"
        >>> margin-top
        'margin-top'

        """
        if not self:
            return self.__class__(other)
        return self.__class__(f"{other}-{self}")

    def __add__(self, other: Union["Var", str]) -> "Var":
        """Generate a new ``Var`` by joining `self` with `other` with a plus.

        Parameters
        ----------
        other : Union[Var, str]
            The string to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Example
        -------
        >>> ul, li = Var.many("ul li")
        >>> ul+li
        'ul+li'
        >>> div = "div"
        >>> li+div
        'li+div'

        """
        if not other:
            return self
        return self.__class__(f"{self}+{other}")

    def __radd__(self, other: Any) -> "Var":
        """Generate a new ``Var`` by joining `other` with `self` with a plus.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.


        Example
        -------
        >>> li = Var("li")
        >>> ul = "ul"
        >>> ul+li
        'ul+li'

        """
        if not self:
            return self.__class__(other)
        return self.__class__(f"{other}+{self}")

    def __truediv__(self, other: Any) -> "Var":
        """Generate a new Var by joining `self` and `other` with a ``/``.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        -------
        >>> foo, bar = Var.many("foo bar")
        >>> foo/bar
        'foo/bar'
        >>> qux = "qux"
        >>> foo/qux
        'foo/qux'

        """
        if not other:
            return self
        return self.__class__(f"{self}/{other}")

    def __rtruediv__(self, other: Any) -> "Var":
        """Generate a new Var by joining `other` and `self` with a ``/``.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        -------
        >>> foo, bar = Var.many("foo bar")
        >>> foo/bar
        'foo/bar'
        >>> qux = "qux"
        >>> qux/foo
        'qux/foo'

        """
        if not self:
            return self.__class__(other)
        return self.__class__(f"{other}/{self}")

    def __call__(  # pylint: disable=invalid-name
        self, *args: Any, s: str = ", "
    ) -> "Var":
        """Generate a new Var by concatenating `self` & `args` in ``()``, joining args with '`, ``.

        It is used to simulate css "functions" like rgb, gradient...

        There is a special case for ``only``, to be used in media queries. Calling ``only(screen)``
        will render ``only screen``, and not ``only(screen)``.

        Parameters
        ----------
        args : Tuple[Any, ...]
            The parts to join with a ``,``.
        s : str
            The separator between the args. Default to ``, `` but can be set for example as a space.

        Returns
        -------
        Var
            The new composed var.

        Examples
        --------
        >>> attr, data, count = Var.many("attr data count")
        >>> attr(data-count)
        'attr(data-count)'

        >>> number = Var("number")
        >>> attr(data-count, number, s=' ')  # default separator is ", ", use ``s`` to change it
        'attr(data-count number)'

        >>> linear, gradient = Var.many("linear gradient")
        >>> linear-gradient("left", "red", "blue", "red")
        'linear-gradient(left, red, blue, red)'

        >>> only, screen = Var.many("only screen")
        >>> only(screen)
        'only screen'

        """
        css_args = s.join(
            join(*arg)
            if isinstance(arg, tuple)
            else many(*arg)
            if isinstance(arg, list)
            else str(arg)
            for arg in args
        )
        if self == "only":
            return self.__class__(f"{self} {css_args}")
        return self.__class__(f"{self}({css_args})")

    def __and__(self, other: Any) -> "Var":
        """Generate a new Var by concatenating `self` and `other` with `` and ``.

        Rules:
        - If `other` is a dict, it is transformed. See ``_tovar``.
        - If one of `self` or `other` is empty ("falsy"), only the other one is rendered.
        - If both are empty, `self` is returned.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> _ = Var("")
        >>> screen, print = Var.many("screen print")
        >>> screen & print
        'screen and print'
        >>> _ & screen
        'screen'
        >>> screen & _
        'screen'
        >>> _ & _
        ''

        >>> orientation, portrait = Var.many("orientation portrait")
        >>> screen & {orientation: portrait}
        'screen and (orientation: portrait)'
        >>> _ & {orientation: portrait}
        '(orientation: portrait)'

        """
        _self = self if self and self != "not " else ""
        prepared_other: "Var" = _tovar(other, kind=self.__class__)
        if _self and prepared_other:
            return self.__class__(f"{self} and {prepared_other}")
        if self and prepared_other:
            return self.__class__(f"{self}{prepared_other}")
        if prepared_other:
            return prepared_other
        return self

    def __rand__(self, other: Any) -> "Var":
        """Generate a new Var by concatenating `other` and `self` with `` and ``.

        Rules:
        - If `other` is a dict, it is transformed. See ``_tovar``.
        - If one of `self` or `other` is empty ("falsy"), only the other one is rendered.
        - If both are empty, `self` is returned.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> _ = Var("")
        >>> screen = Var("screen")
        >>> "print" & screen
        'print and screen'
        >>> "print" & _
        'print'
        >>> "" & screen
        'screen
        >>> "" & _
        ''

        >>> orientation, portrait = Var.many("orientation portrait")
        >>> {orientation: portrait} & screen
        '(orientation: portrait) and screen'
        >>> {orientation: portrait} & _
        '(orientation: portrait)'

        """
        prepared_other: "Var" = _tovar(other, kind=self.__class__)
        if self and prepared_other:
            return self.__class__(f"{prepared_other} and {self}")
        if prepared_other:
            return prepared_other
        return self

    def __or__(self, other: Any) -> "Var":
        """Generate a new Var by concatenating `self` and `other` with `` or ``.

        When used in @-rules, its the rule that decides if the " or " should be
        replaced with something else, like ", " for @media.

        Rules:
        - If `other` is a dict, it is transformed. See ``_tovar``.
        - If one of `self` or `other` is empty ("falsy"), only the other one is rendered.
        - If both are empty, `self` is returned.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> _ = Var("")
        >>> screen, print = Var.many("screen print")
        >>> screen | print
        'screen or print'
        >>> _ | screen
        'screen'
        >>> screen | _
        'screen'
        >>> _ | _
        ''

        >>> orientation, portrait = Var.many("orientation portrait")
        >>> screen | {orientation: portrait}
        'screen or (orientation: portrait)'
        >>> _ | {orientation: portrait}
        '(orientation: portrait)'

        """
        _self = self if self and self != "not " else ""
        prepared_other: "Var" = _tovar(other, kind=self.__class__)
        if _self and prepared_other:
            return self.__class__(f"{self} or {prepared_other}")
        if self and prepared_other:
            return self.__class__(f"{self}{prepared_other}")
        if prepared_other:
            return prepared_other
        return self

    def __ror__(self, other: Any) -> "Var":
        """Generate a new Var by concatenating `other` and `self` with `` or ``.

        When used in @-rules, its the rule that decides if the " or " should be
        replaced with something else, like ", " for @media.

        Rules:
        - If `other` is a dict, it is transformed. See ``_tovar``.
        - If one of `self` or `other` is empty ("falsy"), only the other one is rendered.
        - If both are empty, `self` is returned.

        Parameters
        ----------
        other : Any
            The thing to concat.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> _ = Var("")
        >>> screen = Var("screen")
        >>> "print" | screen
        'print, screen'
        >>> "print" | _
        'print'
        >>> "" | screen
        'screen
        >>> "" | _
        ''

        >>> orientation, portrait = Var.many("orientation portrait")
        >>> {orientation: portrait} | screen
        '(orientation: portrait),  screen'
        >>> {orientation: portrait} | _
        '(orientation: portrait)'

        """
        prepared_other: "Var" = _tovar(other, kind=self.__class__)
        if self and prepared_other:
            return self.__class__(f"{prepared_other} or {self}")
        if prepared_other:
            return prepared_other
        return self

    def __invert__(self) -> "Var":
        """Generate a new Var by prefixing `self` with ``not ``.

        If self is "falsy", it is returned without being inverted.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> screen = Var("screen")
        >>> ~screen
        'not screen'

        """
        return self.__class__(f"not {self}")


def _tovar(value: Any, kind: Type["Var"] = Var) -> "Var":
    """Convert a dict/set into a ``Var`` on the format suitable for @-rules..

    It is mainly used for @-rules..

    A dict will be converted to ``(key1: value1, key2: value2)``.
    A set will be converted to ``(val1, val2)``.

    Parameters
    ----------
    value : Any
        A ``Var`` will be returned as is. A dict or a set will have a special conversion to
        a ``Var``. All other it will be simply converted to a ```Var```.
        If it's a dict , it will be converted to a ``Var``. Else it will be returned as is.
    kind : Type[Var]
        The type of ``Var`` to use for the return value. Default to ``Var``.

    Returns
    -------
    Union[Var, Any]
        A ``Var`` computed from `value` if it's a dict, else, `value`, untouched.

    Examples
    --------
    >>> _tovar({"foo": "bar"})
    '(foo: bar)'
    >>> _tovar({"foo"})
    '(foo)'
    >>> _tovar("foo")
    'foo'

    """
    if isinstance(value, Var):
        return value

    if isinstance(value, dict):
        parts = ", ".join(f"{key}: {value}" for key, value in value.items())
    elif isinstance(value, set):
        parts = ", ".join(value)
    else:
        return kind(value)

    return kind(f"({parts})")


class Join(Var):
    """``Var`` that, when called, allows to have css shortcut by joining them with spaces."""

    def __call__(self, *values: Any) -> str:  # type: ignore
        """Allow to have css shortcut by joining them with spaces.

        Note that in ``render_css``, if a tuple is encountered, it will be converted as a ``Join``
        so using ``(solid, blue, 1*px)`` will be the same as ``join(solid, blue, 1*px)``.

        Parameters
        ----------
        values : Tuple[Any, ...]
            The values to join with a space.

        Returns
        -------
        str
            The new composed string.

        Examples
        --------
        >>> from mixt.contrib.css.vars import join
        >>> border = Var("border")
        >>> color, style = "red", "solid"
        >>> {border: join(color, style, "1px")}
        {'border': 'red solid 1px'}
        >>> {border: (color, style, "1px")}
        {'border': 'red solid 1px'}

        """
        return " ".join(
            many(*value) if isinstance(value, list) else str(value) for value in values
        )


class Many(Var):
    """``Var`` that, when called, allows to have multiple css values by joining them with commas."""

    def __call__(self, *values: Any) -> str:  # type: ignore
        """Allow to have multiple css values by joining them with commas.

        Note that in ``render_css``, if a list is encountered, it will be converted as a ``Many``
        so using ``["foo", "bar", "baz"]`` will be the same as ``many("foo", "bar" "baz")``.

        Parameters
        ----------
        values : Tuple[Any, ...]
            The values to join with a comma.

        Returns
        -------
        str
            The new composed string.

        Examples
        --------
        >>> from mixt.contrib.css.units import Unit
        >>> from mixt.contrib.css.vars import join, many
        >>> color1, color2 = "red", "blue"
        >>> text, shadow = Var.many("text shadow")
        >>> px, em = Unit.many("px em")
        >>> {text-shadow: many(
        ...     join(1*px, 1*px, 2*px, color1),
        ...     join(0, 0, 1*em, color2),
        ...     join(0, 0, 0.2*em, color2),
        ... )}
        {'text-shadow': '1px 1px 2px red, 0 0 1em blue, 0 0 0.2em blue'}
        >>> {text-shadow: [
        ...     (1*px, 1*px, 2*px, color1),
        ...     (0, 0, 1*em, color2),
        ...     (0, 0, 0.2*em, color2),
        ... ]}
        {'text-shadow': '1px 1px 2px red, 0 0 1em blue, 0 0 0.2em blue'}

        """
        return ", ".join(
            join(*value) if isinstance(value, tuple) else str(value) for value in values
        )


class Override(Var):
    """``Var`` that, when called, allows to define a css key multiple times.

    Attributes
    ----------
    declarations : Sequence[str]
        The list of overridden declarations.
        Set when the instance is called with these declarations.

    """

    def __init__(self, _str_: str) -> None:  # pylint: disable=unused-argument
        """Init the var and its declarations list.

        For the parameters, see ``str``.

        """
        super().__init__()
        self.declarations: Sequence[Var] = []

    def __call__(self, *declarations: Any) -> "Override":  # type: ignore
        r"""Allow to have a css key defined multiple times.

        Parameters
        ----------
        declarations : Tuple[Any, ...]
            The different declarations to set for a key.

        Returns
        -------
        Override
            A new instance of ``Override`` with filled declarations.

        Examples
        --------
        >>> from mixt.contrib.css import render_css
        >>> from mixt.contrib.css.vars import override
        >>> col1, col2 = "blue", "red"
        >>> background, webkit, moz, ms, o, linear, gradient, left = \
        ... Var.many("background webkit moz ms o linear gradient left")
        >>> render_css({background: override(
        ...     -webkit-linear-gradient(left, col1, col2, col1),
        ...     -moz-linear-gradient(left, col1, col2, col1),
        ...     -ms-linear-gradient(left, col1, col2, col1),
        ...     -o-linear-gradient(left, col1, col2, col1),
        ...     linear-gradient(left, col1, col2, col1),
        ... )})
        {
        background: -webkit-linear-gradient(left, blue, red, blue);
        background: -moz-linear-gradient(left, blue, red, blue);
        background: -ms-linear-gradient(left, blue, red, blue);
        background: -o-linear-gradient(left, blue, red, blue);
        background: linear-gradient(left, blue, red, blue);
        }



        """
        new_obj = self.__class__(self)
        new_obj.declarations = declarations

        return new_obj


class Extend(Var):
    """``Var`` that, when called, allows to extend a previously defined css dict.

    Attributes
    ----------
    extends : Sequence[Union[str, Dict[str, Any]]]
        The list of css we extend.
        An extend can be the name of a previously defined "extend" (key starting with `%`)
        in the same css dict (same level or above), or directly a dict.
        Set when the instance is called with this extend.
    css : Optional[Union[Dict[str, Any], Combine]]
        If set, some CSS to add to the selector.

    """

    def __init__(self, _str_: str) -> None:  # pylint: disable=unused-argument
        """Init the var and its attributes.

        For the parameters, see ``str``.

        """
        super().__init__()
        self.extends: Sequence[Union[str, Dict[str, Any]]] = ""
        self.css: Optional[Union[Dict[str, Any], Combine]] = None

    def __call__(  # type: ignore
        self, *extends: Union[str, Dict[str, Any]], css: Optional[Dict[str, Any]] = None
    ) -> "Extend":
        r"""Allow to have a css key defined multiple times.

        Parameters
        ----------
        extends : Tuple[Union[str, Dict[str, Any]]]
            The list of names or dicts to extend.
        css : Union[Dict[str, Any], Combine]
            If set, some CSS to add to the selector. ``None`` by default.

        Returns
        -------
        Extend
            A new instance of ``Extend`` with filled extends.

        Examples
        --------
        >>> from mixt.contrib.css import render_css
        >>> from mixt.contrib.css.vars import extend
        >>> render_css({
        ...     "%box": {"border": "solid red 1px"},
        ...     ".foo": extend("box"),
        ...     ".bar": extend("box", css={"color": "black"}),
        ... })
        .foo, .bar {
          border: solid red 1px;
        }
        .bar {
          color: black;
        }

        """
        new_obj = self.__class__(self)
        new_obj.extends = extends
        new_obj.css = css

        return new_obj


class Raw(Var):
    """``Var`` that, when called, tells the rendered that the value should be rendered untouched.

    Attributes
    ----------
    counter : int
        Will be incremented on each call to produce a different key each time.
    prefix : str
        The beginning of the key to produce.

    """

    counter = 0
    prefix = ":raw:"

    def __call__(self) -> Var:  # type: ignore  # pylint: disable=arguments-differ
        """Generate a new unique key starting with ``:raw:``, to be used as a CSS key.

        When encountering this key, the rendered will render the value untouched., outside
        of any selector.

        Alias: ``r()``

        Returns
        -------
        str
            A new generated string with a unique key.

        """
        self.__class__.counter += 1  # type: ignore
        return Var(f"{self.prefix}{self.__class__.counter}")  # type: ignore


class Comment(Raw):
    """``Var`` that, when called, tells the rendered that the values is a CSS comment."""

    counter = 0
    prefix = "/*"

    def __call__(  # type: ignore  # pylint: disable=useless-super-delegation
        self,
    ) -> str:
        """Generate a new unique key starting with ``/*``, to be used as a CSS key.

        When encountering this key, the rendered will encapsulate the value in ``/* */`` and
        will render it.

        Alias: ``c()``

        Returns
        -------
        str
            A new generated string with a unique key.

        """
        return super().__call__()  # we need the docstring for documentation


class AtRule(Var):
    """``Var`` that, when called, allows to define a CSS '@-rule'.

    Attributes
    ----------
    if_empty : str
        A string to use if there is no args passed to ``__call__``.
    separator : str
        Default to `` or ``, it is the string that will join the different args
        passed to ``__call__``.
        If not `` or ``, all occurrences of `` or `` present in the args will be
        replaced by this value.
        Exists because @media use ``, ``, but @supports use `` or ``.
    quote_args: bool
        If ``True``, args will be put in quotes. Else, the default, they will be put as is.

    """

    if_empty: str = ""
    separator: str = " or "
    quote_args: bool = False

    def __new__(
        cls, _str_: str, if_empty: str = "", s: str = " or ", quote_args: bool = False
    ) -> "AtRule":
        """Create the ``AtRule`` and save parameters.

        Parameters
        ----------
        _str_ : str
            The string of the current ``Var``

        For the other parameters, see the class docstring (``if_empty`` and ``quote_args`` have
        the same name as the arguments to ``__new__`, but ``separator`` comes from the ``s``
        argument.

        Returns
        -------
        AtRule
            The newly created AtRule.

        """
        obj = super().__new__(cls, _str_)  # type: ignore
        obj.if_empty = if_empty
        obj.separator = s
        obj.quote_args = quote_args
        return obj

    def __call__(  # type: ignore  # pylint: disable=invalid-name
        self, *args: Any
    ) -> str:
        r"""Create a CSS @-rule declaration (@media, @support...).

        Parameters
        ----------
        args : Tuple[Any, ...]
            The args of the rule.

            An arg can be:

            - a ``Var``, like ``screen``
            - a key/value arg, in the form a of dict: ``{min-width: 30*em}``
              will become ``(min-width: 30em)``

            To use the ``and`` and ``not`` operators normally used in @-rules, you must use
            python binary operators: ``&`` and ``~``.
            To use the ``, `` operator, if it's at the first level you can separate args by a
            coma, else you must use the ``|`` python binary operator.

            If two args are to be joined by a ``&``, or if one is to be negated with ``~``,
            it must be converted to a usable dict by joining it with an empty ``Var``. See
            in examples.

        Returns
        -------
        str
            The @-rule declaration.

        Examples
        --------
        >>> from mixt.contrib.css.units import Unit
        >>> from mixt.contrib.css.vars import media

        >>> screen, print, min, width, height, orientation, portrait = \
        ... Var.many("screen print min width height orientation portrait")
        >>> em, px = Unit.many("em px")

        >>> media(screen, print)  # as it's a builtin you can also use ``_print``
        ''@media screen, print'

        >>> media({min-width: 30*em})  # no need for ``_`` as it is alone
        '@media (min-width: 30em)'
        >>> media({min-width: 30*em} & {min-height: 10*em})  # you need ``_``
        Traceback (most recent call last)
        ...
        TypeError: unsupported operand type(s) for &: 'dict' and 'dict'
        >>> _ = Var("")
        >>> media(_ & {min-width: 30*em} & {min-height: 10*em})
        '@media (min-width: 30em) and (min-height: 10em)'

        >>> media(~{min-width: 30*em})
        Traceback (most recent call last)
        ...
        TypeError: bad operand type for unary ~: 'dict'
        >>> media(~(_&{min-width: 30*em}))
        '@media not (min-width: 30em)'

        >>> media({min-height: 680*px}, screen & {orientation: portrait})  # using comma for "or"
        '@media (min-height: 680px), screen and (orientation: portrait)'

        >>> media({min-height: 680*px} | screen & {orientation: portrait})  # using pipe for "or"
        '@media (min-height: 680px), screen and (orientation: portrait)'

        """
        tovar: Callable[[Any], Var] = _tovar
        if self.quote_args:
            tovar = lambda var: Var(repr(str(_tovar(var))))

        if args:
            args = tuple(tovar(arg) for arg in args if arg)
            if self == "import":
                if len(args) > 1:
                    joined_args = " ".join([args[0], self.separator.join(args[1:])])
                else:
                    joined_args = args[0]
            else:
                joined_args = self.separator.join(args)

            if self.separator != " or ":
                joined_args = joined_args.replace(" or ", self.separator)

        else:
            joined_args = tovar(self.if_empty)

        return f"@{self} {joined_args}" if joined_args else f"@{self}"


class String(Var):
    """``Var`` that, when called, allows to print a string in quotes."""

    def __call__(  # type: ignore  # pylint: disable=arguments-differ
        self, value: Any
    ) -> str:
        """Allow to have a quoted string in css. For example for the ``content`` attribute.

        Aliases: ``str``, ``repr``

        Parameters
        ----------
        value : Any
            The value to quote. Note that the result is a call to ``repr(str(value))``.

        Returns
        -------
        str
            The quoted string

        Examples
        --------
        >>> from mixt.contrib.css.vars import string
        >>> string("foo")
        "'foo'"

        >>> from mixt.contrib.css import render_css
        >>> content = Var("content")
        >>> print(
        ...     render_css({
        ...         '.foo:after': {
        ...             content: string("foo")
        ...         }
        ...     })
        ... )
        .foo:after {
          content: 'foo';
        }

        """
        return repr(str(value))


class Negate(Var):
    """``Var`` that, when called, will prefix args with ``not``."""

    def __call__(  # type: ignore  # pylint: disable=arguments-differ
        self, *args: Any
    ) -> Var:
        """Allow to negate (using ``not``) the given arguments.

        Parameters
        ----------
        args : Tuple[Any]
            The args to be negated. If more than one, they will be surrounded by
            parentheses.

        Returns
        -------
        Var
            The newly created ``Var``.

        Examples
        --------
        >>> from mixt.contrib.css.vars import Not
        >>> Not("foo")
        'not foo'
        >>> Not("foo", "bar")
        'not (foo or bar)'

        """
        joined_args = " or ".join(_tovar(arg) for arg in args if arg)

        if len(args) > 1:
            return self.__class__(f"not ({joined_args})")
        return self.__class__(f"not {joined_args}")


class Merge(Var):
    """`Var` that, when called, will merge its given dicts."""

    def __call__(  # type: ignore  # pylint: disable=arguments-differ
        self, *dicts: Union[Dict, "Combine"]
    ) -> CssDict:
        """Merge many dictionaries into one, recursively.

        For keys that have dict as values, they are also merged.
        For values other than dicts, the last defined wins.

        Parameters
        ----------
        dicts : Tuple[Union[Dict, Combine], ...]
            The different dicts (or instances of ``Combine``) to join.

        Returns
        -------
        CssDict
            The joined dicts in a ``CssDict`` (subclass of ``dict``)

        Raises
        ------
        TypeError
            If at least one of ``dicts`` is not a dict or an instance of ``Combine``.

        Examples
        --------
        >>> from mixt.contrib.css.vars import merge
        >>> merge({
        ...    "foo": {"a": 1, "b": 2, "c": 3},
        ...    "bar": {"A": 11}
        ... }, {
        ...     "foo": {"b": 20, "c": None, "d": 4},
        ...     "baz": {"ZZ": 22},
        ... })
        {
            'foo': {'a': 1, 'b': 20, 'd': 4},
            'bar': {'A': 11},
            'baz': {'ZZ': 22}
        }

        """
        if not dicts:
            return CssDict()
        result: Dict[str, Any] = {}
        for dct in dicts:
            dcts: Sequence[Dict[str, Any]]
            if isinstance(dct, dict):
                dcts = [dct]
            elif isinstance(dct, Combine):
                dcts = dct.dicts
            else:
                raise TypeError(
                    "`merge` accepts only dicts or instances of ``Combine``"
                )
            for sub_dct in dcts:
                result = _dict_merge(result, sub_dct, update=False)
        return CssDict(result)


class Combine(Var):
    """``Var`` that, when called, allows to define a css dict from many dicts.

    Attributes
    ----------
    dicts : Sequence[Dict[str, Any]]]
        The list of css dicts to combine.
        Set when the instance is called with these dicts.

    """

    def __init__(self, _str_: str) -> None:  # pylint: disable=unused-argument
        """Init the var and its dicts list.

        For the parameters, see ``str``.

        """
        super().__init__()
        self.dicts: Sequence[Dict[str, Any]] = []

    def __call__(  # type: ignore
        self, *dicts: Union[Dict[str, Any], "Combine", str]
    ) -> Union["Combine", CssDict]:
        r"""Allow to define a css pseudo "dict" from many dicts.

        Parameters
        ----------
        dicts : Union[Dict[str, Any], "Combine"]
            The different dicts to combine. Can be a dict or already a ``Combine`` that will
            be expanded to its own dicts, or a string, in which case it will be converted to a
            raw CSS entry (using ``raw()`` as key)

        Returns
        -------
        Union[Combine, CssDict]
            If no dicts have a shared key, will return a new ``CssDict`` with all keys,
            else new instance of ``Combine`` with with the given dicts

        Examples
        --------
        >>> from mixt.contrib.css.vars import combine, Combine
        >>> css = combine({"foo": 1}, {"bar": 2})
        >>> isinstance(css, Combine)
        False
        >>> isinstance(css, dict)
        True
        >>> css
        {'foo': 1, 'bar': 2}
        >>> css = combine({"foo": 1}, {"foo": 2})
        >>> isinstance(css, Combine)
        True
        >>> isinstance(css, dict)
        False
        >>> css.dicts
        [{'foo': 1}, {'foo': 2}]

        """
        result_dicts: List[Dict[str, Any]] = []
        for dct in dicts:
            if isinstance(dct, Combine):
                result_dicts.extend(dct.dicts)
            elif isinstance(dct, str):
                result_dicts.append({raw(): dct})
            else:
                result_dicts.append(dct)

        if not result_dicts:
            return CssDict()
        if len(result_dicts) == 1:
            return CssDict(result_dicts[0])

        nb_total_keys = sum(len(dct) for dct in result_dicts)

        final_dict: Dict[str, Any] = {}
        for dct in result_dicts:
            final_dict.update(dct)

        if len(final_dict) == nb_total_keys:
            return CssDict(final_dict)

        new_obj = self.__class__(self)
        new_obj.dicts = result_dicts
        return new_obj

    def __hash__(self) -> int:
        """Return the hash of the object as the sum of the hash of all its dicts.

        Returns
        -------
        int
            The hash of the object.

        """
        if self.dicts:
            return sum(dict_hash(dct) for dct in self.dicts)
        return hash(str(self))

    def __iter__(self) -> Iterator[str]:
        """Iterate through the keys of all dicts.

        Yields
        ------
        str
            Each key for each dict.

        """
        yield from self.keys()

    def keys(self) -> Iterator[str]:
        """Iterate through the keys of all dicts.

        Yields
        ------
        str
            Each key for each dict.

        """
        for dct in self.dicts:
            yield from dct.keys()

    def values(self) -> Iterator[Any]:
        """Iterate through the values of all dicts.

        Yields
        ------
        Any
            Each values for each dict.

        """
        for dct in self.dicts:
            yield from dct.values()

    def items(self) -> Iterator[Tuple[str, Any]]:
        """Iterate through the key/value pairs of all dicts.

        Yields
        ------
        Tuple[str, Any]
            Each key/value pair for each dict.

        """
        for dct in self.dicts:
            yield from dct.items()


CssValuesType = Dict[Tuple[Any, Any], Any]


class CssVarsDict(dict):
    """A ``dict`` subclass that allows to access by keys or attrs, also creating undefined vars.

    Attributes
    ----------
    __values__ : CssValuesType
        Will hold "unique" values. Used to create new vars that have different keys but the same
        values.

    Examples
    --------
    >>> obj = CssVarsDict(foo='FOO')
    >>> obj['foo']
    'FOO'
    >>> obj.foo
    'FOO'
    >>> obj.bar
    'bar
    >>> obj['baz']
    'baz'

    """

    def __init__(self, **kwargs: Any) -> None:
        """Init the dict and create the ``__values__`` attribute.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The key/value pairs to store in the dict at create time.

        """
        super().__init__(**kwargs)
        self.__values__: CssValuesType = {}

    def __getattr__(self, name: str) -> Any:
        """Return the value stored for the key `name`.

        See ``__getitem__`` for how non-existing keys are handled.

        Parameters
        ----------
        name : str
            The name of key to retrieve from the dict.

        Returns
        -------
        Any
            The value stored for the key.

        Raises
        ------
        AttributeError
            For pytest when it tries to access ``__wrapped__`` and ``__name__``.

        """
        if name in ("__wrapped__", "__name__"):
            # special case for pytest
            raise AttributeError
        return self[name]

    def __getitem__(self, key: Any) -> Any:
        """Return, creating it if necessary, the value for `key`.

        If the `key` does not exist in the dict, it will be auto-created by calling ``add_css_var``.

        Parameters
        ----------
        key : Any
            The key to get, and create if needed

        Returns
        -------
        Any
            The value stored at `key`, that may have just been created.

        """
        try:
            return super().__getitem__(key)
        except KeyError:
            add_css_var(key, css_vars=self)
            return super().__getitem__(key)


def add_css_var(  # pylint: disable=too-many-branches
    name: str,
    kind: Optional[Type[Var]] = Var,
    value: Optional[Any] = None,
    aliases: Optional[List[str]] = None,
    css_vars: Optional[CssVarsDict] = None,
) -> None:
    """Add one or many css variables.

    Parameters
    ----------
    name : str
        The base name of the var to be created. If can be split with ``_`` or ``-``, additional
        variables will be created for each split parts.
        Each var will be saved in:

        - lowercase
        - snake_case
        - camelCase
        - PascalCase

    kind : Optional[Type[Var]]
        The kind of ``Var`` to create. Default to ``Var``. Can be ``None`` if not a ``Var``. For
        example for functions.

    value : Optional[Any]
        The value to use for all vars to be created. If not set, it will be extracted from
        the name.

    aliases : Optional[List[str]]
        Other names to be saved with the same value as for `name`.

    css_vars : Optional[CssVarsDict]
        The dict in which to store the new var(s). If not set, the global ``CSS_VARS``
        will be used.

    """
    if css_vars is None:
        css_vars = CSS_VARS

    names_by_value: Dict[str, List] = defaultdict(list)

    def get_value(name: str) -> Union[Var, str]:
        """Return the value to use for the given name.

        Parameters
        ----------
        name : str
            The name for which we want the value.

        Returns
        -------
        Union[Var, str]
            This is done in two steps:

            1. We get a value. It will be ``value`` if defined, else the `name` with ``_`` replaced
               by ``-`.
            2. If ``kind`` is defined, an instance of this ``kind`` will be returned, with the
               value got from 1. Else, this value is returned directly.

        """
        val = name.replace("_", "-").lower() if value is None else value
        return kind(val) if kind else val

    # pylint: disable=redefined-argument-from-local

    for name in [name] + (aliases or []):
        name = (
            name.replace("_", "-").strip("-") if name.count("_") != len(name) else name
        )
        if "-" in name:
            parts = name.split("-")
            if value is None:
                for part in parts:
                    if not part:
                        continue
                    names_by_value[get_value(part)].extend([part, part.capitalize()])
            name = "_".join(parts)
            titled = name.replace("_", " ").title().replace(" ", "")
            names_by_value[get_value(name)].extend(
                [name, titled, name[0] + titled[1:]]  # foo_bar  # FooBar  # fooBar
            )
        else:
            names_by_value[get_value(name)].extend([name, name.capitalize()])

    for value, names in names_by_value.items():

        final_names = []
        for name in names:
            if iskeyword(name):
                final_names.append(f"_{name}")
                continue
            if isbuiltin(name):
                final_names.append(f"_{name}")
            final_names.append(name)

        css_values_key = (kind, value)

        if css_values_key not in css_vars.__values__:
            css_vars.__values__[css_values_key] = value

        for name in final_names:
            # print(f"Registering `{name}`: `{value}`")
            css_vars[name] = css_vars.__values__[css_values_key]


CSS_VARS: CssVarsDict = CssVarsDict()

# pylint: disable=invalid-name,attribute-defined-outside-init

dummy = Var("")
dummy.__doc__ = """Special "empty" var.

To use to force things to behave like a ``Var``.

Alias: ``_``

Examples
--------
>>> from mixt.contrib.css.vars import dummy as _
>>> _
''
>>> _ + "foo"
'+foo'
>>> _("foo")
'(foo)'
>>> _ & {"foo": "bar"}
'(foo: bar)'
"""

join = Join("join")
many = Many("many")
override = Override("override")
extend = Extend("extend")
raw = Raw("raw")
comment = Comment("comment")
string = String("string")
Not = negate = Negate("not")
merge = Merge("merge")
combine = Combine("combine")

for special_var in [join, many, override, extend, string, Not, negate, merge]:
    special_var.__doc__ = special_var.__call__.__doc__

charset = AtRule("charset", if_empty="UTF-8", quote_args=True)  # type: ignore
_import = AtRule("import", s=", ")  # type: ignore
namespace = AtRule("namespace", s=" ")  # type: ignore
media = AtRule("media", if_empty="all", s=", ")  # type: ignore
supports = AtRule("supports")
document = AtRule("document", s=", ")  # type: ignore
page = AtRule("page")
font_face = AtRule("font-face")
keyframes = AtRule("keyframes")
viewport = AtRule("viewport")
counter_style = AtRule("counter-style")
font_feature_values = AtRule("font-feature-values")
swash = AtRule("swash")
annotation = AtRule("annotation")
ornaments = AtRule("ornaments")
stylistic = AtRule("stylistic")
styleset = AtRule("styleset")
character_variant = AtRule("character-variant")
# pylint: enable=invalid-name,attribute-defined-outside-init


def load_defaults() -> None:
    """Load all default vars: utils functions..."""
    add_css_var("_", kind=None, value=dummy, aliases=["dummy"])
    add_css_var("join", kind=None, value=join)
    add_css_var("many", kind=None, value=many)
    add_css_var("override", kind=None, value=override)
    add_css_var("extend", kind=None, value=extend)
    add_css_var("raw", kind=None, value=raw, aliases=["r"])
    add_css_var("comment", kind=None, value=comment, aliases=["c"])
    add_css_var("string", kind=None, value=string, aliases=["str", "repr"])
    add_css_var("not", kind=None, value=negate)
    add_css_var("b", kind=None, value=builtins, aliases=["builtins"])
    add_css_var("merge", kind=None, value=merge)
    add_css_var("combine", kind=None, value=combine)

    add_css_var("charset", kind=None, value=charset)
    add_css_var("import", kind=None, value=_import)
    add_css_var("namespace", kind=None, value=namespace)
    add_css_var("media", kind=None, value=media)
    add_css_var("supports", kind=None, value=supports)
    add_css_var("document", kind=None, value=document)
    add_css_var("page", kind=None, value=page)
    add_css_var("font_face", kind=None, value=font_face)
    add_css_var("keyframes", kind=None, value=keyframes)
    add_css_var("viewport", kind=None, value=viewport)
    add_css_var("counter_style", kind=None, value=counter_style)
    add_css_var("font_feature_values", kind=None, value=font_feature_values)
    add_css_var("swash", kind=None, value=swash)
    add_css_var("annotation", kind=None, value=annotation)
    add_css_var("ornaments", kind=None, value=ornaments)
    add_css_var("stylistic", kind=None, value=stylistic)
    add_css_var("styleset", kind=None, value=styleset)
    add_css_var("character_variant", kind=None, value=character_variant)


load_defaults()
