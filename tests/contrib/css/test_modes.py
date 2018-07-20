from mixt.contrib.css import Modes, render_css


css = {
    ".content": {
        "color": "blue",
        "font-weight": "bold",
        "background": "green",
        ".foo": {"color": "green"},
        "@media(all and (max-width: 600px)": {
            "": {"color": "red", "font-weight": "normal", ".foo": {"color": "yellow"}}
        },
        ".bar": {"color": "orange"},
        "z-index": 1,
    },
    ".baz": {
        "a": {"margin": "1px"},
        "b": {"margin": "2px"},
    }
}


def test_mode_compressed():
    assert (
        render_css(css, Modes.COMPRESSED)
        == """.content{color:blue;font-weight:bold;background:green}.content .foo{color:green}@media(all and (max-width: 600px){.content{color:red;font-weight:normal}.content .foo{color:yellow}}.content .bar{color:orange}.content{z-index:1}.baz a{margin:1px}.baz b{margin:2px}"""
    )


def test_mode_compact():
    assert (
        render_css(css, Modes.COMPACT)
        == """\
.content {color: blue; font-weight: bold; background: green}
.content .foo {color: green}
@media(all and (max-width: 600px) {
 .content {color: red; font-weight: normal}
 .content .foo {color: yellow}
}
.content .bar {color: orange}
.content {z-index: 1}
.baz a {margin: 1px}
.baz b {margin: 2px}
"""
    )


def test_mode_normal():
    assert (
        render_css(css, Modes.NORMAL)
        == """\
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
    font-weight: normal;
  }
  .content .foo {
    color: yellow;
  }
}
.content .bar {
  color: orange;
}
.content {
  z-index: 1;
}
.baz a {
  margin: 1px;
}
.baz b {
  margin: 2px;
}
"""
    )


def test_mode_indent():
    assert (
        render_css(css, Modes.INDENT)
        == """\
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
            font-weight: normal;
        }

            .content .foo {
                color: yellow;
            }
    }

    .content .bar {
        color: orange;
    }

.content {
    z-index: 1;
}

.baz a {
    margin: 1px;
}

.baz b {
    margin: 2px;
}

"""
    )


def test_mode_indent2():
    assert (
        render_css(css, Modes.INDENT2)
        == """\
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
                font-weight: normal;
            }

            .content .foo {
                    color: yellow;
                }
        }

    .content .bar {
            color: orange;
        }

.content {
        z-index: 1;
    }

.baz a {
        margin: 1px;
    }

.baz b {
        margin: 2px;
    }

"""
    )


def test_mode_indent3():
    assert (
        render_css(css, Modes.INDENT3)
        == """\
.content {
    color: blue;
    font-weight: bold;
    background: green }

    .content .foo {
        color: green }

    @media(all and (max-width: 600px) {

        .content {
            color: red;
            font-weight: normal }

            .content .foo {
                color: yellow } }

    .content .bar {
        color: orange }

.content {
    z-index: 1 }

.baz a {
    margin: 1px }

.baz b {
    margin: 2px }

"""
    )
