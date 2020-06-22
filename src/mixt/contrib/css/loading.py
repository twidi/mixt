"""Functions used to load CSS vars."""
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generator, List, Optional

import wrapt

from .vars import CSS_VARS, add_css_var, load_defaults


def css_vars(  # noqa: D202
    namespace: Dict[str, Any], max_undefined_vars: int = 1000
) -> Callable:
    """Decorate a function to auto-load CSS vars and auto-add undefined ones.

    It must be called with ``globals()`` for the `namespace` argument, in order to have all the
    CSS variables imported in the scope of the caller.

    Parameters
    ----------
    namespace : Dict[str, Any]
        The dict where to add the vars defined in ``CSS_VARS``.
    max_undefined_vars : int
        Number of allowed undefined vars. Default to 1000.

    Returns
    -------
    Callable
        A wrapper that will import CSS vars in the namespace and auto-create undefined ones.

    Examples
    --------
    >>> from mixt.contrib.css import css_vars, render_css
    >>> @css_vars(globals())
    ... def css():
    ...     return {
    ...         ".foo": {
    ...             margin-top: 3*px
    ...         }
    ...     }
    >>> print(render_css(css()))
    ... .foo {
    ...   margin-top: 3px;
    ... }

    """

    @wrapt.decorator  # type: ignore
    def wrapper(  # pylint: disable=unused-argument
        wrapped: Callable, instance: Any, args: Any, kwargs: Any
    ) -> Any:
        """Decorate a function to auto-add undefined vars as CSS vars.

        It works by running the `wrapped` function, catching ``NameError`` and create the variable
        that caused this exception. This is repeated until there is no more ``NameError``.

        Parameters
        ----------
        wrapped : Callable
            The function to decorate.
        instance : Any
            The instance calling the function if `wrapped` is a method.
        args : Any
            The named arguments passed to the `wrapped` function.
        kwargs : Any
            The unnamed arguments passed to the `wrapped` function.

        Raises
        ------
        RecursionError
            When more than ``max_undefined_vars`` undefined variables where found.

        Returns
        -------
        Any
            The result of the call to `wrapper`.

        """
        iterations = 0
        while iterations < max_undefined_vars:
            try:
                with import_css(namespace):
                    return wrapped(*args, **kwargs)
            except NameError as exc:
                name = str(exc).split("'")[1]
                # print(f"Resolve {name}")
                add_css_var(name)
                iterations += 1

        raise RecursionError(
            f"Too much iteration to decode `{wrapped.__name__}` (last: `{name}`)"
        )

    return wrapper


@contextmanager
def import_css(  # pylint: disable=missing-yield-doc,missing-yield-type-doc
    namespace: Dict[str, Any]
) -> Generator:
    """Import all vars defined in ``CSS_VARS`` into the given `namespace`.

    It must be called with ``globals()`` for the `namespace` argument, in order to have all the
    CSS variables imported in the scope of the caller.

    Must be used as a context manager, to have the namespace restored at the end.

    Parameters
    ----------
    namespace : Dict[str, Any]
        The dict where to add the vars defined in ``CSS_VARS``.

    Examples
    --------
    >>> from mixt.contrib.css import import_css, load_css_keywords
    >>> load_css_keywords()
    >>> print(margin)
    Traceback (most recent call last)
    ...
    NameError: name 'margin' is not defined
    >>> with import_css(globals()):
    ...    builtins.print(margin)
    'margin'
    >>> print(margin)
    Traceback (most recent call last)
    ...
    NameError: name 'margin' is not defined

    """
    namespace_copy = namespace.copy()
    try:
        namespace.update(CSS_VARS)
        yield
    finally:
        namespace.clear()
        namespace.update(namespace_copy)


def import_css_global(namespace: Dict[str, Any]) -> None:
    """Import all vars defined in ``CSS_VARS`` into the given `namespace`.

    Same as ``import_css`` but it is not a context manager and global state cannot be restored.

    Parameters
    ----------
    namespace : Dict[str, Any]
        The dict where to add the vars defined in ``CSS_VARS``.

    Examples
    --------
    >>> from mixt.contrib.css import import_css_global, load_css_keywords
    >>> load_css_keywords()
    >>> print(margin)
    Traceback (most recent call last)
    ...
    NameError: name 'margin' is not defined
    >>> import_css_global(globals())
    >>> builtins.print(margin)

    """
    namespace.update(CSS_VARS)


def load_css_keywords(keywords: Optional[List[str]] = None) -> None:
    """Load all the given list of CSS keywords and units in ``CSS_VARS``.

    If the list of keywords is not set, it will load the one from
    ``mixt.contrib.css.css_keywords_list``.

    Default vars and units will be reloaded after the loading of the keyword to be sure
    to always have them available.

    Parameters
    ----------
    keywords : List[str]
        The list of css keywords to load. Default to ``None``. In this case, will use the
        full list from ``mixt.contrib.css.css_keywords_list``.

    """
    from .units import load_css_units  # pylint: disable=import-outside-toplevel

    if keywords is None:
        if load_css_keywords.main_is_done:  # type: ignore
            return
        load_css_keywords.main_is_done = True  # type: ignore
        from .css_keywords_list import (  # pylint: disable=import-outside-toplevel
            KEYWORDS,
        )

        keywords = KEYWORDS

    for name in keywords:
        add_css_var(name)

    # we always reload our defaults and units
    load_defaults()
    load_css_units()


load_css_keywords.main_is_done = False  # type: ignore
