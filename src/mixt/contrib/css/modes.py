"""Provides the different rendering modes for ``render_css``."""
from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict


class Modes(Enum):
    """Rendering modes for ``render_css``.

    Attributes
    ----------
    COMPRESSED : dict
        The minimal mode, reduces the white space at the minimum, on one line.
        Comments are not rendered.
    COMPACT : dict
        Render each selector on its own line, without indentation except for @ rules content.
        Comments are not rendered.
    NORMAL : dict
        Each selector and each declaration is on its own line. Declarations are indented.
        Selectors are not, except in @ rules.
        Comments are rendered.
    INDENT : dict
        Same as ``NORMAL`` but with each "sub" selector indented from is parent (".foo bar" is
        indented one more level than ".foo").
    INDENT2 : dict
        Same as ``INDENT`` but declarations are indented twice, and closing ``}`` is indented
        once, to be at the same level as the sub selectors.
    INDENT3 : dict
        Same as ``INDENT`` but closing ``}`` are put at the end of the previous declaration.

    Examples
    --------
    >>> css = {
    ...     ".content": {
    ...         "color": "blue",
    ...         "font-weight": "bold",
    ...         "background": "green",
    ...         ".foo": {
    ...             "color": "green",
    ...         },
    ...         "@media(all and (max-width: 600px)": {
    ...             "": {
    ...                 "color": "red",
    ...                 "/*": "a comment",
    ...                 "font-weight": "normal",
    ...                 ".foo": {
    ...                     "color": "yellow",
    ...                 }
    ...             }
    ...         },
    ...         ":raw:": ".foo-bar {color: black}",
    ...         ".bar": {
    ...             "color": "orange",
    ...         },
    ...         "z-index": 1,
    ...     },
    ... }

    >>> from mixt.contrib.css import Modes, render_css
    >>> print(render_css(css, Modes.COMPRESSED))
    .content{color:blue;font-weight:bold;background:green}.content .foo{color:green}@media(all and (
    max-width: 600px){.content{color:red;font-weight:normal}.content .foo{color:yellow}}.foo-bar {
    color: black}.content .bar{color:orange}.content{z-index:1}

    >>> print(render_css(css, Modes.COMPACT))
    .content {color: blue; font-weight: bold; background: green}
    .content .foo {color: green}
    @media(all and (max-width: 600px) {
     .content {color: red; font-weight: normal}
     .content .foo {color: yellow}
    }
    .foo-bar {color: black}
    .content .bar {color: orange}
    .content {z-index: 1}

    >>> print(render_css(css, Modes.NORMAL))
    .content {
      color: blue;
      font-weight: bold;
      background: green;
    }
    .content .foo {
      color: green;
    }
    @media(all and (max-width: 600px) {
      .content {
        color: red;
        /* a comment */
        font-weight: normal;
      }
      .content .foo {
        color: yellow;
      }
    }
    .foo-bar {color: black}
    .content .bar {
      color: orange;
    }
    .content {
      z-index: 1;
    }

    >>> print(render_css(css, Modes.INDENT))
    .content {
        color: blue;
        font-weight: bold;
        background: green;
    }

        .content .foo {
            color: green;
        }

        @media(all and (max-width: 600px) {

            .content {
                color: red;
                /* a comment */
                font-weight: normal;
            }

                .content .foo {
                    color: yellow;
                }
        }

        .foo-bar {color: black}

        .content .bar {
            color: orange;
        }

    .content {
        z-index: 1;
    }

    >>> print(render_css(css, Modes.INDENT2))
    .content {
            color: blue;
            font-weight: bold;
            background: green;
        }

        .content .foo {
                color: green;
            }

        @media(all and (max-width: 600px) {

            .content {
                    color: red;
                    /* a comment */
                    font-weight: normal;
                }

                .content .foo {
                        color: yellow;
                    }
            }

        .foo-bar {color: black}

        .content .bar {
                color: orange;
            }

    .content {
            z-index: 1;
        }

    >>> print(render_css(css, Modes.INDENT3))
    .content {
        color: blue;
        font-weight: bold;
        background: green }

        .content .foo {
            color: green }

        @media(all and (max-width: 600px) {

            .content {
                color: red;
                /* a comment */
                font-weight: normal }

                .content .foo {
                    color: yellow } }

        .foo-bar {color: black}

        .content .bar {
            color: orange }

    .content {
        z-index: 1 }

    """

    COMPRESSED: Dict = {
        "indent": "",
        "endline": "",
        "sel_after_endline": "",
        "decl_endline": "",
        "indent_closing_incr": 0,
        "decl_incr": 0,
        "space": "",
        "opening_endline": "",
        "closing_endline": "",
        "indent_children": False,
        "force_indent_rule_children": "",
        "last_semi": False,
        "display_comments": False,
    }
    COMPACT: Dict = {
        "indent": "",
        "endline": "",
        "sel_after_endline": "\n",
        "decl_endline": " ",
        "indent_closing_incr": 0,
        "decl_incr": 0,
        "space": " ",
        "opening_endline": "",
        "closing_endline": "",
        "indent_children": False,
        "force_indent_rule_children": " ",
        "last_semi": False,
        "display_comments": False,
    }
    NORMAL: Dict = {
        "indent": "  ",
        "endline": "\n",
        "sel_after_endline": "\n",
        "decl_endline": "\n",
        "indent_closing_incr": 0,
        "decl_incr": 1,
        "space": " ",
        "opening_endline": "\n",
        "closing_endline": "\n",
        "indent_children": False,
        "force_indent_rule_children": "",
        "last_semi": True,
        "display_comments": True,
    }
    INDENT: Dict = {
        "indent": "    ",
        "endline": "\n",
        "sel_after_endline": "\n\n",
        "decl_endline": "\n",
        "indent_closing_incr": 0,
        "decl_incr": 1,
        "space": " ",
        "opening_endline": "\n",
        "closing_endline": "\n",
        "indent_children": True,
        "force_indent_rule_children": "",
        "last_semi": True,
        "display_comments": True,
    }
    INDENT2: Dict = {
        "indent": "    ",
        "endline": "\n",
        "sel_after_endline": "\n\n",
        "decl_endline": "\n",
        "indent_closing_incr": 1,
        "decl_incr": 2,
        "space": " ",
        "opening_endline": "\n",
        "closing_endline": "\n",
        "indent_children": True,
        "force_indent_rule_children": "",
        "last_semi": True,
        "display_comments": True,
    }
    INDENT3: Dict = {
        "indent": "    ",
        "endline": "\n",
        "sel_after_endline": "\n\n",
        "decl_endline": "\n",
        "indent_closing_incr": -100,
        "decl_incr": 1,
        "space": " ",
        "opening_endline": "\n",
        "closing_endline": " ",
        "indent_children": True,
        "force_indent_rule_children": "",
        "last_semi": False,
        "display_comments": True,
    }


__DEFAULT_MODE__ = Modes.NORMAL


def set_default_mode(mode: Modes) -> None:
    """Change the default CSS rendering mode.

    Parameters
    ----------
    mode : Modes
        The rendering mode to use.

    Examples
    --------
    >>> from mixt.contrib.css import Modes, set_default_mode, get_default_mode
    >>> get_default_mode().name
    'NORMAL'
    >>> set_default_mode(Modes.COMPACT)
    >>> get_default_mode().name
    'COMPACT'

    """
    global __DEFAULT_MODE__  # pylint: disable=global-statement
    __DEFAULT_MODE__ = mode


@contextmanager
def override_default_mode(  # pylint: disable=missing-yield-doc,missing-yield-type-doc
    mode: Modes,
) -> Any:
    """Create a context manager to change the default rendering mode in a ``with`` block.

    Parameters
    ----------
    mode : Modes
        The rendering mode to use in the ``with`` block.

    Examples
    --------
    >>> from mixt.contrib.css import Modes, override_default_mode, get_default_mode
    >>> get_default_mode().name
    'NORMAL'
    >>> with override_default_mode(Modes.COMPACT):
    ...     print(get_default_mode().name)
    ...     with override_default_mode(Modes.INDENT3):
    ...         print(get_default_mode().name)
    ...     print(get_default_mode().name)
    ... print(get_default_mode().name)
    COMPACT
    INDENT3
    COMPACT
    NORMAL

    """
    old_default_mode: Modes = __DEFAULT_MODE__
    try:
        set_default_mode(mode=mode)
        yield
    finally:
        set_default_mode(mode=old_default_mode)


def get_default_mode() -> Modes:
    """Return the actual default rendering mode.

    Returns
    -------
    Modes
        The actual default rendering mode.

    Examples
    --------
    >>> from mixt.contrib.css import Modes, set_default_mode, get_default_mode
    >>> get_default_mode().name
    'NORMAL'
    >>> set_default_mode(Modes.COMPACT)
    >>> get_default_mode().name
    'COMPACT'

    """
    return __DEFAULT_MODE__
