"""Manages CSS units as python vars, with math operations. Helps to produce ``calc`` CSS calls."""

from decimal import Decimal
from fractions import Fraction
from typing import Any, Dict, List, NoReturn, Sequence, Union, cast

from .vars import Var, add_css_var


UNITS = """
cap ch em ex ic lh rem rlh vh vw vi vb vmin vmax px cm mm Q in pt deg grad rad turn
fr Hz KHz dpi dpcm dppx s ms
""".split()


# pylint: disable=invalid-name
Number = Union[int, float, Decimal]
AdditionPart = Union["Addition", "QuantifiedUnit"]
# pylint: enable=invalid-name


def is_number(value: Any) -> bool:
    """Tell if `value` is a number, ie an ``int``, a ``float`` or a ``Decimal``.

    Parameters
    ----------
    value : Any
        The value to test.

    Returns
    -------
    bool
        ``True`` if `value` is a number, ``False`` otherwise.

    """
    return isinstance(value, (int, float, Decimal))


def is_addition_part(value: Any) -> bool:
    """Tell if `value` is an addition part, ie a ``QuantifiedUnit``, or an ``Addition``.

    Parameters
    ----------
    value : Any
        The value to test.

    Returns
    -------
    bool
        ``True`` if `value` is an addition part, ``False`` otherwise.

    """
    return isinstance(value, (Addition, QuantifiedUnit))


def is_quantified_unit(value: Any) -> bool:
    """Tell if `value` is a ``QuantifiedUnit``.

    Parameters
    ----------
    value : Any
        The value to test.

    Returns
    -------
    bool
        ``True`` if `value` is a ``QuantifiedUnit``, ``False`` otherwise.

    """
    return isinstance(value, QuantifiedUnit)


def decimalize(value: Number) -> Decimal:
    """Convert a number to a ``Decimal``.

    Parameters
    ----------
    value : Number
        The value to convert. If already a ``Decimal``, nothing will be changed.

    Returns
    -------
    Decimal
        The converted value.

    """
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class Addition:
    """An addition is a list of part to be added together.

    Parts can be given as ``QuantifiedUnit`` and ``Addition``.

    The goal is to produce a minimal ``calc`` css call.

    Parameters
    ----------
    parts: Sequence[Union[QuantifiedUnit, Addition]]
        The parts to add together.

    Attributes
    ----------
    parts : Sequence[QuantifiedUnit]
        Before saving, parts are reduced to a minimal list of ``QuantifiedUnit``. See ``reduce``.

    """

    def __init__(self, parts: Sequence[AdditionPart]) -> None:
        """Init object by saving parts after reducing them."""
        self.parts: Sequence[QuantifiedUnit] = self.reduce(parts)

    def __str__(self) -> str:
        """Return a string representation of the addition.

        Returns
        -------
        str
            The stringified ``Addition``, computed by joining parts with operators,
            surrounding the whole with parentheses and prefix the final result with "calc".
            If no operations (or all with "0" as value), will return "0", and if only one, will
            return it without the "calc" surrounding, but only if it's not a fraction.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> str(Addition([px(4), em(2)]))
        'calc(4px + 2em)'
        >>> str(Addition([]))
        '0'
        >>> str(Addition([px(3), em(2), px(-3)]))
        '2em'
        >>> str(Addition([px(3), em(2)/3, px(-3), em(4)]))
        'calc(14em / 3)'
        >>> str(Addition([px(3), em(2), px(-3), em(-2)]))
        '0'

        """
        operations = self.operations
        if not operations:
            return "0"
        if len(operations) == 1:
            result = str(operations[0])
            if "/" not in result:
                return result
        return f"calc({' '.join(self.operations)})"

    def __repr__(self) -> str:
        """Return the string representation of the addition.

        Returns
        -------
        str
            The output of the call to ``__str__``.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> repr(Addition([px(4), em(2)]))
        'calc(4px + 2em)'

        """
        return str(self)

    @property
    def operations(self) -> List[str]:  # noqa: D202
        """Get the final operations for this addition.

        Will correctly manage +/- operators and convert float to fractions.

        Returns
        -------
        List[str]
            The list of stringified operation.

        Examples
        --------
        >>> px, em, cm = Unit.many("px em cm")
        >>> Addition([px(4), em(-2), cm(1)]).operations
        ['4px', '- 2em', '+ '1cm']
        >>>

        """

        def normalize_part(part: QuantifiedUnit, index: int) -> str:
            """Correctly prefix a quantified unit with a + or - operator.

            Parameters
            ----------
            part :  QuantifiedUnit
                The addition part to normalize.
            index : int
                The position of the part in the whole list of parts.

            Returns
            -------
            str
                The normalized part.

            """
            need_negate = index and part.value < 0
            part = -part if need_negate else part
            str_part: str

            fraction: Fraction = Fraction(part.value).limit_denominator()
            if fraction.denominator == 1:
                str_part = f"{fraction.numerator}{part.unit}"
            else:
                str_part = f"{fraction.numerator}{part.unit} / {fraction.denominator}"

            if not index:
                return str_part
            if need_negate:
                return f"- {str_part}"
            return f"+ {str_part}"

        return [normalize_part(part, index) for index, part in enumerate(self.parts)]

    def reduce(self, parts: Sequence[AdditionPart]) -> Sequence["QuantifiedUnit"]:
        """Convert given ``parts`` to a minimal list of ``QuantifiedUnit``.

        Parts of type ``Addition`` will be reduced into ``QuantifiedUnit``.
        All ``QuantifiedUnit`` of the same "unit" will be added.

        At the end there will be only ``QuantifiedUnit`` entries, and at max one for each type of
        unit.

        Parameters
        ----------
        parts : Sequence[AdditionPart]
            The parts we want to reduce.

        Returns
        -------
        Sequence["QuantifiedUnit"]
            The minimal list of parts resulting in the reducing.

        Raises
        ------
        TypeError
            When one of the given `part` is not a ``QuantifiedUnit`` or an ``Addition``.

        """
        units: Dict[str, QuantifiedUnit] = {}
        final_parts: List[QuantifiedUnit] = []

        todo_parts: List[AdditionPart] = list(parts)

        while todo_parts:
            part = todo_parts.pop(0)
            if isinstance(part, Addition):
                todo_parts[:0] = part.parts
                continue
            if not is_quantified_unit(part):
                raise TypeError(
                    f"{part.__class__.__name__} not accepted as part of an `Addition`."
                )
            part = cast(QuantifiedUnit, part)
            if part.unit in units:
                units[part.unit].value += part.value
                continue
            units[part.unit] = part
            final_parts.append(part)

        return [part for part in final_parts if part.value]

    def __neg__(self) -> "Addition":
        """Return a new ``Addition`` with all values being negated.

        Returns
        -------
        Addition
            The new composed ``Addition``.

        """
        return Addition([-part for part in self.parts])

    def __add__(self, other: AdditionPart) -> "Addition":
        """Add the given part, `other`, to the current ones. Raises if `other` is not a part.``.

        Parameters
        ----------
        other : Number
            The right hand side of the operation.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> Addition([px(4), em(2)]) + px(2)
        calc(6px + 2em)
        >>> Addition([px(4), em(2)]) + Addition([px(2), em(1)])
        calc(6px + 3em)

        Returns
        -------
        Addition
            A new ``Addition`` with all parts from `self` plus `other`.

        Raises
        ------
        TypeError
            If `other` is not an ``Addition`` or a ``QuantifiedUnit``.

        """
        if is_addition_part(other):
            return Addition(cast(List[AdditionPart], self.parts) + [other])
        raise TypeError(
            "unsupported operand type(s) for +: "
            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'"
        )

    def __radd__(self, other: AdditionPart) -> "Addition":  # type: ignore
        """Add the given part, `other`, to the current ones. Raises if `other` is not a part.``.

        Parameters
        ----------
        other : Number
            The left hand side of the operation.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> px(2) + Addition([px(4), em(2)])
        calc(6px + 2em)
        >>> Addition([px(4), em(2)]) + Addition([px(2), em(1)])
        calc(6px + 3em)

        Returns
        -------
        Addition
            A new ``Addition`` with all parts from `self` plus `other`.

        Raises
        ------
        TypeError
            If `other` is not an ``Addition`` or a ``QuantifiedUnit``.

        """
        if is_addition_part(other):
            return Addition([other] + cast(List[AdditionPart], self.parts))
        raise TypeError(
            "unsupported operand type(s) for +: "
            f"'{other.__class__.__name__}' and '{self.__class__.__name__}'"
        )

    def __sub__(self, other: AdditionPart) -> "Addition":
        """Add the neg given part, `other`, to the current ones. Raises if `other` is not a part.``.

        Parameters
        ----------
        other : Number
            The right hand side of the operation.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> Addition([px(4), em(2)]) - px(2)
        calc(2px + 2em)
        >>> Addition([px(4), em(2)]) - Addition([px(2), em(1)])
        calc(2px + 1em)

        Returns
        -------
        Addition
            A new ``Addition`` with all parts from `self` plus `other`, `other` being negated.

        Raises
        ------
        TypeError
            If `other` is not an ``Addition`` or a ``QuantifiedUnit``.

        """
        if is_addition_part(other):
            return Addition(cast(List[AdditionPart], self.parts) + [-other])
        raise TypeError(
            "unsupported operand type(s) for -: "
            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'"
        )

    def __rsub__(self, other: AdditionPart) -> "Addition":  # type: ignore
        """Add the neg given part, `other`, to the current ones. Raises if `other` is not a part.``.

        Parameters
        ----------
        other : Number
            The left hand side of the operation.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> 2px - Addition([px(4), em(2)])
        calc(2px + 2em)
        >>> Addition([px(4), em(2)]) - Addition([px(2), em(1)])
        calc(2px + 1em)

        Returns
        -------
        Addition
            A new ``Addition`` with all parts from `self` plus `other`, `other` being negated.

        Raises
        ------
        TypeError
            If `other` is not an ``Addition`` or a ``QuantifiedUnit``.

        """
        if is_addition_part(other):
            return Addition([-other] + cast(List[AdditionPart], self.parts))
        raise TypeError(
            "unsupported operand type(s) for -: "
            f"'{other.__class__.__name__}' and '{self.__class__.__name__}'"
        )

    def __mul__(self, other: Number) -> "Addition":
        """Multiply all parts by the given number, `other`. Raises if `other` is not a number.``.

        Parameters
        ----------
        other : Number
            The right hand side of the operation.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> Addition([px(4), em(2)]) * 2
        calc(8px + 2em)

        Returns
        -------
        Addition
            A new ``Addition`` with all parts from `self` multiplied by `other`.

        Raises
        ------
        TypeError
            If `other` is not a number.

        """
        if is_number(other):
            return Addition([cast(AdditionPart, part * other) for part in self.parts])
        raise TypeError(
            "unsupported operand type(s) for *: "
            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'"
        )

    def __rmul__(self, other: Number) -> "Addition":
        """Multiply all parts by the given number, `other`. Raises if `other` is not a number.``.

        Parameters
        ----------
        other : Number
            The left hand side of the operation.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> 2 * Addition([px(4), em(2)])
        calc(8px + 2em)

        Returns
        -------
        Addition
            A new ``Addition`` with all parts from `self` multiplied by `other`.

        Raises
        ------
        TypeError
            If `other` is not a number.

        """
        if is_number(other):
            return Addition([cast(AdditionPart, part * other) for part in self.parts])
        raise TypeError(
            "unsupported operand type(s) for *: "
            f"'{other.__class__.__name__}' and '{self.__class__.__name__}'"
        )

    def __truediv__(self, other: Number) -> "Addition":
        """Divide all parts by the given number, `other`. Raises if `other` is not a number.``.

        Parameters
        ----------
        other : Number
            The right hand side of the operation.

        Returns
        -------
        Addition
            A new ``Addition`` with all parts from `self` divided by `other`.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> Addition([px(4), em(2)]) / 2
        calc(2px + 1em)

        Raises
        ------
        TypeError
            If `other` is not a number.

        """
        if is_number(other):
            return Addition([cast(AdditionPart, part / other) for part in self.parts])
        raise TypeError(
            "unsupported operand type(s) for /: "
            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'"
        )

    def __rtruediv__(self, other: Any) -> NoReturn:
        """Unsupported operation. Nothing can be divided by an ``AdditionPart``.

        Parameters
        ----------
        other : Any
            The left hand side of the operation.

        Raises
        ------
        TypeError
            In all cases.

        """
        raise TypeError(
            "unsupported operand type(s) for /: "
            f"'{other.__class__.__name__}' and '{self.__class__.__name__}'"
        )


class QuantifiedUnit:
    """Store a number for a certain unit.

    For example "3px" is a ``QuantifiedUnit`` with ``value=3`` and ``unit=Unit("px")``.

    Attributes
    ----------
    value : Decimal
        The number of ``unit``
    unit : Unit
        The stored unit.

    """

    def __init__(self, value: Number, unit: "Unit") -> None:
        """Init object by saving `value` and `unit`.

        Parameters
        ----------
        value : Number
            The number of ``unit``. Will be converted to a ``Decimal``.
        unit : Unit
            The stored unit.

        """
        self.value: Decimal = decimalize(value)
        self.unit: Unit = unit

    def __str__(self) -> str:
        """Return a string representation of the quantified unit.

        Returns
        -------
        str
            The stringified ``QuantifiedUnit``, computed by joining the value and the unit.

        Examples
        --------
        >>> str(QuantifiedUnit(3, Unit("px")))
        '3px'

        """
        return f"{self.value}{self.unit}"

    def __repr__(self) -> str:
        """Return the string representation of the quantified unit.

        Returns
        -------
        str
            The output of the call to ``__str__``.

        Examples
        --------
        >>> repr(QuantifiedUnit(3, Unit("px")))
        '3px'

        """
        return str(self)

    def __neg__(self) -> "QuantifiedUnit":
        """Return a new ``QuantifiedUnit`` with the value negated.

        Returns
        -------
        QuantifiedUnit
            The new ``QuantifiedUnit`` with the value negated.

        Examples
        --------
        >>> -QuantifiedUnit(3, Unit("px")))
        -3px

        """
        return QuantifiedUnit(-self.value, self.unit)

    def __add__(self, other: Any) -> Union[Var, AdditionPart]:  # type: ignore
        """Return an addition part if `other` is a quantified unit. Else, a ``Var``.

        Parameters
        ----------
        other : Any
            The right hand side of the operation.

        Returns
        -------
        Union[Var, AdditionPart]
            - If `other` is a ``QuantifiedUnit`` of the same "unit" as the current one, both
              ``value`` are added and a new ``QuantifiedUnit`` is returned.
            - If `other` is a ``QuantifiedUnit`` of another "unit" than the current one, an
              ``Addition`` is returned, passing it ``self`` and ``other``.
            - If `other` is an ``Addition``, let ``Addition`` manage the operation to return a new
              ``Addition``.
            - In all other cases, returns a ``Var`` joining `self` and `other` with ``+``.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> qu = QuantifiedUnit(4, px)
        >>> qu + QuantifiedUnit(3, px)
        7px
        >>> qu + QuantifiedUnit(3, em)
        calc(4px + 3em)
        >>> qu + "foo"
        '4px+foo'

        """
        if is_quantified_unit(other):
            if other.unit == self.unit:
                return QuantifiedUnit(self.value + other.value, self.unit)
            return Addition([self, other])
        if is_addition_part(other):
            return other.__radd__(self)
        return Var(f"{self}+{other}")

    def __radd__(self, other: Any) -> Var:
        """Return a ``Var`` joining `other` and `self` with ``+``.

        Parameters
        ----------
        other : Any
            The left hand side of the operation.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> px = Unit("px")
        >>> qu = QuantifiedUnit(4, px)
        >>> 2 + qu
        '2+4px'
        >>> "foo" + qu
        'foo+4px'

        """
        return Var(f"{other}+{self}")

    def __sub__(self, other: Any) -> Union[Var, AdditionPart]:  # type: ignore
        """Return an addition part if `other` is a quantified unit. Else, a ``Var``.

        Parameters
        ----------
        other : Any
            The right hand side of the operation.

        Returns
        -------
        Union[Var, AdditionPart]
            - If `other` is a ``QuantifiedUnit`` of the same "unit" as the current one, the value
             from `other` is subtracted from the one from `self` and a new ``QuantifiedUnit``
             is returned.
            - If `other` is a ``QuantifiedUnit`` of another "unit" than the current one, an
              ``Addition`` is returned, passing it ``self`` and ``-other``.
            - If `other` is an ``Addition``, let ``Addition`` manage the operation to return a new
              ``Addition``.
            - In all other cases, returns a ``Var`` joining `self` and `other` with ``-``.

        Examples
        --------
        >>> px, em = Unit.many("px em")
        >>> qu = QuantifiedUnit(4, px)
        >>> qu - QuantifiedUnit(3, px)
        1px
        >>> qu - QuantifiedUnit(3, em)
        calc(4px - 3em)
        >>> qu - "foo"
        '4px-foo'

        """
        if is_quantified_unit(other):
            if other.unit == self.unit:
                return QuantifiedUnit(self.value - other.value, self.unit)
            return Addition([self, -other])
        if is_addition_part(other):
            return (-other).__rsub__(self)
        return Var(f"{self}-{other}")

    def __rsub__(self, other: Any) -> Var:
        """Return a ``Var`` joining `other` and `self` with ``+``.

        Parameters
        ----------
        other : Any
            The left hand side of the operation.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> px = Unit("px")
        >>> qu = QuantifiedUnit(4, px)
        >>> 2 - qu
        '2-4px'
        >>> "foo" - qu
        'foo+4px'

        """
        return Var(f"{other}-{self}")

    def __mul__(self, other: Any) -> Union[Var, "QuantifiedUnit"]:
        """Return a new ``QuantifiedUnit`` if `other` is a number. Else, a ``Var``.

        Parameters
        ----------
        other : Any
            The right hand side of the operation. If a number, it is used to multiply the current
            number of units.

        Returns
        -------
        Union[Var, QuantifiedUnit]
            - If other is a ``Number``, returns a new ``QuantifiedUnit`` is returned, with the
              current ``value`` being multiplied by `other`.
            - In all other cases, returns a ``Var`` joining `self` and `other` with ``*``.

        Examples
        --------
        >>> px = Unit("px")
        >>> qu = QuantifiedUnit(4, px)
        >>> qu * 2
        8px
        >>> qu * QuantifiedUnit(2, px)
        '4px*2px'
        >>> qu * "foo"
        '4px*foo'

        """
        if is_number(other):
            return QuantifiedUnit(self.value * decimalize(other), self.unit)
        return Var(f"{self}*{other}")

    def __rmul__(self, other: Any) -> Union[Var, "QuantifiedUnit"]:
        """Return a new ``QuantifiedUnit`` if `other` is a number. Else, a ``Var``.

        Parameters
        ----------
        other : Any
            The left hand side of the operation. If a number, it is used to multiply the current
            number of units.

        Returns
        -------
        Union[Var, QuantifiedUnit]
            - If other is a ``Number``, returns a new ``QuantifiedUnit`` is returned, with the
              current ``value`` being multiplied by `other`.
            - In all other cases, returns a ``Var`` joining `other` and `self` with ``*``.

        Examples
        --------
        >>> px = Unit("px")
        >>> qu = QuantifiedUnit(4, px)
        >>> 2 * qu
        8px
        >>> QuantifiedUnit(2, px) * qu
        '2px*4px'
        >>> qu * "foo"
        'foo*4px'

        """
        if is_number(other):
            return QuantifiedUnit(self.value * decimalize(other), self.unit)
        return Var(f"{other}*{self}")

    def __truediv__(self, other: Any) -> Union[Var, "QuantifiedUnit"]:
        """Return a new ``QuantifiedUnit`` if `other` is a number. Else, a ``Var``.

        Parameters
        ----------
        other : Any
            The right hand side of the operation. If a number, it is used to divide the current
            number of units.

        Returns
        -------
        Union[Var, QuantifiedUnit]
            - If other is a ``Number``, returns a new ``QuantifiedUnit`` is returned, with the
              current ``value`` being divided by `other`.
            - In all other cases, returns a ``Var`` joining `self` and `other` with ``/``.

        Examples
        --------
        >>> px = Unit("px")
        >>> qu = QuantifiedUnit(4, px)
        >>> qu / 2
        2px
        >>> qu / QuantifiedUnit(2, px)
        '4px/2px'
        >>> qu / "foo"
        '4px/foo'

        """
        if is_number(other):
            return QuantifiedUnit(self.value / decimalize(other), self.unit)
        return Var(f"{self}/{other}")

    def __rtruediv__(self, other: Any) -> Union[Var, "QuantifiedUnit"]:
        """Return a ``Var`` joining `other` and `self` with ``/``.

        Parameters
        ----------
        other : Any
            The left hand side of the operation.

        Returns
        -------
        Var
            The new composed ``Var``.

        Examples
        --------
        >>> px = Unit("px")
        >>> qu = QuantifiedUnit(4, px)
        >>> 2 / qu
        '2/4px'
        >>> QuantifiedUnit(2, px) / qu
        '2px/4px'
        >>> "foo" / qu
        'foo/4px'

        """
        return Var(f"{other}/{self}")


class Unit(Var):
    """A subclass of ``Var`` with specific behavior for units.

    If multiplied by a number, we have a ``QuantifiedUnit``, with the value being the number, and
    the unit, the current "var".

    If called with a number, it's the same as multiplying it by this number.

    Examples
    --------
    >>> px = Unit("px")
    >>> 3*px
    '3px'
    >>> px*3
    '3px'
    >>> px(3)
    '3px'

    """

    def __call__(  # type: ignore  # pylint: disable=arguments-differ
        self, value: Number
    ) -> QuantifiedUnit:
        """Get a ``QuantifiedUnit`` for this unit.

        Parameters
        ----------
        value : Number
            The value to use as a number for this unit.

        Returns
        -------
        QuantifiedUnit
            An ``QuantifiedUnit`` with `value` as the number and `self` as the unit.

        """
        return QuantifiedUnit(value=value, unit=self)

    def __mul__(self, other: Number) -> QuantifiedUnit:  # type: ignore
        """Get a ``QuantifiedUnit`` for this unit.

        Parameters
        ----------
        other : Number
            The value to use as a number for this unit.

        Returns
        -------
        QuantifiedUnit
            An ``QuantifiedUnit`` with `other` as the number and `self` as the unit.

        """
        return QuantifiedUnit(value=other, unit=self)

    def __rmul__(self, other: Number) -> QuantifiedUnit:  # type: ignore
        """Get a ``QuantifiedUnit`` for this unit.

        Parameters
        ----------
        other : Number
            The value to use as a number for this unit.

        Returns
        -------
        QuantifiedUnit
            An ``QuantifiedUnit`` with `other` as the number and `self` as the unit.

        """
        return QuantifiedUnit(value=other, unit=self)


def load_css_units() -> None:
    """Load all units defined in ``UNITS`` in ``CSS_VARS``."""
    for name in UNITS:
        add_css_var(name, Unit)
    add_css_var("pc", kind=Unit, value="%", aliases=["percent"])


load_css_units()
