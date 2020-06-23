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

       And if we want to generate many html files and be sure the external css file will have
       everything that is needed, we can use the ``reuse`` feature.

       It tells a collector to reuse another collector for some content. By default it's all the
       content, but it can be limited to global or non-global content, and it can also be limited
       to some namespaces only.

       .. code-block:: python

           >>> global_collector = CSSCollector()

           >>> ref = Ref()
           >>> def render(content):
           ...     return <html>
           ...         <head>
           ...             {lambda: ref.current.render_collected("default")}
           ...         </head>
           ...         <body>
           ...             <CSSCollector
           ...               ref={ref}
           ...               reuse={global_collector}
           ...               reuse_global=True  # the default
           ...               reuse_non_global=False
           ...               reuse_namespaces=None  # the default, else can be a list of namespaces
           ...             >
           ...             {content}
           ...             </CSSCollector>
           ...        </body>
           ...     </html>

           # each file will have its own non-global styles
           >>> save_to_file(str(render("page 1")), 'page1.html')
           >>> save_to_file(str(render("page 2")), 'page2.html')

           # we'll have the global styles for every components used on each page
           # useful if one component used on page 2 but not on page 1 for example
           >>> css = global_collector.render_collected(with_tag=False)
           >>> save_to_file(css, 'index.css')

**Note**: you can use ``mixt.contrib.css`` with the CSS collector.
See `Related documentation <contrib-css.html#ContribCss-collector>`_.

"""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type, Union, cast

from mixt.contrib.css import CssDict, get_default_mode, render_css
from mixt.contrib.css.vars import Combine, combine

from ..element import Element
from ..exceptions import InvalidPropValueError, MixtException
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
        reuse : Collector
            Tell the collector to use data from the given collector. Useful to collect from many
            components not in the same tree and extract collected content for all at once.
        reuse_global : bool
            If ``True`` (the default) and if ``reuse`` is set, the globally collected stuff will
            be collected by the reused collector.
        reuse_non_global : bool
            If ``True`` (the default) and if ``reuse`` is set, the non-globally collected stuff
            will be collected by the reused collector.
        reuse_namespaces : Optional[List[str]]
            If not ``None`` (the default), only the given namespaces will be collected by the
            ``reuse``, the other being collected by ``self``.. Else (if ``None``),  all namespaces
            will be collected by ``reuse``.

        """

        render_position: DefaultChoices = cast(
            DefaultChoices, [None, "before", "after"]
        )
        reuse: Any
        reuse_global: bool = True
        reuse_non_global: bool = True
        reuse_namespaces: List[str]

    def __init__(self, **kwargs: Any) -> None:
        """Create the collector with an empty list of collected children..

        ``__collected`` will contain all children of collected children.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The props to set on this collector.

        Raises
        ------
        InvalidPropValueError
            If the ``reuse`` prop if not an instance of the exact same class.

        """
        self.__collected__: Dict[str, List[AnElement]] = defaultdict(list)
        self.__classes_no_methods__: Dict[Type, Set[str]] = defaultdict(set)
        self.__global_methods_done_for_namespaces__: Dict[  # pylint: disable=invalid-name
            str, Set[Callable]
        ] = defaultdict(
            set
        )

        super().__init__(**kwargs)

        reuse = self.prop("reuse", None)
        if reuse and reuse.__class__ is not self.__class__:
            raise InvalidPropValueError(
                self.__display_name__, "reuse", reuse, self.__class__
            )
        # fasten access to reuse* props
        self.reuse: Collector = reuse
        self.reuse_global: bool = self.prop("reuse_global")
        self.reuse_non_global: bool = self.prop("reuse_non_global")
        self.reuse_namespaces: Optional[Set[str]] = None
        if (
            self.has_prop("reuse_namespaces")
            and self.prop("reuse_namespaces") is not None
        ):
            self.reuse_namespaces = set(self.prop("reuse_namespaces"))

    def postrender_child_element(  # pylint: disable=too-many-branches
        self, child: "Element", child_element: AnElement, context: OptionalContext
    ) -> None:
        """Catch child render_{KIND} method, or child content if a ``Collect``.

        If there is KIND:

        - try to collect  the``render_{KIND}_global`` class method if not already done for the child
        's class (it will collect this method for all parents, starting for the higher in the mro:
        do not use ``super`` in this class)
        - try to collect ``render_{KIND}

        Then collect if it's a ``Collect`` instance.

        For the parameters, see ``Element.postrender_child_element``.

        Raises
        ------
        MixtException

            - If the ``render_{KIND}_global`` is not a class method.
            - If the ``render_{KIND}`` is not a method

        """
        if self.KIND:
            no_methods = self.__classes_no_methods__[child.__class__]

            method_name = f"render_{self.KIND}_global"
            if method_name not in no_methods:
                for base in reversed(child.__class__.__mro__):
                    no_methods_base = self.__classes_no_methods__[base]
                    if method_name in no_methods_base:
                        continue
                    if not hasattr(base, method_name):
                        no_methods_base.add(method_name)
                        continue
                    method = getattr(base, method_name)
                    if not hasattr(method, "__func__"):
                        if getattr(base, "__display_name__", None):
                            name = f"<{base.__display_name__}>"  # type: ignore
                        else:
                            name = str(base)
                        raise MixtException(
                            f"{name}.{method_name} must be a classmethod"
                        )
                    self.append_collected(
                        self.call_collected_method(method, context, True),
                        is_global=True,
                        global_method=method.__func__,
                    )

            method_name = f"render_{self.KIND}"
            if method_name not in no_methods:
                if not hasattr(child, method_name):
                    no_methods.add(method_name)
                else:
                    method = getattr(child, method_name)
                    if not callable(method):
                        if getattr(child, "__display_name__", None):
                            name = f"<{child.__display_name__}>"  # type: ignore
                        else:
                            name = str(child)
                        raise MixtException(f"{name}.{method_name} must be a method")
                    self.append_collected(
                        self.call_collected_method(method, context, False),
                        is_global=False,
                    )

        if isinstance(child, self.Collect):
            self.append_collected(
                child, is_global=False, default_namespace=child.namespace
            )

    def append_collected(
        self,
        collected: Union[Dict[str, AnElement], AnElement],
        is_global: bool,
        default_namespace: str = "default",
        global_method: Optional[Callable] = None,
    ) -> None:
        """Add the given `collected` content to the collector.

        Parameters
        ----------
        collected : Union[Dict[str, AnElement], AnElement]
            If it's a dict, the keys are used to save their content to "sub" collectors.
            If not, the `default_namespace` will be used as the name of the "sub" collector where to
            collect.
        is_global : bool
            If the collected data is global one (ie from ``render_{KIND}_global``) or not.
        default_namespace : str
            The name of the "sub" collector where to save the `collected` content if it is not
            a dict. Default to "default".
        global_method : Optional[Callable]
            If ``is_global`` is ``True``, this is the method called to get the content to collect,
            to mark it as already collected.

        """
        if not isinstance(collected, dict) or isinstance(collected, CssDict):
            collected = {default_namespace: collected}

        for namespace, collected_for_namespace in collected.items():
            collector: Collector = self
            if not collected:
                continue

            if self.reuse and (
                self.reuse_namespaces is None or namespace in self.reuse_namespaces
            ):
                if (is_global and self.reuse_global) or (
                    not is_global and self.reuse_non_global
                ):
                    collector = self.reuse

            if is_global and global_method:
                if (
                    global_method
                    in collector.__global_methods_done_for_namespaces__[namespace]
                ):
                    continue

                collector.__global_methods_done_for_namespaces__[namespace].add(
                    global_method
                )

            collector.__collected__[namespace].append(collected_for_namespace)

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

        Will call ``render_one_collected`` for each collected part for the given
        namespaces, then concat the rendered string.

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
        acc: List[AnElement] = []

        if not namespaces:
            namespaces = cast(tuple, self.__collected__.keys())

        for name in namespaces:
            for collected in self.__collected__[name]:
                self.render_one_collected(collected, acc)

        return self.render_accumulated_collected_to_string(acc)

    def render_one_collected(self, collected: AnElement, acc: List) -> None:
        """Convert a collected thing and add it the the `acc` accumulator.

        Parameters
        ----------
        collected : AnElement
            A "thing" that was collected, to convert.
        acc : List
            The accumulator where to store the converted element

        """
        if isinstance(collected, Base) and not isinstance(collected, RawHtml):
            for child in collected.__children__:
                self._render_element_to_list(child, acc)
        elif isinstance(collected, str):
            acc.append(collected)
        else:
            self._render_element_to_list(collected, acc)

    def render_accumulated_collected_to_string(self, acc: List) -> str:
        """Render the colected things accumulated in `acc` to a sting.

        Parameters
        ----------
        acc : List
            The list where the collected things where accumulated.

        Returns
        -------
        str
            The final string to display.

        """
        return self._str_list_to_string(acc)

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

    You can use ``mixt.contrib.css`` with the CSS collector.
    See `Related documentation <contrib-css.html#ContribCss-collector>`_.

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

    def render_one_collected(self, collected: AnElement, acc: List) -> None:
        """Convert a collected thing and add it the the `acc` accumulator.

        For this ``CSSCollector``, manages ``CssDicts`` and ``Combine``.

        For the parameters, see ``Collector.render_one_collected``.
        """
        if isinstance(collected, (CssDict, Combine)):
            acc.append(collected)
        else:
            super().render_one_collected(collected, acc)

    def render_accumulated_collected_to_string(self, acc: List) -> str:
        """Render the accumulated CSS parts to a string.

        All the parts are aggregated in a ``Combine``, that will convert strings to ``Raw``.
        This allow any parts to use "extends" defined previously.

        For the parameters, see ``Collector.render_accumulated_collected_to_string``.

        Returns
        -------
        str
            The final CSS to display.

        """
        final_list: List = []
        for item in acc:
            if isinstance(item, Combine) or not callable(item):
                final_list.append(item)
                continue

            self.render_one_collected(item(), final_list)

        return get_default_mode().value["endline"] + render_css(combine(*final_list))


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
