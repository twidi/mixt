import pytest

from mixt.contrib.css import render_css, Modes
from mixt.contrib.css.vars import extend, merge, combine


def test_external_dict():
    foo = {"margin": "1px"}

    css = {
        ".foo": {"margin": "2px"},
        ".bar": extend(foo),
        ".baz": {
            "a": {"margin": "3px"},
            "b": extend(foo, css={"margin": "4px"}),
        }
    }

    assert render_css(css) == """\
.foo {
  margin: 2px;
}
.bar, .baz b {
  margin: 1px;
}
.baz a {
  margin: 3px;
}
.baz b {
  margin: 4px;
}
"""


def test_internal_dict():
    css = {
        ".foo": {"margin": "2px"},
        ".bar": extend({"margin": "1px"}),
        ".baz": {
            "a": {"margin": "3px"},
            "b": extend({"margin": "1px"}, css={"margin": "4px"}),
        }
    }

    assert render_css(css) == """\
.foo {
  margin: 2px;
}
.bar, .baz b {
  margin: 1px;
}
.baz a {
  margin: 3px;
}
.baz b {
  margin: 4px;
}
"""


def test_internal_named_dict():
    css = {
        ".foo": {"margin": "2px"},
        '%my-extend': {"margin": "1px"},
        ".bar": extend('my-extend'),
        ".baz": {
            "a": {"margin": "3px"},
            "b": extend('my-extend', css={"margin": "4px"}),
        }
    }

    assert render_css(css) == """\
.foo {
  margin: 2px;
}
.bar, .baz b {
  margin: 1px;
}
.baz a {
  margin: 3px;
}
.baz b {
  margin: 4px;
}
"""

    assert render_css(css, mode=Modes.COMPRESSED) == """\
.foo{margin:2px}.bar, .baz b{margin:1px}.baz a{margin:3px}.baz b{margin:4px}"""

    assert render_css(css, mode=Modes.COMPACT) == """\
.foo {margin: 2px}
.bar, .baz b {margin: 1px}
.baz a {margin: 3px}
.baz b {margin: 4px}
"""

    assert render_css(css, mode=Modes.INDENT) == """\
.foo {
    margin: 2px;
}

.bar, .baz b {
    margin: 1px;
}

.baz a {
    margin: 3px;
}

.baz b {
    margin: 4px;
}

"""

    assert render_css(css, mode=Modes.INDENT2) == """\
.foo {
        margin: 2px;
    }

.bar, .baz b {
        margin: 1px;
    }

.baz a {
        margin: 3px;
    }

.baz b {
        margin: 4px;
    }

"""

    assert render_css(css, mode=Modes.INDENT3) == """\
.foo {
    margin: 2px }

.bar, .baz b {
    margin: 1px }

.baz a {
    margin: 3px }

.baz b {
    margin: 4px }

"""


def test_using_undefined_name():
    css = {
        ".foo": extend('my-extend'),
    }

    with pytest.raises(ValueError) as raised:
        render_css(css)

    assert str(raised.value) == "Cannot extend `.foo` with undefined/not yet defined `%my-extend`"


def test_using_name_not_yet_defined():
    css = {
        ".foo": extend('my-extend'),
        '%my-extend': {"margin": "1px"},
    }

    with pytest.raises(ValueError) as raised:
        render_css(css)

    assert str(raised.value) == "Cannot extend `.foo` with undefined/not yet defined `%my-extend`"


def test_defining_name_twice_in_same_scope():
    css = {
        '%my-extend': {"margin": "1px"},
        ".foo": {
            '%my-extend': {"margin": "1px"},
        }
    }

    with pytest.raises(ValueError) as raised:
        render_css(css)

    assert str(raised.value) == "The extend `%my-extend` already exists"


def test_defining_name_twice_in_different_scopes():
    css = {
        ".foo": {
            '%my-extend': {"margin": "1px"},
            "a": extend("my-extend"),
        },
        ".bar": {
            '%my-extend': {"margin": "2px"},
            "a": extend("my-extend"),
        }
    }

    assert render_css(css) == """\
.foo a {
  margin: 1px;
}
.bar a {
  margin: 2px;
}
"""


def test_empty_name():
    css = {
        "%": {"margin": "1px"}
    }

    with pytest.raises(ValueError) as raised:
        render_css(css)

    assert str(raised.value) == "An extend must have a name: it cannot be `%` alone"


def test_blank_name():
    css = {
        "% ": {"margin": "1px"}
    }

    with pytest.raises(ValueError) as raised:
        render_css(css)

    assert str(raised.value) == "An extend must have a name: it cannot be `%` alone"


def test_with_merge():
    lib = {
        '%my-extend': {"margin": "1px"},
    }

    css = {
        ".foo": {"margin": "2px"},
        ".bar": extend('my-extend'),
        ".baz": {
            "a": {"margin": "3px"},
            "b": extend('my-extend', css={"margin": "4px"}),
        }
    }

    assert render_css(merge(lib, css)) == """\
.bar, .baz b {
  margin: 1px;
}
.foo {
  margin: 2px;
}
.baz a {
  margin: 3px;
}
.baz b {
  margin: 4px;
}
"""


def test_with_combine():
    lib = {
        '%my-extend': {"margin": "1px"},
    }

    css = {
        ".foo": {"margin": "2px"},
        ".bar": extend('my-extend'),
        ".baz": {
            "a": {"margin": "3px"},
            "b": extend('my-extend', css={"margin": "4px"}),
        }
    }

    assert render_css(combine(lib, css)) == """\
.bar, .baz b {
  margin: 1px;
}
.foo {
  margin: 2px;
}
.baz a {
  margin: 3px;
}
.baz b {
  margin: 4px;
}
"""


def test_not_used():
    css = {
        ".foo": {"margin": "2px"},
        '%my-extend': {"margin": "1px"},
        ".baz": {
            "a": {"margin": "3px"},
        }
    }

    assert render_css(css) == """\
.foo {
  margin: 2px;
}
.baz a {
  margin: 3px;
}
"""


def test_extend_many():
    ext1 = {"color": "ext1"}
    css = {
        ".foo": {"margin": "2px"},
        "%ext2": {"color": "ext2"},  # all ext2 usages are here
        ".bar": extend(ext1),  # all ext1 usages are here
        ".baz": {
            "a": {"margin": "3px"},
            "b": extend(ext1, "ext2", css={"margin": "4px"}),
        }

    }

    assert render_css(css) == """\
.foo {
  margin: 2px;
}
.baz b {
  color: ext2;
}
.bar, .baz b {
  color: ext1;
}
.baz a {
  margin: 3px;
}
.baz b {
  margin: 4px;
}
"""


def test_at_rule():
    ext1 = {"color": "ext1"}
    css = {
        ".foo": {"margin": "2px"},
        "%ext2": {"color": "ext2"},  # all ext2 usages are here, except from media
        ".bar": extend(ext1),  # all ext1 usages are here, except from media
        "@media all": {
            # all ext2 in media are before, because named extend
            "%ext3": {"color": "ext3"},  # all ext3 in media are here
            ".barbar": extend(ext1),  # all ext1 in media are here, because dict extend
            ".bazbaz": {
                ".qux1": {"margin": "33px"},
                ".qux2": extend(ext1, "ext2", "ext3", css={"margin": "44px"}),
            }
        },
        ".baz": {
            "a": {"margin": "3px"},
            "b": extend(ext1, "ext2", css={"margin": "4px"}),
        }

    }

    assert render_css(css) == """\
.foo {
  margin: 2px;
}
.baz b {
  color: ext2;
}
.bar, .baz b {
  color: ext1;
}
@media all {
  .bazbaz .qux2 {
    color: ext2;
  }
  .barbar, .bazbaz .qux2 {
    color: ext1;
  }
  .bazbaz .qux2 {
    color: ext3;
  }
  .bazbaz .qux1 {
    margin: 33px;
  }
  .bazbaz .qux2 {
    margin: 44px;
  }
}
.baz a {
  margin: 3px;
}
.baz b {
  margin: 4px;
}
"""

def test_with_children():
    my_extend = {
        "color": "red",
        "a": {
            "color": "blue",
        }
    }

    css = {
        ".foo": extend(my_extend, css={
           "background": "white",
            "a": {
                "background": "yellow"
            }
        }),
        ".bar": extend(my_extend),
    }

    assert render_css(css) == """\
.foo, .bar {
  color: red;
}
.foo a, .bar a {
  color: blue;
}
.foo {
  background: white;
}
.foo a {
  background: yellow;
}
"""


def test_chaining():
    pad = {
        "padding": ".5em"
    }
    pad_box = extend(pad, css={
        "a": {
            "text-decoration": "underline"
        },
        "p, div": {
            "border": "solid black 1px",
        },
    })
    css = {
        "%message": extend(pad_box),
        "%message-important": extend("message", css={
            "font-weight": "bold",
            "a": { "color": "red" }
        }),
        "%message-light": extend("message", css={  # won't appear as not used
            "opacity": "0.8",
        }),
        ".message-error": extend("message-important"),
        ".message-warning": extend("message-important"),
        ".message-success, .message-info": extend("message", css={
            "a": { "color": "white" }
        }),
    }

    assert render_css(css) == """\
.message-error, .message-warning, .message-success, .message-info {
  padding: .5em;
}
.message-error a, .message-warning a, .message-success a, .message-info a {
  text-decoration: underline;
}
.message-error p, .message-error div, .message-warning p, .message-warning div, .message-success p, .message-success div, .message-info p, .message-info div {
  border: solid black 1px;
}
.message-error, .message-warning {
  font-weight: bold;
}
.message-error a, .message-warning a {
  color: red;
}
.message-success a, .message-info a {
  color: white;
}
"""


def test_inner_combine():
    ext1 = combine({"foo": 1}, {"foo": 11})
    css = {
        "%ext2": combine({"bar": 2}, {"bar": 22}),
        "qux": extend(ext1, "ext2", css=combine({"baz": 3}, {"baz": 33})),
        "zzz": extend(ext1, "ext2", css=combine({"zzz": 4}, {"zzz": 44}))
    }

    assert render_css(css) == """\
qux, zzz {
  bar: 2;
  bar: 22;
}
qux, zzz {
  foo: 1;
  foo: 11;
}
qux {
  baz: 3;
  baz: 33;
}
zzz {
  zzz: 4;
  zzz: 44;
}
"""
