"""Provide the ``Element`` class to create reusable components."""


from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type, cast

from ..element import Element
from ..exceptions import MixtException
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
        name : str
            The name of the class to construct.
        parents : Sequence[type]
            A tuple with the direct parent classes of the class to construct.
        attrs : Dict[str, Any]
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
                    context : OptionalContext
                        The context passed through the tree.

                    """
                    pass

            cls.Collect = Collect


class Collector(Element, metaclass=CollectorMetaclass):
    """Base of all collectors. Render children and collect ones of its own Collect class."""

    KIND: Optional[str] = None

    class PropTypes:
        """Base PropTypes for collectors.

        Attributes
        ----------
        render_position : DefaultChoices
            Tell where to insert the collected content.

            If set, the collected content will be inserted ``before`` opening tag of the collector
            or ``after`` its closing tag.

            If not set, the content won't be inserted: the ``render_collected`` method will need
            to be called to get the content. For example using the ``ref`` prop.

        """

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
        self.__global_classes__: Set[Type[Base]] = set()
        self.__global_methods__: Set[Callable] = set()
        super().__init__(**kwargs)

    def postrender_child_element(
        self, child: "Element", child_element: AnElement, context: OptionalContext
    ) -> None:
        """Catch child render_{KIND} method, or child content if a ``Collect``.

        If there is KIND:
        - try to collect  the``render_{KIND}_global`` class method if not already done for the child
        's class (it will collect this method for all parents, starting for the higher in the mro:
        do not use ``super`` in this class)
        - try to collect ``render_{KIND}

        Then collect if it's a ``Collect`` instance.

        Parameters
        ----------
        child : Element
            The element in a tree on which ``render`` was just called.
        child_element : AnElement
            The element rendered by the call of the ``render`` method of `child`.
        context : OptionalContext
            The context passed through the tree.

        Raises
        ------
        MixtException
            If the ``render_{KIND}_global`` is not a ``classmethod``.

        """
        if self.KIND:
            if child.__class__ not in self.__global_classes__:
                for base in reversed(child.__class__.__mro__):
                    if base in self.__global_classes__:
                        continue
                    self.__global_classes__.add(base)
                    if not hasattr(base, f"render_{self.KIND}_global"):
                        continue
                    method = getattr(base, f"render_{self.KIND}_global")
                    if not hasattr(method, "__func__"):
                        if getattr(base, "__display_name__", None):
                            name = f"<{base.__display_name__}>"  # type: ignore
                        else:
                            name = str(base)
                        raise MixtException(
                            f"{name}.render_{self.KIND}_global must be a classmethod"
                        )
                    if method.__func__ in self.__global_methods__:
                        continue
                    self.__global_methods__.add(method.__func__)
                    self.__collected__.append(
                        self.call_collected_method(method, context, True)
                    )

            if hasattr(child, f"render_{self.KIND}"):
                method = getattr(child, f"render_{self.KIND}")
                if callable(method):
                    self.__collected__.append(
                        self.call_collected_method(method, context, False)
                    )

        if isinstance(child, self.Collect):
            self.__collected__.append(child)

    def call_collected_method(
        self,
        method: Callable,
        context: OptionalContext,
        is_global: bool,  # pylint: disable=unused-argument
    ) -> str:
        """Call the collected `method`, passing it the `context`.

        Parameters
        ----------
        method : Callable
            The method to run to collect the output.
        context : OptionalContext
            The context passed through the tree.
        is_global : bool
            If the `method` to execute is a global one (ie ``render_{KIND}_global``) or not.

        Returns
        -------
        str
            The result of the call to `method`, ready to be collected.

        """
        return method(context)

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
        acc : List
            The accumulator list where to append the parts.

        """
        if self.render_position == "before":
            acc.append(self.render_collected)
        super()._to_list(acc)
        if self.render_position == "after":
            acc.append(self.render_collected)


class CSSCollector(Collector):
    """A collector that'll surround collected content in a ``<style>`` tag in ``render_collected``.

    It can collect via the ``<CSSCollector.Collect>`` tag, and/or via the ``render_css`` method
    on the child.

    Examples
    --------
    # Using ``render_position``:
    >>> from mixt import CSSCollector, Element, Ref, Required, h, html

    # First a component we want to style:
    >>> class Component(Element):
    ...     class PropTypes:
    ...         id: Required[str]  # already exists but we force it via Required
    ...         color: str
    ...
    ...     @classmethod
    ...     def render_css_global(cls, context):
    ...         return '''
    ... /* rendered once via render_css_global */
    ... .comp { color: red; }
    ...         '''
    ...
    ...     def render_css(self, context):
    ...         if self.has_prop('color'):
    ...             return '''
    ... /* rendered for each component via render_css */
    ... #%(id)s.comp { color: %(color)s; }
    ...             '''{
    ...                 'id': self.id,
    ...                 'color': self.color,
    ...             }
    ...
    ...     def render(self, context):
    ...         return <div class="comp" id={self.id}  />

    # Now we can render many instances of this component and collect the CSS:
    >>> print(
    ...     <CSSCollector render_position=after>
    ...         <CSSCollector.Collect>{h.Raw('''
    ... /* rendered once via Collect */
    ... div { color: black;}
    ...         ''')}</CSSCollector.Collect>
    ...         <Component id=c1 color=blue />
    ...         <Component id=c2 color=green />
    ...     </CSSCollector>
    ... )
    <div class="comp" id="c1"></div><div class="comp" id="c2"></div><style type="text/css">
    /* rendered once via Collect */
    div { color: black;}

    /* rendered once via render_css_global */
    .comp { color: red; }

    /* rendered for each component via render_css */
    #c1.comp { color: blue; }

    /* rendered for each component via render_css */
    #c2.comp { color: green; }
                </style>

    # Same component, but this time using a ref and ``render_collected``:
    >>> css_ref = Ref()
    >>> print(
    ... <html>
    ...     <head>
    ...         {lambda: css_ref.current.render_collected()}
    ...     </head>
    ...     <body>
    ...         <CSSCollector ref={css_ref}>
    ...             <CSSCollector.Collect>{h.Raw('''
    ... /* rendered once via Collect */
    ... div { color: black;}
    ...         ''')}</CSSCollector.Collect>
    ...             <Component id=c1 color=blue />
    ...             <Component id=c2 color=green />
    ...         </CSSCollector>
    ...     </body>
    ... </html>
    ... )
    <html><head><style type="text/css">
    /* rendered once via Collect */
    div { color: black;}

    /* rendered once via render_css_global */
    .comp { color: red; }

    /* rendered for each component via render_css */
    #c1.comp { color: blue; }

    /* rendered for each component via render_css */
    #c2.comp { color: green; }
    </style></head><body>
    <div class="comp" id="c1"></div><div class="comp" id="c2"></div></body></html>


    """

    KIND = "css"

    class PropTypes:
        """PropTypes for the ``CSSCollector`` component.

        Attributes
        ----------
        type : str
            The value of the ``type`` attribute of the ``style`` tag that will be generated.

        """

        type: str = "text/css"

    def render_collected(self) -> OneOrManyElements:
        """Render the content of all collected children at once.

        Simply put the result of the normal call to ``render_collected`` into a
        ``<style>`` tag.

        """
        str_collected: str = cast(str, super().render_collected())

        return Style(type=self.type)(Raw(str_collected))


class JSCollector(Collector):
    """A collector that'll surround collected content in a ``<script>`` tag in ``render_collected``.

    It can collect via the ``<JSCollector.Collect>`` tag, and/or via the ``render_js`` method
    on the child.

    Examples
    --------
    # See example from ``CSSCollector``.
    # The same principles apply with ``JSCollector``:
    # - a ``JSCollector.Collect`` component
    # - ``render_js_global`` class methods are collected once
    # - ``render_js`` methods are collected for every component

    """

    KIND = "js"

    class PropTypes:
        """PropTypes for the ``JSCollector`` component.

        Attributes
        ----------
        type : str
            The value of the ``type`` attribute of the ``script`` tag that will be generated.

        """

        type: str = "text/javascript"

    def render_collected(self) -> OneOrManyElements:
        """Render the content of all collected children at once.

        Simply put the result of the normal call to ``render_collected`` into a
        ``<script>`` tag.

        """
        str_collected: str = cast(str, super().render_collected())

        return Script(type=self.type)(Raw(str_collected))
