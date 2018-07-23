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
                    for name in 'join many override extend raw comment string Not merge'.split()
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
