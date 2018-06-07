"""Internal mixt code to help creating HTML tags. Also contains some special HTML "tags"."""

from typing import Any, Dict, List, Optional, Sequence, cast

from ..exceptions import InvalidChildrenError
from ..proptypes import Choices, NotProvided
from .base import Base, BaseMetaclass, OneOrManyElements, WithClass, escape
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
        name: str
            The name of the class to construct.
        parents: Sequence[type]
            A tuple with the direct parent classes of the class to construct.
        attrs: Dict[str, Any]
            Dict with the attributes defined in the class.

        """
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

    def _render_attributes(self) -> List[str]:
        """Return a string of the current instance attributes, from props, ready for html.

        For boolean props, we only render them if they are "True', without value.

        Returns
        -------
        List[str]
            A list of string parts to be joined.

        """
        result: List[str] = []
        for name, value in self.props.items():
            html_name = BasePropTypes.__to_html__(name)
            if self.PropTypes.__is_bool__(name):  # type: ignore
                if value:
                    result.extend((" ", html_name))
            else:
                result.extend((" ", html_name, '="', escape(value), '"'))
        return result

    def get_id(self) -> str:
        """Return the ``id`` prop of the element."""
        return self.prop("id")


class HtmlElement(HtmlBaseElement):
    """Base for all HTML tags accepting children."""

    def _to_list(self, acc: List) -> None:
        """Add the tag, its attributes and its children to the list `acc`.

        Parameters
        ----------
        acc: List
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
        child_or_children: OneOrManyElements
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
        acc: List
            The accumulator list where to append the parts.

        """
        acc.append(f"<{self.__tag__}")
        acc.extend(self._render_attributes())
        acc.append(" />")


class RawHtml(HtmlElementNoChild):
    """Element to handle raw text in html."""

    class PropTypes:
        text: str

    def _to_list(self, acc: List) -> None:
        """Add the text prop to the list `acc`.

        Parameters
        ----------
        acc: List
            The list where to append the text.

        """
        acc.append(self.text)


def Raw(text: str) -> RawHtml:  # pylint: disable=invalid-name
    """Help to easily construct a RawHtml element.

    Parameters
    ----------
    text: str
        The text to pass as a prop to the RawHtml element to construct.

    Returns
    -------
    RawHtml
        The newly constructed element.

    """
    return RawHtml(text=text)  # type: ignore


class Fragment(WithClass):
    """An invisible tag that is used to hold many others."""

    class PropTypes:
        id: str

    def _to_list(self, acc: List) -> None:
        """Add the children parts to the list `acc`.

        Parameters
        ----------
        acc: List
            The accumulator list where to append the parts.

        """
        self._render_children_to_list(acc)

    def get_id(self) -> str:
        """Return the ``id`` prop of the element."""
        return self.prop("id")


class Comment(Base):
    """Implement HTML comments. Will not set them in final HTML."""

    class PropTypes:
        comment: str

    def _to_list(self, acc: List) -> None:
        """Add nothing to `acc`.

        It was a decision from ``pyxl`` to ignore HTML comments.

        Parameters
        ----------
        acc: List
            The list where to append nothing.

        """
        pass


class Doctype(Base):
    """Implement HTML doctype declaration."""

    class PropTypes:
        doctype: str

    def _to_list(self, acc: List) -> None:
        """Add the doctype html declaration to the list `acc`.

        Parameters
        ----------
        acc: List
            The accumulator list where to append the parts.

        """
        acc.append(f"<!DOCTYPE {self.prop('doctype')}>")


class CData(Base):
    """Implement HTML CDATA declaration."""

    class PropTypes:
        cdata: str

    def _to_list(self, acc: List) -> None:
        """Add the cdata html declaration to the list `acc`.

        Parameters
        ----------
        acc: List
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
        acc: List
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
        acc: List
            The accumulator list where to append the parts.

        """
        acc.extend(("<!--[if ", self._render_cond(), "]><!-->"))
        self._render_children_to_list(acc)
        acc.append("<!--<![endif]-->")


class IFStack:
    """Class used by the parser to handle stacked IF/ELSE and their conditions."""

    stack: List[bool] = []
    last: Optional[bool] = None

    @staticmethod
    def push_condition(cond: bool) -> bool:
        """Add a condition in the IF stack. For <if>/<else> tags.

        Parameters
        ----------
        cond: bool
            The condition to add to the stack.

        Returns
        -------
        bool
            The given condition

        """
        IFStack.stack.append(cond)
        return cond

    @staticmethod
    def leave_if() -> List:
        """Leave a <if> tag so pop the last condition, now used.

        Returns
        -------
        List
            An empty list to be used as an empty list of children to add.

        """
        IFStack.last = IFStack.stack.pop()
        return []
