"""Provide the ``Element`` class to create reusable components."""

from typing import List, Optional, Type, Union

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

    >>> # coding: mixt

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
                select = lambda x: hasattr(x, 'get_id') and compare_str == x.get_id()

            # filter by tag name
            else:
                select = lambda x: hasattr(x, '__tag__') and selector == x.__tag__

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

            element: Optional[OneOrManyElements] = self.render(
                self.context or EmptyContext
            )

            if isinstance(element, (list, tuple)):
                element = Fragment()(element)  # type: ignore

            self._element = element  # type: ignore

            if isinstance(self._element, Base):
                self._element._attach_to_parent(self)
                self._element._set_context(
                    self.context  # pass None if context not defined, not EmptyContext
                )

            self.postrender(self._element, context)  # type: ignore

            parent = self.__parent__
            while parent:
                if isinstance(parent, Element):
                    parent.postrender_child_element(  # type: ignore
                        self, self._element, context
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
        pass

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
        pass

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
        pass
