# coding: mixt

from mixt import html, h
from mixt.contrib import css as contrib_css
from mixt.contrib.css import css_vars, CssDict

from ...code_utils import load_docstring, resolve_class, resolve_function
from ... import datatypes
from ..doc import DocPart, DocHeader
from ..generic import Rst, Details
from ..generic.rst import htmlize_rst
from ..models import Class, Code, DocString, Function
from .base import _Manual


class ContribCss(_Manual):

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        return CssDict({
            comment(): f"<{cls.__module__}.{cls.__name__}>",
            "#ContribCss-class-Modes-attributes .attr-details": {
                display: none,
            },
            ".ContribCss-special_vars-doc-part": {
                "> .content > details:not(.doc-part) > summary": {
                    opacity: 0.25,
                },
                "&:hover > .content > details:not(.doc-part):not([open]) > summary": {
                    opacity: 1,
                }
            },
            "#ContribCss-at-rules_rules ul": {
                list-style: disc,
            },
            comment(): f"</{cls.__module__}.{cls.__name__}>",
        })

    def render(self, context):
        id_prefix = f'{self.id_prefix}ContribCss'

        return <div>
            {htmlize_rst(contrib_css.__doc__)}

            <DocPart kind={id_prefix} subkind="modes" id_prefix={id_prefix} level={self.h_level} open>
                <DocHeader menu="Rendering modes">Rendering modes</DocHeader>
                <Rst>
                    ``render_css`` can render CSS in different ways. The choices are provided by ``Modes``,
                    to import from ``mixt.contrib.css``:
                </Rst>

                <Class h_level={self.h_level+1} id_prefix="{id_prefix}-" obj={resolve_class(
                    klass=contrib_css.Modes,
                    attrs=['COMPRESSED', 'COMPACT', 'NORMAL', 'INDENT', 'INDENT2', 'INDENT3'],
                    methods=[],
                    name='Modes',
                )} />

                <DocPart kind={id_prefix} subkind="modes-functions" id_prefix={id_prefix} level={self.h_level+1} open>
                    <DocHeader menu="Functions">Functions</DocHeader>

                    {[
                        <Function obj={resolve_function(name, getattr(contrib_css, name))} h_level={self.h_level+2} id_prefix="{id_prefix}-functions-"/>
                        for name in ['set_default_mode', 'override_default_mode', 'get_default_mode']
                    ]}

                </DocPart>

            </DocPart>

            <DocPart kind={id_prefix} subkind="modes-vars" id_prefix={id_prefix} level={self.h_level} open>
                <DocHeader menu="Special vars">Special vars</DocHeader>

                <Rst>{h.Raw(
# language=RST
"""
Here is a list of special vars that are available in functions decorated by ``css_vars(globals())``.

Except for ``dummy`` and ``builtins``, they are normal CSS vars when used normally, ie they simply render their own name, but they have a special behaviour when called.
"""
                )}</Rst>

                {[
                    <Function obj={resolve_function(name, getattr(contrib_css.vars, name).__class__.__call__)} h_level={self.h_level+1} id_prefix="{id_prefix}-special_vars-" />
                    for name in 'join many override extend combine raw comment string Not merge'.split()
                ]}

                {self.render_dummy(f"{id_prefix}-special_vars", self.h_level+1)}
                {self.render_builtins(f"{id_prefix}-special_vars", self.h_level+1)}

            </DocPart>

            <DocPart kind={id_prefix} subkind="at-rules" id_prefix={id_prefix} level={self.h_level} open>
                <DocHeader menu="At-rules">At-rules</DocHeader>

                <Rst id_prefix="{id_prefix}-at-rules" h_level={self.h_level+1}>{h.Raw(
# language=RST
"""
At-rules are special vars but when called, are converted to CSS at-rules, ie rules starting with a ``@``.

Example
-------
.. code-block:: python

    >>> from mixt.contrib.css import css_vars, render_css, load_css_keywords
    
    >>> load_css_keywords()
    
    >>> @css_vars(globals())
    >>> def css():
    ...     return {
    ...         ".foo": {
    ...             width: 5*em,
    ...             media(screen & {max-width: 600*px}): {
    ...                 width: 3*em,
    ...             }
    ...         }
    ...     }
    
    >>> print(render_css(css()))

.. code-block:: css

    .foo {
      width: 5em;
    }
    @media screen and (max-width: 600px) {
      .foo {
        width: 3em;
      }
    }

Rules
-----

""" + self.get_at_rules()
                )}</Rst>

            </DocPart>

            <DocPart kind={id_prefix} subkind="collector" id_prefix={id_prefix} level={self.h_level} open>
                <DocHeader menu="Usage with CSS collector">Usage with CSS collector</DocHeader>

                <Rst id_prefix="{id_prefix}-at-rules" h_level={self.h_level+1}>{h.Raw(
# language=RST
"""
``mixt.contrib.css`` can be used on its own but it is totally possible to use it with the
``mixt`` `CSS collector <api.html#module-collectors-classes-class-CSSCollector>`_. 

In fact, it uses it all the times even if the collected CSS are just strings.

To have your ``render_css_global`` or ``render_css`` method be able to return a CSS dict, you
cannot return directly a dict because it is used to handle namespaces.

So you have two 0ptions:

- Convert the dict to a ``CssDict``
- Return a call to ``combine``

The first is useful when you have a simple CssDict: ``return CssDict({foo: bar})``.

The second can serve the exact same purpose: ``return combine({foo: bar})``, but is also useful to
combine many dicts: ``return combine({foo: bar}, call_to_function_that_return_a_dict())``.

And of course don't forget to decorate your method.

Here is an example:

.. code-block:: python

    from mixt.contrib.css import css_vars

    class MyComponent(Element):

        @css_vars(globals())
        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                ".foo": {
                    color: white;
                }
            })

Don't forget to call ``load_css_keywords()``, for example in the ``__init__.py`` file of your
components directory.

Note that calls to ``extend`` will work between components, as soon as the name of the extend
is defined before.

You can do this with a "Css library" component like we do in the following example to defined a 
``ext`` named extend, that is used in our components. This work because we include the ``CssLib``
component in the app.

.. code-block:: python

    class CssLib(Element):
        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                "%ext": {"ext": "end"}
            })

    class Foo(Element):
        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                ".foo": extend("ext", css={
                    "color": "FOO",
                })
            })

    class Bar(Element):
        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                ".bar": extend("ext", css={
                    "color": "BAR",
                })
            })

    class App(Element):
        def render(self, context):
            return <CSSCollector render_position="before">
                <CssLib />
                <Foo />
                <Bar />
            </CSSCollector>

    print(str(App())

.. code-block:: html

    <style type="text/css">
    .foo, .bar {
      ext: end;
    }
    .foo {
      color: FOO;
    }
    .bar {
      color: BAR;
    }
    </style>

This of course can also be done without the ``CssLib`` component as you can directly use dicts when
calling ``extend``:

.. code-block:: python

    # this could be in an other python files, available for all your components
    extends = {
        "ext": {"ext": "end"}
    }

    class Foo(Element):
        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                ".foo": extend(extends["ext"], css={
                    "color": "FOO",
                })
            })

    class Bar(Element):
        @classmethod
        def render_css_global(cls, context):
            return CssDict({
                ".bar": extend(extends["ext"], css={
                    "color": "BAR",
                })
            })

    class App(Element):
        def render(self, context):
            return <CSSCollector render_position="before">
                <Foo />
                <Bar />
            </CSSCollector>

    print(str(App())

.. code-block:: html

    <style type="text/css">
    .foo, .bar {
      ext: end;
    }
    .foo {
      color: FOO;
    }
    .bar {
      color: BAR;
    }
    </style>

"""

                )}</Rst>

            </DocPart>

        </div>

    def render_dummy(self, id_prefix, h_level):
        dummy_docstring = load_docstring(contrib_css.vars.dummy)
        dummy_doc = datatypes.SimpleDocString(dummy_docstring["Summary"], dummy_docstring["Extended Summary"])

        return \
            <DocPart kind={id_prefix} subkind="dummy" id_prefix={id_prefix} level={h_level} open>
                <DocHeader menu="dummy">dummy</DocHeader>

                <DocString doc={dummy_doc} hide_details=True />

                <Details class="linked-to-parent">
                    <summary>Details</summary>

                    <DocString doc={dummy_doc} hide_summary=True />

                    <DocPart kind="{id_prefix}-dummy" subkind="example" id_prefix="{id_prefix}-dummy" level={h_level+1} open>
                        <DocHeader menu="Example">Example</DocHeader>
                        <Code code={datatypes.Code(dummy_docstring["Examples"], language="python"
                        )} />
                    </DocPart>
                </Details>
            </DocPart>

    def render_builtins(self, id_prefix, h_level):
        builtins_doc = datatypes.SimpleDocString(
            ["Make available python builtins that may have been replaced by css vars."],
            [
                ["Alias: ``b``"]
            ]
        )

        return \
            <DocPart kind={id_prefix} subkind="builtins" id_prefix={id_prefix} level={h_level} open>
                <DocHeader menu="builtins">builtins</DocHeader>

                <DocString doc={builtins_doc} hide_details=True />

                <Details class="linked-to-parent">
                    <summary>Details</summary>

                    <DocString doc={builtins_doc} hide_summary=True />

                    <DocPart kind="{id_prefix}-builtins" subkind="example" id_prefix="{id_prefix}-builtins" level={h_level+1} open>
                        <DocHeader menu="Example">Example</DocHeader>
                        <Code code={datatypes.Code(
                            # language=Python
"""
>>> from mixt.contrib.css import css_vars, render_css, load_css_keywords

>>> load_css_keywords()

>>> @css_vars(globals())
>>> def css():
...
...     b.print("foo")  # the real python `print`
...
...     return {
...         ".bar": {bar: print("bar")},  # not the python `print`
...     }

>>> print(render_css(css()))
foo
.bar {
  bar: print(bar);
}

""", language="python"
                        )} />
                    </DocPart>
                </Details>
            </DocPart>

    def get_at_rules(self):
        _seen = set()

        def seen(v):
            if v in _seen:
                return True
            _seen.add(v)
            return False

        return "\n".join([
            f"  - **{k}**\(foo): {v('foo')}"
            for k,v
            in contrib_css.c.items()
            if isinstance(v, contrib_css.vars.AtRule)
            and not seen(v)
        ])
