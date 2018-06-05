"""Define the class that will handle everything about props."""

from contextlib import contextmanager
import keyword
from typing import Any, Dict, Sequence, Set, Type, get_type_hints

from enforce.exceptions import RuntimeTypeError

from ..exceptions import PyxlException  # noqa: T484
from ..proptypes import Choices, DefaultChoices, NotProvided, Required  # noqa: T484


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

    __dev_mode__: bool = True

    @staticmethod
    def __to_html__(name: str) -> str:
        """Convert a prop name to be usable as an html attribute name.

        Parameters
        ----------
        name: str
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
        name: str
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
            raise NameError
        if keyword.iskeyword(name) or name in FUTURE_KEYWORDS:
            name = "_" + name
        return name

    @classmethod
    def __allow__(cls, name: str) -> bool:
        """Tell if the given name is an allowed python prop name.

        Parameters
        ----------
        name: str
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
        name: str
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
        name: str
            The name of the prop we ask for.

        Returns
        -------
        bool
            ``True`` if the type of the prop is ``Choices``. False otherwise.

        """
        return issubclass(cls.__type__(name), Choices)

    @classmethod
    def __is_bool__(cls, name: str) -> bool:
        """Tell if the type of the prop defined by `name` is ``bool``.

        Parameters
        ----------
        name: str
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
        name: str
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
    def __validate_types__(cls: Type["BasePropTypes"]) -> None:
        """Validate the types of the props defined in the current PropTypes class.

        Raises
        ------
        PyxlException
            - If a prop is a ``Choices`` with no or empty list.
            - If a prop is a ``DefaultChoices`` and is marked as ``Required``.
            - For all other props marked as ``Required`` if there is a value.
            - If the default value is not valid for the prop type.

        """
        cls.__types__ = {
            name: prop_type
            for name, prop_type in get_type_hints(cls).items()
            if not hasattr(BasePropTypes, name)
        }

        for name, prop_type in cls.__types__.items():

            is_required = False
            if issubclass(prop_type, Required):
                is_required = True
                prop_type = prop_type.__args__[0]
                cls.__types__[name] = prop_type
                cls.__required_props__.add(name)

            if cls.__is_choice__(name):

                if not getattr(cls, name, []):
                    raise PyxlException(
                        f"<{cls.__owner_name__}> must have a list of values for prop `{name}`"
                    )

                choices = getattr(cls, name)
                if not isinstance(choices, Sequence) or isinstance(choices, str):
                    raise PyxlException(
                        f"<{cls.__owner_name__}> must have a list of values for prop `{name}`"
                    )

                if issubclass(cls.__type__(name), DefaultChoices):
                    if choices[0] is not NotProvided:
                        if is_required:
                            raise PyxlException(
                                f"<{cls.__owner_name__}> cannot have a default "
                                f"value for the required prop `{name}`"
                            )
                        cls.__default_props__[name] = choices[0]

                continue

            default = getattr(cls, name, NotProvided)
            if default is NotProvided:
                continue

            if is_required:
                raise PyxlException(
                    f"<{cls.__owner_name__}> cannot have a default value "
                    f"for the required prop `{name}`"
                )

            try:
                cls.__validate__(name, default)
            except PyxlException:
                raise PyxlException(
                    f"<{cls.__owner_name__}>.{name}: {type(default)} `{default}` "
                    f"is not a valid default value"
                )

            cls.__default_props__[name] = default

    @classmethod  # noqa: C901
    def __validate__(  # pylint: disable=too-many-return-statements,too-many-branches
        cls, name: str, value: Any
    ) -> Any:
        """Validate the `value` for the prop defined by `name` and return it if ok.

        If ``dev_mode`` is not active, validation will be very minimal, or totally absent,
        depending of the type of the prop.

        Parameters
        ----------
        name: str
            The name of the prop for which we want to validate the value.
        value: Any
            The value we want to validate.

        Returns
        -------
        Any
            The validated value. It may have changed, for example for boolean props.

        Raises
        ------
        PyxlException
            If the value is not valid.

        """
        if name.startswith("data_") or name.startswith("aria_"):
            return value

        if cls.__is_choice__(name):
            if not BasePropTypes.__dev_mode__:
                return value

            if value in getattr(cls, name):
                return value

            raise PyxlException(
                f"<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid choice"
            )

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

            raise PyxlException(
                f"<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value"
            )

        # normal check

        if not BasePropTypes.__dev_mode__:
            return value

        prop_type = cls.__type__(name)
        try:
            if isinstance(value, prop_type):
                return value
            raise PyxlException(
                f"<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value"
            )

        except TypeError:
            # we use "enforce" to check complex types
            import enforce

            @enforce.runtime_validation  # type: ignore
            def check(  # type: ignore  # pylint: disable=missing-param-doc,missing-type-doc,unused-argument
                prop_value: prop_type  # type: ignore
            ):
                """Let ``enforce`` check that the value is valid."""
                pass

            try:
                check(value)
            except RuntimeTypeError:
                raise PyxlException(
                    f"<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value"
                )

            return value

    @classmethod
    def __validate_required__(cls, props: Dict[str, Any]) -> None:
        """Validate that all required props are present in `props`.

        Parameters
        ----------
        props: Dict[str, Any]
            The props to check.

        Raises
        ------
        PyxlException
            If a required prop is not defined in `props`, of if its value is ``NotProvided``.

        """
        if not BasePropTypes.__dev_mode__:
            return
        for name in cls.__required_props__:
            if props.get(name, NotProvided) is NotProvided:
                raise PyxlException(
                    f"<{cls.__owner_name__}>.{name}: is required but not set"
                )

    @classmethod
    def __set_dev_mode__(cls, dev_mode: bool = True) -> None:
        """Change the dev-mode. Activate it if `dev_mode` is not defined.

        Parameters
        ----------
        dev_mode: bool
            The new dev mode wanted. Default to ``True``. Will be casted to ``bool``

        """
        cls.__dev_mode__ = dev_mode

    @classmethod
    def __unset_dev_mode__(cls) -> None:
        """Deactivate the dev-mode."""
        cls.__set_dev_mode__(dev_mode=False)

    @classmethod
    @contextmanager
    def __override_dev_mode__(  # pylint: disable=missing-yield-doc,missing-yield-type-doc
        cls, dev_mode: bool
    ) -> Any:
        """Create a context manager to change the dev-mode in a ``with`` block.

        Parameters
        ----------
        dev_mode: bool
            The dev-mode wanted inside the ``with`` block.

        Examples
        --------
        >>> assert PropTypes.__in_dev_mode__()
        >>> with PropTypes.__override_dev_mode__(False):
        ...     assert not PropTypes.__in_dev_mode__()
        >>> assert PropTypes.__in_dev_mode__()

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

        """
        return cls.__dev_mode__