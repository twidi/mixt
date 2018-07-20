import pytest

from mixt.contrib.css.units import Unit
from mixt.contrib.css.vars import Not, Var, dummy as _, media


def test_1():
    assert media() == "@media all"


def test_2():
    assert media({"foo": "bar"}) == "@media (foo: bar)"


def test_3():
    assert media(_ & {"foo": "bar"}) == "@media (foo: bar)"


def test_4():
    assert media({"foo": "bar"}, {"baz": "qux"}) == "@media (foo: bar), (baz: qux)"


def test_5():
    with pytest.raises(TypeError):
        media({"foo": "bar"} & {"baz": "qux"})


def test_6():
    assert (
        media(_ & {"foo": "bar"} & {"baz": "qux"}) == "@media (foo: bar) and (baz: qux)"
    )
    assert media(_ | {"foo": "bar"} | {"baz": "qux"}) == "@media (foo: bar), (baz: qux)"


def test_7():
    screen = Var("screen")
    assert (
        media(screen & {"foo": "bar"} & {"baz": "qux"})
        == "@media screen and (foo: bar) and (baz: qux)"
    )


def test8():
    assert media(~_ & {"foo": "bar"}) == "@media not (foo: bar)"
    assert media(~_ | {"foo": "bar"}) == "@media not (foo: bar)"
    assert media(Not({"foo": "bar"})) == "@media not (foo: bar)"


def test9():
    all, max, width = Var.many("all max width")
    em = Unit("em")
    assert (
        media(~all & {max-width: 40 * em}) == "@media not all and (max-width: 40em)"
    )


def test10():
    assert media(Not({"foo": "bar"})) == "@media not (foo: bar)"


def test11():
    screen, print, color = Var.many("screen print color")
    assert (
        media(~screen & {color}, print & {color})
        == "@media not screen and (color), print and (color)"
    )


def test12():
    # https://css-tricks.com/logic-in-media-queries/#article-header-id-8
    expected = (
        "@media "
        "only screen and (min-width: 100px), "
        "not all and (min-width: 100px), "
        "not print and (min-height: 100px), "
        "(color), "
        "(min-height: 100px) and (max-height: 1000px), "
        "handheld and (orientation: landscape)"
    )

    only, screen, min, width, all, print, height, color, max, handheld, orientation, landscape = Var.many(
        "only screen min width all print height color max handheld orientation landscape"
    )
    px = Unit("px")

    m = media(
        only(screen) & {min-width: 100 * px},
        ~all & {min-width: 100 * px},
        ~print & {min-height: 100 * px},
        {color},
        _ & {min-height: 100 * px} & {max-height: 1000 * px},
        handheld & {orientation: landscape},
    )
    assert m == expected

    minw = 100 * px
    minh = 100 * px
    maxh = 1000 * px

    m = media(
        only(screen) & {min-width: minw},
        ~all & {min-width: minw},
        ~print & {min-height: minh},
        {color},
        _ & {min-height: minh} & {max-height: maxh},
        handheld & {orientation: landscape},
    )
    assert m == expected

    minw = {min-width: 100 * px}
    minh = {min-height: 100 * px}
    maxh = {max-height: 1000 * px}

    m = media(
        only(screen) & minw,
        ~all & minw,
        ~print & minh,
        {color},
        _ & minh & maxh,
        handheld & {orientation: landscape},
    )
    assert m == expected
