"""Provide the ``Element`` class to create reusable components."""
from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast

from mixt.exceptions import ElementError

from .html import Fragment
from .internal.base import (
    AnElement,
    Base,
    BaseMetaclass,
    EmptyContext,
    ManyElements,
    OneOrManyElements,
    OptionalContext,
    Props,
    WithClass,
)


class Element(WithClass):
    """Base element for reusable components.

    Examples
    --------
    # In pure python:

    >>> from mixt import Element, Required, html

    >>> class Greeting(Element):
    ...     class PropTypes:
    ...         name: Required[str]
    ...
    ...     def render(self, context):
    ...        return html.Div(
    ...            'Hello, ',
    ...            html.Strong()(self.name)
    ...        )

    >>> print(<Greeting name='World' />)
    <div>Hello, <strong>World</strong></div>

    # In "mixt", aka 'html in python":
    # Notes: "html in python" does not work in a python shell, only in files.
    # And you must import ``html`` from ``mixt`` to use normal html tags.

    >>> #  coding: mixt

    >>> from mixt import Element, Required, html

    >>> class Greeting(Element):
    ...     class PropTypes:
    ...         name: Required[str]
    ...
    ...     def render(self, context):
    ...        return <div>Hello, <strong>{self.name}</strong></div>

    >>> print(<Greeting name='World' />)
    <div>Hello, <strong>World</strong></div>

    # And to show how the ``__tag__`` and ``__display_name__`` attributes are composed by default:
    >>> Greeting.__tag__
    'Greeting'

    >>> Greeting.__display_name__
    'Greeting'

    """

    class PropTypes:
        """Default props for all elements.

        Attributes
        ----------
        id : str
            The id of the element. It will not be passed down the tree like ``_class``.

        Examples
        --------
        >>> class Component(Element):
        ...    def render(self, context):
        ...        return <div id={self.id}>Hello</div>

        >>> print(<Component class="some class" id="FOO" />)
        <div id="FOO" class="some class">Hello</div>

        """

        id: str

    _element: Optional[
        AnElement
    ] = None  # render() output cached by _rendered_element()

    def __repr__(self) -> str:
        """Return a string representation of the element.

        Returns
        -------
        str
            The representation of the element.

        """
        obj_id = self.prop("id", None)
        classes = self.get_class()
        return "<{}{}{}>".format(
            self.__display_name__,
            (' id="{}"'.format(obj_id)) if obj_id else "",
            (' class="{}"'.format(classes)) if classes else "",
        )

    def _get_base_element(self) -> AnElement:
        """Return the element rendered with its children.

        Manage context css classes inheritance by concatening all the classes down to the the first
        html tag.

        Returns
        -------
        Base
            A element ready to be rendered as a string.

        """
        out = self._rendered_element()
        context = self.context
        classes = self.classes

        while isinstance(out, Element):
            out._use_context(context)
            context = out.context
            new_out = out._rendered_element()
            classes = out.classes + classes
            out = new_out

        if classes and isinstance(out, Base):
            classes = out.classes + classes
            out.set_prop(
                "class", " ".join(dict.fromkeys(classes))  # keep ordering in py3.6
            )

        return out

    def get_id(self) -> Union[None, str]:
        """Return the ``id`` prop of the element."""
        return self.prop("id", default=None)

    def children(  # pylint: disable=arguments-differ
        self, selector: Optional[Union[str, Type[Base]]] = None, exclude: bool = False
    ) -> ManyElements:
        """Return the (direct) children, maybe filtered.

        Parameters
        ----------
        selector : Union[str, Type[Base]
            Empty by default. Used to filter the children.

            If it's a string to specify how to filter the children:

            - If it starts with a dot ``.``, we select children having this class.
            - If it starts with a sharp ``#``, we select children having this id.
            - Else we select children having this tag name.

            If it's a class, only instances of this class (or subclass) are returned
        exclude : bool
            ``False`` by default. If ``True``, the result of the selection done by ``selector`` is
            reversed. Ie we select ALL BUT children having this class/id/tag.

        Returns
        -------
        ManyElements
            A List, maybe empty, of all the children, maybe filtered.

        Examples
        --------
        >>> class Details(Element):
        ...    def render(self, context):
        ...        p_element = self.children(html.P)
        ...        other_children = self.children(html.P, exclude=True)
        ...        return <details>
        ...            <summary>{p_element}</summary>
        ...            {other_children}
        ...        </details>

        """
        children = super().children()

        if not selector:
            return children

        if isinstance(selector, str):

            compare_str: str = selector[1:]

            # filter by class
            if selector[0] == ".":
                select = lambda x: isinstance(x, WithClass) and compare_str in x.classes

            # filter by id
            elif selector[0] == "#":
                select = lambda x: hasattr(x, "get_id") and compare_str == x.get_id()

            # filter by tag name
            else:
                select = lambda x: hasattr(x, "__tag__") and selector == x.__tag__

        elif issubclass(selector, Base):
            select = lambda x: isinstance(x, selector)  # type: ignore

        if exclude:
            func = lambda x: not select(x)  # type: ignore
        else:
            func = select

        return list(filter(func, children))

    def _to_list(self, acc: List) -> None:
        """Add the element parts (with its children) to the list `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        self._render_element_to_list(self._get_base_element(), acc)

    def _rendered_element(self) -> AnElement:
        """Call ``prerender``, ``render`` then ``postrender`` and return the rendered element.

        If ``render`` returns many elements, they are grouped in a ``Fragment``.

        Returns
        -------
        Union[str, Base]
            The rendered element. Can be a string, an Element, a RawHtml...

        """
        if self._element is None:
            context = self.context or EmptyContext

            self.prerender(context)

            element: Optional[OneOrManyElements] = self.render(context)

            if isinstance(element, (list, tuple)):
                element = Fragment()(element)  # type: ignore

            self._element = element  # type: ignore

            if isinstance(self._element, Base):
                self._element._attach_to_parent(self)

            self.postrender(self._element, context)  # type: ignore

            parent = self.__parent__
            while parent:
                if isinstance(parent, Element):
                    parent.postrender_child_element(
                        self, self._element, context  # type: ignore
                    )
                parent = parent.__parent__

        return self._element  # type: ignore

    def render(  # noqa: B950  # pylint: disable=unused-argument
        self, context: OptionalContext
    ) -> Optional[OneOrManyElements]:
        """Return elements to be rendered as html.

        Returns only all children (``self.children()``) by default.

        Must be implemented in subclasses to do something else.

        Must return a component, a list of components, a fragment, or False/None. See example for
        more details.

        Parameters
        ----------
        context : OptionalContext
            The context passed through the tree.

        Returns
        -------
        Optional[OneOrManyElements]
            None, or one or many elements or strings.

        Examples
        --------
        # It can return a single element (a normal html tag or another component),
        # which can have children:
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: Required[str]
        ...
        ...     def render(self, context):
        ...         return <div>Hello, <strong>{self.name}</strong>{self.children()}</div>

        >>> print(<Greeting name="John">, you look great today!</Greeting>)
        <div>Hello, <strong>John</strong>, you look great today!</div>

        # It can return many nodes, using ``<Fragment>``:
        >>>     def render(self, context):
        ...         return <Fragment>
        ...             <div>Foo</div>
        ...             <div>Bar</div>
        ...         </Fragment>
        <div>Foo</div><div>Bar</div>

        # It can return many nodes, using an iterable (note the commas after each entry). The
        # main purpose is to be able to compose the list before calling ``return``:
        >>>     def render(self, context):
        ...         return [
        ...             <div>Foo</div>,
        ...             <div>Bar</div>,
        ...         ]
        <div>Foo</div><div>Bar</div>

        # It can return a simple string:
        >>>     def render(self, context):
        ...         return "Foo Bar"
        Foo Bar

        # And a list of strings:
        >>>     def render(self, context):
        ...         return ["Foo", "Bar"]
        FooBar

        # ``False`` and ``None`` are ignored:
        >>>     def render(self, context):
        ...         return [
        ...             False,
        ...             <div>Foo</div>,
        ...             None,
        ...             <div>Bar</div>,
        ...         ]
        <div>Foo</div><div>Bar</div>

        # All of these rules can be mized up.
        # Note how lists can be used not only at the first level:
        >>>     def render(self, context):
        ...         return [
        ...             False,
        ...             [
        ...                 <div>Foo</div>,
        ...                 <div>Bar</div>,
        ...             ],
        ...             None,
        ...             "Baz"
        ...         ]
        <div>Foo</div><div>Bar</div>Baz

        """
        return self.children()

    def prerender(self, context: OptionalContext) -> None:
        """Provide a hook to do things before the element is rendered.

        Default behavior is to do nothing.

        Parameters
        ----------
        context : OptionalContext
            The context passed through the tree.

        Examples
        --------
        >>> class Component(Element):
        ...     def prerender(self, context):
        ...         self.started_at = datetime.utcnow()
        ...         print(f"Rendering <{self.__display_name__}>...")
        ...     def postrender(self, element, context):
        ...         duration = datetime.utcnow() - self.started_at
        ...         print(f"Rendered <{self.__display_name__}> in {duration}")

        """

    def postrender(self, element: AnElement, context: OptionalContext) -> None:
        """Provide a hook to do things after the element is rendered.

        Default behavior is to do nothing. See ``prerender`` for an example.

        Parameters
        ----------
        element : AnElement
            The element rendered by ``render``. Could be an Element, an html tag, a RawHtml...
        context : OptionalContext
            The context passed through the tree.

        """

    def postrender_child_element(
        self, child: "Element", child_element: AnElement, context: OptionalContext
    ) -> None:
        """Provide a hook for every parent to do things after any child is rendered.

        Default behavior is to do nothing. Useful to collect stuff for delayed rendering (see
        ``CSSCollector`` and ``JSCollector``), stats...

        Parameters
        ----------
        child : Element
            The element in a tree on which ``render`` was just called.
        child_element : AnElement
            The element rendered by the call of the ``render`` method of `child`.
        context : OptionalContext
            The context passed through the tree.

        Examples
        --------
        >>> class ComponentCounter(Element):
        ...     def __init__(self, **kwargs):
        ...         self.count = defaultdict(int)
        ...         super().__init__(**kwargs)
        ...
        ...     def postrender_child_element(self, child, child_element, context):
        ...         self.count[child.__class__.__name__] += 1

        >>> counter = Ref()
        >>> print(
        ...     <ComponentCounter ref={counter}>
        ...         <div>
        ...             Rendered:
        ...             {lambda: str(dict(counter.current.count))}
        ...         </div>
        ...         <Greeting name='World'/>
        ...         <Greeting name='John'/>
        ...     </ComponentCounter>
        ... )
        <div>Rendered: {'Greeting': 2}</div><div>Hello, <strong>World</strong></div><div>Hello,
        <strong>John</strong></div>

        """

    def props_for(self, component: Type["Base"]) -> Props:
        """Get the props defined for the given component.

        Used when using ``ElementProxy`` to get the props of the proxied and the base.

        Parameters
        ----------
        component : Type[Base]
            The component for which we want to restrict the props

        Returns
        -------
        Props
            The dict of properties limited to the one of the given component.

        Examples
        --------
        >>> class Component(ElementProxy):
        ...     class PropTypes:
        ...         val: int
        >>> ComponentForCanvas = Component.For(html.Canvas)
        >>> obj = ComponentForCanvas(val=3, height=300)
        >>> obj.props
        {'val': 3, 'height': 300}
        >>> obj.props_for(html.Canvas)
        {'height': 300}
        >>> obj.props_for(Component)
        {'val': 3}

        Raises
        ------
        ElementError
            If the component is not an Element or an HtmlElement

        """
        if not isinstance(component, type) or not issubclass(component, Base):
            raise ElementError(
                self.__display_name__,
                ".props_for: the argument must be a subclass of `Base`",
            )

        return {
            name: value
            for name, value in self.props.items()
            if name in component.PropTypes.__types__
        }


class ElementProxyMetaclass(BaseMetaclass):
    """Metaclass of the ``ElementProxy`` class to manage base proxy."""

    def __new__(
        mcs, name: str, parents: Tuple[type, ...], attrs: Dict[str, Any]  # noqa: B902
    ) -> "ElementProxyMetaclass":
        """Create a new ElementProxy subclass, with an intermediate "base proxy" if needed.

        Parameters
        ----------
        mcs: type
            The metaclass
        name : str
            The name of the class to construct.
        parents : Sequence[type]
            A tuple with the direct parent classes of the class to construct.
        attrs : Dict[str, Any]
            Dict with the attributes defined in the class.

        Returns
        -------
        Type[ElementProxy]
            The newly created ElementProxy subclass

        Raises
        ------
        ElementError
            If `parents` contain more than one class based on ``ElementProxy``.

        """
        attrs["__proxied_classes__"] = {}
        if "proxied" not in attrs:
            attrs["proxied"] = None

        try:
            proxies = [klass for klass in parents if issubclass(klass, ElementProxy)]
        except NameError:
            # we are creating the ElementProxy class
            pass
        else:
            # only one ElementProxy in parents
            if len(proxies) > 1:
                raise ElementError(
                    "ElementProxy", " can only be present once in the inheritance tree"
                )

            proxy_parent = cast(ElementProxy, proxies[0])
            if proxy_parent.__proxy_base__ != proxy_parent:
                # the proxy parent is `proxy_parent.For(proxied)`
                # so we create a class using __proxy_base__ instead of the parent
                base_parents = tuple(
                    proxy_parent.__proxy_base__ if parent is proxy_parent else parent
                    for parent in parents
                )
                new_base = cast(Type["ElementProxy"], mcs(name, base_parents, attrs))
                # and we return a new class for this proxied
                return new_base._For(proxy_parent.proxied, is_source=True)

        cls = cast(Type["ElementProxy"], super().__new__(mcs, name, parents, attrs))

        if not attrs.get("__proxy_base__"):
            cls.__proxy_base__ = cls
        return cls


class ElementProxy(Element, metaclass=ElementProxyMetaclass):
    """A subclass of ``Element`` that is a proxy to another.

    Attributes
    ----------
    proxied : Type[Base]
        The proxied component to be used in ``render``. It's the one passed to the ``For``
        method.

    Examples
    --------
    # You can define a proxy for an html element. Using `ElementProxy.For` allows to have
    # a default proxied element. Without `.For`, the new proxy will need to be called later
    # with `.For`.

    >>> class Button(ElementProxy.For(html.Button)):
    ...     class PropTypes:
    ...         label: str = 'button'
    ...     def render(self, context):
    ...         # we pass the the proxied element its own props
    ...         return self.proxied(**self.proxied_props)(
    ...             html.Span()(self.label)
    ...         )

    # The "props" value is for the button element.
    >>> str(Button(value=1)) == '<button value="1"><span>button</span></button>'

    # To change the proxied element, use `For`:
    >>> str(Button.For(html.Div)("ok")) == '<div><span>ok</span></div>'

    """

    proxied: Type[Base]
    __proxy_base__: Type["ElementProxy "]
    __proxied_classes__: Dict[Type[Base], Type["ElementProxy"]] = {}
    __not_an_html_tag__: bool = True

    @classmethod
    def For(cls, component: Type[Base]) -> Type["ElementProxy"]:
        """Return a new version of this proxy, for the given element to proxy.

        Parameters
        ----------
        component : Type[Base]
            The element be be proxied

        Returns
        -------
        Type[ElementProxy]
            A new version of this proxy

        """
        return cls._For(component, is_source=False)

    @classmethod
    def _For(cls, component: Type[Base], is_source: bool) -> Type["ElementProxy"]:
        """Return a new version of this proxy, for the given element to proxy.

        Parameters
        ----------
        component : Type[Base]
            The element be be proxied
        is_source : bool
            If ``True``, the name will be the name of the proxy base, because this proxy base
            class was created by inheriting from a call to `For` of another proxy.
            If ``False``, it's for all other cases, and we compose the new name based on the
            current proxy base and the given component.

        Returns
        -------
        Type[ElementProxy]
            A new version of this proxy

        Raises
        ------
        ElementError
            If the `component` is not a subclass of ``Base``

        """
        if not isinstance(component, type) or not issubclass(component, Base):
            raise ElementError(
                cls.__display_name__, ".For: the argument must be a subclass of `Base`"
            )

        if component not in cls.__proxy_base__.__proxied_classes__:

            if is_source:
                name = cls.__proxy_base__.__tag__
            else:
                name = (
                    f"{cls.__proxy_base__.__tag__}"
                    "For"
                    f"{component.__tag__[0].upper()}{component.__tag__[1:]}"
                )

            cls.__proxy_base__.__proxied_classes__[component] = cast(
                Type[ElementProxy],
                ElementProxyMetaclass(
                    name,
                    (cls.__proxy_base__,),
                    {
                        "__proxy_base__": cls.__proxy_base__,
                        "PropTypes": type(
                            "PropTypes",
                            (component.PropTypes, cls.__proxy_base__.PropTypes),
                            {},
                        ),
                        "proxied": component,
                        "__tag__": name,
                        "__display_name__": name,
                    },
                ),
            )

        return cls.__proxy_base__.__proxied_classes__[component]

    def __init__(self, **kwargs: Any) -> None:
        """Check that an ``ElementProxy`` can only be used if it actually proxy something.

        For the parameters, see ``Element.__init__``.

        """
        if not self.proxied:
            raise ElementError(
                self.__display_name__,
                f" has nothing to proxy. `{self.__class__.__name__}.For(...)` must be used",
            )
        super().__init__(**kwargs)

    @property
    def declared_props(self) -> Props:
        """Get the props that are declared in ``PropTypes`` (no ``data_*`` and ``aria_*``).

        Returns
        -------
        Props
            The props limited to the ones declared in ``PropTypes``.

        """
        return dict(self.own_props, **self.props_for(self.proxied))

    @property
    def proxied_props(self) -> Props:
        """Get the props for the proxied element (with ``data_*`` and ``aria_*``).

        Returns
        -------
        Props
            The props limited to the ones for the proxied element and non declared ones.

        Examples
        --------
        >>> class Component(ElementProxy):
        ...     class PropTypes:
        ...         val: int
        >>> ComponentForCanvas = Component.For(html.Canvas)
        >>> obj = ComponentForCanvas(val=3, height=300, data_foo=1)
        >>> obj.props
        {'val': 3, 'height': 300, 'data_foo': 1}
        >>> obj.proxied_props
        {'height': 300, data_foo: 1}

        """
        return dict(self.props_for(self.proxied), **self.non_declared_props)

    @property
    def own_props(self) -> Props:
        """Get the props for the base proxy element (no ``data_*`` and ``aria_*``).

        Returns
        -------
        Props
            The props limited to the ones for the base proxy element.

        Examples
        --------
        >>> class Component(ElementProxy):
        ...     class PropTypes:
        ...         val: int
        >>> ComponentForCanvas = Component.For(html.Canvas)
        >>> obj = ComponentForCanvas(val=3, height=300, data_foo: 1)
        >>> obj.props
        {'val': 3, 'height': 300, data_foo: 1}
        >>> obj.own_props
        {'val': 3}

        """
        return self.props_for(self.__proxy_base__)
