#!/usr/bin/env python

from .base import Base, WithClass, EmptyContext
from .html import Fragment


class Element(WithClass):

    class PropTypes:
        _class: str
        id: str

    _element = None  # render() output cached by _rendered_element()

    def _get_base_element(self):
        out = self._rendered_element()
        classes = self.classes

        while isinstance(out, Element):
            new_out = out._rendered_element()
            classes = out.classes + classes
            out = new_out

        if classes and isinstance(out, Base):
            classes = out.classes + classes
            out.set_prop('class', ' '.join(dict.fromkeys(classes)))  # keep ordering in py3.6

        return out

    def get_id(self):
        return self.prop('id')

    def children(self, selector=None, exclude=False):
        children = super().children()

        if not selector:
            return children

        # filter by class
        if selector[0] == '.':
            select = lambda x: selector[1:] in x.classes

        # filter by id
        elif selector[0] == '#':
            select = lambda x: selector[1:] == x.get_id()

        # filter by tag name
        else:
            select = lambda x: selector == x.__tag__

        if exclude:
            func = lambda x: not select(x)
        else:
            func = select

        return list(filter(func, children))

    def _to_list(self, l):
        self._render_child_to_list(self._get_base_element(), l)

    def _rendered_element(self):
        if self._element is None:
            context = self.context if self.context is not None else EmptyContext
            self.prerender(context)
            self._element = self.render(self.context or EmptyContext)
            if isinstance(self._element, (list, tuple)):
                self._element = Fragment()(self._element)
            if isinstance(self._element, Base):
                self._element._set_context(self.context)  # pass None if context not defined, not EmptyContext
            self.postrender(self._element, context)
        return self._element

    def render(self, context):
        raise NotImplementedError()

    def prerender(self, context):
        """
        Hook to do things before the element is rendered.  Default behavior is
        to do nothing.
        """
        pass

    def postrender(self, element, context):
        """
        Hook to do things after the element is rendered.  Default behavior
        is to do nothing
        """
        pass
