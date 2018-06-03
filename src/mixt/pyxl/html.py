#!/usr/bin/env python

from .utils import escape
from .base import Base, BaseMetaclass, BasePropTypes, Base, WithClass

# for backwards compatibility.
from .browser_hacks import ConditionalComment

_if_condition_stack = []
_last_if_condition = None

def _push_condition(cond):
    _if_condition_stack.append(cond)
    return cond

def _leave_if():
    global _last_if_condition
    _last_if_condition = _if_condition_stack.pop()
    return []


class HtmlElementMetaclass(BaseMetaclass):
    def __init__(self, name, parents, attrs):
        attrs['__tag__'] =  name.lower()
        super().__init__(name, parents, attrs)


class HtmlBaseElement(WithClass, metaclass=HtmlElementMetaclass):

    class PropTypes:
        # HTML attributes
        accesskey: str
        _class: str
        dir: str
        id: str
        lang: str
        maxlength: str
        role: str
        style: str
        tabindex: int
        title: str
        xmllang: str

        # Microdata HTML attributes
        itemtype: str
        itemscope: str
        itemprop: str
        itemid: str
        itemref: str

        # JS attributes
        onabort: str
        onblur: str
        onchange: str
        onclick: str
        ondblclick: str
        onerror: str
        onfocus: str
        onkeydown: str
        onkeypress: str
        onkeyup: str
        onload: str
        onmousedown: str
        onmouseenter: str
        onmouseleave: str
        onmousemove: str
        onmouseout: str
        onmouseover: str
        onmouseup: str
        onreset: str
        onresize: str
        onselect: str
        onsubmit: str
        onunload: str

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
        l.extend(('<', self.__tag__))
        l.extend(self._render_attributes())
        l.append('>')
        self._render_children_to_list(l)
        l.extend(('</', self.__tag__, '>'))


class HtmlElementNoChild(HtmlBaseElement):
    def append(self, child):
        raise Exception('<%s> does not allow children.', self.__tag__)

    def _to_list(self, l):
        l.extend(('<', self.__tag__))
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


class A(HtmlElement):
    class PropTypes:
        href: str
        rel: str
        type: str
        name: str
        target: str
        download: str

class Abbr(HtmlElement):
    pass

class Acronym(HtmlElement):
    pass

class Address(HtmlElement):
    pass

class Area(HtmlElementNoChild):
    class PropTypes:
        alt: str
        coords: str
        href: str
        nohref: str
        target: str

class Article(HtmlElement):
    pass

class Aside(HtmlElement):
    pass

class Audio(HtmlElement):
    class PropTypes:
        src: str

class B(HtmlElement):
   pass

class Big(HtmlElement):
   pass

class Blockquote(HtmlElement):
    class PropTypes:
        cite: str

class Body(HtmlElement):
    class PropTypes:
        contenteditable: str

class Br(HtmlElementNoChild):
   pass

class Button(HtmlElement):
    class PropTypes:
        disabled: bool
        name: str
        type: str
        value: str

class Canvas(HtmlElement):
    class PropTypes:
        height: str
        width: str

class Caption(HtmlElement):
   pass

class Cite(HtmlElement):
   pass

class Code(HtmlElement):
   pass

class Col(HtmlElementNoChild):
    class PropTypes:
        align: str
        char: str
        charoff: int
        span: int
        valign: str
        width: str

class Colgroup(HtmlElement):
    class PropTypes:
        align: str
        char: str
        charoff: int
        span: int
        valign: str
        width: str

class Datalist(HtmlElement):
    pass

class Dd(HtmlElement):
   pass

class Del(HtmlElement):
    class PropTypes:
        cite: str
        datetime: str

class Div(HtmlElement):
   class PropTypes:
        contenteditable: str

class Dfn(HtmlElement):
   pass

class Dl(HtmlElement):
   pass

class Dt(HtmlElement):
   pass

class Em(HtmlElement):
   pass

class Embed(HtmlElement):
    class PropTypes:
        src: str
        width: str
        height: str
        allowscriptaccess: str
        allowfullscreen: str
        name: str
        type: str

class Figure(HtmlElement):
   pass

class Figcaption(HtmlElement):
   pass

class Fieldset(HtmlElement):
   pass

class Footer(HtmlElement):
    pass

class Form(HtmlElement):
    class PropTypes:
        action: str
        accept: str
        accept_charset: str
        autocomplete: str
        enctype: str
        method: str
        name: str
        novalidate: bool
        target: str

class Frame(HtmlElementNoChild):
    class PropTypes:
        frameborder: str
        longdesc: str
        marginheight: str
        marginwidth: str
        name: str
        noresize: str
        scrolling: str
        src: str

class Frameset(HtmlElement):
    class PropTypes:
        rows: str
        cols: str

class H1(HtmlElement):
   pass

class H2(HtmlElement):
   pass

class H3(HtmlElement):
   pass

class H4(HtmlElement):
   pass

class H5(HtmlElement):
   pass

class H6(HtmlElement):
   pass

class Head(HtmlElement):
    class PropTypes:
        profile: str

class Header(HtmlElement):
    pass

class Hr(HtmlElementNoChild):
    pass

class Html(HtmlElement):
    class PropTypes:
        content: str
        scheme: str
        http_equiv: str
        xmlns: str
        xmlns__og: str
        xmlns__fb: str

class I(HtmlElement):
   pass

class Iframe(HtmlElement):
    class PropTypes:
        frameborder: str
        height: str
        longdesc: str
        marginheight: str
        marginwidth: str
        name: str
        sandbox: str
        scrolling: str
        src: str
        width: str
        # rk: 'allowTransparency' is not in W3C's HTML spec, but it's supported in most modern browsers.
        allowtransparency: str
        allowfullscreen: bool

class Video(HtmlElement):
    class PropTypes:
        autoplay: bool
        controls: str
        height: str
        loop: bool
        muted: bool
        poster: str
        preload: str
        src: str
        width: str

class Img(HtmlElementNoChild):
    class PropTypes:
        alt: str
        src: str
        height: str
        ismap: bool
        longdesc: str
        usemap: str
        vspace: str
        width: str

class Input(HtmlElementNoChild):
    class PropTypes:
        accept: str
        align: str
        alt: str
        autofocus: bool
        checked: bool
        disabled: bool
        list: str
        max: str
        maxlength: str
        min: str
        name: str
        pattern: str
        placeholder: str
        readonly: str
        size: str
        src: str
        step: str
        type: str
        value: str
        autocomplete: str
        autocorrect: str
        required: bool
        spellcheck: str
        multiple: bool

class Ins(HtmlElement):
    class PropTypes:
        cite: str
        datetime: str

class Kbd(HtmlElement):
    pass

class Label(HtmlElement):
    class PropTypes:
        _for: str

class Legend(HtmlElement):
   pass

class Li(HtmlElement):
   pass

class Link(HtmlElementNoChild):
    class PropTypes:
        charset: str
        href: str
        hreflang: str
        media: str
        rel: str
        rev: str
        sizes: str
        target: str
        type: str

class Main(HtmlElement):
    # we are not enforcing the w3 spec of one and only one main element on the
    # page
    class PropTypes:
        role: str

class Map(HtmlElement):
    class PropTypes:
        name: str

class Meta(HtmlElementNoChild):
    class PropTypes:
        content: str
        http_equiv: str
        name: str
        property: str
        scheme: str
        charset: str

class Nav(HtmlElement):
    pass

class Noframes(HtmlElement):
   pass

class Noscript(HtmlElement):
   pass

class Object(HtmlElement):
    class PropTypes:
        align: str
        archive: str
        border: str
        classid: str
        codebase: str
        codetype: str
        data: str
        declare: bool
        height: str
        hspace: str
        name: str
        standby: str
        type: str
        usemap: str
        vspace: str
        width: str

class Ol(HtmlElement):
   pass

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

class P(HtmlElement):
   pass

class Param(HtmlElement):
    class PropTypes:
        name: str
        type: str
        value: str
        valuetype: str

class Pre(HtmlElement):
   pass

class Progress(HtmlElement):
    class PropTypes:
        max: int
        value: int

class Q(HtmlElement):
    class PropTypes:
        cite: str

class Samp(HtmlElement):
   pass

class Script(HtmlElement):
    class PropTypes:
        async: bool
        charset: str
        defer: bool
        src: str
        type: str

class Section(HtmlElement):
    pass

class Select(HtmlElement):
    class PropTypes:
        disabled: bool
        multiple: bool
        name: str
        size: str
        required: bool

class Small(HtmlElement):
   pass

class Span(HtmlElement):
   pass

class Strong(HtmlElement):
   pass

class Style(HtmlElement):
    class PropTypes:
        media: str
        type: str

class Sub(HtmlElement):
   pass

class Sup(HtmlElement):
   pass

class Table(HtmlElement):
    class PropTypes:
        border: str
        cellpadding: str
        cellspacing: str
        frame: str
        rules: str
        summary: str
        width: str

class Tbody(HtmlElement):
    class PropTypes:
        align: str
        char: str
        charoff: str
        valign: str

class Td(HtmlElement):
    class PropTypes:
        abbr: str
        align: str
        axis: str
        char: str
        charoff: str
        colspan: str
        headers: str
        rowspan: str
        scope: str
        valign: str

class Textarea(HtmlElement):
    class PropTypes:
        cols: str
        rows: str
        disabled: bool
        placeholder: str
        name: str
        readonly: bool
        autocorrect: str
        autocomplete: str
        autocapitalize: str
        spellcheck: str
        autofocus: str
        required: bool

class Tfoot(HtmlElement):
    class PropTypes:
        align: str
        char: str
        charoff: str
        valign: str

class Th(HtmlElement):
    class PropTypes:
        abbr: str
        align: str
        axis: str
        char: str
        charoff: str
        colspan: str
        rowspan: str
        scope: str
        valign: str

class Thead(HtmlElement):
    class PropTypes:
        align: str
        char: str
        charoff: str
        valign: str

class Time(HtmlElement):
    class PropTypes:
        datetime: str

class Title(HtmlElement):
   pass

class Tr(HtmlElement):
    class PropTypes:
        align: str
        char: str
        charoff: str
        valign: str

class Tt(HtmlElement):
    pass

class U(HtmlElement):
    pass

class Ul(HtmlElement):
    pass

class Var(HtmlElement):
    pass
