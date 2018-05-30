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
            result.extend((' ', name, '="', escape(value), '"'))
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
    __attrs__ = {
        'comment': str,
        }

    def _to_list(self, l):
        pass

class HtmlDeclaration(Base):
    __attrs__ = {
        'decl': str,
        }

    def _to_list(self, l):
        l.extend(('<!', self.attr('decl'), '>'))

class HtmlMarkedDeclaration(Base):
    __attrs__ = {
        'decl': str,
        }

    def _to_list(self, l):
        l.extend(('<![', self.attr('decl'), ']]>'))

class HtmlMSDeclaration(Base):
    __attrs__ = {
        'decl': str,
        }

    def _to_list(self, l):
        l.extend(('<![', self.attr('decl'), ']>'))

class RawHtml(HtmlElementNoChild):
    __attrs__= {
        'text': str,
        }

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
    __attrs__ = {
        'href': str,
        'rel': str,
        'type': str,
        'name': str,
        'target': str,
        'download': str,
        }

class Abbr(HtmlElement):
    pass

class Acronym(HtmlElement):
    pass

class Address(HtmlElement):
    pass

class Area(HtmlElementNoChild):
    __attrs__ = {
        'alt': str,
        'coords': str,
        'href': str,
        'nohref': str,
        'target': str,
        }

class Article(HtmlElement):
    pass

class Aside(HtmlElement):
    pass

class Audio(HtmlElement):
    __attrs__ = {
        'src': str
        }

class B(HtmlElement):
   pass

class Big(HtmlElement):
   pass

class Blockquote(HtmlElement):
    __attrs__ = {
        'cite': str,
        }

class Body(HtmlElement):
    __attrs__ = {
        'contenteditable': str,
        }

class Br(HtmlElementNoChild):
   pass

class Button(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'name': str,
        'type': str,
        'value': str,
        }

class Canvas(HtmlElement):
    __attrs__ = {
        'height': str,
        'width': str,
        }

class Caption(HtmlElement):
   pass

class Cite(HtmlElement):
   pass

class Code(HtmlElement):
   pass

class Col(HtmlElementNoChild):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': int,
        'span': int,
        'valign': str,
        'width': str,
        }

class Colgroup(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': int,
        'span': int,
        'valign': str,
        'width': str,
        }

class Datalist(HtmlElement):
    pass

class Dd(HtmlElement):
   pass

class Del(HtmlElement):
    __attrs__ = {
        'cite': str,
        'datetime': str,
        }

class Div(HtmlElement):
   __attrs__ = {
        'contenteditable': str,
       }

class Dfn(HtmlElement):
   pass

class Dl(HtmlElement):
   pass

class Dt(HtmlElement):
   pass

class Em(HtmlElement):
   pass

class Embed(HtmlElement):
    __attrs__ = {
        'src': str,
        'width': str,
        'height': str,
        'allowscriptaccess': str,
        'allowfullscreen': str,
        'name': str,
        'type': str,
        }

class Figure(HtmlElement):
   pass

class Figcaption(HtmlElement):
   pass

class Fieldset(HtmlElement):
   pass

class Footer(HtmlElement):
    pass

class Form(HtmlElement):
    __attrs__ = {
        'action': str,
        'accept': str,
        'accept-charset': str,
        'autocomplete': str,
        'enctype': str,
        'method': str,
        'name': str,
        'novalidate': str,
        'target': str,
        }

class Frame(HtmlElementNoChild):
    __attrs__ = {
        'frameborder': str,
        'longdesc': str,
        'marginheight': str,
        'marginwidth': str,
        'name': str,
        'noresize': str,
        'scrolling': str,
        'src': str,
        }

class Frameset(HtmlElement):
    __attrs__ = {
        'rows': str,
        'cols': str,
        }

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
    __attrs__ = {
        'profile': str,
        }

class Header(HtmlElement):
    pass

class Hr(HtmlElementNoChild):
    pass

class Html(HtmlElement):
    __attrs__ = {
        'content': str,
        'scheme': str,
        'http-equiv': str,
        'xmlns': str,
        'xmlns:og': str,
        'xmlns:fb': str,
        }

class I(HtmlElement):
   pass

class Iframe(HtmlElement):
    __attrs__ = {
        'frameborder': str,
        'height': str,
        'longdesc': str,
        'marginheight': str,
        'marginwidth': str,
        'name': str,
        'sandbox': str,
        'scrolling': str,
        'src': str,
        'width': str,
        # rk: 'allowTransparency' is not in W3C's HTML spec, but it's supported in most modern browsers.
        'allowtransparency': str,
        'allowfullscreen': str,
        }

class Video(HtmlElement):
    __attrs__ = {
        'autoplay': str,
        'controls': str,
        'height': str,
        'loop': str,
        'muted': str,
        'poster': str,
        'preload': str,
        'src': str,
        'width': str,
        }

class Img(HtmlElementNoChild):
    __attrs__ = {
        'alt': str,
        'src': str,
        'height': str,
        'ismap': str,
        'longdesc': str,
        'usemap': str,
        'vspace': str,
        'width': str,
        }

class Input(HtmlElementNoChild):
    __attrs__ = {
        'accept': str,
        'align': str,
        'alt': str,
        'autofocus': str,
        'checked': str,
        'disabled': str,
        'list': str,
        'max': str,
        'maxlength': str,
        'min': str,
        'name': str,
        'pattern': str,
        'placeholder': str,
        'readonly': str,
        'size': str,
        'src': str,
        'step': str,
        'type': str,
        'value': str,
        'autocomplete': str,
        'autocorrect': str,
        'required': str,
        'spellcheck': str,
        'multiple': str,
        }

class Ins(HtmlElement):
    __attrs__ = {
        'cite': str,
        'datetime': str,
        }

class Kbd(HtmlElement):
    pass

class Label(HtmlElement):
    __attrs__ = {
        'for': str,
        }

class Legend(HtmlElement):
   pass

class Li(HtmlElement):
   pass

class Link(HtmlElementNoChild):
    __attrs__ = {
        'charset': str,
        'href': str,
        'hreflang': str,
        'media': str,
        'rel': str,
        'rev': str,
        'sizes': str,
        'target': str,
        'type': str,
        }

class Main(HtmlElement):
    # we are not enforcing the w3 spec of one and only one main element on the
    # page
    __attrs__ = {
        'role': str,
    }

class Map(HtmlElement):
    __attrs__ = {
        'name': str,
        }

class Meta(HtmlElementNoChild):
    __attrs__ = {
        'content': str,
        'http-equiv': str,
        'name': str,
        'property': str,
        'scheme': str,
        'charset': str,
        }

class Nav(HtmlElement):
    pass

class Noframes(HtmlElement):
   pass

class Noscript(HtmlElement):
   pass

class Object(HtmlElement):
    __attrs__ = {
        'align': str,
        'archive': str,
        'border': str,
        'classid': str,
        'codebase': str,
        'codetype': str,
        'data': str,
        'declare': str,
        'height': str,
        'hspace': str,
        'name': str,
        'standby': str,
        'type': str,
        'usemap': str,
        'vspace': str,
        'width': str,
        }

class Ol(HtmlElement):
   pass

class Optgroup(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'label': str,
        }

class Option(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'label': str,
        'selected': str,
        'value': str,
        }

class P(HtmlElement):
   pass

class Param(HtmlElement):
    __attrs__ = {
        'name': str,
        'type': str,
        'value': str,
        'valuetype': str,
        }

class Pre(HtmlElement):
   pass

class Progress(HtmlElement):
    __attrs__ = {
        'max': int,
        'value': int,
    }

class Q(HtmlElement):
    __attrs__ = {
        'cite': str,
        }

class Samp(HtmlElement):
   pass

class Script(HtmlElement):
    __attrs__ = {
        'async': str,
        'charset': str,
        'defer': str,
        'src': str,
        'type': str,
        }

class Section(HtmlElement):
    pass

class Select(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'multiple': str,
        'name': str,
        'size': str,
        'required': str,
        }

class Small(HtmlElement):
   pass

class Span(HtmlElement):
   pass

class Strong(HtmlElement):
   pass

class Style(HtmlElement):
    __attrs__ = {
        'media': str,
        'type': str,
        }

class Sub(HtmlElement):
   pass

class Sup(HtmlElement):
   pass

class Table(HtmlElement):
    __attrs__ = {
        'border': str,
        'cellpadding': str,
        'cellspacing': str,
        'frame': str,
        'rules': str,
        'summary': str,
        'width': str,
        }

class Tbody(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class Td(HtmlElement):
    __attrs__ = {
        'abbr': str,
        'align': str,
        'axis': str,
        'char': str,
        'charoff': str,
        'colspan': str,
        'headers': str,
        'rowspan': str,
        'scope': str,
        'valign': str,
        }

class Textarea(HtmlElement):
    __attrs__ = {
        'cols': str,
        'rows': str,
        'disabled': str,
        'placeholder': str,
        'name': str,
        'readonly': str,
        'autocorrect': str,
        'autocomplete': str,
        'autocapitalize': str,
        'spellcheck': str,
        'autofocus': str,
        'required': str,
        }

class Tfoot(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class Th(HtmlElement):
    __attrs__ = {
        'abbr': str,
        'align': str,
        'axis': str,
        'char': str,
        'charoff': str,
        'colspan': str,
        'rowspan': str,
        'scope': str,
        'valign': str,
        }

class Thead(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class Time(HtmlElement):
    __attrs__ = {
        'datetime': str,
        }

class Title(HtmlElement):
   pass

class Tr(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class Tt(HtmlElement):
    pass

class U(HtmlElement):
    pass

class Ul(HtmlElement):
    pass

class Var(HtmlElement):
    pass
