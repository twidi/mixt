#!/usr/bin/env python

from .base import Base


class Element(Base):

    class PropTypes:
        _class: str
        id: str

    _element = None  # render() output cached by _rendered_element()

    def _get_base_element(self):
        # Adding classes costs ~10%
        out = self._rendered_element()
        # Note: get_class() may return multiple space-separated classes.
        cls = self.get_class()
        classes = set(cls.split(' ')) if cls else set()

        while isinstance(out, Element):
            new_out = out._rendered_element()
            cls = out.get_class()
            if cls:
                classes.update(cls.split(' '))
            out = new_out

        if classes and isinstance(out, Base):
            classes.update(out.get_class().split(' '))
            out.set_prop('class', ' '.join([_f for _f in classes if _f]))

        return out

    def add_class(self, xclass):
        if not xclass: return
        current_class = self.prop('class')
        if current_class: current_class += ' ' + xclass
        else: current_class = xclass
        self.set_prop('class', current_class)

    def get_id(self):
        return self.prop('id')

    def get_class(self):
        return self.prop('class', '')

    def children(self, selector=None, exclude=False):
        children = super().children()

        if not selector:
            return children

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

        return list(filter(func, children))

    def _to_list(self, l):
        self._render_child_to_list(self._get_base_element(), l)

    def _rendered_element(self):
        if self._element is None:
            self.prerender()
            self._element = self.render()
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
