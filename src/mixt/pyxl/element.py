#!/usr/bin/env python

from .base import Base, WithClass
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
            self.prerender()
            self._element = self.render()
            if isinstance(self._element, (list, tuple)):
                self._element = Fragment()(self._element)
            self.postrender(self._element)
        return self._element

    def render(self):
        raise NotImplementedError()

    def prerender(self):
        """
        Hook to do things before the element is rendered.  Default behavior is
        to do nothing.
        """
        pass

    def postrender(self, element):
        """
        Hook to do things after the element is rendered.  Default behavior
        is to do nothing
        """
        pass
