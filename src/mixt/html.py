"""All available HTML tags, with their props.

We support only actual (and not deprecated) tags in the HTML5 spec, with all their - not
deprecated - attributes.

All tags in this ``html`` module must be used in lowercase in "mixt" mode. For example
``html.A`` is used like this: ``<a>``.

To use in "mixt" mode, a file must import ``html`` from ``mixt``.

There is also a shortcut: ``from mixt import h`` to use directly. But still, for "mixt" mode,
importing ``html`` is mandatory.

All props of type ``bool`` are considered ``False`` by default, in the sense of ``HTML``: the prop
is not passed to the tag. But using ``el.bool_prop`` or ``el.prop("bool_prop")`` won't work if
not specifically set. Use ``el.prop("bool_prop", False)`` if you need to access such a prop from
a parent component.

"""

from typing import Any, Dict, Type, Union, cast

from .exceptions import InvalidPropChoiceError, InvalidPropNameError, RequiredPropError
from .internal.html import (  # noqa: F401  # pylint: disable=unused-import
    AUTOCAPITALIZES,
    CROSSORIGINS,
    FORMENCTYPES,
    INPUTMODES,
    REFERRERPOLICIES,
    CData,
    Comment,
    ConditionalComment,
    ConditionalNonComment,
    Doctype,
    Fragment,
    HtmlElement,
    HtmlElementNoChild,
    Raw,
    RawHtml,
)
from .proptypes import Choices, Number, Required


class _Hyperlink(HtmlElement):
    """Base for ``A`` and ``Area`` elements."""

    class PropTypes:
        download: Union[bool, str]
        href: str
        hreflang: str
        referrerpolicy: Choices = REFERRERPOLICIES
        rel: str
        target: str


class A(_Hyperlink):  # pylint: disable=invalid-name
    """Implement the ``a`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "button",
                "checkbox",
                "menuitem",
                "menuitemcheckbox",
                "menuitemradio",
                "option",
                "radio",
                "switch",
                "tab",
                "treeitem",
            ],
        )
        ping: str
        type: str


class Abbr(HtmlElement):
    """Implement the ``abbr`` HTML tag."""


class Address(HtmlElement):
    """Implement the ``address`` HTML tag."""


class Area(_Hyperlink):
    """Implement the ``area`` HTML tag."""

    class PropTypes:
        alt: str
        coords: str
        media: str
        shape: Choices = cast(Choices, ["rect", "poly", "default"])


class Article(HtmlElement):
    """Implement the ``article`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices,
            ["application", "document", "feed", "main", "presentation", "region"],
        )


class Aside(HtmlElement):
    """Implement the ``aside`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices, ["feed", "note", "presentation", "region", "search"]
        )


class _Media(HtmlElement):
    """Base for ``Audio`` and ``Video`` elements."""

    class PropTypes:
        role: Choices = cast(Choices, ["application"])
        autoplay: bool
        controls: bool
        crossorigin: Choices = CROSSORIGINS
        loop: bool
        muted: bool
        preload: Choices = cast(Choices, ["", "auto", "none", "metadata"])
        src: str


class Audio(_Media):
    """Implement the ``audio`` HTML tag."""


class B(HtmlElement):  # pylint: disable=invalid-name
    """Implement the ``b`` HTML tag."""

    class PropTypes:
        role: str


class Base(HtmlElementNoChild):
    """Implement the ``base`` HTML tag."""

    class PropTypes:
        href: str
        target: str


class Bdi(HtmlElement):
    """Implement the ``bdi`` HTML tag."""

    class PropTypes:
        role: str


class Bdo(HtmlElement):
    """Implement the ``bdo`` HTML tag."""

    class PropTypes:
        role: str
        dir: Choices = cast(Choices, ["ltr", "rtl"])


class Blockquote(HtmlElement):
    """Implement the ``blockquote`` HTML tag."""

    class PropTypes:
        role: str
        cite: str


class Body(HtmlElement):
    """Implement the ``body`` HTML tag."""

    class PropTypes:
        onafterprint: str
        onbeforeprint: str
        onbeforeunload: str
        onhashchange: str
        onlanguagechange: str
        onmessage: str
        onoffline: str
        ononline: str
        onpopstate: str
        onredo: str
        onstorage: str
        onundo: str
        onunload: str


class Br(HtmlElementNoChild):
    """Implement the ``br`` HTML tag."""

    class PropTypes:
        role: str


class Button(HtmlElement):
    """Implement the ``button`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "checkbox",
                "link",
                "menuitem",
                "menuitemcheckbox",
                "menuitemradio",
                "radio",
                "switch",
                "tab",
            ],
        )
        autofocus: bool
        autocomplete: Choices = cast(Choices, ["off"])
        disabled: bool
        form: str
        formaction: str
        formenctype: Choices = FORMENCTYPES
        formmethod: Choices = cast(Choices, ["get", "post"])
        formnovalidate: bool
        formtarget: str
        name: str
        type: Choices = cast(Choices, ["submit", "reset", "button"])
        value: Any


class Canvas(HtmlElement):
    """Implement the ``canvas`` HTML tag."""

    class PropTypes:
        role: str
        height: Number
        width: Number


class Caption(HtmlElement):
    """Implement the ``caption`` HTML tag."""


class Cite(HtmlElement):
    """Implement the ``cite`` HTML tag."""

    class PropTypes:
        role: str


class Code(HtmlElement):
    """Implement the ``code`` HTML tag."""

    class PropTypes:
        role: str


class Col(HtmlElementNoChild):
    """Implement the ``col`` HTML tag."""

    class PropTypes:
        span: int


class Colgroup(HtmlElement):
    """Implement the ``colgroup`` HTML tag."""

    class PropTypes:
        span: int


class Data(HtmlElement):
    """Implement the ``data`` HTML tag."""

    class PropTypes:
        value: str


class Datalist(HtmlElement):
    """Implement the ``datalist`` HTML tag."""


class Dd(HtmlElement):
    """Implement the ``dd`` HTML tag."""


class Del(HtmlElement):
    """Implement the ``del`` HTML tag."""

    class PropTypes:
        role: str
        cite: str
        datetime: str


class Details(HtmlElement):
    """Implement the ``details`` HTML tag."""

    class PropTypes:
        open: bool


class Dfn(HtmlElement):
    """Implement the ``dfn`` HTML tag."""

    class PropTypes:
        role: str


class Div(HtmlElement):
    """Implement the ``div`` HTML tag."""

    class PropTypes:
        role: str


class Dl(HtmlElement):
    """Implement the ``dl`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["group", "presentation"])


class Dt(HtmlElement):
    """Implement the ``dt`` HTML tag."""


class Em(HtmlElement):
    """Implement the ``em`` HTML tag."""

    class PropTypes:
        role: str


class Embed(HtmlElement):
    """Implement the ``embed`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices, ["application", "document", "img", "presentation"]
        )
        height: Number
        src: str
        type: str
        widht: str


class Fieldset(HtmlElement):
    """Implement the ``fieldset`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["group", "presentation"])
        disabled: bool
        form: str
        name: str


class Figcaption(HtmlElement):
    """Implement the ``figcaption`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["group", "presentation"])


class Figure(HtmlElement):
    """Implement the ``figure`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["group", "presentation"])


class Footer(HtmlElement):
    """Implement the ``footer`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["group", "presentation"])


class Form(HtmlElement):
    """Implement the ``form`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["group", "presentation"])
        accept_charset: str
        action: str
        autocapitalize: Choices = AUTOCAPITALIZES
        autocomplete: Choices = cast(Choices, ["on", "off"])
        enctype: Choices = FORMENCTYPES
        method: Choices = cast(Choices, ["get", "post"])
        name: str
        target: str


class H(HtmlElement):  # noqa: E742  # pylint: disable=invalid-name
    """Can replace H* tags by passing a ``level`` prop."""

    class PropTypes:
        role: Choices = cast(Choices, ["tab", "presentation"])
        level: Required[Choices] = cast(Required[Choices], [1, 2, 3, 4, 5, 6])

    def __init__(self, **kwargs: Any) -> None:
        """Create the Hx* tag using the ``level`` prop.

        For the parameters, see ``Base.__init__``.

        """
        super().__init__(**kwargs)
        self.level = kwargs.pop("level")
        self.unset_prop("level")
        self.__tag__ = f"h{self.level}"


class _H(HtmlElement):
    """Base for normal H* elements."""


class H1(_H):
    """Implement the ``h1`` HTML tag."""


class H2(_H):
    """Implement the ``h2`` HTML tag."""


class H3(_H):
    """Implement the ``h3`` HTML tag."""


class H4(_H):
    """Implement the ``h4`` HTML tag."""


class H5(_H):
    """Implement the ``h5`` HTML tag."""


class H6(_H):
    """Implement the ``h6`` HTML tag."""


class Head(HtmlElement):
    """Implement the ``head`` HTML tag."""


class Header(HtmlElement):
    """Implement the ``header`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["group", "presentation"])


class Hr(HtmlElementNoChild):
    """Implement the ``hr`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["presentation"])


class Html(HtmlElement):
    """Implement the ``html`` HTML tag."""

    class PropTypes:
        xmlns: str
        xmlns__og: str
        xmlns__fb: str


class I(HtmlElement):  # noqa: E742  # pylint: disable=invalid-name
    """Implement the ``i`` HTML tag."""

    class PropTypes:
        role: str


class Iframe(HtmlElement):
    """Implement the ``iframe`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["application", "document", "img"])
        allowfullscreen: bool
        allowpaymentrequest: bool
        height: Number
        name: str
        referrerpolicy: Choices = REFERRERPOLICIES
        sandbox: str
        src: str
        srcdoc: str
        width: Number


class Img(HtmlElementNoChild):
    """Implement the ``img`` HTML tag."""

    class PropTypes:
        role: str
        alt: str
        crossorigin: Choices = CROSSORIGINS
        decoding: Choices = cast(Choices, ["sync", "async", "auto"])
        height: Number
        ismap: bool
        referrerpolicy: Choices = REFERRERPOLICIES
        sizes: str
        src: str
        srcset: str
        width: Number
        usemap: str


class Input(HtmlElementNoChild):
    """Implement the ``input`` HTML tag.

    The props defined in this class are the one available for each input types.
    Each type has its own class, ``InputXXX``, defining their own props.

    Notes
    -----
    An instance of ``Input`` is never constructed: an instance of a subclass is always returned
    to validate the correct props. This is done in the ``__new__`` method.

    Attributes
    ----------
    __types__ : dict
        Contains the class to use for each input types.

    """

    __types__: Dict[str, Type["Input"]] = {}
    __type__: str = ""

    class PropTypes:
        type: Choices = cast(
            Choices,
            [
                "button",
                "checkbox",
                "color",
                "date",
                "datetime-local",
                "email",
                "file",
                "hidden",
                "image",
                "month",
                "number",
                "password",
                "radio",
                "range",
                "reset",
                "search",
                "submit",
                "tel",
                "text",
                "time",
                "url",
                "week",
            ],
        )
        autocomplete: Choices = cast(
            Choices,
            [
                "off",
                "on",
                "name",
                "honorific-prefix",
                "given-name",
                "additional-name",
                "family-name",
                "honorific-suffix",
                "nickname",
                "email",
                "username",
                "new-password",
                "current-password",
                "organization-title",
                "organization",
                "street-address",
                "address-line1",
                "address-line2",
                "address-line3",
                "address-level4",
                "address-level3",
                "address-level2",
                "address-level1",
                "country",
                "country-name",
                "postal-code",
                "cc-name",
                "cc-given-name",
                "cc-additional-name",
                "cc-family-name",
                "cc-number",
                "cc-exp",
                "cc-exp-month",
                "cc-exp-year",
                "cc-csc",
                "cc-type",
                "transaction-currency",
                "transaction-amount",
                "language",
                "bday",
                "bday-day",
                "bday-month",
                "bday-year",
                "sex",
                "tel",
                "tel-country-code",
                "tel-national",
                "tel-area-code",
                "tel-local",
                "tel-local-prefix",
                "tel-local-suffix",
                "tel-extension",
                "url",
                "photo",
            ],
        )
        autofocus: bool
        disabled: bool
        form: str
        formaction: str
        formenctype: Choices = FORMENCTYPES
        formmethod: Choices = cast(Choices, ["get", "post"])
        formnovalidate: bool
        formtarget: str
        _list: str
        name: str

    @property
    def type(self) -> str:
        """Emulate the ``type`` prop for subclasses."""
        return self.__type__

    def __new__(cls, **kwargs: Any) -> "Input":
        """Create an instance of a subclass of ``Input``.

        If already a subclass, we raise if the ``type`` prop is passed. Then we create the instance.
        If the class is ``Input``, we ensure the type is present and valid, then we create an
        instance of a subclass.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            Props that will be passed to the instance to be created.

        Returns
        -------
        Input
            The newly created instance.

        Raises
        ------
        RequiredPropError
            If `cls` is ``Input`` and the ``type`` prop is not given.
        InvalidPropChoiceError
            If `cls` is ``Input`` and the ``type`` prop given but invalid.
        InvalidPropNameError
            If `cls` is a subclass and the ``type`` prop is given.

        """
        if not Input.__types__:

            # Add all subclasses to the ``__type__`` dict.
            def add(klass: Type[Input]) -> None:
                """Add all subclasses with ``__type__`` attr as available input type.

                Parameters
                ----------
                klass : type(Input)
                    The class for which to iterate on subclasses.

                """
                for subclass in klass.__subclasses__():
                    if getattr(subclass, "__type__", None):
                        Input.__types__[subclass.__type__] = subclass
                        subclass.__display_name__ = (
                            f"{subclass.__tag__} (input type={subclass.__type__})"
                        )
                    add(subclass)

            add(Input)

        if cls is not Input:
            # For a subclass, we don't accept the ``type`` prop.
            if "type" in kwargs:
                raise InvalidPropNameError(cls.__display_name__, "type")
            return super().__new__(cls)

        try:
            input_type: str = kwargs.pop("type")
        except KeyError:
            raise RequiredPropError("input", "type")
        else:
            if input_type not in Input.__types__:
                raise InvalidPropChoiceError(
                    "input", "type", input_type, list(Input.__types__.keys())
                )

        obj = super().__new__(Input.__types__[input_type])
        obj.__init__(**kwargs)
        return obj

    def __init__(self, **kwargs: Any) -> None:
        """Create the input and set its type prop and tag.

        Notes
        -----
        The ``Input`` class is never used to create an instance, it's always a subclass, thanks
        to ``__new__``.

        For the parameters, see ``Base.__init__``

        """
        if "type" not in kwargs:
            kwargs = dict(
                type=self.__type__, **kwargs
            )  # we force type to be first attr

        self.__tag__ = "input"  # replace fake tag (itext, inumber...)

        super().__init__(**kwargs)


class _KeyboardInput(Input):
    """Base for input types meant to be filled via keyboard."""

    class PropTypes:
        inputmode: Choices = INPUTMODES
        minlength: int
        maxlength: int
        pattern: str
        placeholder: str
        readonly: bool
        required: bool
        size: int
        spellcheck: Choices = cast(Choices, ["true", "false"])
        value: str


class InputButton(Input):
    """Implement the ``input type='button'`` HTML tag."""

    __tag__ = "ibutton"
    __type__ = "button"

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "link",
                "menuitem",
                "menuitemcheckbox",
                "menuitemradio",
                "radio",
                "switch",
                "tab",
            ],
        )


class InputCheckbox(Input):
    """Implement the ``input type='checkbox'`` HTML tag."""

    __tag__ = "icheckbox"
    __type__ = "checkbox"

    class PropTypes:
        role: Choices = cast(
            Choices, ["button", "menuitemcheckbox", "option", "switch"]
        )
        checked: bool
        required: bool


class InputImage(Input):
    """Implement the ``input type='image'`` HTML tag."""

    __tag__ = "iimage"
    __type__ = "image"

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "link",
                "menuitem",
                "menuitemcheckbox",
                "menuitemradio",
                "radio",
                "switch",
            ],
        )
        height: Number
        src: str
        width: Number


class InputRadio(Input):
    """Implement the ``input type='radio'`` HTML tag."""

    __tag__ = "iradio"
    __type__ = "radio"

    class PropTypes:
        role: Choices = cast(Choices, ["menuitemradio"])
        checked: bool
        required: bool


class InputColor(Input):
    """Implement the ``input type='color'`` HTML tag."""

    __tag__ = "icolor"
    __type__ = "color"

    class PropTypes:
        required: bool


class InputDate(Input):
    """Implement the ``input type='date'`` HTML tag."""

    __tag__ = "idate"
    __type__ = "date"

    class PropTypes:
        min: str
        max: str
        readonly: bool
        required: bool
        step: Union[str, Number]


class InputDateTimeLocal(Input):
    """Implement the ``input type='datetime'`` HTML tag."""

    __tag__ = "idatetimelocal"
    __type__ = "datetime-local"

    class PropTypes:
        min: str
        max: str
        readonly: bool
        required: bool
        step: Union[str, Number]


class InputEmail(_KeyboardInput):
    """Implement the ``input type='email'`` HTML tag."""

    __tag__ = "iemail"
    __type__ = "email"

    class PropTypes:
        multiple: bool


class InputFile(Input):
    """Implement the ``input type='file'`` HTML tag."""

    __tag__ = "ifile"
    __type__ = "file"

    class PropTypes:
        accept: str
        capture: bool
        multiple: bool
        required: bool


class InputHidden(Input):
    """Implement the ``input type='hidden'`` HTML tag."""

    __tag__ = "ihidden"
    __type__ = "hidden"


class InputMonth(Input):
    """Implement the ``input type='month'`` HTML tag."""

    __tag__ = "imonth"
    __type__ = "month"

    class PropTypes:
        readonly: bool
        required: bool


class InputNumber(_KeyboardInput):
    """Implement the ``input type='number'`` HTML tag."""

    __tag__ = "inumber"
    __type__ = "number"

    class PropTypes:
        min: Number
        max: Number
        step: Union[str, Number]


class InputPassword(_KeyboardInput):
    """Implement the ``input type='password'`` HTML tag."""

    __tag__ = "ipassword"
    __type__ = "password"

    class PropTypes:
        required: bool


class InputRange(Input):
    """Implement the ``input type='range'`` HTML tag."""

    __tag__ = "irange"
    __type__ = "range"

    class PropTypes:
        required: bool


class InputReset(Input):
    """Implement the ``input type='reset'`` HTML tag."""

    __tag__ = "ireset"
    __type__ = "reset"


class InputSearch(_KeyboardInput):
    """Implement the ``input type='search'`` HTML tag."""

    __tag__ = "isearch"
    __type__ = "search"


class InputSubmit(Input):
    """Implement the ``input type='submit'`` HTML tag."""

    __tag__ = "isubmit"
    __type__ = "submit"


class InputTel(_KeyboardInput):
    """Implement the ``input type='tel'`` HTML tag."""

    __tag__ = "itel"
    __type__ = "tel"


class InputText(_KeyboardInput):
    """Implement the ``input type='text'`` HTML tag."""

    __tag__ = "itext"
    __type__ = "text"


class InputUrl(_KeyboardInput):
    """Implement the ``input type='url'`` HTML tag."""

    __tag__ = "iurl"
    __type__ = "url"


class InputWeek(Input):
    """Implement the ``input type='week'`` HTML tag."""

    __tag__ = "iweek"
    __type__ = "week"

    class PropTypes:
        readonly: bool
        required: bool


class Ins(HtmlElement):
    """Implement the ``ins`` HTML tag."""

    class PropTypes:
        role: str
        cite: str
        datetime: str


class Kbd(HtmlElement):
    """Implement the ``kbd`` HTML tag."""

    class PropTypes:
        role: str


class Label(HtmlElement):
    """Implement the ``label`` HTML tag."""

    class PropTypes:
        _for: str
        form: str


class Legend(HtmlElement):
    """Implement the ``legend`` HTML tag."""


class Li(HtmlElement):
    """Implement the ``li`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "menuitem",
                "menuitemcheckbox",
                "menuitemradio",
                "option",
                "presentation",
                "radio",
                "separator",
                "tab",
                "treeitem",
            ],
        )
        value: int


class Link(HtmlElementNoChild):
    """Implement the ``link`` HTML tag."""

    class PropTypes:
        _as: str
        crossorigin: Choices = CROSSORIGINS
        href: str
        hreflang: str
        integrity: str
        media: str
        prefetch: str
        referrerpolicy: Choices = REFERRERPOLICIES
        rel: str
        sizes: str
        title: str
        type: str


class Main(HtmlElement):
    """Implement the ``main`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["main", "presentation"])


class Map(HtmlElement):
    """Implement the ``map`` HTML tag."""

    class PropTypes:
        name: str


class Mark(HtmlElement):
    """Implement the ``mark`` HTML tag."""

    class PropTypes:
        role: str


class Meta(HtmlElementNoChild):
    """Implement the ``meta`` HTML tag."""

    class PropTypes:
        charset: str
        content: str
        http_equiv: Choices = cast(Choices, ["content-security-policy", "refresh"])
        name: Choices = cast(
            Choices,
            [
                "application-name",
                "author",
                "description",
                "generator",
                "keywords",
                "referrer",
                "creator",
                "googlebot",
                "publisher",
                "robots",
                "slurp",
                "viewport",
            ],
        )


class Meter(HtmlElement):
    """Implement the ``meter`` HTML tag."""

    class PropTypes:
        value: Number
        min: Number
        max: Number
        low: Number
        high: Number
        optimum: Number
        form: str


class Nav(HtmlElement):
    """Implement the ``nav`` HTML tag."""


class Noscript(HtmlElement):
    """Implement the ``noscript`` HTML tag."""


class Object(HtmlElement):
    """Implement the ``object`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["application", "document", "image"])
        data: str
        form: str
        height: Number
        name: str
        type: str
        typemustmatch: bool
        usemap: str
        width: Number


class Ol(HtmlElement):
    """Implement the ``ol`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "directory",
                "group",
                "listbox",
                "menu",
                "menubar",
                "radiogroup",
                "tablist",
                "toolbar",
                "tree",
                "presentation",
            ],
        )
        reversed: bool
        start: int
        type: Choices = cast(Choices, ["1", "a", "A", "i", "I"])


class Optgroup(HtmlElement):
    """Implement the ``optgroup`` HTML tag."""

    class PropTypes:
        disabled: bool
        label: str


class Option(HtmlElement):
    """Implement the ``option`` HTML tag."""

    class PropTypes:
        disabled: bool
        label: str
        selected: bool
        value: str


class Output(HtmlElement):
    """Implement the ``output`` HTML tag."""

    class PropTypes:
        role: str
        _for: str
        form: str
        name: str


class P(HtmlElement):  # pylint: disable=invalid-name
    """Implement the ``p`` HTML tag."""

    class PropTypes:
        role: str


class Param(HtmlElement):
    """Implement the ``param`` HTML tag."""

    class PropTypes:
        name: str
        value: str


class Picture(HtmlElement):
    """Implement the ``picture`` HTML tag."""


class Pre(HtmlElement):
    """Implement the ``pre`` HTML tag."""

    class PropTypes:
        role: str


class Progress(HtmlElement):
    """Implement the ``progress`` HTML tag."""

    class PropTypes:
        max: Number
        value: Number


class Q(HtmlElement):  # pylint: disable=invalid-name
    """Implement the ``q`` HTML tag."""

    class PropTypes:
        role: str
        cite: str


class Rp(HtmlElement):
    """Implement the ``rp`` HTML tag."""

    class PropTypes:
        role: str


class Rt(HtmlElement):
    """Implement the ``rt`` HTML tag."""

    class PropTypes:
        role: str


class Rtc(HtmlElement):
    """Implement the ``rtc`` HTML tag."""

    class PropTypes:
        role: str


class Ruby(HtmlElement):
    """Implement the ``ruby`` HTML tag."""

    class PropTypes:
        role: str


class S(HtmlElement):  # pylint: disable=invalid-name
    """Implement the ``s`` HTML tag."""

    class PropTypes:
        role: str


class Samp(HtmlElement):
    """Implement the ``samp`` HTML tag."""

    class PropTypes:
        role: str


class Script(HtmlElement):
    """Implement the ``script`` HTML tag."""

    class PropTypes:
        _async: bool
        crossorigin: Choices = CROSSORIGINS
        defer: bool
        integrity: str
        nomodule: bool
        nonce: str
        src: str
        type: str


class Section(HtmlElement):
    """Implement the ``section`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "alert",
                "alertdialog",
                "application",
                "banner",
                "complementary",
                "contentinfo",
                "dialog",
                "document",
                "feed",
                "log",
                "main",
                "marquee",
                "navigation",
                "search",
                "status",
                "tabpanel",
            ],
        )


class Select(HtmlElement):
    """Implement the ``select`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["menu"])
        autofocus: bool
        disabled: bool
        form: str
        multiple: bool
        name: str
        required: bool
        size: int


class Slot(HtmlElement):
    """Implement the ``slot`` HTML tag."""

    class PropTypes:
        name: str


class Source(HtmlElementNoChild):
    """Implement the ``source`` HTML tag."""

    class PropTypes:
        sizes: str
        src: str
        srccet: str
        type: str
        media: str


class Span(HtmlElement):
    """Implement the ``span`` HTML tag."""

    class PropTypes:
        role: str


class Strong(HtmlElement):
    """Implement the ``strong`` HTML tag."""

    class PropTypes:
        role: str


class Style(HtmlElement):
    """Implement the ``style`` HTML tag."""

    class PropTypes:
        media: str
        nonce: str
        title: str
        type: str


class Sub(HtmlElement):
    """Implement the ``sub`` HTML tag."""

    class PropTypes:
        role: str


class Summary(HtmlElement):
    """Implement the ``summary`` HTML tag."""

    class PropTypes:
        role: Choices = cast(Choices, ["button"])


class Sup(HtmlElement):
    """Implement the ``sup`` HTML tag."""

    class PropTypes:
        role: str


class Table(HtmlElement):
    """Implement the ``table`` HTML tag."""

    class PropTypes:
        role: str


class Tbody(HtmlElement):
    """Implement the ``tbody`` HTML tag."""

    class PropTypes:
        role: str


class Td(HtmlElement):
    """Implement the ``td`` HTML tag."""

    class PropTypes:
        role: str
        colspan: int
        headers: str
        rowspan: int


class Template(HtmlElement):
    """Implement the ``template`` HTML tag."""


class Textarea(HtmlElement):
    """Implement the ``textarea`` HTML tag."""

    class PropTypes:
        autocapitalize: Choices = AUTOCAPITALIZES
        autocomplete: Choices = cast(Choices, ["on", "off"])
        autofocus: bool
        cols: int
        disabled: bool
        form: str
        maxlength: int
        minlength: int
        name: str
        placeholder: str
        readonly: bool
        required: bool
        wrap: Choices = cast(Choices, ["soft", "hard", "off"])


class Tfoot(HtmlElement):
    """Implement the ``tfoot`` HTML tag."""

    class PropTypes:
        role: str


class Th(HtmlElement):
    """Implement the ``th`` HTML tag."""

    class PropTypes:
        role: str
        abbr: str
        colspan: int
        headers: str
        rowspan: int
        scope: Choices = cast(Choices, ["row", "col", "rowgroup", "colgroup", "auto"])


class Thead(HtmlElement):
    """Implement the ``thead`` HTML tag."""

    class PropTypes:
        role: str


class Time(HtmlElement):
    """Implement the ``time`` HTML tag."""

    class PropTypes:
        role: str
        datetime: str


class Title(HtmlElement):
    """Implement the ``title`` HTML tag."""


class Tr(HtmlElement):
    """Implement the ``tr`` HTML tag."""

    class PropTypes:
        role: str


class Track(HtmlElementNoChild):
    """Implement the ``track`` HTML tag."""

    class PropTypes:
        default: bool
        kind: Choices = cast(
            Choices, ["subtitles", "captions", "descriptions", "chapters", "metadata"]
        )
        label: str
        src: str
        srclang: str


class U(HtmlElement):  # pylint: disable=invalid-name
    """Implement the ``u`` HTML tag."""

    class PropTypes:
        role: str


class Ul(HtmlElement):
    """Implement the ``ul`` HTML tag."""

    class PropTypes:
        role: Choices = cast(
            Choices,
            [
                "directory",
                "group",
                "listbox",
                "menu",
                "menubar",
                "radiogroup",
                "tablist",
                "toolbar",
                "tree",
                "presentation",
            ],
        )


class Var(HtmlElement):
    """Implement the ``var`` HTML tag."""

    class PropTypes:
        role: str


class Video(_Media):
    """Implement the ``video`` HTML tag."""

    class PropTypes:
        height: Number
        poster: str
        width: Number
        playsinline: bool


class Wbr(HtmlElement):
    """Implement the ``wbr`` HTML tag."""

    class PropTypes:
        role: str
