from mixt.contrib.css import Modes, render_css
from mixt.contrib.css.vars import Var, dummy as _, join, many, media, override


# basic rendering (from dict of strings) is tested in ``test_modes.py``


def test_explicit_join():
    css = {".foo": {"margin": join("1px", "2px", "3px", "4px")}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  margin: 1px 2px 3px 4px;
}
"""
    )


def test_implicit_join():
    css = {".foo": {"margin": ("1px", "2px", "3px", "4px")}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  margin: 1px 2px 3px 4px;
}
"""
    )


def test_explicit_many():
    css = {".foo": {"font-family": many("Gill", "Helvetica", "sans-serif")}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  font-family: Gill, Helvetica, sans-serif;
}
"""
    )


def test_implicit_many():
    css = {".foo": {"font-family": ["Gill", "Helvetica", "sans-serif"]}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  font-family: Gill, Helvetica, sans-serif;
}
"""
    )


def test_explicit_many_and_join():
    css = {
        ".foo": {
            "text-shadow": many(
                join("1px", "1px", "2px", "red"),
                join(0, 0, "1em", "blue"),
                join(0, 0, "0.2em", "blue"),
            )
        }
    }

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  text-shadow: 1px 1px 2px red, 0 0 1em blue, 0 0 0.2em blue;
}
"""
    )


def test_implicit_many_and_join():
    css = {
        ".foo": {
            "text-shadow": [
                ("1px", "1px", "2px", "red"),
                (0, 0, "1em", "blue"),
                (0, 0, "0.2em", "blue"),
            ]
        }
    }

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  text-shadow: 1px 1px 2px red, 0 0 1em blue, 0 0 0.2em blue;
}
"""
    )


def test_override():
    webkit, moz, ms, o, linear, gradient = Var.many("webkit moz ms o linear gradient")
    css = {
        ".foo": {
            "background": override(
                -webkit-linear-gradient("left", "blue", "red", "blue"),
                -moz-linear-gradient("left", "blue", "red", "blue"),
                -ms-linear-gradient("left", "blue", "red", "blue"),
                -o-linear-gradient("left", "blue", "red", "blue"),
                linear-gradient("left", "blue", "red", "blue"),
            )
        }
    }

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  background: -webkit-linear-gradient(left, blue, red, blue);
  background: -moz-linear-gradient(left, blue, red, blue);
  background: -ms-linear-gradient(left, blue, red, blue);
  background: -o-linear-gradient(left, blue, red, blue);
  background: linear-gradient(left, blue, red, blue);
}
"""
    )


def test_key_explicit_nested():
    css = {".foo": {"padding": "1px", "& .bar": {"padding": "none"}}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
.foo .bar {
  padding: none;
}
"""
    )


def test_key_implicit_nested():
    css = {".foo": {"padding": "1px", ".bar": {"padding": "none"}}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
.foo .bar {
  padding: none;
}
"""
    )


def test_ampersand_other_position():
    css = {
        ".foo": {
            "padding": "1px",
            ".bar &": {"padding": "none"},
            "&-bar": {"padding": "2px"},
        }
    }

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
.bar .foo {
  padding: none;
}
.foo-bar {
  padding: 2px;
}
"""
    )


def test_ampersand_repeated():
    css = {".foo": {"padding": "1px", "&:hover, &:focus": {"padding": "none"}}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
.foo:hover, .foo:focus {
  padding: none;
}
"""
    )


def test_implicit_ampersand_if_many_selectors():
    css = {".foo": {"padding": "1px", ".bar, .baz": {"padding": "none"}}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
.foo .bar, .foo .baz {
  padding: none;
}
"""
    )


def test_many_selectors_are_managed():
    css = {
        ".foo": {
            "padding": "1px",
            (".bar", ".baz"): {  # as tuple
                "padding": "none",
                "[data-foo], [data-bar]": {  # as comma separated string
                    (f"&:{x}" for x in ["hover", "focus"]): {  # as generator
                        "padding": "2px"
                    }
                },
            },
        }
    }

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
.foo .bar, .foo .baz {
  padding: none;
}
.foo .bar [data-foo]:hover, .foo .bar [data-foo]:focus, .foo .bar [data-bar]:hover, .foo .bar [data-bar]:focus, .foo .baz [data-foo]:hover, .foo .baz [data-foo]:focus, .foo .baz [data-bar]:hover, .foo .baz [data-bar]:focus {
  padding: 2px;
}
"""
    )


def test_use_space_to_repeat_selectors():
    css = {
        ".foo": {"padding": "1px"},
        ".bar .foo": {"padding": "2px"},
        ".foo ": {  # added space to repeat the selector, as order is important in css
            "padding": "3px"
        },
    }

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
.bar .foo {
  padding: 2px;
}
.foo {
  padding: 3px;
}
"""
    )


def test_at_rule():
    css = {
        ".foo": {
            "padding": "1px",
            media({"max-width": "1280px"}): {
                "padding": "2px",  # direct properties
                "": {"padding": "2.1px"},  # or as empty string
                "&": {"padding": "2.2px"},  # or as "&"
                ".bar": {"padding": "3px"},
            },
            ".bar": {
                "padding": "4px",
                media({"min-width": "640px"}): {
                    "padding": "5px",
                    _: {"padding": "5.1px"},  # or as "_" (dummy var = empty string)
                },
            },
        }
    }
    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
.foo {
  padding: 1px;
}
@media (max-width: 1280px) {
  .foo {
    padding: 2px;
  }
  .foo {
    padding: 2.1px;
  }
  .foo {
    padding: 2.2px;
  }
  .foo .bar {
    padding: 3px;
  }
}
.foo .bar {
  padding: 4px;
}
@media (min-width: 640px) {
  .foo .bar {
    padding: 5px;
  }
  .foo .bar {
    padding: 5.1px;
  }
}
"""
    )


def test_at_rule_at_first_level():
    css = {
        "@media": {
            "should": "work",  # invalid for media but valid for other @-rules
            "should-work": "too",
            ".foo": {"padding": "1px"},
        }
    }

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
@media {
  should: work;
  should-work: too;
  .foo {
    padding: 1px;
  }
}
"""
    )


def test_declaration_without_value():
    css = {"@charset 'UTF-8'": None, ".bar": {"padding": "1px"}}

    assert (
        render_css(css, mode=Modes.NORMAL)
        == """\
@charset 'UTF-8';
.bar {
  padding: 1px;
}
"""
    )
