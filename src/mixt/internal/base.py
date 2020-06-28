"""Base class to handle html tags and custom elements."""

from itertools import chain
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Union, cast
from xml.sax.saxutils import escape as xml_escape, unescape as xml_unescape

from ..exceptions import InvalidPropNameError, UnsetPropError
from ..proptypes import NotProvided
from .proptypes import BasePropTypes


# pylint: disable=invalid-name
OptionalContext = Union["BaseContext", None]
AnElement = Union["Base", str, Callable]
ManyElements = List[AnElement]
OneOrManyElements = Union[AnElement, List[AnElement]]
Props = Dict[str, Any]
# pylint: enable=invalid-name

IGNORED_CHILDREN = [None, False]  # cannot use a Set because elements are not hashable


ESCAPE_CHARS = {'"': "&quot;"}
UNESCAPE_CHARS = {"&quot;": '"'}


def escape(obj: Any) -> str:
    """Escape xml entities.

    Parameters
    ----------
    obj : Any
        Can be anything that will be converted to string, then where xml entities will be escaped.

    Returns
    -------
    str
        The escaped string version of `obj`.

    """
    return xml_escape(str(obj), ESCAPE_CHARS)


def unescape(obj: Any) -> str:
    """Unescape xml entities.

    Parameters
    ----------
    obj : Any
        Can be anything that will be converted to string, then where xml entities will be unescaped.

    Returns
    -------
    str
        The unescaped string version of `obj`.

    """
    return xml_unescape(str(obj), UNESCAPE_CHARS)


class BaseMetaclass(type):
    """Metaclass of the ``Base`` class to manage tag name and prop types."""

    def __init__(
        cls, name: str, parents: Sequence[type], attrs: Dict[str, Any]  # noqa: B902
    ) -> None:
        """Construct the class, save its tag and combine prop types with parents.

        Parameters
        ----------
        name : str
            The name of the class to construct.
        parents : Sequence[type]
            A tuple with the direct parent classes of the class to construct.
        attrs : Dict[str, Any]
            Dict with the attributes defined in the class.

        """
        super().__init__(name, parents, attrs)  # type: ignore

        tag = attrs.get("__tag__") or name
        cls.__tag__ = tag
        display_name = attrs.get("__display_name__") or tag
        cls.__display_name__ = display_name

        proptypes_classes = []
        exclude: Set[str] = set()

        proptypes_doc = None
        if "PropTypes" in attrs:
            proptypes_classes.append(attrs["PropTypes"])
            exclude = getattr(attrs["PropTypes"], "__exclude__", exclude)
            proptypes_doc = getattr(attrs["PropTypes"], "__doc__", None)

        proptypes_classes.extend(
            [
                parent.PropTypes  # type: ignore
                for parent in parents
                if hasattr(parent, "PropTypes")
            ]
        )

        class PropTypes(*proptypes_classes):  # type: ignore
            __owner_name__: str = display_name
            __types__: Dict[str, Any] = {}
            __required_props__: Set[str] = set()
            __default_props__: Dict[str, Any] = {}
            __excluded_props__: Set[str] = exclude.union(
                *[
                    getattr(klass, "__excluded_props__", [])
                    for klass in proptypes_classes
                ]
            )

        if proptypes_doc:
            PropTypes.__doc__ = proptypes_doc

        PropTypes.__validate_types__()

        cls.PropTypes = PropTypes


class Ref:
    """An object storing the reference to an element.

    The goal is to use it later, once the element is rendered. For example by "collectors", like
    the first example below (or ``CSSCollector`` and ``JSCollector``).

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

    # Here we use the ref to display data from the referenced component, once it is rendered.
    # Without this, it would not be possible. Also note the ``lambda``: this is mandatory
    # because without it, we would not have the finalized data.

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

    # Another example, using a ref inside the ``render`` method to, for example,
    # access it in ``postrender``.
    # Using ``ref = self.add_ref()`` in an element is the same as using ``ref = Ref()``.

    >>> class Greeting(Element):
    ...     class PropTypes:
    ...         name: Required[str]
    ...
    ...     def render(self, context):
    ...         self.strong_ref = self.add_ref()
    ...         return <div>Hello, <strong ref={self.strong_ref}>{self.name}</strong></div>
    ...
    ...     def postrender(self, element, context):
    ...         self.strong_ref.current.add_class('very-strong')

    >>> print(<Greeting name="John"></Greeting>)
    <div>Hello, <strong class="very-strong">John</strong></div>

    """

    __element__: Optional["Base"] = None

    @property
    def current(self) -> Optional["Base"]:
        """Get the actual value of this ref.

        Returns
        -------
        Optional["Base"]
            If the ref was set, return the saved value, else ``None``.

        """
        return self.__element__

    def _set(self, element: "Base") -> None:
        """Set the given `element` as the ref value.

        Parameters
        ----------
        element : Base
            The new element to save in this ref.

        """
        self.__element__ = element


class Base(metaclass=BaseMetaclass):
    """The base of all elements. Manage PropTypes, props, context and children.

    Attributes
    ----------
    __tag__ : str
        The tag to use when using the element in "html". If not set in the class, it will be, by
        default, the name of the class itself.

    __display_name__ : str
        A "human" representation of ``__tag__``. Will be used in exceptions and can be changed to
        give more information.

    """

    __tag__: str = ""
    __display_name__: str = ""

    class PropTypes(BasePropTypes):
        """Props used in every mixt elements/components...

        Attributes
        ----------
        ref : Ref
            A reference to the element itself that can be used later. See ``Ref`` for more
            information.

        """

        ref: Ref

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns
        -------
        str
            The representation of the object.

        """
        return "<{}>".format(self.__display_name__)

    def __init__(self, **kwargs: Any) -> None:
        """Create the element and validate then save props.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The props to set on this element.

        """
        self.__props__: Props = {}
        self.__children__: ManyElements = []
        self.__parent__: Optional["Base"] = None
        self.context: OptionalContext = None
        self._context_merged: bool = False

        ref = kwargs.pop("ref", None)
        if ref and ref is not NotProvided:
            ref._set(self)

        for name, value in kwargs.items():
            self.set_prop(name, value)

        self.PropTypes.__validate_required__(self.__props__)

    def add_ref(self) -> Ref:
        """Create and return a new ``Ref`` object.

        Returns
        -------
        Ref
            The ref, without value, ready to be set.

        Examples
        --------
        # This:
        >>> class Component(Element):
        ...     def render(self, context):
        ...         some_ref = self.add_ref()

        # Is exactly the same as:
        >>> from mixt import Ref
        >>> class Component(Element):
        ...     def render(self, context):
        ...         some_ref = Ref()

        # It will simply avoid an import.

        # See ``Ref`` documentation to know more about refs.

        """
        return Ref()

    def __call__(self, *children: AnElement) -> "Base":
        """Add the given `children` to the current element.

        Parameters
        ----------
        children : OneOrManyElements
            List of children to add.

        Returns
        -------
        self
            The current object is returned so it can be chained.

        Examples
        --------
        >>> MyElement(prop=value)(
        ...     html.Div(_class="foo")(  # the div is the only child
        ...         html.Span(_class="bar"),  # the div a two spans as children
        ...         html.Span(_class="baz"),  # and both spans doesn't have any children
        ...     )
        ... )

        """
        self.append(cast(OneOrManyElements, children))
        return self

    def children(self) -> ManyElements:
        """Return all the children of the current element.

        Returns
        -------
        ManyElements
            All the children.

        """
        return self.__children__

    def _attach_children(self, children: ManyElements) -> None:
        """Attach the given `children` to the current element.

        It will set the current element as their parent, and propagate the context.

        Parameters
        ----------
        children : ManyElements
            The children to attach. Nothing is done for strings children.

        """
        for child in children:
            if isinstance(child, Base):
                child._attach_to_parent(self)

    def _attach_to_parent(self, parent: "Base") -> None:
        """Save the given `parent` as the parent of the current element.

        Parameters
        ----------
        parent : Base
            The element that will be saved as the parent of the current element.

        """
        self.__parent__ = parent

    def _child_to_children(self, child_or_children: OneOrManyElements) -> ManyElements:
        """Make a flat list of children from the given one(s).

        Parameters
        ----------
        child_or_children : OneOrManyElements
            This can be a single child, or a list of children,
            each one possibly being also a list, etc...
            Every children that is ``None`` or ``False`` is ignored.
            A fragment is converted to a list of its children.

        Returns
        -------
        ManyElements
            The flattened list of children.

        """
        if isinstance(child_or_children, Fragment):
            child_or_children = child_or_children.__children__

        if isinstance(child_or_children, (list, tuple)):
            children = list(
                chain.from_iterable(
                    self._child_to_children(c)
                    for c in child_or_children
                    if c not in IGNORED_CHILDREN
                )
            )
        elif child_or_children not in IGNORED_CHILDREN:
            children = [cast(AnElement, child_or_children)]
        else:
            return []
        return children

    def append(self, child_or_children: OneOrManyElements) -> None:
        """Append some children to the current element.

        In the process, we propagate the actual context to the children.

        Parameters
        ----------
        child_or_children : OneOrManyElements
            The child(ren) to add.

        Examples
        --------
        >>> class AddNote(Element):
        ...     class PropTypes:
        ...         note: Required[str]
        ...     def prerender(self, context):
        ...         self.append(<aside class="note">Note: {self.note}</aside>)

        >>> print(<div><AddNote note="you're welcome"><p>Hello, John</p></AddNote></div>)
        <div><p>Hello, John</p><aside class="note">Note: you're welcome</aside></div>

        """
        children = self._child_to_children(child_or_children)
        self._attach_children(children)
        self.__children__.extend(children)

    def prepend(self, child_or_children: OneOrManyElements) -> None:
        """Prepend some children to the current element.

        In the process, we propagate the actual context to the children.

        Parameters
        ----------
        child_or_children : OneOrManyElements
            The child(ren) to add.

        Examples
        --------
        >>> class Title(Element):
        ...     class PropTypes:
        ...         text: Required[str]
        ...         level: Required[int]
        ...     def prerender(self, context):
        ...         self.prepend(<h level={self.level}>{self.text}</h>)

        >>> print(<Title text="Welcome" level=1><p>Hello, John</p></Title>)
        <h1>Welcome</h1><p>Hello, John</p>

        """
        children = self._child_to_children(child_or_children)
        self._attach_children(children)
        self.__children__[0:0] = children

    def remove(self, child_or_children: OneOrManyElements) -> None:
        """Remove some children from the current element.

        Parameters
        ----------
        child_or_children : OneOrManyElements
            The child(ren) to remove.

        Examples
        --------
        >>> class NoHr(Element):
        ...     def prerender(self, context):
        ...     self.remove(self.children(html.Hr))

        >>> print(<NoHr><p>Foo</p><hr /><p>Bar</p><hr /><p>Baz</p></NoHr>)
        <p>Foo</p><p>Bar</p><p>Baz</p>

        """
        children_to_remove = self._child_to_children(child_or_children)
        new_children = []
        for child in self.__children__:
            if child in children_to_remove:
                if isinstance(child, Base):
                    child.__parent__ = None
                continue
            new_children.append(child)
        self.__children__[:] = new_children

    def __getattr__(self, name: str) -> Any:
        """Return a prop defined by `name`, if it is defined.

        If the prop exists but is not set and the prop has a default value, this default value is
        returned.

        It the same as calling ``self.prop(name)``, except that it always raise an
        ``AttributeError`` for all failures.

        Parameters
        ----------
        name : str
            The name of the wanted prop.

        Returns
        -------
        Any
            The actual value of the prop or its default value.

        Raises
        ------
        AttributeError
            If the prop does not exist and is a dunder attribute ("__xxx__")
        InvalidPropNameError
            If there is no prop with the given `name`.
        UnsetPropError
            If the prop is not set and no default value is available.

        """
        if len(name) > 4 and name.startswith("__") and name.endswith("__"):
            # For dunder name (e.g. __iter__),raise AttributeError, not MixtException.
            raise AttributeError(name)

        return self.prop(name)

    @classmethod
    def prop_name(cls, name: str) -> str:
        """Return the corrected name for the prop defined by `name`, if the prop exists.

        For example, if `name` is "class", it will return "_class". If "data-foo", it will
        return "data_foo".

        Parameters
        ----------
        name : str
            The name we want to validate.

        Returns
        -------
        str
            The real name of the given prop.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        Examples
        --------
        >>> class Component(Element):
        ...     class PropTypes:
        ...         some_name: str

        >>> Component.prop_name('some-name')
        'some_name'
        >>> Component.prop_name('class')
        '_class'

        """
        name = BasePropTypes.__to_python__(name)
        if not cls.PropTypes.__allow__(name):
            raise InvalidPropNameError(cls.__display_name__, name)
        return name

    def prop(self, name: str, default: Any = NotProvided) -> Any:
        """Return a prop defined by `name`, if it is defined, or the `default` if provided.

        If the prop exists but is not set, `default` is not provided, and the prop has a default
        value, this default value is returned.

        Calling ``el.prop("name")`` is the same as calling ``el.name``.

        Parameters
        ----------
        name : str
            The name of the wanted prop.
        default : Any
            The value to return if the prop is not set. If ``NotProvided``, the default value set
            in PropTypes is used. Else we raise.

        Returns
        -------
        Any
            The value of the prop or a default one.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.
        UnsetPropError
            If the prop is not set and no default value is available.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> <Greeting />.prop("name")
        'World'
        >>> <Greeting />.name
        'World'

        >>> <Greeting />.prop("surname")
        Traceback (most recent call last):
        ...
        mixt.exceptions.UnsetPropError: <Greeting>.surname: prop is not set

        >>> <Greeting />.surname
        Traceback (most recent call last):
        ...
        mixt.exceptions.UnsetPropError: <Greeting>.surname: prop is not set

        >>> <Greeting />.prop("surname", "J")
        'J'
        >>> <Greeting surname="JJ"/>.prop("surname")
        'JJ'
        >>> <Greeting name="John"/>.prop("name")
        'John'

        >>> <Greeting />.prop("firstname")
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        >>> <Greeting />.firstname
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        """
        name = self.prop_name(name)

        # First we try to get the actual prop value
        value = self.__props__.get(name, NotProvided)
        if value is not NotProvided:
            return value

        # Then if a default is provided, use it
        if default is not NotProvided:
            return default

        # Else, use the default set in PropTypes
        prop_default = self.PropTypes.__default__(name)
        if prop_default is not NotProvided:
            return prop_default

        # Finally, no value is available, we raise
        raise UnsetPropError(self.__display_name__, name)

    def has_prop(self, name: str, allow_invalid: bool = True) -> bool:
        """Tell if the prop defined by `name` is defined (or has a default value.

        Parameters
        ----------
        name : str
            The name of the prop to check.
        allow_invalid : bool
            If set to ``True``, it will return ``False`` if the `name` if for a prop that is
            not allowed. Else if will raise ``InvalidPropNameError``.

        Returns
        -------
        bool
            ``True`` if the prop is defined, ``False`` otherwise.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name` and `allow_invalid` is False.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> <Greeting />.has_prop("name")
        True
        >>> <Greeting />.has_prop("surname")
        False
        >>> <Greeting surname="J"/>.has_prop("surname")
        True
        >>> <Greeting name="John"/>.has_prop("name")
        True

        >>> <Greeting />.has_prop("firstname")
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        >>> <Greeting />.has_prop("firstname", allow_invalid=True)
        False

        """
        try:
            self.prop(name)
        except InvalidPropNameError:
            if allow_invalid:
                return False
            raise
        except UnsetPropError:
            return False
        return True

    def set_prop(self, name: str, value: Any) -> Any:
        """Set the `value` of the prop defined by `name`, if it is valid.

        The value is validated only if not in dev-mode. But still converted if needed, like for
        booleans.
        If `value` is ``NotProvided``, the prop is unset.

        Parameters
        ----------
        name : str
            The name of the prop to set.
        value : Any
            The value to set to the prop.
            If set to ``NotProvided``, this will unset the actual set value for this prop.

        Returns
        -------
        Any
            If `value` is not ``NotProvided`` returns the value that is really set. It may have been
            changed by the validation process.
            If `value` is ``NotProvided``, returns the value that was stored in the prop before
            deleting it.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.
        InvalidPropValueError
            If the value is not valid.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> el = <Greeting />
        >>> el.set_prop("name", "John")
        >>> el.name
        'John'

        >>> el.set_prop("name", {"first": "John"})
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropValueError: <Greeting>.name: `{'first': 'John'}` is not a
        valid value for this prop (type: <class 'dict'>, expected: <class 'str'>)

        >>> el.set_prop("firstname", "John")
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        """
        name = self.prop_name(name)

        if value is NotProvided:
            return self.__props__.pop(name, NotProvided)

        self.__props__[name] = self.PropTypes.__validate__(name, value)
        return self.__props__[name]

    def unset_prop(self, name: str) -> Any:
        """Unset the actual value of the prop defined by `name`.

        Parameters
        ----------
        name : str
            The name of the prop to unset.

        Returns
        -------
        Any
            The value that was stored in the prop before deleting it.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> el = <Greeting />
        >>> el.set_prop("name", "John")
        >>> el.name
        'John'

        >>> el.unset_prop("name")
        >>> el.name
        'World'

        >>> el.set_prop("surname", "JJ")
        >>> el.surname
        'JJ'

        >>> el.unset_prop("surname")
        >>> el.surnname
        Traceback (most recent call last):
        ...
        mixt.exceptions.UnsetPropError: <Greeting>.surname: prop is not set

        >>> el.unset_prop("firstname")
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        """
        return self.set_prop(name, value=NotProvided)

    def prop_default(self, name: str) -> Any:
        """Return the default value of the prop defined by `name`.

        Parameters
        ----------
        name : str
            The name of the prop for which we want the default value

        Returns
        -------
        Any
            The default value defined in ``PropTypes`` or ``NotProvided`` if not set.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> <Greeting />.prop_default("name")
        'World'

        >>> <Greeting />.prop_default("surname")
        <class 'mixt.proptypes.NotProvided'>

        >>> <Greeting />.prop_default("firstname")
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        """
        return self.PropTypes.__default__(self.prop_name(name))

    def is_prop_default(self, name: str, value: Any = NotProvided) -> bool:
        """Tell if the actual (or given) value for the prop defined by `name` is the default one.

        Parameters
        ----------
        name : str
            The name of the prop we are asking for.
        value : Any
            If set, will use this value to check if it is the default one. Else (if
            ``NotProvided``), it will use the actual prop.

        Returns
        -------
        bool
            ``True`` if the given value or the prop value is the default one, ``False`` otherwise.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> <Greeting />.is_prop_default("name", "John")
        False
        >>> <Greeting />.is_prop_default("name", "World")
        True
        >>> <Greeting />.is_prop_default("name")
        True

        >>> <Greeting name="John"/>.is_prop_default("name", "World")
        True
        >>> <Greeting name="John"/>.is_prop_default("name", "John")
        False
        >>> <Greeting name="John"/>.is_prop_default("name")
        False

        >>> <Greeting />.is_prop_default("surname")
        Traceback (most recent call last):
        ...
        mixt.exceptions.UnsetPropError: <Greeting>.surname: prop is not set

        >>> <Greeting />.is_prop_default("surname", "JJ")
        False
        >>> <Greeting surname="JJ" />.is_prop_default("surname")
        False

        """
        name = self.prop_name(name)

        if value is NotProvided:
            value = self.prop(name)

        return value == self.prop_default(name)

    @classmethod
    def prop_type(cls, name: str) -> Any:
        """Return the type of the prop defined by `name`.

        Parameters
        ----------
        name : str
            The name of the prop we want the type

        Returns
        -------
        Any
            The type, coming from ``PropTypes``

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> Greeting.prop_type("name")
        <class 'str'>
        >>> Greeting.prop_type("surname")
        <class 'str'>
        >>> Greeting.prop_type("firstname")
        Traceback (most recent call last):
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        """
        return cls.PropTypes.__type__(cls.prop_name(name))

    @classmethod
    def is_prop_required(cls, name: str) -> bool:
        """Tell if the prop defined by `name` is a required one.

        Parameters
        ----------
        name : str
            The name of the prop we want to know if it is required.

        Returns
        -------
        bool
            ``True`` if the prop is required, ``False`` otherwise.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: Required[str]

        >>> Greeting.is_prop_required("name")
        False
        >>> Greeting.is_prop_required("surname")
        True
        >>> Greeting.is_prop_required("firstname")
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        """
        return cls.PropTypes.__is_required__(cls.prop_name(name))

    @property
    def props(self) -> Props:
        """Get all the available and set props, including default ones.

        Returns
        -------
        Props
            A dict with each defined props. If a prop is not set but has a default value, this one
            is used.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> <Greeting />.props)
        {'name': 'World'}

        >>> <Greeting name="John" surname="JJ"/>.props)
        {'name': 'John', 'surname': 'JJ'}

        """
        return dict(self.PropTypes.__default_props__, **self.__props__)

    @property
    def declared_props(self) -> Props:
        """Get the props that are declared in ``PropTypes`` (no ``data_*`` and ``aria_*``).

        Returns
        -------
        Props
            The props limited to the ones declared in ``PropTypes``.

        Examples
        --------
        >>> class Component(Element):
        ...     class PropTypes:
        ...         val: int
        >>> obj = Component(val=3, data_foo="bar", aria_disabled="true")
        >>> obj.props
        {'val': 3, 'data_foo': 'bar', 'aria_disabled': 'true'}
        >>> obj.declared_props
        {'val': 3}

        """
        return {
            name: value
            for name, value in self.props.items()
            if name in self.PropTypes.__types__
        }

    @property
    def non_declared_props(self) -> Props:
        """Get the props that are not declared in ``PropTypes`` (only ``data_*`` or ``aria_*``).

        Returns
        -------
        Props
            The props limited to the non declared ones.

        Examples
        --------
        >>> class Component(Element):
        ...     class PropTypes:
        ...         val: int
        ...         data_val: int
        ...         aria_val: int
        >>> obj = Component(val=3, data_val=1, data_foo="bar", aria_val=2, aria_disabled="true")
        >>> obj.props
        {'val': 3, 'data_val': 1, 'data_foo': 'bar', 'aria_val': 2, 'aria_disabled': 'true'}
        >>> obj.non_declared_props
        {'data_foo': 'bar', 'aria_disabled': 'true'}

        """
        declared_props = self.declared_props
        return {
            name: value
            for name, value in self.props.items()
            if name not in declared_props
        }

    def prefixed_props(self, prefix: str) -> Props:
        """Get the props matching the given `prefix`.

        Parameters
        ----------
        prefix : str
            The prefix to match.

        Returns
        -------
        Props
            The props limited to the ones starting with `prefix`.

        Examples
        --------
        >>> class Compoment(Element):
        ...     class PropTypes:
        ...         foo: str
        ...         val1: int
        ...         val2: int
        >>> obj = Component(foo='bar', val1=11, val2=22)
        >>> obj.props
        {'foo': 'bar', 'val1': 11, 'val2': 22}
        >>> obj.prefixed_props('val')
        {'val1': 11, 'val2': 22}

        """
        return {
            name: value for name, value in self.props.items() if name.startswith(prefix)
        }

    def set_props(self, props: Props) -> None:
        """Set some props in addition/replacement to the already set ones.

        Parameters
        ----------
        props : Props
            A dict with each prop to set. If a prop is already set, it will be replaced.

        Raises
        ------
        InvalidPropNameError
            If a prop does not exist.
        InvalidPropValueError
            If a value is not valid (if dev-mode)

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str

        >>> el = <Greeting />
        >>> el.set_props({"name": "John", "surname": "JJ"})
        >>> el.name
        'John'
        >>> el.surname
        'JJ'

        >>> el.set_props({"name": {"first": "John"}})
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropValueError: <Greeting>.name: `{'first': 'John'}` is not a
        valid value for this prop (type: <class 'dict'>, expected: <class 'str'>)

        >>> el.set_props({"firstname": "John"})
        Traceback (most recent call last):
        ...
        mixt.exceptions.InvalidPropNameError: <Greeting>.firstname: is not an allowed prop

        """
        for name, value in props.items():
            self.set_prop(name, value)

    def _str_list_to_string(self, str_list: List) -> str:
        """Convert an accumulated list from ``_to_list`` to a string.

        It will resolve entries that are in fact callables by calling them.

        Parameters
        ----------
        str_list : List
            List of strings or callable to render.

        Returns
        -------
        str
            The concatenated list of strings, ie some HTML.

        """
        final_str_list: List[str] = []
        for item in str_list:
            if not callable(item):
                final_str_list.append(item)
                continue
            str_sublist: List = []
            self._render_element_to_list(item(), str_sublist)
            final_str_list.append(self._str_list_to_string(str_sublist))

        return "".join(final_str_list)

    def to_string(self) -> str:
        """Convert the element into an html string.

        Returns
        -------
        str
            The html ready to be used.

        Examples
        --------
        >>> class Greeting(Element):
        ...     class PropTypes:
        ...         name: str = "World"
        ...         surname: str
        ...
        ...     def render(self, context):
        ...         return <div>Hello, <strong>{self.name}</strong></div>

        >>> <Greeting />.to_string()
        <div>Hello, <strong>World</strong></div>

        # It's what is actually called when using ``str(...)``
        >>> str(<Greeting />)
        <div>Hello, <strong>World</strong></div>

        """
        str_list: List[Union[str, Callable[[], Any]]] = []
        self._to_list(str_list)
        return self._str_list_to_string(str_list)

    def _to_list(self, acc: List) -> None:
        """Fill the list `acc` with strings that will be concatenated to produce the html string.

        To be implemented in subclasses.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        raise NotImplementedError()

    def __str__(self) -> str:
        """Convert the element into an html string.

        Returns
        -------
        str
            The html ready to be used.

        """
        return self.to_string()

    def _use_context(self, context: OptionalContext) -> None:
        """Make the element use the new context.

        Parameters
        ----------
        context : OptionalContext
            The context to use. Will be merged with the current one if any.

        Notes
        -----
        Nothing will be done if this method was already called for the element.

        """
        if self._context_merged:
            return
        if context and context is not EmptyContext:
            if self.context and self.context is not EmptyContext:
                self.context = context.merge_with(self.context)
            else:
                self.context = context
        self._context_merged = True

    def _render_element_to_list(self, element: AnElement, acc: List) -> None:
        """Fill the list `acc` with html string part of the given element.

        Parameters
        ----------
        element : AnElement
            The element to be converted to string parts.
        acc : List
            The accumulator list where to append the parts.

        """
        if isinstance(element, Base):
            element._use_context(self.context)
            element._to_list(acc)
        elif callable(element):
            acc.append(element)
        elif element not in IGNORED_CHILDREN:
            acc.append(escape(element))

    def _render_children_to_list(self, acc: List) -> None:
        """Fill the list `acc` with html string part of all the children.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        for child in self.__children__:
            self._render_element_to_list(child, acc)


class WithClass(Base):
    """A special base element that will inherit the "class" prop and concatenate it.

    Used by ``element.Element`` and ``html.Fragment``. The higher a class is in the tree, the later
    it will appear in the final class.

    Examples
    --------
    >>> class Elem(Element):
    ...     def render(self, context):
    ...         return <div class="from-div" />
    >>> print(<Elem class="from-elem" />)
    <div class="from-div from-elem></div>"

    """

    class PropTypes:
        """Default props for all elements having a class.

        Attributes
        ----------
        _class : str
            A string containing the "class" html attribute that will be passed down to the first
            rendered html element.

        Examples
        --------
        >>> class Component(Element)


        """

        id: str
        _class: str

    def get_class(self) -> str:
        """Return the actual "class" prop or an empty string if not set.

        The class prop can be a single class, or many classes, represented as a space separated
        list of classes, like in html/css.

        Returns
        -------
        str
            The "class" prop, stripped.

        """
        try:
            klass = self.prop("class")
        except UnsetPropError:
            klass = ""
        return klass.strip()

    @property
    def classes(self) -> List[str]:
        """Return a list of the classes defined in the "class" prop, or an empty list if not set.

        Returns
        -------
        List[str]
            List of all the classes defined in the "class" prop.

        Examples
        --------
        >>> class Component(Element):
        ...     pass

        >>> <Component />.classes
        []
        >>> <Component class="foo bar" />.classes
        ['foo', 'bar']

        """
        return self.get_class().split()

    def add_class(self, klass: str, prepend: bool = False) -> str:
        """Add the given class(es) (`klass`) to the actual list of classes.

        Parameters
        ----------
        klass : str
            The class to add. If contains spaces, it will be a list of classes.
        prepend : bool
            If ``False`` (the default), the new class(es) will be added at the end of the existing
            list. If ``True``, it/they will be added at the beginning.

        Returns
        -------
        str
            The new value of the ``class`` prop.

        Examples
        --------
        >>> class Component(Element):
        ...     pass

        >>> el = <Component />
        >>> el.add_class("foo")
        >>> el.classes
        ['foo']

        >>> el.add_class("bar baz")
        >>> el.classes
        ['foo', 'bar', 'baz']

        >>> el.add_class("zab rab", prepend=True)
        >>> el.classes
        ['zab', 'rab', 'foo', 'bar', 'baz']

        """
        klasses: List[str] = klass.split()
        if not klasses:
            return self.get_class()

        classes = self.classes
        if classes:
            if prepend:
                classes[0:0] = klasses
            else:
                classes.extend(klasses)
        else:
            classes = list(klasses)

        return self.set_prop("class", " ".join(classes))

    def prepend_class(self, klass: str) -> str:
        """Add the given class(es) (`klass`) to the beginning of the actual list of classes.

        Parameters
        ----------
        klass : str
            The class to add. If contains spaces, it will be a list of classes.

        Returns
        -------
        str
            The new value of the ``class`` prop.

        Examples
        --------
        >>> class Component(Element):
        ...     pass

        >>> el = <Component />
        >>> el.prepend_class("foo")
        >>> el.classes
        ['foo']

        >>> el.prepend_class("bar baz")
        >>> el.classes
        ['bar', 'baz', 'foo']

        """
        return self.add_class(klass, prepend=True)

    def append_class(self, klass: str) -> str:
        """Add the given class(es) (`klass`) to the end of the actual list of classes.

        Parameters
        ----------
        klass : str
            The class to add. If contains spaces, it will be a list of classes.

        Returns
        -------
        str
            The new value of the ``class`` prop.

        Examples
        --------
        >>> class Component(Element):
        ...     pass

        >>> el = <Component />
        >>> el.append_class("foo")
        >>> el.classes
        ['foo']

        >>> el.append_class("bar baz")
        >>> el.classes
        ['foo', 'bar', 'baz']

        """
        return self.add_class(klass, prepend=False)

    def remove_class(self, klass: str) -> None:
        """Remove the given class(es) (`klass`) from the actual list of classes.

        Parameters
        ----------
        klass : str
            The class to remove. If contains spaces, it will be a list of classes.

        Returns
        -------
        str
            The new value of the ``class`` prop.

        Examples
        --------
        >>> class Component(Element):
        ...     pass

        >>> el = <Component class="foo bar"/>
        >>> el.remove_class("baz")
        >>> el.classes
        ['foo', 'bar']

        >>> el.remove_class("bar")
        >>> el.classes
        ['foo']

        >>> el.remove_class("foo bar baz")
        >>> el.classes
        []

        """
        klasses: Set[str] = set(klass.split())
        return self.set_prop(
            "class", " ".join(c for c in self.classes if c not in klasses)
        )

    def has_class(self, klass: str) -> bool:
        """Tell if the given `class` is in the actual list of classes.

        Parameters
        ----------
        klass : str
            The class to check.

        Returns
        -------
        bool
            The new value of the ``class`` prop.

        Examples
        --------
        >>> class Component(Element):
        ...     pass

        >>> el = <Component class="foo"/>
        >>> el.has_class("foo")
        True
        >>> el.has_class("bar")
        True

        """
        return klass.strip() in self.classes


class Fragment(WithClass):
    """An invisible tag that is used to hold many other tags.

    Examples
    --------
        >>> class Component(Element):
        ...     def render(self, context):
        ...         return <Fragment>
        ...             <div>Foo</div>
        ...             <div>Bar</div>
        ...         </Fragment>

        >>> print(<Component />)
        <div>Foo</div><div>Bar</div>

    """

    class PropTypes:
        id: str

    def _to_list(self, acc: List) -> None:
        """Add the children parts to the list `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        self._render_children_to_list(acc)

    def get_id(self) -> str:
        """Return the ``id`` prop of the element."""
        return self.prop("id")

    def _attach_to_parent(self, parent: "Base") -> None:
        """Save the given `parent` as the parent of the children of the fragment.

        Parameters
        ----------
        parent : Base
            The element that will be saved as the parent of children of the fragment.

        """
        super()._attach_to_parent(parent)

        for child in self.__children__:
            if isinstance(child, Base):
                child._attach_to_parent(parent)


class BaseContext(Base):
    """A special element used in ``Base`` to propagate its props down the tree.

    Examples
    --------
    >>> class Context(BaseContext):
    ...     class PropTypes:
    ...         authenticated: Required[bool]
    ...         username: str

    >>> class NavBar(Element):
    ...     def render(self, context):
    ...         return <div class={"authenticated" if context.authenticated else ""}>
    ...             <if cond={context.authenticated}>
    ...                 Hello {context.username}
    ...             </if>
    ...             <else>
    ...                 Please Log-in
    ...             </else>
    ...         </div>

    >>> class App(Element):
    ...     def render(self, context):
    ...         return <Fragment>
    ...             <NavBar />
    ...             <div>App content...</div>
    ...         </Fragment>

    >>> print(<Context authenticated={True} username="John"><App /></Context>)
    <div class="authenticated">Hello John</div><div>App content...</div>

    """

    def __init__(self, **kwargs: Any) -> None:
        """Init the context by settings its own context to itself.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The props to set on this context.

        """
        super().__init__(**kwargs)
        self.context: "BaseContext" = self

    def _to_list(self, acc: List) -> None:
        """Add the the children to the list `acc`.

        Parameters
        ----------
        acc: List
            The accumulator list where to append the parts.

        """
        self._render_children_to_list(acc)

    def merge_with(self, context: "BaseContext") -> "BaseContext":
        """Merge the current context with the given one.

        Parameters
        ----------
        context : OptionalContext
            The context to merge with the current one.

        Returns
        -------
        BaseContext
            A new context with merged props.

        """
        # we create a new context class as a subclass having both as parents
        name = f"{self.context.__tag__}MergedWith{context.__tag__}"
        bases = {self.context.__class__, context.__class__}
        context_class = type(
            name, tuple(bases), {"__tag__": name, "__display_name__": name},
        )
        # we can instantiate the new context class, passing props of both
        # if some are defined many times, the given context wins
        return context_class(**dict(self.context.props, **context.props))


EmptyContext = BaseContext()  # pylint: disable=invalid-name
