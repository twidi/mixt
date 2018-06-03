#!/usr/bin/env python

import keyword

from contextlib import contextmanager
from itertools import chain
from typing import get_type_hints, Sequence, Generic, TypeVar, Any

from enforce.exceptions import RuntimeTypeError

from .utils import escape


class PyxlException(Exception):
    pass


class NotProvided: ...


class Required(Generic[TypeVar("T")]): ...



class Choices(Sequence): ...


class BasePropTypes:

    __owner_name__ = None
    __types__ = {}
    __required_props__ = set()
    __default_props__ = {}

    __dev_mode__ = True

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
        return cls.__types__.get(name, NotProvided)

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

            is_required = False
            if issubclass(prop_type, Required):
                is_required = True
                prop_type = prop_type.__args__[0]
                cls.__types__[name] = prop_type
                cls.__required_props__.add(name)

            if cls.__is_choice__(name):

                if not getattr(cls, name, []):
                    raise PyxlException(f'<{cls.__owner_name__}> must have a list of values for prop `{name}`')

                choices = getattr(cls, name)
                if not isinstance(choices, Sequence) or isinstance(choices, str):
                    raise PyxlException(f'<{cls.__owner_name__}> must have a list of values for prop `{name}`')

                if choices[0] is not NotProvided:
                    if is_required:
                        raise PyxlException(f'<{cls.__owner_name__}> cannot have a default value for the required prop `{name}`')
                    cls.__default_props__[name] = choices[0]

                continue

            default =  getattr(cls, name, NotProvided)
            if default is NotProvided:
                continue

            if is_required:
                raise PyxlException(f'<{cls.__owner_name__}> cannot have a default value for the required prop `{name}`')

            try:
                cls.__validate__(name, default)
            except PyxlException:
                raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(default)} `{default}` is not a valid default value')

            cls.__default_props__[name] = default

    @classmethod
    def __validate__(cls, name, value):

        if name.startswith('data_') or name.startswith('aria_'):
            return value

        if cls.__is_choice__(name):
            if not PropTypes.__dev_mode__:
                return value

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
            # We do this even in non-dev mode because we want a boolean. Just, in case of error
            # we return the given value casted to a boolean.

            if value in ('', name, True):
                return True
            if value is False:
                return False

            str_value = str(value).capitalize()
            if str_value == 'True':
                return True
            if str_value  == 'False':
                return False

            if not PropTypes.__dev_mode__:
                return bool(value)

            raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value')

        # normal check

        if not PropTypes.__dev_mode__:
            return value

        prop_type = cls.__type__(name)
        try:
            if isinstance(value, prop_type):
                return value
            raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value')

        except TypeError:
            # we use "enforce" to check complex types
            import enforce

            @enforce.runtime_validation
            def check(prop_value: prop_type): ...

            try:
                check(value)
            except RuntimeTypeError:
                raise PyxlException(f'<{cls.__owner_name__}>.{name}: {type(value)} `{value}` is not a valid value')

            return value


    @classmethod
    def __validate_required__(cls, props):
        if not PropTypes.__dev_mode__:
            return
        for name in cls.__required_props__:
            if props.get(name, NotProvided) is NotProvided:
                raise PyxlException(f'<{cls.__owner_name__}>.{name}: is required but not set')

    @classmethod
    def __set_dev_mode__(cls, dev_mode=True):
        cls.__dev_mode__ = dev_mode

    @classmethod
    def __unset_dev_mode__(cls):
        cls.__set_dev_mode__(dev_mode=False)

    @classmethod
    @contextmanager
    def __override_dev_mode__(cls, dev_mode):
        old_dev_mode = cls.__dev_mode__
        try:
            cls.__set_dev_mode__(dev_mode=dev_mode)
            yield
        finally:
            cls.__set_dev_mode__(dev_mode=old_dev_mode)

    @classmethod
    def __in_dev_mode__(cls):
        return cls.__dev_mode__


PropTypes = BasePropTypes
set_dev_mode = PropTypes.__set_dev_mode__
unset_dev_mode = PropTypes.__unset_dev_mode__
override_dev_mode = PropTypes.__override_dev_mode__
in_dev_mode = PropTypes.__in_dev_mode__


class BaseMetaclass(type):
    def __init__(self, name, parents, attrs):
        super().__init__(name, parents, attrs)

        setattr(self, '__tag__', attrs.get('__tag__') or name)

        proptypes_classes = []

        if 'PropTypes' in attrs:
            proptypes_classes.append(attrs['PropTypes'])

        proptypes_classes.extend([parent.PropTypes for parent in parents[::-1] if hasattr(parent, 'PropTypes')])

        class PropTypes(*proptypes_classes):
            __owner_name__ = name
            __types__ = {}
            __required_props__ = set()
            __default_props__ = {}

        PropTypes.__validate_types__()

        setattr(self, 'PropTypes', PropTypes)


class Base(object, metaclass=BaseMetaclass):

    class PropTypes(BasePropTypes):
        pass

    def __init__(self, **kwargs):
        self.__props__ = {}
        self.__children__ = []
        self.context = None

        for name, value in kwargs.items():
            self.set_prop(name, value)

        self.PropTypes.__validate_required__(self.__props__)

    def __call__(self, *children):
        self.append(children)
        return self

    def children(self):
        return self.__children__

    def _set_context(self, context):
        if context is None:
            return

        if self.context is not None and not issubclass(context.__class__, self.context.__class__):
            # merge if not already done
            context_class = type('%s__%s' % (context.__tag__, self.context.__tag__), (context.__class__, self.context.__class__), {})
            context = context_class(**dict(context.props, **self.context.props))

        self.context = context
        for child in self.__children__:
            if isinstance(child, Base):
                child._set_context(context)

    def _propagate_context(self, children):
        if self.context is None:
            return
        context = self.context
        for child in children:
            child._set_context(context)

    def _child_to_children(self, child):
        if type(child) in (list, tuple):
            children = list(chain.from_iterable(self._child_to_children(c) for c in child if c not in (None, False)))
        elif child not in (None, False):
            children = [child]
        else:
            return []
        return children

    def append(self, child):
        children = self._child_to_children(child)
        self._propagate_context(children)
        self.__children__.extend(children)

    def prepend(self, child):
        children = self._child_to_children(child)
        self._propagate_context(children)
        self.__children__[0:0] = children

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

    def _render_children_to_list(self, l, children=None):
        for child in (children or self.__children__):
            self._render_child_to_list(child, l)


class WithClass(Base):
    class PropTypes:
        _class: str

    def get_class(self):
        return self.prop('class', '')

    @property
    def classes(self):
        return self.get_class().split()

    def add_class(self, xclass, prepend=False):
        if not xclass: return
        current_class = self.get_class()
        if current_class:
            if prepend:
                current_class = xclass + ' ' + current_class
            else:
                current_class += ' ' + xclass
        else: current_class = xclass
        self.set_prop('class', current_class)

    def prepend_class(self, xclass):
        self.add_class(xclass, prepend=True)

    def append_class(self, xclass):
        self.add_class(xclass, prepend=False)

    def remove_class(self, xclass):
        self.set_prop('class', ' '.join([c for c in self.classes if c != xclass]))


class BaseContext(Base):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = self

    def _to_list(self, l):
        self._render_children_to_list(l)


class EmptyContext(BaseContext):
    pass

EmptyContext = EmptyContext()
