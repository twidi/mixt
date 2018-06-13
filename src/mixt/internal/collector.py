"""Provide the ``Element`` class to create reusable components."""


from typing import cast, Any, Dict, List, Optional, Sequence, Type

from ..element import Element
from ..html import Raw, Script, Style
from ..proptypes import DefaultChoices
from .base import AnElement, Base, BaseMetaclass, OneOrManyElements, OptionalContext
from .html import RawHtml


class CollectorMetaclass(BaseMetaclass):
    """A metaclass for collector classes."""

    def __init__(
        cls, name: str, parents: Sequence[type], attrs: Dict[str, Any]  # noqa: B902
    ) -> None:
        """Construct the class, and create a ``Collect`` inside class if not given in `attrs`.

        Parameters
        ----------
        name: str
            The name of the class to construct.
        parents: Sequence[type]
            A tuple with the direct parent classes of the class to construct.
        attrs: Dict[str, Any]
            Dict with the attributes defined in the class.

        """
        super().__init__(name, parents, attrs)
        if not attrs.get("Collect"):

            class Collect(Element):
                """Element that renders nothing."""

                def render(self, context: OptionalContext) -> None:
                    """Return nothing, the collector will render if needed.

                    Parameters
                    ----------
                    context: OptionalContext
                        The context passed through the tree.

                    """
                    pass

            cls.Collect = Collect


class Collector(Element, metaclass=CollectorMetaclass):
    """Base of all collectors. Render children and collect ones of its own Collect class."""

    KIND: Optional[str] = None

    class PropTypes:
        render_position: DefaultChoices = cast(
            DefaultChoices, [None, "before", "after"]
        )

    def __init__(self, **kwargs: Any) -> None:
        """Create the collector with an empty list of collected children..

        ``__collected`` will contain all children of collected children.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The props to set on this collector.

        """
        self.__collected__: List[AnElement] = []
        self.__global__: List[Type[Base]] = []
        super().__init__(**kwargs)

    def render(self, context: OptionalContext) -> OneOrManyElements:
        """Return the children of a collector, to be rendered as html.

        Parameters
        ----------
        context: OptionalContext
            The context passed through the tree.

        Returns
        -------
        Optional[OneOrManyElements]
            None, or one or many elements or strings.

        """
        return self.children()

    def postrender_child_element(
        self, child: "Element", child_element: AnElement, context: OptionalContext
    ) -> None:
        """Catch child render_{KIND} method, or child content if a ``Collect``.

        If there is KIND:
        - try to collect ``render_{KIND}_global`` if not already done for the child's class
        - try to collect ``render_{KIND}
        Then collect if it's a ``Collect`` instance.

        Parameters
        ----------
        child: Element
            The element in a tree on which ``render`` was just called.
        child_element: AnElement
            The element rendered by the call of the ``render`` method of `child`.
        context: OptionalContext
            The context passed through the tree.

        """
        if self.KIND:

            if child.__class__ not in self.__global__:
                self.__global__.append(child.__class__)
                if hasattr(child, f"render_{self.KIND}_global"):
                    method = getattr(child, f"render_{self.KIND}_global")
                    if callable(method):
                        self.__collected__.append(method(context))

            if hasattr(child, f"render_{self.KIND}"):
                method = getattr(child, f"render_{self.KIND}")
                if callable(method):
                    self.__collected__.append(method(context))

        if isinstance(child, self.Collect):
            self.__collected__.append(child)

    def render_collected(self) -> OneOrManyElements:
        """Render the content of all collected children at once.

        It's done as if all the children of the collected ``Collect`` instances
        were in the same ``Fragment``.

        Returns
        -------
        str
            All collected content stringified and concatened.

        """
        str_list: List[AnElement] = []

        for collected in self.__collected__:
            if isinstance(collected, Base) and not isinstance(collected, RawHtml):
                for child in collected.__children__:
                    self._render_element_to_list(child, str_list)
            elif isinstance(collected, str):
                str_list.append(collected)
            else:
                self._render_element_to_list(collected, str_list)

        return self._str_list_to_string(str_list)

    def _to_list(self, acc: List) -> None:
        """Fill the list `acc` with strings that will be concatenated to produce the html string.

        Simply prepend/append ``self.render_collected`` as a callable depening on the
        ``render_position`` prop.

        Parameters
        ----------
        acc: List
            The accumulator list where to append the parts.

        """
        if self.render_position == "before":
            acc.append(self.render_collected)
        super()._to_list(acc)
        if self.render_position == "after":
            acc.append(self.render_collected)


class CSSCollector(Collector):
    """A collector that will surround collected content in a <style> tag in ``render_collected``.

    It can collect via the ``<CSSCollector.Collect>`` tag, and/or via the ``render_css`` method
    on the child.

    """

    KIND = "css"

    class PropTypes:
        type: str = "text/css"

    def render_collected(self) -> OneOrManyElements:
        """Render the content of all collected children at once.

        Simply put the result of the normal call to ``render_collected`` into a
        ``<style>`` tag.

        """
        str_collected: str = cast(str, super().render_collected())

        return Style(type=self.type)(Raw(str_collected))


class JSCollector(Collector):
    """A collector that will surround collected content in a <script> tag in ``render_collected``.

    It can collect via the ``<JSCollector.Collect>`` tag, and/or via the ``render_js`` method
    on the child.

    """

    KIND = "js"

    class PropTypes:
        type: str = "text/javascript"

    def render_collected(self) -> OneOrManyElements:
        """Render the content of all collected children at once.

        Simply put the result of the normal call to ``render_collected`` into a
        ``<script>`` tag.

        """
        str_collected: str = cast(str, super().render_collected())

        return Script(type=self.type)(Raw(str_collected))
