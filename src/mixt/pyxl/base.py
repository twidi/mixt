#!/usr/bin/env python

# We want a way to generate non-colliding 'pyxl<num>' ids for elements, so we're
# using a non-cryptographically secure random number generator. We want it to be
# insecure because these aren't being used for anything cryptographic and it's
# much faster (2x). We're also not using NumPy (which is even faster) because
# it's a difficult dependency to fulfill purely to generate random numbers.

import keyword
import random
import sys

from typing import get_type_hints, Sequence

from .utils import escape


class PyxlException(Exception):
    pass


class Choices(Sequence): ...


class BasePropTypes:
    # Rules for props names
    # a starting `_` will be removed in final html attribute
    # a single `_` will be changed to `-`
    # a double `__` will be changed to `:`

    @staticmethod
    def to_html(name):
        if name.startswith('_'):
            name = name[1:]
        return name.replace('__', ':').replace('_', '-')

    @staticmethod
    def to_python(name):
        name = name.replace('-', '_').replace(':', '__')
        if not name.isidentifier():
            raise NameError
        if keyword.iskeyword(name):
            name = '_' + name
        return name

    @classmethod
    def allow(cls, name):
        return name in cls._types or name.startswith('data_') or name.startswith('aria_')

    @classmethod
    def type(cls, name):
        return cls._types.get(name, str)


class BaseMetaclass(type):
    def __init__(self, name, parents, attrs):
        super().__init__(name, parents, attrs)

        proptypes_classes = []

        if 'PropTypes' in attrs:
            proptypes_classes.append(attrs['PropTypes'])

        proptypes_classes.extend([parent.PropTypes for parent in parents[::-1] if hasattr(parent, 'PropTypes')])

        class PropTypes(*proptypes_classes):
            pass

        PropTypes._types = get_type_hints(PropTypes)

        setattr(self, 'PropTypes', PropTypes)

        setattr(self, '__tag__', name)

class Base(object, metaclass=BaseMetaclass):

    class PropTypes(BasePropTypes):
        # HTML attributes
        accesskey: str
        _class: str
        dir: str
        id: str
        lang: str
        maxlength: str
        role: str
        style: str
        tabindex: int
        title: str
        xmllang: str

        # Microdata HTML attributes
        itemtype: str
        itemscope: str
        itemprop: str
        itemid: str
        itemref: str

        # JS attributes
        onabort: str
        onblur: str
        onchange: str
        onclick: str
        ondblclick: str
        onerror: str
        onfocus: str
        onkeydown: str
        onkeypress: str
        onkeyup: str
        onload: str
        onmousedown: str
        onmouseenter: str
        onmouseleave: str
        onmousemove: str
        onmouseout: str
        onmouseover: str
        onmouseup: str
        onreset: str
        onresize: str
        onselect: str
        onsubmit: str
        onunload: str

    def __init__(self, **kwargs):
        self.__props__ = {}
        self.__children__ = []

        for name, value in kwargs.items():
            self.set_prop(name, value)

    def __call__(self, *children):
        self.append_children(children)
        return self

    def get_id(self):
        eid = self.prop('id')
        if not eid:
            eid = 'pyxl%d' % random.randint(0, sys.maxsize)
            self.set_prop('id', eid)
        return eid

    def children(self, selector=None, exclude=False):
        if not selector:
            return self.__children__

        # filter by class
        if selector[0] == '.':
            select = lambda x: selector[1:] in x.get_class()

        # filter by id
        elif selector[0] == '#':
            select = lambda x: selector[1:] == x.get_id()

        # filter by tag name
        else:
            select = lambda x: x.__class__.__name__ == selector

        if exclude:
            func = lambda x: not select(x)
        else:
            func = select

        return list(filter(func, self.__children__))

    def append(self, child):
        if type(child) in (list, tuple) or hasattr(child, '__iter__'):
            self.__children__.extend(c for c in child if c is not None and c is not False)
        elif child is not None and child is not False:
            self.__children__.append(child)

    def prepend(self, child):
        if child is not None and child is not False:
            self.__children__.insert(0, child)

    def __getattr__(self, name):
        if len(name) > 4 and name.startswith('__') and name.endswith('__'):
            # For dunder name (e.g. __iter__),raise AttributeError, not PyxlException.
            raise AttributeError(name)
        return self.prop(name)

    def prop(self, name, default=None):  # TODO: default could maybe be `NotProvided` ?
        name = BasePropTypes.to_python(name)
        if not self.PropTypes.allow(name):
            raise PyxlException('<%s> has no prop named "%s"' % (self.__tag__, name))

        value = self.__props__.get(name)

        if value is not None:
            return value

        prop_type = self.PropTypes.type(name)

        if issubclass(prop_type, Choices):
            values_enum = getattr(self.PropTypes, name)

            if not values_enum:
                # TODO: this must be checked in the metaclass
                raise PyxlException('Invalid prop definition')

            if None in values_enum[1:]:
                # TODO: this must be checked in the metaclass
                raise PyxlException('None must be the first, default value')

            # TODO: return ``default`` if ``values_enum[0] is None``
            return values_enum[0]

        return default  # TODO get value from PropTypes if defined if default is None

    def set_prop(self, name, value):
        name = BasePropTypes.to_python(name)
        if not self.PropTypes.allow(name):
            raise PyxlException('<%s> has no prop named "%s"' % (self.__tag__, name))

        if value is not None:
            prop_type = self.PropTypes.type(name)

            if issubclass(prop_type, Choices):
                # support for enum values in pyxl attributes
                values_enum = getattr(self.PropTypes, name)
                assert values_enum, 'Invalid attribute definition'

                if value not in values_enum:
                    msg = '%s: %s: incorrect value "%s" for "%s". Expecting enum value %s' % (
                        self.__tag__, self.__class__.__name__, value, name, values_enum)
                    raise PyxlException(msg)

            elif prop_type is bool:
                # Special case for bool.
                # We can have True:
                #     In html5, bool attributes can set to an empty string or the attribute name.
                #     We also accept python True or a string that is 'true' lowercased.
                #     We force the value to True.
                # We can have False:
                #     In html5, bool attributes can set to an empty string or the attribute name
                #     We also accept python True or a string that is 'true' lowercased.
                #     We force the value to True.
                # All other cases generate an error

                if value in ('', name, True):
                    value = True
                elif value is False:
                    value = False
                else:
                    str_value = str(value).capitalize()
                    if str_value == 'True':
                        value = True
                    elif str_value  == 'False':
                        value = False
                    else:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        msg = '%s: %s: incorrect value for boolean "%s". expected nothing, ' \
                              'an empty string, "%s", or True or False, as python bool ' \
                              'or as string, got %s: %s' % (
                            self.__tag__, self.__class__.__name__, name, name, type(value), value)
                        exception = PyxlException(msg)
                        raise exception.with_traceback(exc_tb)
            else:
                try:
                    # Validate type of prop and cast to correct type if possible
                    value = value if isinstance(value, prop_type) else prop_type(value)
                except Exception:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    msg = '%s: %s: incorrect type for "%s". expected %s, got %s' % (
                        self.__tag__, self.__class__.__name__, name, prop_type, type(value))
                    exception = PyxlException(msg)
                    raise exception.with_traceback(exc_tb)

            self.__props__[name] = value

        elif name in self.__props__:
            del self.__props__[name]

    def get_class(self):
        return self.prop('class', '')

    def add_class(self, xclass):
        if not xclass: return
        current_class = self.prop('class')
        if current_class: current_class += ' ' + xclass
        else: current_class = xclass
        self.set_prop('class', current_class)

    def append_children(self, children):
        for child in children:
            self.append(child)

    @property
    def props(self):
        return self.__props__

    def set_props(self, props):
        for name, value in props.items():
            self.set_prop(name, value)

    def to_string(self):
        l = []
        self._to_list(l)
        return ''.join(l)

    def _to_list(self, l):
        raise NotImplementedError()

    def __str__(self):
        return self.to_string()

    @staticmethod
    def _render_child_to_list(child, l):
        if isinstance(child, Base): child._to_list(l)
        elif child is not None: l.append(escape(child))
