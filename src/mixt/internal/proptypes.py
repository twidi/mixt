"""Define the class that will handle everything about props."""

from collections.abc import Sequence
from contextlib import contextmanager
import keyword
from typing import Any, Dict, Set, Type, get_type_hints

from ..exceptions import (
    InvalidPropBoolError,
    InvalidPropChoiceError,
    InvalidPropValueError,
    PropTypeChoicesError,
    PropTypeRequiredError,
    RequiredPropError,
)
from ..proptypes import Choices, DefaultChoices, NotProvided, Required
from ..vendor.pytypes import (  # we use "pytypes" to check complex types
    TypeCheckError,
    typechecked,
)


FUTURE_KEYWORDS: Set[str] = {
    "async"
}  # used prop that are not yet keywords but that will be


class BasePropTypes:
    """Base class for prop types.

    In particular, it will handle python props to html attributes and vice-versa:

    From python to html:

    - a starting `_` will be removed in final html attribute
    - a single `_` will be changed to `-`
    - a double `__` will be changed to `:`

    For example:
        ``_class`` <=> ``class``
        ``xmlns__og`` <=> ``xmlns:og``
        ``data_value`` <=> ``data-value``

    """

    __owner_name__: str = ""
    __types__: Dict[str, Any] = {}
    __required_props__: Set[str] = set()
    __default_props__: Dict[str, Any] = {}
    __excluded_props__: Set[str] = set()

    __dev_mode__: bool = True

    @staticmethod
    def __to_html__(name: str) -> str:
        """Convert a prop name to be usable as an html attribute name.

        Parameters
        ----------
        name : str
            The name to convert.

        Returns
        -------
        str
            The converted name.

        """
        if name.startswith("_"):
            name = name[1:]
        return name.replace("__", ":").replace("_", "-")

    @staticmethod
    def __to_python__(name: str) -> str:
        """Convert an html attribute name to be usable as a python prop name.

        Parameters
        ----------
        name : str
            The name to convert.

        Returns
        -------
        str
            The converted name.

        Raises
        ------
        NameError
            If the name is not a valid python idendifier, after ``-`` and ``:`` substitution.
            (It won't raise if its a python keyword, which is a valid idenfifier for
            the ``isidentifier`` method.)

        """
        name = name.replace("-", "_").replace(":", "__")
        if not name.isidentifier():
            raise NameError(name)
        if keyword.iskeyword(name) or name in FUTURE_KEYWORDS:
            name = "_" + name
        return name

    @classmethod
    def __allow__(cls, name: str) -> bool:
        """Tell if the given name is an allowed python prop name.

        Parameters
        ----------
        name : str
            The name to check.

        Returns
        -------
        bool
            ``True`` if the name is allowed, ie defined as a prop, or starting with ``aria_``
            or ``data_``.  ``False`` otherwise.

        """
        return (
            name in cls.__types__
            or name.startswith("data_")
            or name.startswith("aria_")
        )

    @classmethod
    def __type__(cls, name: str) -> Any:
        """Return the type of the prop defined by `name`.

        If the prop is not defined, we return ``NotProvided``.

        Parameters
        ----------
        name : str
            The name of the prop for which we want the type.

        Returns
        -------
        Any
            The resolved type for the prop. If not a prop, will return ``NotProvided``.

        """
        return cls.__types__.get(name, NotProvided)

    @classmethod
    def __is_choice__(cls, name: str) -> bool:
        """Tell if the type of the prop defined by `name` is ``Choices``.

        Parameters
        ----------
        name : str
            The name of the prop we ask for.

        Returns
        -------
        bool
            ``True`` if the type of the prop is ``Choices``. False otherwise.

        """
        try:
            return issubclass(cls.__type__(name), Choices)
        except TypeError:
            return False

    @classmethod
    def __is_bool__(cls, name: str) -> bool:
        """Tell if the type of the prop defined by `name` is ``bool``.

        Parameters
        ----------
        name : str
            The name of the prop we ask for.

        Returns
        -------
        bool
            ``True`` if the type of the prop is ``bool``. False otherwise.

        """
        return cls.__type__(name) is bool

    @classmethod
    def __default__(cls, name: str) -> Any:
        """Return the default value for the prop defined by `name`.

        Parameters
        ----------
        name : str
            The name of the prop we ask for.

        Returns
        -------
        Any
            If the prop is of type ``DefaultChoices``, it will return the first value of the list.
            If the props is of type ``Choices``, it will return ``NotProvided``.
            In all other cases, it will return the value defined for the props, or ``NotProvided``
            if no value was defined.

        """
        return cls.__default_props__.get(name, NotProvided)

    @classmethod
    def __is_required__(cls, name: str) -> bool:
        """Tell if the prop defined by `name` is a required one.

        Parameters
        ----------
        name : str
            The name of the prop we want to know if it is required.

        Returns
        -------
        bool
            ``True`` if the prop is required, ``False`` otherwise.

        """
        return name in cls.__required_props__

    @classmethod
    def __validate_types__(  # pylint: disable=too-many-branches; # noqa: C901
        cls: Type["BasePropTypes"],
    ) -> None:
        """Validate the types of the props defined in the current PropTypes class.

        Raises
        ------
        PropTypeChoicesError

            - If a prop is a ``Choices`` with no value or empty list.
            - If a prop is a ``Choices`` with something else than a list.

        PropTypeRequiredError

            - If a prop is a ``DefaultChoices`` and is marked as ``Required``.
            - For all other props marked as ``Required`` if there is a value.

        InvalidPropValueError

            - If the default value is not valid for the prop type.

        """
        cls.__types__ = {
            name: prop_type
            for name, prop_type in get_type_hints(cls).items()
            if not hasattr(BasePropTypes, name) and name not in cls.__excluded_props__
        }

        for name, prop_type in cls.__types__.items():

            is_required = False

            try:
                if issubclass(prop_type, Required):
                    is_required = True
            except TypeError:
                try:
                    if prop_type.__origin__ is Required:
                        is_required = True
                except AttributeError:
                    pass

            if is_required:
                prop_type = prop_type.__args__[0]
                cls.__types__[name] = prop_type
                cls.__required_props__.add(name)

            if cls.__is_choice__(name):

                if not getattr(cls, name, []):
                    raise PropTypeChoicesError(
                        cls.__owner_name__,
                        name,
                        "a 'choices' prop must have a list of values",
                    )

                choices = getattr(cls, name)

                if not isinstance(choices, Sequence) or isinstance(choices, str):
                    raise PropTypeChoicesError(
                        cls.__owner_name__,
                        name,
                        "the value for a 'choices' prop must be a list",
                    )

                if issubclass(cls.__type__(name), DefaultChoices):
                    if choices[0] is not NotProvided:
                        if is_required:
                            raise PropTypeRequiredError(
                                cls.__owner_name__,
                                name,
                                "a 'choices' prop with a default value cannot be required",
                            )
                        cls.__default_props__[name] = choices[0]

                continue

            default = getattr(cls, name, NotProvided)
            if default is NotProvided:
                continue

            if is_required:
                raise PropTypeRequiredError(
                    cls.__owner_name__,
                    name,
                    "a prop with a default value cannot be required",
                )

            cls.__default_props__[name] = cls.__validate__(name, default)

    @classmethod
    def __validate__(  # pylint: disable=too-many-branches, too-many-return-statements; # noqa: C901
        cls, name: str, value: Any
    ) -> Any:
        """Validate the `value` for the prop defined by `name` and return it if ok.

        If ``dev_mode`` is not active, validation will be very minimal, or totally absent,
        depending of the type of the prop.

        Parameters
        ----------
        name : str
            The name of the prop for which we want to validate the value.
        value : Any
            The value we want to validate.

        Returns
        -------
        Any
            The validated value. It may have changed, for example for boolean props.

        Raises
        ------
        InvalidPropValueError
            If the value is not a Choices or a bool and not valid.
        InvalidPropChoiceError
            If the value is a Choices and not in the list.
        InvalidPropBoolError
            If the value is a bool and not in the list of acceptable choices.

        """
        if name.startswith("data_") or name.startswith("aria_"):
            return value

        if cls.__is_choice__(name):
            if not BasePropTypes.__dev_mode__:
                return value

            choices = getattr(cls, name)
            if value in choices:
                return value

            raise InvalidPropChoiceError(cls.__owner_name__, name, value, choices)

        if cls.__is_bool__(name):
            # Special case for bool.
            # We can have True:
            #     In html5, bool attributes can set to an empty string or the attribute name.
            #     We also accept python True or a string that is 'true' lowercased.
            #     We force the value to True.
            # We can have False:
            #     In html5, bool attributes can set to an empty string or the attribute name
            #     We also accept python True or a string that is 'true' lowercased.
            #     We force the value to True.
            # All other cases generate an error
            # We do this even in non-dev mode because we want a boolean. Just, in case of error
            # we return the given value casted to a boolean.

            if value in ("", name, True):
                return True
            if value is False:
                return False

            str_value = str(value).capitalize()
            if str_value == "True":
                return True
            if str_value == "False":
                return False

            if not BasePropTypes.__dev_mode__:
                return bool(value)

            raise InvalidPropBoolError(cls.__owner_name__, name, value)

        # normal check
        prop_type = cls.__type__(name)

        # allow numbers to be passed without quotes
        if (
            prop_type is str
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
        ):
            value = str(value)

        if not BasePropTypes.__dev_mode__:
            return value

        try:
            if isinstance(value, prop_type):
                return value
            raise InvalidPropValueError(cls.__owner_name__, name, value, prop_type)

        except TypeError:

            @typechecked  # type: ignore
            def check(  # type: ignore  # pylint: disable=missing-param-doc,missing-type-doc,unused-argument
                prop_value: prop_type,  # type: ignore
            ):
                """Let ``enforce`` check that the value is valid."""

            try:
                check(value)
            except TypeCheckError:
                raise InvalidPropValueError(cls.__owner_name__, name, value, prop_type)

            return value

    @classmethod
    def __validate_required__(cls, props: Dict[str, Any]) -> None:
        """Validate that all required props are present in `props`.

        Parameters
        ----------
        props : Dict[str, Any]
            The props to check.

        Raises
        ------
        RequiredPropError
            If a required prop is not defined in `props`, of if its value is ``NotProvided``.

        """
        if not BasePropTypes.__dev_mode__:
            return
        for name in cls.__required_props__:
            if props.get(name, NotProvided) is NotProvided:
                raise RequiredPropError(cls.__owner_name__, name)

    @classmethod
    def __set_dev_mode__(cls, dev_mode: bool = True) -> None:
        """Change the dev-mode. Activate it if `dev_mode` is not defined.

        Parameters
        ----------
        dev_mode : bool
            The new dev mode wanted. Default to ``True``. Will be casted to ``bool``.

        Examples
        --------
        >>> from mixt import set_dev_mode, in_dev_mode
        >>> in_dev_mode()
        True
        >>> set_dev_mode(False)
        >>> in_dev_mode()
        False
        >>> set_dev_mode()
        >>> in_dev_mode()
        True

        """
        cls.__dev_mode__ = dev_mode

    @classmethod
    def __unset_dev_mode__(cls) -> None:
        """Deactivate the dev-mode.

        Examples
        --------
        >>> from mixt import unset_dev_mode, in_dev_mode
        >>> in_dev_mode()
        True
        >>> unset_dev_mode()
        >>> in_dev_mode()
        False

        """
        cls.__set_dev_mode__(dev_mode=False)

    @classmethod
    @contextmanager
    def __override_dev_mode__(  # pylint: disable=missing-yield-doc,missing-yield-type-doc
        cls, dev_mode: bool
    ) -> Any:
        """Create a context manager to change the dev-mode in a ``with`` block.

        Parameters
        ----------
        dev_mode : bool
            The dev-mode wanted inside the ``with`` block.

        Examples
        --------
        >>> from mixt import override_dev_mode, in_dev_mode
        >>> in_dev_mode()
        True
        >>> with override_dev_mode(False):
        ...     print('off:', in_dev_mode())
        ...     with override_dev_mode(True):
        ...         print('on:', in_dev_mode())
        ...     print('back off:', in_dev_mode())
        ... print('back on:', in_dev_mode())
        off: False
        on: True
        back off: False
        back on: True

        """
        old_dev_mode: bool = cls.__dev_mode__
        try:
            cls.__set_dev_mode__(dev_mode=dev_mode)
            yield
        finally:
            cls.__set_dev_mode__(dev_mode=old_dev_mode)

    @classmethod
    def __in_dev_mode__(cls) -> bool:
        """Return the actual dev-mode.

        Returns
        -------
        bool
            The value of the actual dev-mode.

        Examples
        --------
        >>> from mixt import set_dev_mode, unset_dev_mode, in_dev_mode
        >>> in_dev_mode()
        True
        >>> unset_dev_mode()
        >>> in_dev_mode()
        False
        >>> set_dev_mode()
        >>> in_dev_mode()
        True


        """
        return cls.__dev_mode__
