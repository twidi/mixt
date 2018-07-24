# noinspection PyUnresolvedReferences
"""**Mixt CSS**: tools to write CSS in python.

Introduction
------------
The goal is to replace the need to use a CSS preprocessor by generating CSS via a real
language (ie Python), so with the ability to have calculations, "mixins", etc done in real python.

And with a few tricks, it allows to write code that resemble a lot like normal CSS. For example
you don't have to use strings for properties or values (only for selectors).

Almost everything in CSS is covered, with additions borrowed from sass and less:

- nesting to avoid selectors repetition
- units management (computations, ``calc``)
- multi-values properties
- at-rules, with nested content (``@media``, ``@support``) or not (``@charset``)
- values overriding (think vendor-prefixes).
- extends (like in sass)
- mixins... because it's python and you can compose dicts how you want

Examples
--------
Here is an example that resumes all the features:

>>> from mixt.contrib.css import load_css_keywords, css_vars, render_css

>>> # Must be done only once. This will load a big list of known CSS keywords and speed up
... # the resolution of the "undefined" variables in your css methods encapsuled by `@css_vars``.
... # It is not mandatory but will speed up a lot your css functions, in exchange of a few ms at
... # start time, and a few dozens of KB in memory (there is a lot of CSS keywords ;) )
... load_css_keywords()

>>> # The `@css_vars(globals())` decorator is mandatory to resolve "undefined" variables. They're
... # will only be a few of them if `load_css_keywords` is called before.
... # The usage of `globals()` is to put the existing and created CSS keywords in the current scope
... # so you can access them in the function without thinking about it.
... @css_vars(globals())
... def css():
...     return { # All must be in a dict.
...
...         # At-rule without content.
...         charset("UTF-8"): None,
...
...         # Html tag selector: no need for quotes
...         body: {
...
...             # No need for quotes for the property name
...             margin: 0,
...
...             # Units usage, could also be written as 2*em
...             # this gives: `padding: 2em`
...             padding: em(2),
...
...         },
...
...         header: {
...             # Need to encapsulate in parentheses: items are joined with a
...             # space, so this gives `margin: 1em 2em`
...             # it's a shortcut of the `join` function, so this could also
...             # be done like this: `margin: join(1*em, 2*em)`
...             margin: (1*em, 2*em),
...
...             # Encapsulation as a list is different than as a tuple (like just above)
...             # items are now joined with a comma, so this gives
...             # `font-family: Gill, Helvetica, sans-serif`
...             # it's a shortcut of the `many` function so tis could also
...             # be done like this: `font-family: many("Gill", "Helvetica", "sans-serif")`
...             font-family: ["Gill", "Helvetica", "sans-serif"],
...
...             # Here is a combination of `many` and `join`.
...             # It could also have been written this way, using explicitly `many` and `join`:
...             # text-shadow: many(
...             #     join(1*px, 1*px, 2*px, blue),
...             #     join(0, 0, 1*em, red),
...             #     join(0, 0, 0.2*em, red),
...             # ),
...             text-shadow: [
...                 (1*px, 1*px, 2*px, blue),
...                 (0, 0, 1*em, red),
...                 (0, 0, 0.2*em, red),
...             ],
...         },
...
...         nav: {
...             # Notice the use of `-`: `margin-top` is not a valid python identifier but
...             # an override of the "sub" operator between two strings.
...             # Also works, without quotes: `marginTop`, `margin_top`, `MarginTop`
...             margin-top: 1*em,
...
...             # The `ul` is nested under `nav`. For nested selectors which don't include the
...             # `&` character, the selector is automatically prefixed with `& ` (the space is
...             # important). So here, `ul` is in fact `& ul`, and `&` will be replaced by the
...             # chaining of the parent selectors, so at the end we'll have `nav ul`.
...             ul: {
...                 # `list` is usually a python builtin but as it's part of a css "keyword", it is
...                 # now a part of a CSS var. To access the `list` builtin, use the `builtins` or
...                 # `b` namespace: `b.list(thing_to_cast_list)`. Note that it is different for
...                 # python keywords, like `for` and `class` (but also non-keywords like `super`,
...                 # `self` and `cls`) that must, to be used as a CSS var, be prefixed with an
...                 # underscore `_` (or used with the first letter in uppercase): `super()` will
...                 # work for the python `super` pseudo-keyword, and `_super` or `Super` will wor
...                 # as a CSS var rendering "super".
...                 list-style: none,  # do not use the python `None` here, it won't work
...
...
...                 # Here we add the `&` ourselves. If we had only `:after`, it would have been
...                 # extended to `& :after` which is, in CSS, completely different than `&:after`.
...                 # Like before, the `&` is replaced by the chaining of the parent selectors, so
...                 # at the end we'll have `nav ul:after`
...                 "&:after": {
...                     # here we don't put anything, so at the end this selector won't be rendered
...                 },
...
...                 # There is nothing that force us to put the `&` at the beginning. Here at the
...                 # end will have `body.theme-red ul nav`.
...                 "body.theme-red &": {
...                     background: red,
...
...                     # and here it will be `body.theme-red nav ul li`
...                     li: {
...                         color: white,
...                     },
...
...                     # You can put comments in the generated CSS. The key must start with `/*`.
...                     "/*": "this is a comment",
...
...                     # If you want many comments at the same level, still start the key with
...                     #  `/*` but complete it, like we did here with another `*`.
...                     # Also note how we can handle a multi-lines comment.
...                     #
...                     "/**": '''this is a
...                               multi-lines comment''',  # number of spaces it not important
...
...                     # If you don't want to bother with the different keys, you can use the
...                     # `comment()` function that will produce a different string key each time.
...                     comment(): "another comment",
...
...                 },
...
...                 li: {
...                     # Here we have a simple calculation, this will render `1.5em` in the
...                     # final CSS.
...                     # It is especially useful if one of the value is a variable previously
...                     # defined like: `min_height = 1*em` and then `height: min_height + 0.5*em`
...                     height: 1*em + 0.5*em,
...
...                     # Here we have a complex calculation that will result in a `calc` call in
...                     # CSS: `width: calc(100% - 2em)`.
...                     # Also note the use of `pc` for "percent", as we cannot use `%` alone
...                     # in python. `percent` is also available.
...                     width: 100*pc - 2*em,
...
...                     # Here we have a media query, which is for `nav ul li`, and every selector
...                     # inside will behave like before: `& ` will be prepended if `&` is not
...                     # present, and `&` will be replaced by the chaining of the parent selectors.
...                     # Notice how we use `&` instead of `and` in the media query condition, and
...                     # a dict. This will translate to `@media screen and (max-width: 800px)`.
...                     media(screen & {max-width: 800*px}): {
...
...                         # Properties directly in a `media` (or any other "at-rule") dict are for
...                         # the selector just before, so here it is for `nav ul li`.
...                         width: 5*em,
...
...                         # And here it is for `nav ul li b`, still for the media query we defined
...                         # We have to quote "b" because it's a shortcut for the `builtins` module
...                         "b": {
...                             background: white,
...                         },
...
...                         # Here the use of `combine` is not needed but it shows how you
...                         # can pass many dicts (not limited to 2) for a selector.
...                         # If no dicts share the same keys, a new dict will be returned, else
...                         # it's a special object that will hold the dicts that will be rendered
...                         # in order. It is useful if you want to compose dicts on the fly, or
...                         # you want to use some "mixins"
...                         a: combine(
...                             {background: white},
...                             {text-decoration: underline}
...                         )
...                     }
...                 }
...             }
...
...         },
...         # Here is another CSS entry for the `header`. We cannot have twice the same key in a
...         # python dict but we can trick it by adding starting/ending spaces that will be removed
...         # when generating the CSS. It can be particularly handy for overriding stuff while
...         # taking advantage of the cascading feature of CSS. Yes we don't need this here, but
...         # it's for the example
...         "header ": {
...
...             # To use vendor-prefixed properties, we could have done the same, using `background`
...             # with one more space each time. Or we can use the `override` function that make
...             # this more clear and simple.
...             # This will produce:
...             # header {
...             #     background: -webkit-linear-gradient(left, blue, red, blue);
...             #     background: -moz-linear-gradient(left, blue, red, blue);
...             #     background: -ms-linear-gradient(left, blue, red, blue);
...             #     background: -o-linear-gradient(left, blue, red, blue);
...             #     background: linear-gradient(left, blue, red, blue);
...             # }
...
...             background: override(
...                 -webkit-linear-gradient(left, blue, red, blue),
...                 -moz-linear-gradient(left, blue, red, blue),
...                 -ms-linear-gradient(left, blue, red, blue),
...                 -o-linear-gradient(left, blue, red, blue),
...                 linear-gradient(left, blue, red, blue),
...             )
...         },
...
...         "body.theme-red": {
...
...             # When you want to have some properties for multiple selectors at once, you
...             # can pass them as a tuple (or a generator, but not a list because a list cannot
...             # be accepted as a dict key). Here the final selector will be:
...             # `body.theme-red p, body.theme-red blockquote`.
...             (p, blockquote): {
...                 border: (solid, red, 1*px),
...
...                 # But you can also pass them as a string in a form of a comma separated list.
...                 # And if the parent is also a multiple-selector, nesting is managed as it
...                 # should.
...                 # Here the final selector will be:
...                 # `body.theme-red p strong, body.theme-red p em,
...                 # body.theme-red blockquote strong, body.theme-red blockquote em`.
...                 "strong, em": {
...                     color: red,
...                 },
...
...                 # Like always, `& ` is prepended to each selector and replaced, but you can put
...                 # it where you want.
...                 # Here the final selector will be:
...                 # `body.theme-red p:target, body.theme-red p:focus,
...                 # body.theme-red blockquote:target, # body.theme-red blockquote:focus`.
...                 "&:target, &:focus": {
...                     border-width: 3*px,
...                 }
...             }
...         },
...
...         # Keys that starts with `%` are meant to be used with `extend`, like below. The key will
...         # be replaced by all the selectors that extend it. If no selector use it, it won't be
...         # rendered
...         "%box": {
...             border: (solid, black, 1*px),
...             # A css to extend can be nested like a regular css.
...             # If ".message" extend "box", we'll have two rules: ".message" and ".message a"
...             a: {
...                 text-decoration: underline,
...             }
...         },
...
...         # This is how we use `extend` by assing the name (without `%`). Instead of a name it can
...         # also be a dict defined directly or as a variable (useful for storing extends in a
...         # "library")
...         ".message": extend("box"),
...
...         # An extend can accept a named `css`. Here, ".message-important" will be used for the
...         # "box" but also as its own rule with the content of the `css` argument.
...         ".message-important": extend("box", css={
...             border-width: 2*px,
...         }),
...
...         # An extend can extend another one
...         "%abs-box": extend("box", css={
...             position: absolute,
...         }),
...
...         # Here, we extend two things. First, the "box", as seen before, then, a dict. Notice we
...         # don't use the `css` argument, so it's an extend. There is no limit on the number of
...         # things we can extend.
...         ".alert": extend("abs-box", {z-index: 1000}),
...
...         # As we extend the same dict as before, the two selectors ".alert" and ".popup" will be
...         # used for the same rule like this: `.alert, .popup: { z-index: 1000 }`
...         ".popup": extend({z-index: 1000}, "abs-box"),
...
...         # You can include "raw" CSS by using the `:raw:` key, or any key starting with `:raw:`.
...         # (because as always you cannot have twice the same key in a python dict).
...         # It can be handy to import CSS generated/copied/whatever from elsewhere.
...         # Note that it's "raw" CSS so there is no nesting with parent selectors, but it will
...         # still be indented to match the current rendering mode.
...         ":raw:": ".foo: { color: blue; }",
...         ":raw::": ".bar { color: white; }",
...
...         # If you don't want to bother with the different keys, you can use, like for comments,
...         # the `raw()` function that will produce a different string key each time.
...         raw(): ".baz { color: red; }"
...     }

>>> # Now we can render this css
... print(render_css(css()))

.. code-block:: css

    @charset 'UTF-8';
    body {
      margin: 0;
      padding: 2em;
    }
    header {
      margin: 1em 2em;
      font-family: Gill, Helvetica, sans-serif;
      text-shadow: 1px 1px 2px blue, 0 0 1em red, 0 0 0.2em red;
    }
    nav {
      margin-top: 1em;
    }
    nav ul {
      list-style: none;
    }
    body.theme-red nav ul {
      background: red;
    }
    body.theme-red nav ul li {
      color: white;
    }
    /* this is a comment */
    /* this is a
       multi-lines comment */
    /* another comment */
    nav ul li {
      height: 1.5em;
      width: calc(100% - 2em);
    }
    @media screen and (max-width: 800px) {
      nav ul li {
        width: 5em;
      }
      nav ul li b {
        background: white;
      }
      nav ul li a {
        background: white;
        text-decoration: underline;
      }
    }
    header {
      background: -webkit-linear-gradient(left, blue, red, blue);
      background: -moz-linear-gradient(left, blue, red, blue);
      background: -ms-linear-gradient(left, blue, red, blue);
      background: -o-linear-gradient(left, blue, red, blue);
      background: linear-gradient(left, blue, red, blue);
    }
    body.theme-red p, body.theme-red blockquote {
      border: solid red 1px;
    }
    body.theme-red p strong, body.theme-red p em, body.theme-red blockquote strong,
    body.theme-red blockquote em {
      color: red;
    }
    body.theme-red p:target, body.theme-red p:focus, body.theme-red blockquote:target,
    body.theme-red blockquote:focus {
      border-width: 3px;
    }
    .message, .message-important, .alert, .popup {
      border: solid black 1px;
    }
    .message a, .message-important a, .alert a, .popup a {
      text-decoration: underline;
    }
    .message-important {
      border-width: 2px;
    }
    .alert, .popup {
      position: absolute;
    }
    .alert, .popup {
      z-index: 1000;
    }
    .foo: { color: blue; }
    .bar { color: white; }
    .baz { color: red; }

"""

from .loading import (  # noqa: F401
    css_vars,
    import_css,
    import_css_global,
    load_css_keywords,
)
from .modes import (  # noqa: F401
    Modes,
    get_default_mode,
    override_default_mode,
    set_default_mode,
)
from .rendering import render_css  # noqa: F401
from .units import load_css_units  # noqa: F401
from .utils import CssDict  # noqa: F401
from .vars import CSS_VARS as c  # noqa: F401
