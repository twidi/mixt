"""Base class to handle html tags and custom elements."""

from itertools import chain
from typing import Any, Dict, List, Sequence, Set, Union, cast
from xml.sax.saxutils import escape as xml_escape, unescape as xml_unescape

from ..exceptions import InvalidPropNameError, UnsetPropError
from ..proptypes import NotProvided
from .proptypes import BasePropTypes


# pylint: disable=invalid-name
OptionalContext = Union["BaseContext", None]
AnElement = Union["Base", str]
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
    obj: Any
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
    obj: Any
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
        name: str
            The name of the class to construct.
        parents: Sequence[type]
            A tuple with the direct parent classes of the class to construct.
        attrs: Dict[str, Any]
            Dict with the attributes defined in the class.

        """
        super().__init__(name, parents, attrs)  # type: ignore

        tag = attrs.get("__tag__") or name
        setattr(cls, "__tag__", tag)
        display_name = attrs.get("__display_name__") or tag
        setattr(cls, "__display_name__", display_name)

        proptypes_classes = []
        exclude: Set[str] = set()

        if "PropTypes" in attrs:
            proptypes_classes.append(attrs["PropTypes"])
            exclude = getattr(attrs["PropTypes"], "__exclude__", exclude)

        proptypes_classes.extend(
            [
                parent.PropTypes  # type: ignore
                for parent in parents[::-1]
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

        PropTypes.__validate_types__()

        setattr(cls, "PropTypes", PropTypes)


class Base(object, metaclass=BaseMetaclass):
    """The base of all elements. Manage PropTypes, props, context and children.

    Attributes
    ----------
    __tag__: str
        The tag to use when using the element in "html". If not set in the class, it will be, by
        default, the name of the class itself.
    __display_name__: str
        A "human" representation of ``__tag__``. Will be used in exceptions and can be changed to
        give more information.

    """

    __tag__: str = ""
    __display_name__: str = ""

    class PropTypes(BasePropTypes):
        pass

    def __init__(self, **kwargs: Any) -> None:
        """Create the element and validate then save props.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The props to set on this element.

        """
        self.__props__: Props = {}
        self.__children__: ManyElements = []
        self.context: OptionalContext = None

        for name, value in kwargs.items():
            self.set_prop(name, value)

        self.PropTypes.__validate_required__(self.__props__)

    def __call__(self, *children: AnElement) -> "Base":
        """Add the given `children` to the current element.

        Parameters
        ----------
        children: OneOrManyElements
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

    def _set_context(self, context: OptionalContext) -> None:
        """Set the given `context` to the element and propagate it to children.

        If the element already have a context, both are merged.

        Parameters
        ----------
        context: OptionalContext
            The context (or ``None``) to set.

        """
        if context is None:
            return

        # merge new context and existing context if not already done
        if self.context is not None and not issubclass(
            context.__class__, self.context.__class__
        ):
            # we create a new context class as a subclass having both as parents
            context_class = type(
                f"{context.__tag__}__{self.context.__tag__}",  # compose a name with both names
                (
                    context.__class__,
                    self.context.__class__,
                ),  # we inherit PropTypes of both
                {},
            )
            # we can instantiate the new context class, passing props of both
            # if some are defined many times, the lowest context in the tree wins, ie the actual one
            context = context_class(**dict(context.props, **self.context.props))

        self.context = context
        self._propagate_context(self.__children__)

    def _propagate_context(self, children: ManyElements) -> None:
        """Propagate the context of the current element to all of the given children.

        Parameters
        ----------
        children: ManyElements
            The children for which to set the context.

        """
        if self.context is None:
            return
        for child in children:
            if isinstance(child, Base):
                child._set_context(self.context)

    def _child_to_children(self, child_or_children: OneOrManyElements) -> ManyElements:
        """Make a flat list of children from the given one(s).

        Parameters
        ----------
        child_or_children : OneOrManyElements
            This can be a single child, or a list of children,
            each one possibly being also a list, etc...
            Every children that is ``None`` or ``False`` is ignored.

        Returns
        -------
        ManyElements
            The flattened list of children.

        """
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
        child_or_children: OneOrManyElements
            The child(ren) to add.

        """
        children = self._child_to_children(child_or_children)
        self._propagate_context(children)
        self.__children__.extend(children)

    def prepend(self, child_or_children: OneOrManyElements) -> None:
        """Prepend some children to the current element.

        In the process, we propagate the actual context to the children.

        Parameters
        ----------
        child_or_children: OneOrManyElements
            The child(ren) to add.

        """
        children = self._child_to_children(child_or_children)
        self._propagate_context(children)
        self.__children__[0:0] = children

    def __getattr__(self, name: str) -> Any:
        """Return a prop defined by `name`, if it is defined.

        If the prop exists but is not set and the prop has a default value, this default value is
        returned.

        It the same as calling ``self.prop(name)``, except that it always raise an
        ``AttributeError`` for all failures.

        Parameters
        ----------
        name: str
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

        Parameters
        ----------
        name: str
            The name we want to validate.

        Returns
        -------
        str
            The real name of the given prop.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        """
        name = BasePropTypes.__to_python__(name)
        if not cls.PropTypes.__allow__(name):
            raise InvalidPropNameError(cls.__display_name__, name)
        return name

    def prop(self, name: str, default: Any = NotProvided) -> Any:
        """Return a prop defined by `name`, if it is defined, or the `default` if provided.

        If the prop exists but is not set, `default` is not provided, and the prop has a default
        value, this default value is returned.

        Parameters
        ----------
        name: str
            The name of the wanted prop.
        default: Any
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
        name: str
            The name of the prop to check.
        allow_invalid: bool
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

        """
        try:
            self.prop(name)
        except InvalidPropNameError:
            if allow_invalid:
                return False
            else:
                raise
        except UnsetPropError:
            return False
        else:
            return True

    def set_prop(self, name: str, value: Any) -> Any:
        """Set the `value` of the prop defined by `name`, if it is valid.

        The value is validated only if not in dev-mode. But still converted if needed, like for
        booleans.
        If `value` is ``NotProvided``, the prop is unset.

        Parameters
        ----------
        name: str
            The name of the prop to set.
        value: Any
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
        name: str
            The name of the prop to unset.

        Returns
        -------
        Any
            The value that was stored in the prop before deleting it.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        """
        return self.set_prop(name, value=NotProvided)

    def prop_default(self, name: str) -> Any:
        """Return the default value of the prop defined by `name`.

        Parameters
        ----------
        name: str
            The name of the prop for which we want the default value

        Returns
        -------
        Any
            The default value defined in ``PropTypes`` or ``NotProvided`` if not set.

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        """
        return self.PropTypes.__default__(self.prop_name(name))

    def is_prop_default(self, name: str, value: Any = NotProvided) -> bool:
        """Tell if the actual (or given) value for the prop defined by `name` is the default one.

        Parameters
        ----------
        name: str
            The name of the prop we are asking for.
        value: Any
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
        name: str
            The name of the prop we want the type

        Returns
        -------
        Any
            The type, coming from ``PropTypes``

        Raises
        ------
        InvalidPropNameError
            If there is no prop with the given `name`.

        """
        return cls.PropTypes.__type__(cls.prop_name(name))

    @property
    def props(self) -> Props:
        """Get all the available and set props, including default ones.

        Returns
        -------
        Props
            A dict with each defined props. If a prop is not set but has a default value, this one
            is used.

        """
        return dict(self.PropTypes.__default_props__, **self.__props__)

    def set_props(self, props: Props) -> None:
        """Set some props in addition/replacement to the already set ones.

        Parameters
        ----------
        props: Props
            A dict with each prop to set. If a prop is already set, it will be replaced.


        Raises
        ------
        InvalidPropNameError
            If a prop does not exist.
        InvalidPropValueError
            If a value is not valid (if dev-mode)

        """
        for name, value in props.items():
            self.set_prop(name, value)

    def to_string(self) -> str:
        """Convert the element into an html string.

        Returns
        -------
        str
            The html ready to be used.

        """
        str_list: List[str] = []
        self._to_list(str_list)
        return "".join(str_list)

    def _to_list(self, acc: List) -> None:
        """Fill the list `acc` with strings that will be concatenated to produce the html string.

        To be implemented in subclasses.

        Parameters
        ----------
        acc: List
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

    @staticmethod
    def _render_element_to_list(element: AnElement, acc: List) -> None:
        """Fill the list `acc` with html string part of the given element.

        Parameters
        ----------
        element: AnElement
            The element to be converted to string parts.
        acc: List
            The accumulator list where to append the parts.

        """
        if isinstance(element, Base):
            element._to_list(acc)
        elif element not in IGNORED_CHILDREN:
            acc.append(escape(element))

    def _render_children_to_list(self, acc: List) -> None:
        """Fill the list `acc` with html string part of all the children.

        Parameters
        ----------
        acc: List
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
        return self.prop("class", "").strip()

    @property
    def classes(self) -> List[str]:
        """Return a list of the classes defined in the "class" prop, or an empty list if not set.

        Returns
        -------
        List[str]
            List of all the classes defined in the "class" prop.

        """
        return self.get_class().split()

    def add_class(self, klass: str, prepend: bool = False) -> str:
        """Add the given `class`(es) to the actual list of class.

        Parameters
        ----------
        klass: str
            The class to add. If contains spaces, it will be a list of classes.
        prepend: bool
            If ``False`` (the default), the new class(es) will be added at the end of the existing
            list. If ``True``, it/they will be added at the beginning.

        Returns
        -------
        str
            The new value of the ``class`` prop.

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
        """Add the given `class`(es) to the beginning of the actual list of class.

        Parameters
        ----------
        klass: str
            The class to add. If contains spaces, it will be a list of classes.

        Returns
        -------
        str
            The new value of the ``class`` prop.

        """
        return self.add_class(klass, prepend=True)

    def append_class(self, klass: str) -> str:
        """Add the given `class`(es) to the end of the actual list of class.

        Parameters
        ----------
        klass: str
            The class to add. If contains spaces, it will be a list of classes.

        Returns
        -------
        str
            The new value of the ``class`` prop.

        """
        return self.add_class(klass, prepend=False)

    def remove_class(self, klass: str) -> None:
        """Remove the given `class`(es) from the actual list of class.

        Parameters
        ----------
        klass: str
            The class to remove. If contains spaces, it will be a list of classes.

        Returns
        -------
        str
            The new value of the ``class`` prop.

        """
        klasses: Set[str] = set(klass.split())
        return self.set_prop(
            "class", " ".join(c for c in self.classes if c not in klasses)
        )


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


EmptyContext = BaseContext()  # pylint: disable=invalid-name
