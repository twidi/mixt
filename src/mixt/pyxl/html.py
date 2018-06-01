#!/usr/bin/env python

from .utils import escape
from .base import Base, BaseMetaclass

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
        super().__init__(name, parents, attrs)
        setattr(self, '__tag__', name.lower())


class HtmlBaseElement(Base, metaclass=HtmlElementMetaclass):
    def _render_attributes(self):
        result = []
        for name, value in self.__attributes__.items():
            html_name = self.Attrs.to_html(name)
            if self.Attrs.type(name) is bool:
                if value:
                    result.extend((' ', html_name))
            else:
                result.extend((' ', html_name, '="', escape(value), '"'))
        return result

class HtmlElement(HtmlBaseElement):
    def _to_list(self, l):
        l.extend(('<', self.__tag__))
        l.extend(self._render_attributes())
        l.append('>')

        for child in self.__children__:
            self._render_child_to_list(child, l)

        l.extend(('</', self.__tag__, '>'))


class HtmlElementNoChild(HtmlBaseElement):
    def append(self, child):
        raise Exception('<%s> does not allow children.', self.__tag__)

    def _to_list(self, l):
        l.extend(('<', self.__tag__))
        l.extend(self._render_attributes())
        l.append(' />')


class HtmlComment(Base):
    class Attrs:
        comment: str

    def _to_list(self, l):
        pass

class HtmlDeclaration(Base):
    class Attrs:
        decl: str

    def _to_list(self, l):
        l.extend(('<!', self.attr('decl'), '>'))

class HtmlMarkedDeclaration(Base):
    class Attrs:
        decl: str

    def _to_list(self, l):
        l.extend(('<![', self.attr('decl'), ']]>'))

class HtmlMSDeclaration(Base):
    class Attrs:
        decl: str

    def _to_list(self, l):
        l.extend(('<![', self.attr('decl'), ']>'))

class RawHtml(HtmlElementNoChild):
    class Attrs:
        text: str

    def _to_list(self, l):
        if not isinstance(self.text, str):
            l.append(str(self.text, 'utf8'))
        else:
            l.append(self.text)

def Raw(text):
    return RawHtml(text=text)

class Fragment(Base):
    def _to_list(self, l):
        for child in self.__children__:
            self._render_child_to_list(child, l)

class A(HtmlElement):
    class Attrs:
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
    class Attrs:
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
    class Attrs:
        src: str

class B(HtmlElement):
   pass

class Big(HtmlElement):
   pass

class Blockquote(HtmlElement):
    class Attrs:
        cite: str

class Body(HtmlElement):
    class Attrs:
        contenteditable: str

class Br(HtmlElementNoChild):
   pass

class Button(HtmlElement):
    class Attrs:
        disabled: bool
        name: str
        type: str
        value: str

class Canvas(HtmlElement):
    class Attrs:
        height: str
        width: str

class Caption(HtmlElement):
   pass

class Cite(HtmlElement):
   pass

class Code(HtmlElement):
   pass

class Col(HtmlElementNoChild):
    class Attrs:
        align: str
        char: str
        charoff: int
        span: int
        valign: str
        width: str

class Colgroup(HtmlElement):
    class Attrs:
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
    class Attrs:
        cite: str
        datetime: str

class Div(HtmlElement):
   class Attrs:
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
    class Attrs:
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
    class Attrs:
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
    class Attrs:
        frameborder: str
        longdesc: str
        marginheight: str
        marginwidth: str
        name: str
        noresize: str
        scrolling: str
        src: str

class Frameset(HtmlElement):
    class Attrs:
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
    class Attrs:
        profile: str

class Header(HtmlElement):
    pass

class Hr(HtmlElementNoChild):
    pass

class Html(HtmlElement):
    class Attrs:
        content: str
        scheme: str
        http_equiv: str
        xmlns: str
        xmlns__og: str
        xmlns__fb: str

class I(HtmlElement):
   pass

class Iframe(HtmlElement):
    class Attrs:
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
    class Attrs:
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
    class Attrs:
        alt: str
        src: str
        height: str
        ismap: bool
        longdesc: str
        usemap: str
        vspace: str
        width: str

class Input(HtmlElementNoChild):
    class Attrs:
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
    class Attrs:
        cite: str
        datetime: str

class Kbd(HtmlElement):
    pass

class Label(HtmlElement):
    class Attrs:
        _for: str

class Legend(HtmlElement):
   pass

class Li(HtmlElement):
   pass

class Link(HtmlElementNoChild):
    class Attrs:
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
    class Attrs:
        role: str

class Map(HtmlElement):
    class Attrs:
        name: str

class Meta(HtmlElementNoChild):
    class Attrs:
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
    class Attrs:
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
    class Attrs:
        disabled: bool
        label: str

class Option(HtmlElement):
    class Attrs:
        disabled: bool
        label: str
        selected: bool
        value: str

class P(HtmlElement):
   pass

class Param(HtmlElement):
    class Attrs:
        name: str
        type: str
        value: str
        valuetype: str

class Pre(HtmlElement):
   pass

class Progress(HtmlElement):
    class Attrs:
        max: int
        value: int

class Q(HtmlElement):
    class Attrs:
        cite: str

class Samp(HtmlElement):
   pass

class Script(HtmlElement):
    class Attrs:
        async: bool
        charset: str
        defer: bool
        src: str
        type: str

class Section(HtmlElement):
    pass

class Select(HtmlElement):
    class Attrs:
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
    class Attrs:
        media: str
        type: str

class Sub(HtmlElement):
   pass

class Sup(HtmlElement):
   pass

class Table(HtmlElement):
    class Attrs:
        border: str
        cellpadding: str
        cellspacing: str
        frame: str
        rules: str
        summary: str
        width: str

class Tbody(HtmlElement):
    class Attrs:
        align: str
        char: str
        charoff: str
        valign: str

class Td(HtmlElement):
    class Attrs:
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
    class Attrs:
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
    class Attrs:
        align: str
        char: str
        charoff: str
        valign: str

class Th(HtmlElement):
    class Attrs:
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
    class Attrs:
        align: str
        char: str
        charoff: str
        valign: str

class Time(HtmlElement):
    class Attrs:
        datetime: str

class Title(HtmlElement):
   pass

class Tr(HtmlElement):
    class Attrs:
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
