from mixt.contrib.css import render_css
from mixt.contrib.css.units import Unit
from mixt.contrib.css.vars import (
    Not,
    Var,
    _import,
    charset,
    counter_style,
    document,
    dummy as _,
    font_face,
    font_feature_values,
    keyframes,
    namespace,
    page,
    string,
    styleset,
    supports,
    viewport,
)


# @media is tested in ``test_media_queries.py``


def test_support():
    # https://developer.mozilla.org/en-US/docs/Web/CSS/@supports
    assert (
        supports({"transform-origin": "5% 5%"}) == "@supports (transform-origin: 5% 5%)"
    )
    assert (
        supports(Not({"transform-origin": "10em 10em 10em"}))
        == "@supports not (transform-origin: 10em 10em 10em)"
    )
    assert (
        supports(_ & {"display": "grid"} & Not({"display": "inline-grid"}))
        == "@supports (display: grid) and not (display: inline-grid)"
    )
    assert (
        supports(
            _
            & {"display": "table-cell"}
            & {"display": "list-item"}
            & {"display": "run-in"}
        )
        == "@supports (display: table-cell) and (display: list-item) and (display: run-in)"
    )
    assert (
        supports(
            _ | {"transform-style": "preserve"} | {"-moz-transform-style": "preserve"}
        )
        == "@supports (transform-style: preserve) or (-moz-transform-style: preserve)"
    )
    assert (
        supports({"transform-style": "preserve"}, {"-moz-transform-style": "preserve"})
        == "@supports (transform-style: preserve) or (-moz-transform-style: preserve)"
    )

    assert (
        supports(
            Not({"text-align-last": "justify"}, {"-moz-text-align-last": "justify"})
        )
        == "@supports not ((text-align-last: justify) or (-moz-text-align-last: justify))"
    )

    foo, green = Var.many("foo green")
    assert supports({--foo: green}) == "@supports (--foo: green)"


def test_document():
    url, prefix, domain, regexp = Var.many("url prefix domain regexp")
    assert (
        document(url(string("https://www.example.com/")))
        == "@document url('https://www.example.com/')"
    )
    assert (
        document(
            url("http://www.w3.org/"),
            url-prefix("http://www.w3.org/Style/"),
            domain("mozilla.org"),
            regexp(string("https:.*")),
        )
        == "@document url(http://www.w3.org/), url-prefix(http://www.w3.org/Style/), domain(mozilla.org), regexp('https:.*')"
    )


def test_page():
    assert page() == "@page"
    assert page(":first") == "@page :first"


# noinspection PyUnresolvedReferences
def test_font_face():
    assert font_face() == "@font-face"

    font, family, src, url, format = Var.many("font family src url format")
    css = {
        font_face(): {
            font-family: string("Open Sans"),
            src: [
                (
                    url(string("/fonts/OpenSans-Regular-webfont.woff2")),
                    format(string("woff2")),
                ),
                (
                    url(string("/fonts/OpenSans-Regular-webfont.woff")),
                    format(string("woff")),
                ),
            ],
        }
    }

    assert (
        render_css(css)
        == """\
@font-face {
  font-family: 'Open Sans';
  src: url('/fonts/OpenSans-Regular-webfont.woff2') format('woff2'), url('/fonts/OpenSans-Regular-webfont.woff') format('woff');
}
"""
    )


def test_keyframes():
    assert keyframes("foo") == "@keyframes foo"

    slidein, margin, left, width, _from, to, p, animation, duration, name, font, size = Var.many(
        "slidein margin left width from to p animation duration name font size"
    )
    pc, s = Unit.many("% s")

    css = {
        keyframes(slidein): {
            _from: {margin-left: pc(100), width: pc(300)},
            pc(75): {font-size: pc(300), margin-left: pc(25), width: pc(150)},
            to: {margin-left: pc(0), width: pc(100)},
        },
        p: {animation-duration: s(3), animation-name: slidein},
    }

    assert (
        render_css(css)
        == """\
@keyframes slidein {
  from {
    margin-left: 100%;
    width: 300%;
  }
  75% {
    font-size: 300%;
    margin-left: 25%;
    width: 150%;
  }
  to {
    margin-left: 0%;
    width: 100%;
  }
}
p {
  animation-duration: 3s;
  animation-name: slidein;
}
"""
    )


def test_viewport():
    assert viewport() == "@viewport"

    width, device = Var.many("width device")
    css = {viewport(): {width: device-width}}

    assert (
        render_css(css)
        == """\
@viewport {
  width: device-width;
}
"""
    )


def test_counter_style():
    assert counter_style("foo") == "@counter-style foo"

    system, fixed, symbols, suffix = Var.many("system fixed symbols suffix")
    css = {
        counter_style("circled-alpha"): {
            system: fixed,
            symbols: "Ⓐ Ⓑ Ⓒ Ⓓ Ⓔ Ⓕ Ⓖ Ⓗ Ⓘ Ⓙ Ⓚ Ⓛ Ⓜ Ⓝ Ⓞ Ⓟ Ⓠ Ⓡ Ⓢ Ⓣ Ⓤ Ⓥ Ⓦ Ⓧ Ⓨ Ⓩ",
            suffix: string(" "),
        }
    }

    assert (
        render_css(css)
        == """\
@counter-style circled-alpha {
  system: fixed;
  symbols: Ⓐ Ⓑ Ⓒ Ⓓ Ⓔ Ⓕ Ⓖ Ⓗ Ⓘ Ⓙ Ⓚ Ⓛ Ⓜ Ⓝ Ⓞ Ⓟ Ⓠ Ⓡ Ⓢ Ⓣ Ⓤ Ⓥ Ⓦ Ⓧ Ⓨ Ⓩ;
  suffix: ' ';
}
"""
    )


def test_font_feature_values():
    assert font_feature_values("Font One") == "@font-feature-values Font One"

    nice, style = Var.many("nice style")
    css = {font_feature_values("Font One"): {styleset(): {nice-style: 12}}}

    assert (
        render_css(css)
        == """\
@font-feature-values Font One {
  @styleset {
    nice-style: 12;
  }
}
"""
    )


def test_charset():
    assert charset("UTF-8") == charset() == "@charset 'UTF-8'"
    assert charset("latin1") == "@charset 'latin1'"

    css = {charset("UTF-8"): None}

    assert (
        render_css(css)
        == """\
@charset 'UTF-8';
"""
    )


def test_import():
    assert _import(string("custom.css")) == "@import 'custom.css'"

    url, print, screen = Var.many("url print screen")
    css = {
        _import(string("custom.css")): None,
        _import(url("fineprint.css"), print): None,
        _import(url("landscape.css"), screen & {"orientation": "landscape"}): None,
        _import(url("landscape.css"), screen | {"orientation": "landscape"}): None,
    }

    assert (
        render_css(css)
        == """\
@import 'custom.css';
@import url(fineprint.css) print;
@import url(landscape.css) screen and (orientation: landscape);
@import url(landscape.css) screen, (orientation: landscape);
"""
    )


def test_namespace():
    assert (
        namespace("http://www.w3.org/1999/xhtml")
        == "@namespace http://www.w3.org/1999/xhtml"
    )

    url = Var("url")
    css = {namespace("svg", url("http://www.w3.org/2000/svg")): None}

    assert (
        render_css(css)
        == """\
@namespace svg url(http://www.w3.org/2000/svg);
"""
    )
