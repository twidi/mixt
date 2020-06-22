"""Types used through mixt and to be used externally."""

from typing import Generic, Sequence, TypeVar, Union


# pylint: disable=invalid-name,pointless-statement


__all__ = ["Choices", "DefaultChoices", "NotProvided", "Number", "Required"]


Number = Union[int, float]


class NotProvided:
    """To be used instead of ``None`` for not provided values.

    It is useful because ``None`` could be the value we want to pass to a function, and it is
    different than "nothing was passed"

    """

    ...


RequiredType = TypeVar("RequiredType")


class Required(Generic[RequiredType]):
    """For PropTypes that MUST be passed. By default they are all optional.

    Examples
    --------
    >>> class MyElement(Element):
    ...     class PropTypes:
    ...         required_value: Required[str]
    ...         optional_value: str

    """

    ...


SequenceItem = TypeVar("SequenceItem", covariant=True)


class Choices(Sequence[SequenceItem]):
    """For PropTypes that must be chosen from a list of values.

    Examples
    --------
    >>> class MyElement(Element):
    ...     class PropTypes:
    ...         # ``value`` MUST be either "a" or "b' or "c"
    ...         value: Choices = ['a', 'b', 'c']

    """

    ...


class DefaultChoices(Choices):
    """For PropTypes that must be chosen from a list of values, with the first being the default.

    Examples
    --------
    >>> class MyElement(Element):
    ...     class PropTypes:
    ...         # ``value`` MUST be either "a" or "b' or "c"
    ...         # but if not set, it will be set to "a"
    ...         value: DefaultChoices = ['a', 'b', 'c']

    """

    ...
