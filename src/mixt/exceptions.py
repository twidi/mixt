"""All mixt exceptions.

Each type of error has its own exception, but there is a tree of exception classes starting from
``MixtException``, so it's easy to catch many exception types at one.

This module can be imported from mixt: ``from mixt import exceptions``.

"""

from typing import Any, List, Tuple

from mixt.codec.state import State


class MixtException(Exception):
    """Default exception raised for all Mixt problems.

    Base: ``Exception``.
    """

    def __init__(self, message: str = "") -> None:
        """Init the exception.

        Parameters
        ----------
        message : str
            The exception message.

        """
        self.message = message

        super().__init__(message)


class ElementError(MixtException):
    """Exception related to element classes.

    Base: ``MixtException``.
    """

    def __init__(self, tag_name: str, message: str = "") -> None:
        """Init the exception.

        Parameters
        ----------
        tag_name : str
            The element tag for which this exception is raised.
        message : str
            The exception message.

        """
        if message and not message.startswith(".") and not message.startswith(" "):
            message = " " + message
        self.tag_name = tag_name

        super().__init__(f"<{tag_name}>{message}")


class PropError(ElementError):
    """Exception related to props.

    Base: ``ElementError``.
    """

    def __init__(self, tag_name: str, prop_name: str, message: str = "") -> None:
        """Init the exception.

        Parameters
        ----------
        prop_name : str
            The prop name for which this exception is raised.

        For the other parameters, see ``ElementError``.


        """
        self.prop_name = prop_name

        super().__init__(tag_name, f".{prop_name}: {message}")


class PropTypeError(PropError):
    """Exception related to prop-types definition.

    Base: ``PropError``.
    """


class PropTypeChoicesError(PropTypeError):
    """Exception related to prop-types definition for type "choices".

    Base: ``PropTypeError``.
    """


class PropTypeRequiredError(PropTypeError):
    """Exception related to prop-types definition for required props.

    Base: ``PropTypeError``.
    """


class InvalidPropNameError(PropError, AttributeError):
    """Exception raised when a name is not in allowed props.

    Bases: ``PropError, AttributeError``.
    """

    def __init__(self, tag_name: str, prop_name: str) -> None:
        """Init the exception.

        For the parameters, see ``PropError``.

        """
        super().__init__(tag_name, prop_name, "is not an allowed prop")


class InvalidPropValueError(PropError, TypeError):
    """Exception raised when a value is not valid for a prop.

    Bases: ``PropError, TypeError``.
    """

    def __init__(
        self, tag_name: str, prop_name: str, value: Any, expected_type: Any
    ) -> None:
        """Init the exception.

        Parameters
        ----------
        value : Any
            The invalid value
        expected_type : Any
            The expected type

        For the other parameters, see ``PropError``.

        """
        self.value = value
        self.expected_type = expected_type

        super().__init__(
            tag_name,
            prop_name,
            f"`{value}` is not a valid value for this prop "
            f"(type: {type(value)}, expected: {expected_type})",
        )


class InvalidPropChoiceError(InvalidPropValueError):
    """Exception raised when a value is not valid for a prop of type "choices".

    Base: ``InvalidPropValueError``.
    """

    def __init__(
        self, tag_name: str, prop_name: str, value: Any, choices: List[Any]
    ) -> None:
        """Init the exception.

        Parameters
        ----------
        choices : List[Any]
            The list of valid choices.

        For the other parameters, see ``InvalidPropValueError``.

        """
        self.value = value
        self.choices = choices

        # super of InvalidPropValueError: PropError
        super(  # type: ignore  # pylint: disable=bad-super-call
            InvalidPropValueError, self
        ).__init__(
            tag_name,
            prop_name,
            f"`{value}` is not a valid choice for this prop (must be in {choices})",
        )


class InvalidPropBoolError(InvalidPropValueError):
    """Exception raised when a value is not valid for a prop of type "bool".

    Base: ``InvalidPropValueError``.
    """

    def __init__(self, tag_name: str, prop_name: str, value: Any) -> None:
        """Init the exception.

        For the parameters, see ``InvalidPropValueError``.

        """
        self.value = value

        # super of InvalidPropValueError: PropError
        super(  # type: ignore  # pylint: disable=bad-super-call
            InvalidPropValueError, self
        ).__init__(
            tag_name,
            prop_name,
            f"`{value}` is not a valid choice for this boolean prop "
            f"(must be in [True, False, 'true', 'false', '', '{prop_name}'])",
        )


class RequiredPropError(PropError, TypeError):
    """Exception raised when a prop is required but not set.

    Bases: ``PropError, TypeError``.
    """

    def __init__(self, tag_name: str, prop_name: str) -> None:
        """Init the exception.

        For the parameters, see ``PropError``.

        """
        super().__init__(tag_name, prop_name, "is a required prop but is not set")


class UnsetPropError(PropError, AttributeError):
    """Exception raised when a prop is accessed but not set (without default).

    Bases: ``PropError, AttributeError``.
    """

    def __init__(self, tag_name: str, prop_name: str) -> None:
        """Init the exception.

        For the parameters, see ``PropError``.

        """
        super().__init__(tag_name, prop_name, "prop is not set")


class InvalidChildrenError(ElementError):
    """Exception related to children of an element.

    Base: ``ElementError``.
    """


class GeneralParserError(Exception):
    """Exception related to parsing mixt-encoded python/html.

    Base: ``Exception``.
    """

    def __init__(self, message: str = "") -> None:
        """Init the exception.

        Parameters
        ----------
        message : str
            The exception message.

        """
        self.message = message
        super().__init__(f"<mixt parser> {message}")


class ParserStateError(GeneralParserError):
    """Parser exceptions with a state.

    Base: ``GeneralParserError``.
    """

    def __init__(self, state: int, message: str = "") -> None:
        """Init the exception.

        Parameters
        ----------
        state : int
            One of the states defined in ``State``

        For the other parameters, see ``GeneralParserError``.

        """
        self.state = state

        super().__init__(f"[State={State.state_name(state)}] {message}")


class BadCharError(ParserStateError):
    """Exception raised by the parser when an unexpected character is found.

    Base: ``ParserStateError``.
    """

    def __init__(self, state: int, char: str) -> None:
        """Init the exception.

        Parameters
        ----------
        char : str
            The unexpected character

        For the other parameters, see ``ParserStateException``.

        """
        self.char = char

        super().__init__(state, f"Unexpected character `{char}`")


class ParserError(GeneralParserError):
    """Exception raised by the mixt parser, with position of the problem.

    Base: ``GeneralParserError``.
    """

    def __init__(
        self,
        message: str,
        pos: Tuple[int, int] = None,
        from_exception: Exception = None,
    ) -> None:
        """Init the exception.

        Parameters
        ----------
        pos : Tuple[int, int]
            One of the states defined in ``State``
        from_exception : Exception
            The exception that may have triggered this one.

        For the other parameters, see ``GeneralParserError``.

        """
        self.pos = pos
        self.from_exception = from_exception

        if pos:
            final_message = f"[line={pos[0]}, col={pos[1]}] {message}"
        else:
            final_message = message

        if isinstance(from_exception, MixtException):
            final_message += (
                f" (Original exception: <{from_exception.__class__.__name__}> "
                f"{from_exception.message}"
            )
        elif from_exception:
            final_message += f" (Original exception: {str(from_exception)}"

        super().__init__(final_message)
