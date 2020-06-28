"""Internal mixt code to help creating HTML tags. Also contains some special HTML "tags"."""

from typing import Any, Dict, List, Sequence, Union, cast

from ..exceptions import InvalidChildrenError
from ..proptypes import Choices, NotProvided, Required
from .base import (  # noqa: F401  # isort: skip  # pylint: disable=unused-import
    Base,
    BaseMetaclass,
    Fragment,
    OneOrManyElements,
    Props,
    WithClass,
    escape,
)
from .proptypes import BasePropTypes


REFERRERPOLICIES = cast(
    Choices,
    [
        "no-referrer",
        "no-referrer-when-downgrade",
        "origin",
        "origin-when-cross-origin",
        "strict-origin-when-cross-origin",
        "unsafe-url",
    ],
)
CROSSORIGINS = cast(Choices, ["", "anonymous", "use-credentials"])
FORMENCTYPES = cast(
    Choices, ["application/x-www-form-urlencoded", "multipart/form-data", "text/plain"]
)
INPUTMODES = cast(Choices, ["none, text, decimal, numeric, tel, search, email, url"])
AUTOCAPITALIZES = cast(Choices, ["sentences", "none", "words", "characters"])

__tags__: Dict[str, str] = {}  # holds the `html tag <-> class name` matching


class HtmlElementMetaclass(BaseMetaclass):
    """Metaclass to construct HTML tags."""

    def __init__(
        cls, name: str, parents: Sequence[type], attrs: Dict[str, Any]  # noqa: B902
    ) -> None:
        """Construct the class and save its tag (create it from `name` if not defined).

        Parameters
        ----------
        name : str
            The name of the class to construct.
        parents : Sequence[type]
            A tuple with the direct parent classes of the class to construct.
        attrs : Dict[str, Any]
            Dict with the attributes defined in the class.

        """
        if not getattr(cls, "__not_an_html_tag__", False):
            if not attrs.get("__tag__"):
                attrs["__tag__"] = name.lower()
            __tags__[attrs["__tag__"]] = name

        super().__init__(name, parents, attrs)


class HtmlBaseElement(WithClass, metaclass=HtmlElementMetaclass):
    """Base for all HTML tags, with common props."""

    class PropTypes:
        accesskey: str
        autocapitalize: Choices = AUTOCAPITALIZES
        _class: str
        contenteditable: Choices = cast(Choices, ["false", "true"])
        contextmenu: str
        dir: Choices = cast(Choices, ["auto", "ltr", "rtl"])
        draggable: Choices = cast(Choices, ["false", "true"])
        dropzone: str
        hidden: bool
        id: str
        itemid: str
        itemprop: str
        itemscope: bool
        itemstype: str
        lang: str
        slot: str
        spellcheck: bool
        style: str
        tabindex: int
        title: str
        translate: Choices = cast(Choices, ["", "yes", "no"])
        onabort: str
        onautocomplete: str
        onautocompleteerror: str
        onblur: str
        oncancel: str
        oncanplay: str
        oncanplaythrough: str
        onchange: str
        onclick: str
        onclose: str
        oncontextmenu: str
        oncuechange: str
        ondblclick: str
        ondrag: str
        ondragend: str
        ondragenter: str
        ondragexit: str
        ondragleave: str
        ondragover: str
        ondragstart: str
        ondrop: str
        ondurationchange: str
        onemptied: str
        onended: str
        onerror: str
        onfocus: str
        oninput: str
        oninvalid: str
        onkeydown: str
        onkeypress: str
        onkeyup: str
        onload: str
        onloadeddata: str
        onloadedmetadata: str
        onloadstart: str
        onmousedown: str
        onmouseenter: str
        onmouseleave: str
        onmousemove: str
        onmouseout: str
        onmouseover: str
        onmouseup: str
        onmousewheel: str
        onpause: str
        onplay: str
        onplaying: str
        onprogress: str
        onratechange: str
        onreset: str
        onresize: str
        onscroll: str
        onseeked: str
        onseeking: str
        onselect: str
        onshow: str
        onsort: str
        onstalled: str
        onsubmit: str
        onsuspend: str
        ontimeupdate: str
        ontoggle: str
        onvolumechange: str
        onwaiting: str

    def _get_attribute_props(self) -> Props:
        """Get the props to render as attributes.

        All props by default, but can be overridden.

        Returns
        -------
        Props
            The props to render as attributes.

        """
        return self.props

    def _render_attributes(self) -> List[str]:
        """Return a string of the current instance attributes, from props, ready for html.

        For boolean props, we only render them if they are "True', without value.

        Returns
        -------
        List[str]
            A list of string parts to be joined.

        """
        result: List[str] = []
        for name, value in self._get_attribute_props().items():
            html_name = BasePropTypes.__to_html__(name)
            if self.PropTypes.__is_bool__(name):  # type: ignore
                if value:
                    result.extend((" ", html_name))
            else:
                result.extend((" ", html_name, '="', escape(value), '"'))
        return result

    def get_id(self) -> Union[None, str]:
        """Return the ``id`` prop of the element."""
        return self.prop("id", default=None)

    def __repr__(self) -> str:
        """Return a string representation of the element.

        Returns
        -------
        str
            The representation of the element.

        """
        obj_id = self.get_id()
        classes = self.get_class()
        return "<{}{}{}>".format(
            self.__display_name__,
            (' id="{}"'.format(obj_id)) if obj_id else "",
            (' class="{}"'.format(classes)) if classes else "",
        )


class HtmlElement(HtmlBaseElement):
    """Base for all HTML tags accepting children."""

    def _to_list(self, acc: List) -> None:
        """Add the tag, its attributes and its children to the list `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        acc.append(f"<{self.__tag__}")
        acc.extend(self._render_attributes())
        acc.append(">")
        self._render_children_to_list(acc)
        acc.append(f"</{self.__tag__}>")


class HtmlElementNoChild(HtmlBaseElement):
    """Base for all HTML tags that does not accept children."""

    def append(self, child_or_children: OneOrManyElements) -> None:
        """Raise if we try to add children.

        Parameters
        ----------
        child_or_children : OneOrManyElements
            The child(ren) we cannot add.

        Raises
        ------
        InvalidChildrenError
            In any cases, as we cannot accept children.


        """
        raise InvalidChildrenError(self.__display_name__, "does not allow children")

    prepend = append

    def _to_list(self, acc: List) -> None:
        """Add the tag and its attributes to the list `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        acc.append(f"<{self.__tag__}")
        acc.extend(self._render_attributes())
        acc.append(" />")


class RawHtml(HtmlElementNoChild):
    """Element to handle raw text in html.

    The rule to know when some text will be automatically escaped or not is simple:

    - if it's python: it will be escaped
    - if it's "mixt": it will not

    ``RawHtml`` helps to tell mixt to not escape some text. It's a component with a ``text``
    prop that is generally used via the ``Raw`` function that take some text as an unnamed
    argument that is passed to the ``text`` prop of a new ``RawHtml`` component.

    So calling ``html.Raw("some text")`` is sugar for calling ``html.RawHtml(text="some text)``.

    Generally you should not have to worry, ``mixt`` does its best to handle things for you.

    But for example, when rendering some JS or CSS, you really want RAW, without escaping.

    Below are some examples to show when text is escaped or not.

    Examples
    --------
    >>> from mixt import h, html  # same but ``html`` for mixt mode, and ``h`` as a shortcut

    # Simple rendered text will be escaped. Because it's seen as python
    >>> class Component(Element):
    ...     def render(self, context):
    ...         return 'Hello "world" !'

    >>> print(<Component />)
    Hello &quot;world&quot; !


    # If we don't want this, we need to mark the text as raw.
    >>> class Component(Element):
    ...     def render(self, context):
    ...         return h.Raw('Hello "world" !')

    >>> print(<Component />)
    Hello "world" !

    # In "mixt" mode, text will NOT be escaped.
    # Because calling ``<div>text</div>`` is in fact calling ``html.Div()(html.Raw('text'))``
    >>> class Component(Element):
    ...     def render(self, context):
            return <div>Hello "world" !</Div>"hello

    >>> print(<Component />)
    <div>Hello "world" !</div>

    # But it will be in attributes:
    >>> class Component(Element):
    ...     def render(self, context):
            return <div data-foo="<bar>">Hello "world" !</div>

    >>> print(<Component />)
    <div data-foo="&lt;bar&gt;">Hello "world" !</div>

    # Even if given as a python string
    >>> class Component(Element):
    ...     def render(self, context):
    ...         return <div data-foo={"<bar>"}>Hello "world" !</div>

    >>> print(<Component />)
    <div data-foo="&lt;bar&gt;">Hello "world" !</div>

    # Text in python mode, will be escaped:
    >>> class Component(Element):
    ...     def render(self, context):
    ...         return h.Fragment()('Hello "world" !')

    >>> print(<Component />)
    <div>Hello &quot;world&quot; !</div>

    # Use ``RawHtml`` to solve this.
    >>> class Component(Element):
    ...     def render(self, context):
    ...         return h.Div()(h.Raw('Hello "world" !'))

    >>> print(<Component />)
    <div>Hello "world" !</div>

    """

    class PropTypes:
        """PropTypes for the ``RawHtml`` component.

        Attributes
        ----------
        text : str
            The text that will be rendered without escaping.

        """

        text: str

    def _to_list(self, acc: List) -> None:
        """Add the text prop to the list `acc`.

        Parameters
        ----------
        acc : List
            The list where to append the text.

        """
        acc.append(self.text)


def Raw(text: str) -> RawHtml:  # pylint: disable=invalid-name
    """Help to easily construct a RawHtml element.

    See ``RawHtml`` for more information.

    Parameters
    ----------
    text : str
        The text to pass as a prop to the RawHtml element to construct.

    Returns
    -------
    RawHtml
        The newly constructed element.

    """
    return RawHtml(text=text)  # type: ignore


class Comment(Base):
    """Implement HTML comments. Will not set them in final HTML."""

    class PropTypes:
        comment: str

    def _to_list(self, acc: List) -> None:
        """Add nothing to `acc`.

        It was a decision from ``pyxl`` to ignore HTML comments.

        Parameters
        ----------
        acc : List
            The list where to append nothing.

        """


class Doctype(Base):
    """Implement HTML doctype declaration.

    Examples
    --------
    # It can be used as a normal HTML doctype:

    >>> class Component(Element):
    ...     def render(self, context):
    ...         return <!DOCTYPE html>

    >>> print(<Component />)
    <!DOCTYPE html>

    # Or using it as a component:

    >>> class Component(Element):
    ...     def render(self, context):
    ...         return <Doctype doctype=html />

    >>> print(<Component />)
    <!DOCTYPE html>

    # Or even better, taking advantage of the default value of the ``doctype`` prop:

    >>> class Component(Element):
    ...     def render(self, context):
    ...         return <Doctype />

    >>> print(<Component />)
    <!DOCTYPE html>

    """

    class PropTypes:
        """PropTypes for the ``Doctype`` element.

        Attributes
        ----------
        doctype : str
            The doctype to use. Default to ``html``.

        """

        doctype: str = "html"

    def _to_list(self, acc: List) -> None:
        """Add the doctype html declaration to the list `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        acc.append(f"<!DOCTYPE {self.prop('doctype')}>")


class CData(Base):
    """Implement HTML CDATA declaration."""

    class PropTypes:
        cdata: Required[str]

    def _to_list(self, acc: List) -> None:
        """Add the cdata html declaration to the list `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        acc.append(f"<![CDATA[{self.prop('cdata')}]]>")


class ConditionalComment(Base):
    """HTML conditional comment."""

    class PropTypes:
        cond: str

    def _render_cond(self) -> str:
        """Render the condition. Allow '&', escape everything else from cond.

        Returns
        -------
        str
            The condition, ready to be used in html.

        """
        cond = self.prop("cond", "")
        if not cond or cond is NotProvided:
            return ""
        # allow '&', escape everything else from cond
        return "&".join(map(escape, cond.split("&")))

    def _to_list(self, acc: List) -> None:
        """Add the if/end tags and the condition `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        acc.extend(("<!--[if ", self._render_cond(), "]>"))
        self._render_children_to_list(acc)
        acc.append("<![endif]-->")


class ConditionalNonComment(ConditionalComment):
    """Conditional comment where browsers which don't support them will parse children."""

    def _to_list(self, acc: List) -> None:
        """Add the if/end tags and the condition `acc`.

        Parameters
        ----------
        acc : List
            The accumulator list where to append the parts.

        """
        acc.extend(("<!--[if ", self._render_cond(), "]><!-->"))
        self._render_children_to_list(acc)
        acc.append("<!--<![endif]-->")
