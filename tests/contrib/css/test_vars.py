from mixt.contrib.css import import_css, vars
from mixt.contrib.css.units import UNITS, Unit
from mixt.contrib.css import vars
from mixt.contrib.css.vars import (
    CssVarsDict,
    Var,
    _tovar,
    add_css_var,
)


def test_var_operations():
    foo = Var("foo")
    bar = Var("bar")

    assert foo == "foo"
    assert -foo == "-foo"
    assert --foo == "--foo"
    assert ~foo == "not foo"

    assert foo - bar == "foo-bar"
    assert foo + bar == "foo+bar"
    assert foo / bar == "foo/bar"
    assert foo & bar == "foo and bar"
    assert foo | bar == "foo or bar"

    assert bar - "baz" == "bar-baz"
    assert bar + "baz" == "bar+baz"
    assert bar / "baz" == "bar/baz"
    assert bar & "baz" == "bar and baz"
    assert bar | "baz" == "bar or baz"

    assert "baz" - bar == "baz-bar"
    assert "baz" + bar == "baz+bar"
    assert "baz" / bar == "baz/bar"
    assert "baz" & bar == "baz and bar"
    assert "baz" | bar == "baz or bar"


def test_var_many():
    aa, bb = Var.many("aa bb")
    assert aa == "aa"
    assert isinstance(aa, Var)
    assert bb == "bb"
    assert isinstance(bb, Var)

    cc, dd = Var.many("cc", "dd")
    assert cc == "cc"
    assert isinstance(cc, Var)
    assert dd == "dd"
    assert isinstance(dd, Var)

    ee, ff = Unit.many("ee", "ff")
    assert ee == "ee"
    assert isinstance(ee, Unit)
    assert ff == "ff"
    assert isinstance(ff, Unit)


def test_empty_var():
    foo = Var("")
    bar = Var("bar")
    qux = Var("")

    assert foo == ""
    assert -foo == ""
    assert --foo == ""
    assert ~foo == "not "

    assert foo - bar == "-bar"
    assert foo + bar == "+bar"
    assert foo / bar == "/bar"
    assert foo & bar == "bar"
    assert foo | bar == "bar"

    assert bar - foo == "bar"
    assert bar + foo == "bar"
    assert bar / foo == "bar"
    assert bar & foo == "bar"
    assert bar | foo == "bar"

    assert foo - "baz" == "-baz"
    assert foo + "baz" == "+baz"
    assert foo / "baz" == "/baz"
    assert foo & "baz" == "baz"
    assert foo | "baz" == "baz"

    assert "baz" - foo == "baz"
    assert "baz" + foo == "baz"
    assert "baz" / foo == "baz"
    assert "baz" & foo == "baz"
    assert "baz" | foo == "baz"

    assert foo - qux == ""
    assert foo + qux == ""
    assert foo / qux == ""
    assert foo & qux == ""
    assert foo | qux == ""

    assert qux - foo == ""
    assert qux + foo == ""
    assert qux / foo == ""
    assert qux & foo == ""
    assert qux | foo == ""

    assert foo - "" == ""
    assert foo + "" == ""
    assert foo / "" == ""
    assert foo & "" == ""
    assert foo | "" == ""

    assert "" - foo == ""
    assert "" + foo == ""
    assert "" / foo == ""
    assert "" & foo == ""
    assert "" | foo == ""

    assert bar - "" == "bar"
    assert bar + "" == "bar"
    assert bar / "" == "bar"
    assert bar & "" == "bar"
    assert bar | "" == "bar"

    assert "" - bar == "-bar"
    assert "" + bar == "+bar"
    assert "" / bar == "/bar"
    assert "" & bar == "bar"
    assert "" | bar == "bar"


def test_tovar():
    obj = _tovar("foo")
    assert obj == "foo"
    assert isinstance(obj, Var)

    obj = _tovar({"foo": "bar"})
    assert obj == "(foo: bar)"
    assert isinstance(obj, Var)

    obj = _tovar({"foo"})
    assert obj == "(foo)"
    assert isinstance(obj, Var)

    obj = _tovar("foo", kind=Unit)
    assert obj == "foo"
    assert isinstance(obj, Unit)


def test_call_var():
    foo = Var("foo")
    obj = foo(1, 2, 3)
    assert obj == "foo(1, 2, 3)"
    assert isinstance(obj, Var)


def test_join():
    assert vars.join - "foo" == "join-foo"  # must be a Var

    assert vars.join(1, 2, 3) == "1 2 3"


def test_many():
    assert vars.many - "foo" == "many-foo"  # must be a Var

    assert vars.many(1, 2, 3) == "1, 2, 3"
    assert vars.many(vars.join(1, 2), vars.join(3, 4)) == "1 2, 3 4"


def test_override():
    assert vars.override - "foo" == "override-foo"  # must be a Var

    obj = vars.override(1, 2, 3)
    assert obj.declarations == (1, 2, 3)


def test_extend():
    assert vars.extend - "foo" == "extend-foo"  # must be a Var

    # other tests in test_extend.py


def test_raw():
    vars.Raw.counter = 0

    assert vars.raw() == ":raw:1"
    assert vars.raw() == ":raw:2"
    assert vars.raw == "raw"


def test_comment():
    vars.Comment.counter = 0

    assert vars.comment() == "/*1"
    assert vars.comment() == "/*2"
    assert vars.comment == "comment"


def test_media():
    assert vars.media - "foo" == "media-foo"  # must be a Var

    assert vars.media("foo", "bar") == "@media foo, bar"
    assert vars.media() == "@media all"


def test_string():
    assert vars.string - "foo" == "string-foo"  # must be a Var

    assert vars.string("foo") == "'foo'"
    assert vars.string(1) == "'1'"


def test_negate():
    assert vars.Not - "foo" == "not-foo"  # must be a Var

    assert vars.Not("foo") == "not foo"
    assert vars.Not("foo", "bar") == "not (foo or bar)"


def test_merge():
    assert vars.merge - "foo" == "merge-foo"  # must be a Var

    assert vars.merge({
        "a": 1,
        "b": {
            "ba": 2,
            "bb": {
                "bba": 3,
                "bbb": {
                    "bbba": 4,
                    "bbbb": 5,
                },
                "bbc": 6
            },

        },
        "c": 7,
        "d": 8,
    }, {
        "a": 2,
        "b": {
            "bb": {
                "bba": None,
                "bbb": {
                    "bbbb": 9
                }
            }
        },
        "d": {
            "dd": 10
        },
    }, {
        "b": {
            "bb": {
                "bba": 11,
                "bbc": None,
            }
        },
        "e": 12,
    }) == {
        "a": 2,
        "b": {
            "ba": 2,
            "bb": {
                "bba": 11,
                "bbb": {
                    "bbba": 4,
                    "bbbb": 9,
                },
            },

        },
        "c": 7,
        "d": {
            "dd": 10,
        },
        "e": 12,
    }


def test_combine():
    assert vars.combine == "combine"

    css = vars.combine()
    assert isinstance(css, dict)
    assert css == {}

    css1 = {"a": "b"}
    css = vars.combine(css1)
    assert isinstance(css, dict)
    assert css == {"a": "b"}


    css1 = {"a": "b"}
    css2 = {"aa": "bb"}
    css3 = {"aaa": "bbb"}
    css = vars.combine(css1, css2, css3)
    assert isinstance(css, dict)
    assert css == {
        "a": "b",
        "aa": "bb",
        "aaa": "bbb"
    }

    css2 = {"a": "bb"}
    css = vars.combine(css1, css2, css3)
    assert isinstance(css, vars.Combine)
    assert css.dicts == [
        {"a": "b"},
        {"a": "bb"},
        {"aaa": "bbb"},
    ]

    css4 = {"a": "bbbb"}
    css = vars.combine(css, css4)
    assert isinstance(css, vars.Combine)
    assert css.dicts == [
        {"a": "b"},
        {"a": "bb"},
        {"aaa": "bbb"},
        {"a": "bbbb"},
    ]

def test_add_css_var():
    def render_dict(d):
        return {
            key: f'{value.__class__.__name__}("{value}")' for key, value in d.items()
        }

    v1 = CssVarsDict()
    add_css_var("foo-bar", aliases=["baz"], css_vars=v1)
    assert render_dict(v1) == {
        "foo": 'Var("foo")',
        "bar": 'Var("bar")',
        "baz": 'Var("baz")',
        "Foo": 'Var("foo")',
        "Bar": 'Var("bar")',
        "Baz": 'Var("baz")',
        "foo_bar": 'Var("foo-bar")',
        "fooBar": 'Var("foo-bar")',
        "FooBar": 'Var("foo-bar")',
    }

    v2 = CssVarsDict()
    add_css_var("xx", kind=Unit, css_vars=v2)
    assert render_dict(v2) == {"xx": 'Unit("xx")', "Xx": 'Unit("xx")'}

    v3 = CssVarsDict()
    join2 = vars.Join("join2")
    add_css_var("join2", kind=None, value=join2, aliases=["nioj2"], css_vars=v3)
    assert render_dict(v3) == {
        "Join2": 'Join("join2")',
        "join2": 'Join("join2")',
        "nioj2": 'Join("join2")',
        "Nioj2": 'Join("join2")',
    }
    assert v3["join2"] is join2
    assert v3["Nioj2"] is join2


def test_get_from_css_vars():
    v = CssVarsDict()
    add_css_var("foo-bar", aliases=["baz"], css_vars=v)
    assert v.foo == "foo"
    assert v["foo"] == "foo"
    assert v.foo is v["foo"]
    assert v.bar == "bar"
    assert v["bar"] == "bar"
    assert v.baz == "baz"
    assert v["baz"] == "baz"
    assert v.Foo == "foo"
    assert v["Foo"] == "foo"
    assert v.Bar == "bar"
    assert v["Bar"] == "bar"
    assert v.Baz == "baz"
    assert v["Baz"] == "baz"
    assert v.foo_bar == "foo-bar"
    assert v["foo_bar"] == "foo-bar"
    assert v.fooBar == "foo-bar"
    assert v["fooBar"] == "foo-bar"
    assert v.FooBar == "foo-bar"
    assert v["FooBar"] == "foo-bar"

    assert v.qux == "qux"
    assert isinstance(v.qux, Var)
    assert v["qux"] == "qux"
    assert v.qux is v["qux"]
    assert v["xuq"] == "xuq"
    assert isinstance(v["xuq"], Var)
    assert v.xuq == "xuq"


# noinspection PyUnresolvedReferences
def test_defaults():
    with import_css(globals()):
        assert _ is vars.dummy
        assert dummy is vars.dummy
        assert join is vars.join
        assert many is vars.many
        assert override is vars.override
        assert extend is vars.extend
        assert raw is vars.raw
        assert r is vars.raw
        assert comment is vars.comment
        assert c is vars.comment
        assert string is vars.string
        assert str is vars.string
        assert repr is vars.string
        assert _not is vars.negate
        assert Not is vars.negate
        assert merge is vars.merge
        assert combine is vars.combine
        assert b is vars.builtins
        assert builtins is vars.builtins

        assert charset is vars.charset
        assert _import is vars._import
        assert Import is vars._import
        assert namespace is vars.namespace
        assert media is vars.media
        assert supports is vars.supports
        assert document is vars.document
        assert page is vars.page
        assert font_face is vars.font_face
        assert keyframes is vars.keyframes
        assert viewport is vars.viewport
        assert counter_style is vars.counter_style
        assert font_feature_values is vars.font_feature_values
        assert swash is vars.swash
        assert annotation is vars.annotation
        assert ornaments is vars.ornaments
        assert stylistic is vars.stylistic
        assert styleset is vars.styleset
        assert character_variant is vars.character_variant

        assert isinstance(px, Unit)
        assert px == "px"

        assert isinstance(pc, Unit)
        assert pc == "%"
        assert percent is pc
