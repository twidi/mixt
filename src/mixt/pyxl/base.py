#!/usr/bin/env python

# We want a way to generate non-colliding 'pyxl<num>' ids for elements, so we're
# using a non-cryptographically secure random number generator. We want it to be
# insecure because these aren't being used for anything cryptographic and it's
# much faster (2x). We're also not using NumPy (which is even faster) because
# it's a difficult dependency to fulfill purely to generate random numbers.

import enforce
import keyword

from typing import get_type_hints, Sequence, Generic, TypeVar

from enforce.exceptions import RuntimeTypeError

from .utils import escape


class PyxlException(Exception):
    pass


class NotProvided: ...


class Mandatory(Generic[TypeVar("T")]): ...



class Choices(Sequence): ...


class BasePropTypes:

    __owner_name__ = None
    __types__ = {}
    __mandatory_props__ = set()
    __default_props__ = {}


    # Rules for props names
    # a starting `_` will be removed in final html attribute
    # a single `_` will be changed to `-`
    # a double `__` will be changed to `:`

    @staticmethod
    def __to_html__(name):
        if name.startswith('_'):
            name = name[1:]
        return name.replace('__', ':').replace('_', '-')

    @staticmethod
    def __to_python__(name):
        name = name.replace('-', '_').replace(':', '__')
        if not name.isidentifier():
            raise NameError
        if keyword.iskeyword(name):
            name = '_' + name
        return name

    @classmethod
    def __allow__(cls, name):
        return name in cls.__types__ or name.startswith('data_') or name.startswith('aria_')

    @classmethod
    def __type__(cls, name):
        return cls.__types__.get(name, str)

    @classmethod
    def __value__(cls, name):
        return getattr(cls, name)

    @classmethod
    def __is_choice__(cls, name):
        return issubclass(cls.__type__(name), Choices)

    @classmethod
    def __is_bool__(cls, name):
        return cls.__type__(name) is bool

    @classmethod
    def __default__(cls, name):
        return cls.__default_props__.get(name, NotProvided)

    @classmethod
    def __validate_types__(cls):
        cls.__types__ = get_type_hints(cls)

        for name, prop_type in cls.__types__.items():

            is_mandatory = False
            if issubclass(prop_type, Mandatory):
                is_mandatory = True
                prop_type = prop_type.__args__[0]
                cls.__types__[name] = prop_type
                cls.__mandatory_props__.add(name)

            if cls.__is_choice__(name):

                if not getattr(cls, name, []):
                    raise PyxlException(f'<{cls.__owner_name__}> must have a list of values for prop `{name}`')

                choices = getattr(cls, name)
                if not isinstance(choices, Sequence) or isinstance(choices, str):
                    raise PyxlException(f'<{cls.__owner_name__}> must have a list of values for prop `{name}`')

                if choices[0] is not NotProvided:
                    if is_mandatory:
                        raise PyxlException(f'<{cls.__owner_name__}> cannot have a default value for the mandatory prop `{name}`')
                    cls.__default_props__[name] = choices[0]

                continue

            default =  getattr(cls, name, NotProvided)
            if default is NotProvided:
                continue

            if is_mandatory:
                raise PyxlException(f'<{cls.__owner_name__}> cannot have a default value for the mandatory prop `{name}`')

            try:
                cls.__validate__(name, default)
            except PyxlException:
                raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(default)} `{default}` is not a valid default value')

            cls.__default_props__[name] = default

    @classmethod
    def __validate__(cls, name, value):

        if cls.__is_choice__(name):
            if value in cls.__value__(name):
                return value

            raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid choice')

        if cls.__is_bool__(name):
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
                return True
            if value is False:
                return False

            str_value = str(value).capitalize()
            if str_value == 'True':
                return True
            if str_value  == 'False':
                return False

            raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value')

        # normal check
        prop_type = cls.__type__(name)
        try:
            if isinstance(value, prop_type):
                return value
            raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value')

        except TypeError:
            # we use "enforce" to check complex types

            @enforce.runtime_validation
            def check(prop_value: prop_type): ...

            try:
                check(value)
            except RuntimeTypeError:
                raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value')

            return value


    @classmethod
    def __validate_mandatory__(cls, props):
        for name in cls.__mandatory_props__:
            if props.get(name, NotProvided) is NotProvided:
                raise PyxlException(f'<{cls.__owner_name__}>.{name}: is mandatory but not set')

class BaseMetaclass(type):
    def __init__(self, name, parents, attrs):
        super().__init__(name, parents, attrs)

        setattr(self, '__tag__', name)

        proptypes_classes = []

        if 'PropTypes' in attrs:
            proptypes_classes.append(attrs['PropTypes'])

        proptypes_classes.extend([parent.PropTypes for parent in parents[::-1] if hasattr(parent, 'PropTypes')])

        class PropTypes(*proptypes_classes):
            __owner_name__ = name
            __types__ = {}
            __mandatory_props__ = set()
            __default_props__ = {}

        PropTypes.__validate_types__()

        setattr(self, 'PropTypes', PropTypes)


class Base(object, metaclass=BaseMetaclass):

    class PropTypes(BasePropTypes):
        pass

    def __init__(self, **kwargs):
        self.__props__ = {}
        self.__children__ = []

        for name, value in kwargs.items():
            self.set_prop(name, value)

        self.PropTypes.__validate_mandatory__(self.__props__)

    def __call__(self, *children):
        self.append_children(children)
        return self

    def children(self):
        return self.__children__

    def append(self, child):
        if type(child) in (list, tuple) or hasattr(child, '__iter__'):
            self.__children__.extend(c for c in child if c is not None and c is not False)
        elif child is not None and child is not False:
            self.__children__.append(child)

    def prepend(self, child):
        if child is not None and child is not False:
            self.__children__.insert(0, child)

    def append_children(self, children):
        for child in children:
            self.append(child)

    def __getattr__(self, name):
        if len(name) > 4 and name.startswith('__') and name.endswith('__'):
            # For dunder name (e.g. __iter__),raise AttributeError, not PyxlException.
            raise AttributeError(name)
        return self.prop(name)

    def prop(self, name, default=NotProvided):
        name = BasePropTypes.__to_python__(name)
        if not self.PropTypes.__allow__(name):
            raise PyxlException('<%s> has no prop named "%s"' % (self.__tag__, name))

        value = self.__props__.get(name, NotProvided)

        if value is not NotProvided:
            return value

        prop_default = self.PropTypes.__default__(name)
        if prop_default is not NotProvided:
            return prop_default

        if default is NotProvided:
            raise AttributeError('%s is not defined' % name)

        return default

    def set_prop(self, name, value):
        name = BasePropTypes.__to_python__(name)
        if not self.PropTypes.__allow__(name):
            raise PyxlException('<%s> has no prop named "%s"' % (self.__tag__, name))

        if value is NotProvided:
            self.__props__.pop(name, None)
            return

        self.__props__[name] = self.PropTypes.__validate__(name, value)

    def unset_prop(self, name):
        self.set_prop(name, value=NotProvided)

    @property
    def props(self):
        return dict(self.PropTypes.__default_props__, **self.__props__)

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
