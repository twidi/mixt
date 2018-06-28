# coding: mixt

from mixt import Element, html, h

from ... import types
from ..doc import DocPart, DocHeader
from ..generic import Rst
from ..models import NamedValue
from .base import _Manual


class PropTypes(_Manual):

    def render(self, context):
        id_prefix = f'{self.id_prefix}PropTypes'

        return <DocPart kind="PropTypes" id_prefix={id_prefix} level={self.h_level}>
            <DocHeader menu="PropTypes">PropTypes</DocHeader>

            <Rst>{h.Raw(
# language=RST
"""
**PropTypes are at the heart of Mixt. The aim si to specify precisely
what kind of data a component is allowed to receive.**

It is then "strongly typed" (sort of). And of course largely inspired by React.

It works by defining a class named ``PropTypes`` inside your components. (see full
example below).

Then, you must define the type
(using the `python typing syntax <https://docs.python.org/3.6/library/typing.html>`_),
and, if you want, a default value. The format is ``prop_name: type`` or
``prop_name: type = default``.
"""
            )}</Rst>

            <DocPart kind="PropTypes" subkind="types" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Special types">Special types</DocHeader>

                <NamedValue id_prefix="{id_prefix}-types-" h_level={self.h_level+2} value={
                    types.NamedValue(
                        name="Required",
                        type='',
                        doc=types.SimpleDocString(
                            ["By default all props are optional. Enclosing a prop type with ``Required[]`` make it... required."],
                            [
                                ["Note: A required prop cannot have a default value."]
                            ]
                        ),
                        example=types.Code(
                            # language=Python
"""
>>> from mixt import Required
>>> class Component(Element):
...     class PropTypes:
...         optional_prop: str
...         required_prop: Required[str]
""", language="python"
                        )
                    )
                } open_doc_details />

                <NamedValue id_prefix="{id_prefix}-types-" h_level={self.h_level+2} value={
                    types.NamedValue(
                        name="Choices",
                        type='',
                        doc=types.SimpleDocString(
                            ["``Choices`` allows to define a list of acceptable value."],
                            [
                                ["In the ``PropTypes`` class, ``Choices`` is used as the type. And the value of this prop is the list of choices."]
                            ]
                        ),
                        example=types.Code(
                            # language=Python
"""
>>> from mixt import Choices
>>> class Component(Element):
...     class PropTypes:
...         size: Choices = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
""", language="python"
                        )
                    )
                } open_doc_details />

                <NamedValue id_prefix="{id_prefix}-types-" h_level={self.h_level+2} value={
                    types.NamedValue(
                        name="DefaultChoices",
                        type='',
                        doc=types.SimpleDocString(
                            ["``DefaultChoices`` is like ``Choices`` but the first entry will be the default prop value."],
                            []
                        ),
                        example=types.Code(
                            # language=Python
"""
>>> from mixt import DefaultChoices
>>> class Component(Element):
...     class PropTypes:
...         size: DefaultChoices = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

>>> <Component />.size
'XS'
""", language="python"
                        )
                    )
                } open_doc_details />

            </DocPart>
            <DocPart kind="PropTypes" subkind="values" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Special values">Special values</DocHeader>


                <NamedValue id_prefix="{id_prefix}-values-" h_level={self.h_level+2} value={
                    types.NamedValue(
                        name="Booleans",
                        type='',
                        doc=types.SimpleDocString(
                            ["boolean props are handled specifically."],
                            [
                                ["A boolean can be passed:"],
                                [
                                    "- in python (``<Comp flagged={False} />``, ``<Comp flagged={bool_value} />``)",
                                    "- as a string (``<Comp flagged=false />``, ``<Comp flagged='false' />``)",
                                    "- without value (``<Comp flagged />``): it is then ``True``",
                                    "- with a empty string (``<Comp flagged='' />``): it is then ``True``",
                                    "- with the name of the prop as value (``<Comp flagged='flagged' />``): it is then ``True``",
                                ],
                                [
                                    "All other case are not valid.",
                                    "Passing without attribute, or with empty string or name "
                                    "of the prop as value is inspired by HTML boolean attributes."
                                ],
                            ]
                        ),
                        example=types.Code(
                            # language=Python
"""
>>> class Component(Element):
...     class PropTypes:
...         flagged: bool = False

>>> <Component />.flagged
False
>>> <Component flagged />.flagged
True
>>> <Component flagged=true />.flagged
True
>>> <Component flagged="true" />.flagged
True
>>> <Component flagged=TRUE />.flagged
True
>>> <Component flagged={True} />.flagged
True
>>> <Component flagged="" />.flagged
True
>>> <Component flagged="flagged" />.flagged
True
>>> <Component flagged="other" />
Traceback (most recent call last):
...
mixt.exceptions.InvalidPropBoolError: <Component>.flagged: `other` is not a valid choice for this boolean prop (must be in [True, False, 'true', 'false', '', 'flagged'])
>>> <Component flagged=false />.flagged
False
>>> <Component flagged="false" />.flagged
False
>>> <Component flagged=FALSE />.flagged
False
>>> <Component flagged={False} />.flagged
False

""", language="python"
                        )
                    )
                } open_doc_details />

                <NamedValue id_prefix="{id_prefix}-values-" h_level={self.h_level+2} value={
                    types.NamedValue(
                        name="Numbers",
                        type='',
                        doc=types.SimpleDocString(
                            ["Numbers (``int`` and ``float``) can be passed as string, and numbers can be passed to strings."],
                            []
                        ),
                        example=types.Code(
                            # language=Python
"""
>>> class Component(Element):
    class PropTypes:
        num: int
        string: str

>>> <Component num=1 />.num
1
>>> <Component num="1" />.num
1
>>> <Component num={1} />.num
1
>>> <Component num={"1"} />
Traceback (most recent call last):
...
mixt.exceptions.InvalidPropValueError: <Component>.num: `1` is not a valid value for this prop (type: <class 'str'>, expected: <class 'int'>)
>>> <Component string=1 />.string
'1'
>>> <Component string={1} />.string
'1'
""", language="python"
                        )
                    )
                } open_doc_details />

                <NamedValue id_prefix="{id_prefix}-values-" h_level={self.h_level+2} value={
                    types.NamedValue(
                        name="None",
                        type='',
                        doc=types.SimpleDocString(
                            ["``None`` will be interpreted as python ``None`` if passed directly or as string."],
                            [
                                ["It is important to note the difference between ``None`` and ``NotProvided``."],
                                ["``None`` is actually a value, and cannot be passed to a prop not having ``None`` as possible type."],
                            ]
                        ),
                        example=types.Code(
                            # language=Python
"""
>>> class Component(Element):
...     class PropTypes:
...         string: str
...         string_or_none: Union[None, str]

>>> <Component string_or_none=None />.string_or_none
None
>>> <Component string_or_none="None" />.string_or_none
None
>>> <Component string_or_none={"None"} />.string_or_none
'None'
>>> <Component string=None />.string
Traceback (most recent call last):
...
mixt.exceptions.InvalidPropValueError: <Component>.string: `None` is not a valid value for this prop (type: <class 'NoneType'>, expected: <class 'str'>)
>>> <Component string="None" />.string
Traceback (most recent call last):
...
mixt.exceptions.InvalidPropValueError: <Component>.string: `None` is not a valid value for this prop (type: <class 'NoneType'>, expected: <class 'str'>)
>>> <Component string="None" />.string
'None'
""", language="python"
                        )
                    )
                } open_doc_details />

                <NamedValue id_prefix="{id_prefix}-values-" h_level={self.h_level+2} value={
                    types.NamedValue(
                        name="NotProvided",
                        type='',
                        doc=types.SimpleDocString(
                            ["Passing ``NotProvided`` (directly, in python or as a string) to a prop is equal to not pass it anything. The prop won't be set."],
                            []
                        ),
                        example=types.Code(
                            # language=Python
"""
>>> from mixt import NotProvided

>>> class Component(Element):
...     class PropTypes:
...         string: str

>>> <Component string=NotProvided />.string
Traceback (most recent call last):
...
mixt.exceptions.UnsetPropError: <Component>.string: prop is not set

>>> <Component string={NotProvided} />.string
Traceback (most recent call last):
...
mixt.exceptions.UnsetPropError: <Component>.string: prop is not set

>>> <Component string="NotProvided" />.string
Traceback (most recent call last):
...
mixt.exceptions.UnsetPropError: <Component>.string: prop is not set

value = NotProvided
>>> <Component string={value} />.string
Traceback (most recent call last):
...
mixt.exceptions.UnsetPropError: <Component>.string: prop is not set

value = "NotProvided"
<Component string={value} />.string
'NotProvided'

""", language="python"
                        )
                    )
                } open_doc_details />

            </DocPart>

        </DocPart>
