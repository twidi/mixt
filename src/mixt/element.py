"""Provide the ``Element`` class to create reusable components."""

from typing import List, Optional

from .html import Fragment
from .internal.base import (
    AnElement,
    Base,
    EmptyContext,
    ManyElements,
    OneOrManyElements,
    OptionalContext,
    WithClass,
)


class Element(WithClass):
    """Base element for reuasable components."""

    class PropTypes:
        _class: str
        id: str

    _element: Optional[
        AnElement
    ] = None  # render() output cached by _rendered_element()

    def _get_base_element(self) -> AnElement:
        """Return the element rendered with its children.

        Manage css classes inheritance by concatening all the classes down to the the first
        html tag.

        Returns
        -------
        Base
            A element ready to be rendered as a string.

        """
        out = self._rendered_element()
        classes = self.classes

        while isinstance(out, Element):
            new_out = out._rendered_element()
            classes = out.classes + classes
            out = new_out

        if classes and isinstance(out, Base):
            classes = out.classes + classes
            out.set_prop(
                "class", " ".join(dict.fromkeys(classes))  # keep ordering in py3.6
            )

        return out

    def get_id(self) -> str:
        """Return the ``id`` prop of the element."""
        return self.prop("id")

    def children(  # pylint: disable=arguments-differ
        self, selector: str = "", exclude: bool = False
    ) -> ManyElements:
        """Return the (direct) children, maybe filtered.

        Parameters
        ----------
        selector: str
            Empty by default, it's a string to specify how to filter the children.
            If it starts with a dot ``.``, we select children having this class.
            If it starts with a sharp ``#``, we select children having this id.
            Else we select children having this tag name.
        exclude : bool
            ``False`` by default. If ``True``, the result of the selection done by ``selector`` is
            reversed. Ie we select ALL BUT children having this clas/id/tag.

        Returns
        -------
        ManyElements
            A List, maybe empty, of all the children, maybe filtered.

        """
        children = super().children()

        if not selector:
            return children

        # filter by class
        if selector[0] == ".":
            select = lambda x: selector[1:] in x.classes

        # filter by id
        elif selector[0] == "#":
            select = lambda x: selector[1:] == x.get_id()

        # filter by tag name
        else:
            select = lambda x: selector == x.__tag__

        if exclude:
            func = lambda x: not select(x)  # type: ignore
        else:
            func = select

        return list(filter(func, children))

    def _to_list(self, acc: List) -> None:
        """Add the element parts (with its children) to the list `acc`.

        Parameters
        ----------
        acc: List
            The accumulator list where to append the parts.

        """
        self._render_element_to_list(self._get_base_element(), acc)

    def _rendered_element(self) -> AnElement:
        """Call prerender, render then postrender and return the rendered element.

        If ``render`` returns many elements, they are grouped in a ``Fragment``.

        Returns
        -------
        Union[str, Base]
            The rendered element. Can be a string, an Element, a RawHtml...

        """
        if self._element is None:
            context = self.context if self.context is not None else EmptyContext

            self.prerender(context)

            element: OneOrManyElements = self.render(self.context or EmptyContext)

            if isinstance(element, (list, tuple)):
                element = Fragment()(element)  # type: ignore

            self._element = element  # type: ignore

            if isinstance(self._element, Base):
                self._element._set_context(
                    self.context  # pass None if context not defined, not EmptyContext
                )

            self.postrender(self._element, context)  # type: ignore

        return self._element  # type: ignore

    def render(self, context: OptionalContext) -> OneOrManyElements:
        """Return element to be rendered as html.

        Must be implemented in subclasses.

        Parameters
        ----------
        context: OptionalContext
            The context passed through the tree

        """
        raise NotImplementedError()

    def prerender(self, context: OptionalContext) -> None:
        """Provide a hook to do things before the element is rendered.

        Default behavior is to do nothing.

        Parameters
        ----------
        context: OptionalContext
            The context passed through the tree

        """
        pass

    def postrender(self, element: AnElement, context: OptionalContext) -> None:
        """Provide a hook to do things after the element is rendered.

        Default behavior is to do nothing.

        Parameters
        ----------
        element: Base
            The element rendered by ``render``. Could be an Element, an html tag, a RawHtml...
        context: OptionalContext
            The context passed through the tree

        """
        pass
