#!/usr/bin/env python

from itertools import chain
from typing import Sequence, Any, Union, List, Dict

from ..exceptions import PyxlException
from ..internal.proptypes import BasePropTypes
from ..proptypes import NotProvided
from .utils import escape

# pylint: disable=invalid-name
OptionalContext = Union['BaseContext', None]
AnElement = Union['Base', str]
ManyElements = Sequence[AnElement]
OneOrManyElements = Union[AnElement, Sequence[AnElement]]
# pylint: enable=invalid-name


class BaseMetaclass(type):
    def __init__(
        cls, name: str, parents: Sequence[type], attrs: Dict[str, Any]  # noqa: B902
    ) -> None:
        super().__init__(name, parents, attrs)

        tag = attrs.get('__tag__') or name
        setattr(cls, '__tag__', tag)
        setattr(cls, '__str_tag__', attrs.get('__str_tag__') or tag)

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

        setattr(cls, 'PropTypes', PropTypes)


class Base(object, metaclass=BaseMetaclass):

    __tag__ = ''
    __str_tag__ = ''

    class PropTypes(BasePropTypes):
        pass

    def __init__(self, **kwargs):
        self.__props__ = {}
        self.__children__ = []
        self.context = None

        for name, value in kwargs.items():
            self.set_prop(name, value)

        self.PropTypes.__validate_required__(self.__props__)

    def __call__(self, *children: OneOrManyElements) -> 'Base':
        self.append(children)
        return self

    def children(self) -> ManyElements:
        return self.__children__

    def _set_context(self, context: OptionalContext) -> None:
        if context is None:
            return

        if self.context is not None and not issubclass(context.__class__, self.context.__class__):
            # merge if not already done
            context_class = type(f'{context.__tag__}__{self.context.__tag__}', (context.__class__, self.context.__class__), {})
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

    def append(self, child: OneOrManyElements) -> None:
        children = self._child_to_children(child)
        self._propagate_context(children)
        self.__children__.extend(children)

    def prepend(self, child: OneOrManyElements) -> None:
        children = self._child_to_children(child)
        self._propagate_context(children)
        self.__children__[0:0] = children

    def __getattr__(self, name):
        if len(name) > 4 and name.startswith('__') and name.endswith('__'):
            # For dunder name (e.g. __iter__),raise AttributeError, not PyxlException.
            raise AttributeError(name)
        return self.prop(name)

    def prop(self, name: str, default: Any = NotProvided) -> Any:
        name = BasePropTypes.__to_python__(name)
        if not self.PropTypes.__allow__(name):
            raise PyxlException(f'<{self.__str_tag__}> has no prop named "{name}"')

        value = self.__props__.get(name, NotProvided)

        if value is not NotProvided:
            return value

        prop_default = self.PropTypes.__default__(name)
        if prop_default is not NotProvided:
            return prop_default

        if default is NotProvided:
            raise AttributeError('%s is not defined' % name)

        return default

    def set_prop(self, name: str, value: Any) -> None:
        name = BasePropTypes.__to_python__(name)
        if not self.PropTypes.__allow__(name):
            raise PyxlException(f'<{self.__str_tag__}> has no prop named "{name}"')

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
    def _render_child_to_list(child: AnElement, l: List) -> None:
        if isinstance(child, Base): child._to_list(l)
        elif child is not None: l.append(escape(child))

    def _render_children_to_list(self, l: List) -> None:
        for child in self.__children__:
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


class _EmptyContext(BaseContext):
    pass

EmptyContext = _EmptyContext()
