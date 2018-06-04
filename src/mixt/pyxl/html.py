#!/usr/bin/env python

from typing import Any, Union

from .utils import escape
from .base import Base, BaseMetaclass, BasePropTypes, Base, WithClass, Choices, Number, PyxlException

# for backwards compatibility.
from .browser_hacks import ConditionalComment

REFERRERPOLICIES = ['no-referrer', 'no-referrer-when-downgrade', 'origin', 'origin-when-cross-origin', 'strict-origin-when-cross-origin', 'unsafe-url']
CROSSORIGINS = ['', 'anonymous', 'use-credentials']
FORMENCTYPES = ['application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']
INPUTMODES = ['none, text, decimal, numeric, tel, search, email, url']
AUTOCAPITALIZES = ['sentences', 'none','words', 'characters']


_if_condition_stack = []
_last_if_condition = None

def _push_condition(cond):
    _if_condition_stack.append(cond)
    return cond

def _leave_if():
    global _last_if_condition
    _last_if_condition = _if_condition_stack.pop()
    return []

__tags__ = {}


class HtmlElementMetaclass(BaseMetaclass):
    def __init__(self, name, parents, attrs):
        if not attrs.get('__tag__'):
            attrs['__tag__'] =  name.lower()
        __tags__[attrs['__tag__']] = name
        super().__init__(name, parents, attrs)


class HtmlBaseElement(WithClass, metaclass=HtmlElementMetaclass):

    class PropTypes:
        accesskey: str
        autocapitalize: Choices = AUTOCAPITALIZES
        _class: str
        contenteditable: Choices = ['false', 'true']
        contextmenu: str
        dir:  Choices = ['auto', 'ltr', 'rtl']
        draggable: Choices = ['false', 'true']
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
        translate: Choices = ['', 'yes', 'no']
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

    def _render_attributes(self):
        result = []
        for name, value in self.props.items():
            html_name = BasePropTypes.__to_html__(name)
            if self.PropTypes.__is_bool__(name):
                if value:
                    result.extend((' ', html_name))
            else:
                result.extend((' ', html_name, '="', escape(value), '"'))
        return result

    def get_id(self):
        return self.prop('id')


class HtmlElement(HtmlBaseElement):
    def _to_list(self, l):
        l.append(f'<{self.__tag__}')
        l.extend(self._render_attributes())
        l.append('>')
        self._render_children_to_list(l)
        l.append(f'</{self.__tag__}>')


class HtmlElementNoChild(HtmlBaseElement):
    def append(self, child):
        raise Exception(f'<{self.__str_tag__}> does not allow children.')

    def _to_list(self, l):
        l.append(f'<{self.__tag__}')
        l.extend(self._render_attributes())
        l.append(' />')


class HtmlComment(Base):
    class PropTypes:
        comment: str

    def _to_list(self, l):
        pass

class HtmlDeclaration(Base):
    class PropTypes:
        decl: str

    def _to_list(self, l):
        l.extend(('<!', self.prop('decl'), '>'))

class HtmlMarkedDeclaration(Base):
    class PropTypes:
        decl: str

    def _to_list(self, l):
        l.extend(('<![', self.prop('decl'), ']]>'))

class HtmlMSDeclaration(Base):
    class PropTypes:
        decl: str

    def _to_list(self, l):
        l.extend(('<![', self.prop('decl'), ']>'))

class RawHtml(HtmlElementNoChild):
    class PropTypes:
        text: str

    def _to_list(self, l):
        if not isinstance(self.text, str):
            l.append(str(self.text, 'utf8'))
        else:
            l.append(self.text)

def Raw(text):
    return RawHtml(text=text)

class Fragment(WithClass):
    class PropTypes:
        id: str

    def _to_list(self, l):
        self._render_children_to_list(l)

    def get_id(self):
        return self.prop('id')


class _Hyperlink(HtmlElement):
    class PropTypes:
        download: Union[bool, str]
        href: str
        hreflang: str
        referrerpolicy: Choices = REFERRERPOLICIES
        rel: str
        target: str


class A(_Hyperlink):
    class PropTypes:
        role: Choices = ['button', 'checkbox', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'option', 'radio', 'switch', 'tab', 'treeitem']
        ping: str
        type: str

class Abbr(HtmlElement):
    pass

class Address(HtmlElement):
    pass

class Area(_Hyperlink):
    class PropTypes:
        alt: str
        coords: str
        media: str
        shape: Choices = ['rect', 'poly', 'default']

class Article(HtmlElement):
    class PropTypes:
        role: Choices = ['application', 'document', 'feed', 'main', 'presentation', 'region']

class Aside(HtmlElement):
    class PropTypes:
        role: Choices = ['feed', 'note', 'presentation', 'region', 'search']

class _Media(HtmlElement):
    class PropTypes:
        role: Choices = ['application']
        autoplay: bool
        controls: bool
        crossorigin: Choices = CROSSORIGINS
        loop: bool
        muted: bool
        preload: Choices = ['', 'auto', 'none', 'metadata']
        src: str

class Audio(_Media):
    pass

class B(HtmlElement):
    class PropTypes:
        role: str

class Base(HtmlElementNoChild):
    class PropTypes:
        href: str
        target: str

class Bdi(HtmlElement):
    class PropTypes:
        role: str

class Bdo(HtmlElement):
    class PropTypes:
        role: str
        dir: Choices = ['ltr', 'rtl']

class Blockquote(HtmlElement):
    class PropTypes:
        role: str
        cite: str

class Body(HtmlElement):
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
    class PropTypes:
        role: str

class Button(HtmlElement):
    class PropTypes:
        role: Choices = ['checkbox', 'link', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'radio', 'switch', 'tab']
        autofocus: bool
        autocomplete: Choices = ['off']
        disabled: bool
        form: str
        formaction: str
        formenctype: Choices = FORMENCTYPES
        formmethod: Choices = ['get', 'post']
        formnovalidate: bool
        formtarget: str
        name: str
        type: Choices = ['submit', 'reset', 'button']
        value: Any

class Canvas(HtmlElement):
    class PropTypes:
        role: str
        height: Number
        width: Number

class Caption(HtmlElement):
   pass

class Cite(HtmlElement):
    class PropTypes:
       role: str

class Code(HtmlElement):
    class PropTypes:
       role: str

class Col(HtmlElementNoChild):
    class PropTypes:
        span: int

class Colgroup(HtmlElement):
    class PropTypes:
        span: int

class Data(HtmlElement):
    class PropTypes:
        value: str

class Datalist(HtmlElement):
    pass

class Dd(HtmlElement):
    pass

class Del(HtmlElement):
    class PropTypes:
        role: str
        cite: str
        datetime: str

class Details(HtmlElement):
    class PropTypes:
        open: bool

class Dfn(HtmlElement):
    class PropTypes:
        role: str

class Div(HtmlElement):
    class PropTypes:
        role: str

class Dl(HtmlElement):
    class PropTypes:
        role: Choices = ['group', 'presentation']

class Dt(HtmlElement):
    pass

class Em(HtmlElement):
    class PropTypes:
        role: str

class Embed(HtmlElement):
    class PropTypes:
        role: Choices = ['application', 'document', 'img', 'presentation']
        height: Number
        src: str
        type: str
        widht: str

class Fieldset(HtmlElement):
    class PropTypes:
        role: Choices = ['group', 'presentation']
        disabled: bool
        form: str
        name: str

class Figcaption(HtmlElement):
    class PropTypes:
        role: Choices = ['group', 'presentation']

class Figure(HtmlElement):
    class PropTypes:
        role: Choices = ['group', 'presentation']

class Footer(HtmlElement):
    class PropTypes:
        role: Choices = ['group', 'presentation']

class Form(HtmlElement):
    class PropTypes:
        role: Choices = ['group', 'presentation']
        accept_charset: str
        action: str
        autocapitalize: Choices = AUTOCAPITALIZES
        autocomplete: Choices = ['on', 'off']
        enctype: Choices = FORMENCTYPES
        method: Choices = ['get', 'post']
        name: str
        target: str

class _H(HtmlElement):
    role: Choices = ['tab', 'presentation']

class H1(_H): ...
class H2(_H): ...
class H3(_H): ...
class H4(_H): ...
class H5(_H): ...
class H6(_H): ...

class Head(HtmlElement):
    pass

class Header(HtmlElement):
    class PropTypes:
        role: Choices = ['group', 'presentation']

class Hr(HtmlElementNoChild):
    class PropTypes:
        role: Choices = ['presentation']

class Html(HtmlElement):
    class PropTypes:
        xmlns: str
        xmlns__og: str
        xmlns__fb: str

class I(HtmlElement):
    class PropTypes:
        role: str

class Iframe(HtmlElement):
    class PropTypes:
        role: Choices = ['application', 'document', 'img']
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
    class PropTypes:
        role: str
        alt: str
        crossorigin: Choices = CROSSORIGINS
        decoding: Choices = ['sync', 'async', 'auto']
        height: Number
        ismap: bool
        referrerpolicy: Choices = REFERRERPOLICIES
        sizes: str
        src: str
        srcset: str
        width: Number
        usemap: str

class Input(HtmlElementNoChild):
    class PropTypes:
        type: Choices = ['button', 'checkbox', 'color', 'date', 'datetime-local', 'email', 'file', 'hidden', 'image', 'month', 'number', 'password', 'radio', 'range', 'reset', 'search', 'submit', 'tel', 'text', 'time', 'url', 'week']
        autocomplete: Choices = ['off', 'on', 'name', 'honorific-prefix', 'given-name', 'additional-name', 'family-name', 'honorific-suffix', 'nickname', 'email', 'username', 'new-password', 'current-password', 'organization-title', 'organization', 'street-address', 'address-line1', 'address-line2', 'address-line3', 'address-level4', 'address-level3', 'address-level2', 'address-level1', 'country', 'country-name', 'postal-code', 'cc-name', 'cc-given-name', 'cc-additional-name', 'cc-family-name', 'cc-number', 'cc-exp', 'cc-exp-month', 'cc-exp-year', 'cc-csc', 'cc-type', 'transaction-currency', 'transaction-amount', 'language', 'bday', 'bday-day', 'bday-month', 'bday-year', 'sex', 'tel', 'tel-country-code', 'tel-national', 'tel-area-code', 'tel-local', 'tel-local-prefix', 'tel-local-suffix', 'tel-extension', 'url', 'photo']
        autofocus: bool
        disabled: bool
        form: str
        formaction: str
        formenctype: Choices = FORMENCTYPES
        formmethod: Choices = ['get', 'post']
        formnovalidate: bool
        formtarget: str
        _list: str
        name: str

    __types__ = {}

    def __new__(cls, **kwargs):
        if not Input.__types__:
            def add(klass):
                for subclass in klass.__subclasses__():
                    if hasattr(subclass, '__type__'):
                        Input.__types__[subclass.__type__] = subclass
                        subclass.__str_tag__ = f'{subclass.__tag__} (input type={subclass.__type__})'
                    add(subclass)
            add(Input)

        if cls is not Input:
            if 'type' in kwargs:
                raise PyxlException(f'<{cls.__str_tag__}>.type: must not be set')
            return super().__new__(cls)

        try:
            type = kwargs.pop('type')
        except KeyError:
            raise PyxlException(f'<input>.type: is required but not set')

        obj = super().__new__(Input.__types__[type])
        obj.__init__(**kwargs)
        return obj

    def _to_list(self, l):
        if self.__class__ is Input:
            super()._to_list(l)
        else:
            l.append(f'<input type="{self.__type__}"')
            l.extend(self._render_attributes())
            l.append(' />')

class _KeyboardInput(Input):
    class PropTypes:
        inputmode: Choices = INPUTMODES
        minlength: int
        maxlength: int
        pattern: str
        placeholder: str
        readonly: bool
        required: bool
        size: int
        spellcheck: Choices = ['true', 'false']
        value: str

class InputButton(Input):
    __tag__ = 'ibutton'
    __type__ = 'button'
    class PropTypes:
        role: Choices = ['link', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'radio', 'switch', 'tab']

class InputCheckbox(Input):
    __tag__ = 'icheckbox'
    __type__ = 'checkbox'
    class PropTypes:
        role: Choices = ['button', 'menuitemcheckbox', 'option', 'switch']
        checked: bool
        required: bool

class InputImage(Input):
    __tag__ = 'iimage'
    __type__ = 'image'
    class PropTypes:
        role: Choices = ['link', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'radio', 'switch']
        height: Number
        src: str
        width: Number

class InputRadio(Input):
    __tag__ = 'iradio'
    __type__ = 'radio'
    class PropTypes:
        role: Choices = ['menuitemradio']
        checked: bool
        required: bool

class InputColor(Input):
    __tag__ = 'icolor'
    __type__ = 'color'
    class PropTypes:
        required: bool

class InputDate(Input):
    __tag__ = 'idate'
    __type__ = 'date'
    class PropTypes:
        min: str
        max: str
        readonly: bool
        required: bool
        step: Union[str, Number]

class InputDateTimeLocal(Input):
    __tag__ = 'idatetimelocal'
    __type__ = 'datetime-local'
    class PropTypes:
        min: str
        max: str
        readonly: bool
        required: bool
        step: Union[str, Number]

class InputEmail(_KeyboardInput):
    __tag__ = 'iemail'
    __type__ = 'email'
    class PropTypes:
        multiple: bool

class InputFile(Input):
    __tag__ = 'ifile'
    __type__ = 'file'
    class PropTypes:
        accept: str
        capture: bool
        multiple: bool
        required: bool

class InputHidden(Input):
    __tag__ = 'ihidden'
    __type__ = 'hidden'

class InputMonth(Input):
    __tag__ = 'imonth'
    __type__ = 'month'
    class PropTypes:
        readonly: bool
        required: bool

class InputNumber(_KeyboardInput):
    __tag__ = 'inumber'
    __type__ = 'number'
    class PropTypes:
        min: Number
        max: Number
        step: Union[str, Number]

class InputPassword(_KeyboardInput):
    __tag__ = 'ipassword'
    __type__ = 'password'
    class PropTypes:
        required: bool

class InputRange(Input):
    __tag__ = 'irange'
    __type__ = 'range'
    class PropTypes:
        required: bool

class InputReset(Input):
    __tag__ = 'ireset'
    __type__ = 'reset'

class InputSearch(_KeyboardInput):
    __tag__ = 'isearch'
    __type__ = 'search'

class InputSubmit(Input):
    __tag__ = 'isubmit'
    __type__ = 'submit'

class InputTel(_KeyboardInput):
    __tag__ = 'itel'
    __type__ = 'tel'

class InputText(_KeyboardInput):
    __tag__ = 'itext'
    __type__ = 'text'

class InputUrl(_KeyboardInput):
    __tag__ = 'iurl'
    __type__ = 'url'

class InputWeek(Input):
    __tag__ = 'iweek'
    __type__ = 'week'
    class PropTypes:
        readonly: bool
        required: bool

class Ins(HtmlElement):
    class PropTypes:
        role: str
        cite: str
        datetime: str

class Kbd(HtmlElement):
    class PropTypes:
        role: str

class Label(HtmlElement):
    class PropTypes:
        _for: str
        form: str

class Legend(HtmlElement):
   pass

class Li(HtmlElement):
    class PropTypes:
        role: Choices = ['menuitem', 'menuitemcheckbox', 'menuitemradio', 'option', 'presentation', 'radio', 'separator', 'tab', 'treeitem']
        value: int

class Link(HtmlElementNoChild):
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
    class PropTypes:
        role: Choices = ['main', 'presentation']

class Map(HtmlElement):
    class PropTypes:
        name: str

class Mark(HtmlElement):
    class PropTypes:
        role: str

class Meta(HtmlElementNoChild):
    class PropTypes:
        charset: str
        content: str
        http_equiv: Choices = ['content-security-policy', 'refresh']
        name: Choices = ['application-name', 'author', 'description', 'generator', 'keywords', 'referrer', 'creator', 'googlebot', 'publisher', 'robots', 'slurp', 'viewport']

class Meter(HtmlElement):
    class PropTypes:
        value: Number
        min: Number
        max: Number
        low: Number
        high: Number
        optimum: Number
        form: str

class Nav(HtmlElement):
    pass

class Noscript(HtmlElement):
   pass

class Object(HtmlElement):
    class PropTypes:
        role: Choices = ['application', 'document', 'image']
        data: str
        form: str
        height: Number
        name: str
        type: str
        typemustmatch: bool
        usemap: str
        width: Number

class Ol(HtmlElement):
    class PropTypes:
        role: Choices = ['directory', 'group', 'listbox', 'menu', 'menubar', 'radiogroup', 'tablist', 'toolbar', 'tree', 'presentation']
        reversed: bool
        start: int
        type: Choices = ['1', 'a', 'A', 'i', 'I']

class Optgroup(HtmlElement):
    class PropTypes:
        disabled: bool
        label: str

class Option(HtmlElement):
    class PropTypes:
        disabled: bool
        label: str
        selected: bool
        value: str

class Output(HtmlElement):
    class PropTypes:
        role: str
        _for: str
        form: str
        name: str


class P(HtmlElement):
    class PropTypes:
        role: str

class Param(HtmlElement):
    class PropTypes:
        name: str
        value: str

class Picture(HtmlElement):
    pass

class Pre(HtmlElement):
    class PropTypes:
        role: str

class Progress(HtmlElement):
    class PropTypes:
        max: Number
        value: Number

class Q(HtmlElement):
    class PropTypes:
        role: str
        cite: str

class Rp(HtmlElement):
    class PropTypes:
        role: str

class Rt(HtmlElement):
    class PropTypes:
        role: str

class Rtc(HtmlElement):
    class PropTypes:
        role: str

class Ruby(HtmlElement):
    class PropTypes:
        role: str

class S(HtmlElement):
    class PropTypes:
        role: str

class Samp(HtmlElement):
    class PropTypes:
        role: str

class Script(HtmlElement):
    class PropTypes:
        async: bool
        crossorigin: Choices = CROSSORIGINS
        defer: bool
        integrity: str
        nomodule: bool
        nonce: str
        src: str
        type: str

class Section(HtmlElement):
    class PropTypes:
        role: Choices = ['alert', 'alertdialog', 'application', 'banner', 'complementary', 'contentinfo', 'dialog', 'document', 'feed', 'log', 'main', 'marquee', 'navigation', 'search', 'status', 'tabpanel']

class Select(HtmlElement):
    class PropTypes:
        role: Choices = ['menu']
        autofocus: bool
        disabled: bool
        form: str
        multiple: bool
        name: str
        required: bool
        size: int

class Slot(HtmlElement):
    class PropTypes:
        name: str

class Source(HtmlElementNoChild):
    class PropTypes:
        sizes: str
        src: str
        srccet: str
        type: str
        media: str

class Span(HtmlElement):
    class PropTypes:
        role: str

class Strong(HtmlElement):
    class PropTypes:
        role: str

class Style(HtmlElement):
    class PropTypes:
        media: str
        nonce: str
        title: str
        type: str

class Sub(HtmlElement):
    class PropTypes:
        role: str

class Summary(HtmlElement):
    class PropTypes:
        role: Choices = ['button']

class Sup(HtmlElement):
    class PropTypes:
        role: str

class Table(HtmlElement):
    class PropTypes:
        role: str

class Tbody(HtmlElement):
    class PropTypes:
        role: str

class Td(HtmlElement):
    class PropTypes:
        role: str
        colspan: int
        headers: str
        rowspan: int

class Template(HtmlElement):
    pass

class Textarea(HtmlElement):
    class PropTypes:
        autocapitalize: Choices = AUTOCAPITALIZES
        autocomplete: Choices = ['on', 'off']
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
        wrap: Choices = ['soft', 'hard', 'off']

class Tfoot(HtmlElement):
    class PropTypes:
        role: str

class Th(HtmlElement):
    class PropTypes:
        role: str
        abbr: str
        colspan: int
        headers: str
        rowspan: int
        scope: Choices = ['row', 'col', 'rowgroup', 'colgroup', 'auto']

class Thead(HtmlElement):
    class PropTypes:
        role: str

class Time(HtmlElement):
    class PropTypes:
        role: str
        datetime: str

class Title(HtmlElement):
   pass

class Tr(HtmlElement):
    class PropTypes:
        role: str

class Track(HtmlElementNoChild):
    class PropTypes:
        default: bool
        kind: Choices = ['subtitles', 'captions', 'descriptions', 'chapters', 'metadata']
        label: str
        src: str
        srclang: str

class U(HtmlElement):
    class PropTypes:
        role: str

class Ul(HtmlElement):
    class PropTypes:
        role: Choices = ['directory', 'group', 'listbox', 'menu', 'menubar', 'radiogroup', 'tablist', 'toolbar', 'tree', 'presentation']

class Var(HtmlElement):
    class PropTypes:
        role: str

class Video(_Media):
    class PropTypes:
        height: Number
        poster: str
        width: Number
        playsinline: bool

class Wbr:
    class PropTypes:
        role: str
