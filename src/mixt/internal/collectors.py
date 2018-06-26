"""Provide the ``*Collectors`` classes to collect data (JS, CSS).

Available collectors: `CSSCollector`, ``JSCollector``.

Usage (we'll use ``CSSCollector`` in these examples but it works the same with ``JSCollector``):

1. Surround the content you want to collect from with a ``<CSSCollector>``:

   .. code-block:: python

        >>> print(<CSSCollector>
        ...     <Component>
        ...         <div>Foo</div>
        ...     </Component>
        ... </CSSCollector>)

2. Collect things

   - Via ``CSSCollector.Collect``

     Everything that is inside a ``CSSCollector.Collect`` tag will be collected. If it's in a
     component that is called many times, it will be collected each times.

     It's important to encapsulate the text to collect in a raw string or text will be html-escaped
     (for example ``>`` will be converted to ``&gt;`` but we really want ``>`` to be there), and
     content of curly braces will be interpreted as "python" (because of the way "mixt" work).

     .. code-block:: python

        >>> class Component(Element):
        ...     def render(self, context):
        ...         return <Fragment>
        ...             <CSSCollector.Collect>{h.Raw('''
        ... .somecontent { color: red; }
        ...             ''')}</CSSCollector.Collect>
        ...             <div class="somecontent">{self.children()}</div>
        ...         </Fragment>

        >>> def render():
        ...     return <body>
        ...         <CSSCollector>
        ...             <CSSCollector.Collect>{h.Raw('''
        ... * { color: black; }
        ...             ''')}</CSSCollector.Collect>
        ...             <Component>
        ...                 <div>Foo</div>
        ...             </Component>
        ...         </CSSCollector>
        ...    </body>

     Here the collected content will be:

     .. code-block:: css

            * { color: black; }
            .somecontent { color: red; }

   - Via the ``render_css`` method of a component

     It works like the ``Collect`` component but allows to separate css from html by moving it
     in a dedicated method.

     This method will be called for every component having it. And like for ``Collect``, if
     a component is called many times, the output will be collected many times.

     Taking our previous example, now the ``Component`` class is simpler. Also note how we don't
     have to use ``h.Raw`` anymore: it's automatic.

     .. code-block:: python

        >>> class Component(Element):
        ...     def render_css(self, context):
        ...         return '''
        ... .somecontent { color: red; }
        ...         '''
        ...
        ...     def render(self, context):
        ...         return <div class="somecontent">{self.children()}</div>

   - Via the ``render_css_global`` method of a component

     It works like the ``render_css`` method but it is a class method and is called only once
     for each component.

     You don't have to call ``super`` in this method: the collector will collect this method for
     the parent classes too if any (using ``super`` would result in the content of the method in
     the parent class to be collected many times).

     So you can use ``render_css_global`` for global style for a component, and ``render_css`` for
     the style belonging to a very specific instance.

     .. code-block:: python

        >>> class Component(Element):
        ...     class PropTypes:
        ...         color: str
        ...
        ...     @classmethod
        ...     def render_css_global(cls, context):
        ...         return '''
        ... .somecontent { color: red; }
        ...         '''
        ...
        ...     def render_css(self, context):
        ...         if not self.has_prop("color"):
        ...             return
        ...
        ...         return '''
        ... #%(id)s { color: %(color)s; }
        ...         ''' % {'id': self.id, 'color': self.color}
        ...
        ...     def render(self, context):
        ...         return <div id={self.id} class="somecontent">{self.children()}</div>

3. Display collected content

   Now that the collected collected all the content, we need a way to render it.

   - Via the ``render_position`` prop.

     The collector accept a prop named ``render_position`` which, if set, must be either "before"
     or "after". In this case, the content will be rendered in the tree just before the opening
     of the collector tag, of just after its closing tag.

     .. code-block:: python

        >>> def render():
        ...     return <body>
        ...         # css will be rendered here in a ``<style>`` tag.
        ...         <CSSCollector render_position="before">
        ...         # ...
        ...         </CSSCollector>
        ...     </body>

     .. code-block:: python

        >>> def render():
        ...     return <body>
        ...         <CSSCollector render_position="after">
        ...         # ...
        ...         </CSSCollector>
        ...         # css will be rendered here in a ``<style>`` tag.
        ...     </body>

   - Via the ``ref`` prop.

     A ref allow to get a reference of a component and use it elsewhere. See ``Ref`` to know more.

     Here, by keeping a reference to the collector we can decide where and when to render the
     collected content.

     - After the collector

       We'll take advantage of the possibility to pass a callable as an element in the tree.

       This callable will be called at the time of the conversion to string, so after the
       rendering itself.

       .. code-block:: python

           >>> ref = Ref()
           >>> def render():
           ...     return <body>
           ...         <CSSCollector ref={ref}>
           ...         # ...
           ...         </CSSCollector>
           ...         {ref.current.render_collected}
           ...     </body>

     - Before the collector

       There is a difference in using the ref before its initialization than after, because of
       course it doesn't exist yet. So we cannot use ``ref.current.render_collected`` because
       ``ref.current`` is not yet set.

       But we can still use the callable idea, with a lambda, because the lambda will be called
       at the end, when ``ref.current`` will be defined.

       .. code-block:: python

           >>> ref = Ref()
           >>> def render():
           ...     return <html>
           ...         <head>
           ...             {lambda: ref.current.render_collected()}
           ...         </head>
           ...         <body>
           ...             <CSSCollector ref={ref}>
           ...             # ...
           ...             </CSSCollector>
           ...        </body>
           ...     </html>

     - Outside of the tree

       You may want to extract the collected content to save it to a file, for example.

       We can use the ref for this, and pass ``with_tag=False`` to ``render_collected`` to not
       have the colected content surrounded by a ``<style>`` tag:

       .. code-block:: python

           >>> ref = Ref()
           >>> def render():
           ...     return <body>
           ...         <CSSCollector ref={ref}>
           ...         # ...
           ...         </CSSCollector>
           ...     </body>

           >>> save_to_file(str(render()), 'index.html')

           >>> css = ref.current.render_collected(with_tag=False)
           >>> save_to_file(css, 'index.css')

     - At different places

       We may want to save in an external file the global css, but on the file the one specific
       to rendered components.

       For this we can use the "namespace" feature of our collector.

       By default, all the collected content is concatenated under a namespace named "default".

       And when ``render_collected`` is used, without passing any namespace, it will render all
       the namespaces.

       To pass a namespace:

       - Using ``Collect``:

         The ``Collect`` component accept a prop named ``namespace``, which default to "default".

         .. code-block:: python

             >>> def render():
             ...     return <body>
             ...         <CSSCollector ref={ref}>
             ...             <CSSCollector.Collect namespace="foo">...</CSSCollector.Collect>
             ...         # ...
             ...         </CSSCollector>
             ...     </body>

       - Using ``render_css`` and ``render_css_global``

         If these methods return a string, it will be collected in the "default" namespace.

         But it can render a dict, the keys being the namespaces to use. The advantage is to be
         able to fill many namespaces at once.

         In the following example, we tell to use the "file" namespace (it's just a string, you
         can use what you want) for the global css, and keep the default namespace for the css
         specific to this instance.

         .. code-block:: python

            >>> class Component(Element):
            ...     class PropTypes:
            ...         color: str
            ...
            ...     @classmethod
            ...     def render_css_global(cls, context):
            ...         return {
            ...            "file": '''
            ... .somecontent { color: red; }
            ...            '''
            ...         }
            ...
            ...     def render_css(self, context):
            ...         if not self.has_prop("color"):
            ...             return
            ...
            ...         return '''
            ... #%(id)s { color: %(color)s; }
            ...         ''' % {'id': self.id, 'color': self.color}
            ...
            ...     def render(self, context):
            ...         return <div id={self.id} class="somecontent">{self.children()}</div>

       And now to render our html and our css, we can pass namespaces to the ``render_collected``
       method:

       .. code-block:: python

           >>> ref = Ref()
           >>> def render():
           ...     return <html>
           ...         <head>
           ...             {lambda: ref.current.render_collected("default")}
           ...         </head>
           ...         <body>
           ...             <CSSCollector ref={ref}>
           ...             # ...
           ...             </CSSCollector>
           ...        </body>
           ...     </html>

           >>> save_to_file(str(render()), 'index.html')

           # here "outside" is an empty (not defined) namespace but it still work
           >>> css = ref.current.render_collected("file", "outside", with_tag=False)
           >>> save_to_file(css, 'index.css')

"""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type, Union, cast

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

                class PropTypes:
                    """PropTypes for the ``Collect`` component of the collector.

                    Attributes
                    ----------
                    namespace : str
                        The namespace of the "sub" collector in which to save the collected content.
                        Default to ``default``.

                    """

                    namespace: str = "default"

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
        self.__collected__: Dict[str, List[AnElement]] = defaultdict(list)
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
                    self.append_collected(
                        self.call_collected_method(method, context, True)
                    )

            if hasattr(child, f"render_{self.KIND}"):
                method = getattr(child, f"render_{self.KIND}")
                if callable(method):
                    self.append_collected(
                        self.call_collected_method(method, context, False)
                    )

        if isinstance(child, self.Collect):
            self.append_collected(child, default_namespace=child.namespace)

    def append_collected(
        self,
        collected: Union[Dict[str, AnElement], AnElement],
        default_namespace: str = "default",
    ) -> None:
        """Add the given `collected` content to the collector.

        Parameters
        ----------
        collected : Union[Dict[str, AnElement], AnElement]
            If it's a dict, the keys are used to save their content to "sub" collectors.
            If not, the `default_namespace` will be used as the name of the "sub" collector where to
            collect.
        default_namespace : str
            The name of the "sub" collector where to save the `collected` content if it is not
            a dict. Default to "default".

        """
        if not isinstance(collected, dict):
            collected = {default_namespace: collected}
        for namespace, collected_for_namespace in collected.items():
            self.__collected__[namespace].append(collected_for_namespace)

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

    def render_collected(self, *namespaces: str) -> str:
        """Render the content of all collected children at once.

        It's done as if all the children of the collected ``Collect`` instances
        were in the same ``Fragment``.

        Parameters
        ----------
        namespaces : Sequence[str]
            The namespaces of the "sub" collectors for which to render the collected content.
            If not set, everything will be rendered.

        Returns
        -------
        str
            All collected content stringified and concatenated.

        """
        str_list: List[AnElement] = []

        if not namespaces:
            namespaces = cast(tuple, self.__collected__.keys())

        for name in namespaces:
            for collected in self.__collected__[name]:
                if isinstance(collected, Base) and not isinstance(collected, RawHtml):
                    for child in collected.__children__:
                        self._render_element_to_list(child, str_list)
                elif isinstance(collected, str):
                    str_list.append(collected)
                else:
                    self._render_element_to_list(collected, str_list)

        return self._str_list_to_string(str_list)

    def render(self, context: OptionalContext) -> Optional[OneOrManyElements]:
        """Return elements to be rendered as html.

        Simply prepend/append ``self.render_collected`` as a callable depending on the
        ``render_position`` prop.

        For the parameters, see ``Element.render``.

        """
        result = [super().render(context)]
        if self.render_position == "before":
            result.insert(0, self.render_collected)
        if self.render_position == "after":
            result.append(self.render_collected)
        return result  # type: ignore


class CSSCollector(Collector):
    """A collector that'll surround collected content in a ``<style>`` tag in ``render_collected``.

    The particularities of ``CSSCollector``:

    - a ``CSSCollector.Collect`` component
    - ``render_css_global`` class methods are collected once
    - ``render_css`` methods are collected for every component
    - the default namespace is "default"

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

    def render_collected(  # type: ignore # pylint: disable=arguments-differ
        self, *namespaces: str, with_tag: bool = True
    ) -> OneOrManyElements:
        """Render the content of all collected children at once.

        Simply put the result of the normal call to ``render_collected`` into a
        ``<style>`` tag.

        Parameters
        ----------
        with_tag : bool
            If ``True`` (the default), the result will be surrounded by a ``<style type=...>`` tag,
            using the ``type`` prop. If ``False``, the collected content will be returned as is.

        For the other parameters, see ``Collector.render_collected``.

        Returns
        -------
        OneOrManyElements
            All collected content stringified and concatenated, maybe surrounded by ``<style>``

        """
        str_collected: str = cast(str, super().render_collected(*namespaces))

        return (  # type: ignore
            Style(type=self.type)(Raw(str_collected)) if with_tag else str_collected
        )


class JSCollector(Collector):
    """A collector that'll surround collected content in a ``<script>`` tag in ``render_collected``.

    The particularities of ``JSCollector``:

    - a ``JSCollector.Collect`` component
    - ``render_js_global`` class methods are collected once
    - ``render_js`` methods are collected for every component
    - the default namespace is "default"

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

    def render_collected(  # type: ignore  # pylint: disable=arguments-differ
        self, *namespaces: str, with_tag: bool = True
    ) -> OneOrManyElements:
        """Render the content of all collected children at once.

        Simply put the result of the normal call to ``render_collected`` into a
        ``<script>`` tag.

        Parameters
        ----------
        with_tag : bool
            If ``True`` (the default), the result will be surrounded by a ``<script type=...>`` tag,
            using the ``type`` prop. If ``False``, the collected content will be returned as is.

        For the other parameters, see ``Collector.render_collected``.

        Returns
        -------
        OneOrManyElements
            All collected content stringified and concatenated, maybe surrounded by ``<style>``

        """
        str_collected: str = cast(str, super().render_collected(*namespaces))

        return (  # type: ignore
            Script(type=self.type)(Raw(str_collected)) if with_tag else str_collected
        )
