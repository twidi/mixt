from typing import Callable, List, Dict

from mixt import Element, html, Required
from mixt.contrib.css import css_vars
from mixt.contrib.css.units import QuantifiedUnit
from mixt.contrib.css.vars import CSS_VARS
from mixt.internal.base import OptionalContext, BaseContext


__colors__: List[str] = [
        "white",
        "#f7fcf0",
        "#e0f3db",
        "#ccebc5",
        "#a8ddb5",
        "#7bccc4",
        "#4eb3d3",
        "#2b8cbe",
        "#0868ac",
        "#084081",
]


# noinspection PyUnresolvedReferences
@css_vars(globals())
def get_extends():
    return {
        "%TAG": {
            font-weight: normal,
            font-size: smaller,
            margin-left: 1*em,
            padding: (1*px, 5*px, 2*px),
            border-radius: 6*px,
            position: relative,
            top: -1*px,
        },
        "%HL": {
            background: __colors__[9],
            color: white,
        },
        "%HL_REVERSE": {
            background: white,
            color: __colors__[9],
        },
    }


class Styles:
    colors: List[str] = __colors__
    breakpoint: QuantifiedUnit = CSS_VARS.rem(50)


class StyleContext(BaseContext):
    class PropTypes:
        styles: Required[Styles]


# language=CSS
TYPESET_CSS = """
/* <components.style.TypesetStyle> */
/* 
  NOTE: updated to remove `typeset` class + some margin changes
  Typeset.css
  https://github.com/joshuarudd/typeset.css
  v0.9.4
  Last updated: 2013-01-18
  Author: Joshua Rudd - http://joshuarudd.com 
  Twitter: @joshuarudd
*/


body {
  line-height: 1.0;
  text-rendering: optimizeLegibility;
}

/* http://paulirish.com/2012/box-sizing-border-box-ftw/ */
* {
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
}

/* Adapted from Eric Meyer's CSS Reset: http://meyerweb.com/eric/tools/css/reset/ */
a, abbr, acronym, address, b, big, cite, code, del, em, i, ins, kbd, mark, output, q, ruby, s, samp, small, strike, strong, sub, sup, time, tt, u, var,
dfn, dl, dt, dd, ol, ul, li,
blockquote, h1, h2, h3, h4, h5, h6, p, pre,
table, caption, tbody, tfoot, thead, tr, th, td,
applet, canvas, embed, figure, figcaption, iframe, img, object {
  background: transparent;
  border: 0;
  font-size: 100%;
  font: inherit;
  line-height: 1.0;
  margin: 0;
  padding: 0;
  vertical-align: baseline;
}

/*
  Initialize spacing and colors
*/

li, dt, dd, p, pre, caption, th, td, figcaption {
  line-height: 1.4;
}
caption, dl, dd, figcaption, figure, h1, h2, h3, h4, h5, h6, p, pre, table, ol, ul {
  margin: 1em 0;
}
blockquote, ol, ul {
  margin-left: 2.8em;
}
code, pre, th {
  background-color: #F3F6FA;
}
code, pre, th, td {
  color: #324354;
}
pre, table, th, td {
  border: 1px solid #dbe2f2;
}

/*
  Inline elements
*/

a {
  text-decoration: underline;
}
strong, b {
  font-weight: bolder;
}
u, em, i {
  font-style: italic;
  text-decoration: none;
}
abbr[title] {
  border-bottom: 1px dotted gray;
}
address {
  /* no style */
}
cite {
  font-style: italic;
}
code {
  /* background-color set above */
  /* color set above */
  font-family: monospace;
  padding: 0.1em 0.2em;
}
dfn {
  /* no style */
}
del {
  color: red;
  text-decoration: line-through;
}
ins {
  color: green;
  text-decoration: none;
}
kbd {
  font-family: monospace;
}
mark {
  background-color: yellow;
  color: black;
}
samp {
  font-family: monospace;
}
small {
  color: gray;
  font-size: 80%;
}
s {
  text-decoration: line-through;
}
sub {
  font-size: 80%;
  vertical-align: sub;
}
sup {
  font-size: 80%;
  vertical-align: super;
}
var {
  font-style: italic;
}

/*
  Lists
*/

ol, ul {
  /* margin set above */
}
ol ol, ul ul, ol ul, ul ol {
  margin-top: 0;
  margin-bottom: 0;
}
ol {
  list-style: decimal;
}
ol ol {
  list-style: lower-alpha;
}
ol ol ol {
  list-style: lower-roman;
}
ol ol ol ol {
  list-style: decimal;
}
ul {
  list-style: square;
}
li {
  /* line-height set above */
}
dl {
  /* margin set above */
}
dt {
  font-weight: bold;
  /* line-height set above */
}
dd {
  /* line-height set above */
  margin-top: 0;
}

/*
  Block-level elements
*/

h1, h2, h3, h4, h5, h6 {
  font-weight: bold;
  /* margin set above */
  margin-bottom: 0;
}
h1 {
  font-size: 200%;
}
h2 {
  font-size: 160%;
}
h3 {
  font-size: 140%;
}
h4 {
  font-size: 120%;
}
h5 {
  font-size: 110%;
}
h6 {
  font-size: 100%;
}
p {
  /* line-height set above */
  /* margin set above */
}
blockquote {
  /* margin-left set above */
}
pre {
  /* background-color set above */
  /* border set above */
  -moz-border-radius: 2px;
  -webkit-border-radius: 2px;
  border-radius: 2px;
  /* color set above */
  display: block;
  font-family: monospace;
  font-size: 12px;
  /* line-height set above */
  /* margin set above */
  max-width: 100%;
  overflow: scroll;
  padding: .7em;
  /* Mozilla, since 1999 */
  white-space: -moz-pre-wrap !important;
  /* css-3 */
  white-space: pre-wrap;
}

/*
  Tables
*/

table {
  /* border set above */
  border-collapse: collapse;
  /* margin set above */
  table-layout: auto;
}
caption {
  caption-side: top;
  font-weight: bold;
  /* line-height set above */
  /* margin set above */
  margin-top: 0;
  text-align: left;
}
thead {
  /* no style */
}
tbody {
  /* no style */
}
tfoot {
  /* no style */
}
th, td {
  /* border set above */
  /* color set above */
  /* line-height set above */
  padding: .7em;
  text-align: left;
}
th {
  /* background-color set above */
  font-weight: normal;
}
td {
  /* no style */
}

/*
  Media
*/

embed, iframe, img, object {
  display: inline;
  max-width: 100%;
}
figure {
  display: block;
  max-width: 100%;
  /* margin set above */
}
figcaption {
  font-size: 80%;
  /* line-height set above */
  /* margin set above */
  text-align: left;
}
/* </components.style.TypesetStyle> */
"""


class TypesetStyle(Element):
    class PropTypes:
        with_tag: bool = True

    def render(self, context):
        css = html.Raw(TYPESET_CSS)
        return html.Style(type="text/css")(css) if self.with_tag else css
