#!/usr/bin/env python

from .utils import escape
from .base import Base

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

class HtmlElement(Base):
    def _to_list(self, l):
        l.extend(('<', self.__tag__))
        for name, value in self.__attributes__.items():
            l.extend((' ', name, '="', escape(value), '"'))
        l.append('>')

        for child in self.__children__:
            self._render_child_to_list(child, l)

        l.extend(('</', self.__tag__, '>'))

class HtmlElementNoChild(Base):
    def append(self, child):
        raise Exception('<%s> does not allow children.', self.__tag__)

    def _to_list(self, l):
        l.extend(('<', self.__tag__))
        for name, value in self.__attributes__.items():
            l.extend((' ', name, '="', escape(value), '"'))
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

def rawhtml(text):
    return RawHtml(text=text)

class Fragment(Base):
    def _to_list(self, l):
        for child in self.__children__:
            self._render_child_to_list(child, l)

class a(HtmlElement):
    __attrs__ = {
        'href': str,
        'rel': str,
        'type': str,
        'name': str,
        'target': str,
        'download': str,
        }

class abbr(HtmlElement):
    pass

class acronym(HtmlElement):
    pass

class address(HtmlElement):
    pass

class area(HtmlElementNoChild):
    __attrs__ = {
        'alt': str,
        'coords': str,
        'href': str,
        'nohref': str,
        'target': str,
        }

class article(HtmlElement):
    pass

class aside(HtmlElement):
    pass

class audio(HtmlElement):
    __attrs__ = {
        'src': str
        }

class b(HtmlElement):
   pass

class big(HtmlElement):
   pass

class blockquote(HtmlElement):
    __attrs__ = {
        'cite': str,
        }

class body(HtmlElement):
    __attrs__ = {
        'contenteditable': str,
        }

class br(HtmlElementNoChild):
   pass

class button(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'name': str,
        'type': str,
        'value': str,
        }

class canvas(HtmlElement):
    __attrs__ = {
        'height': str,
        'width': str,
        }

class caption(HtmlElement):
   pass

class cite(HtmlElement):
   pass

class code(HtmlElement):
   pass

class col(HtmlElementNoChild):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': int,
        'span': int,
        'valign': str,
        'width': str,
        }

class colgroup(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': int,
        'span': int,
        'valign': str,
        'width': str,
        }

class datalist(HtmlElement):
    pass

class dd(HtmlElement):
   pass

class del_(HtmlElement):
    __attrs__ = {
        'cite': str,
        'datetime': str,
        }

class div(HtmlElement):
   __attrs__ = {
        'contenteditable': str,
       }

class dfn(HtmlElement):
   pass

class dl(HtmlElement):
   pass

class dt(HtmlElement):
   pass

class em(HtmlElement):
   pass

class embed(HtmlElement):
    __attrs__ = {
        'src': str,
        'width': str,
        'height': str,
        'allowscriptaccess': str,
        'allowfullscreen': str,
        'name': str,
        'type': str,
        }

class figure(HtmlElement):
   pass

class figcaption(HtmlElement):
   pass

class fieldset(HtmlElement):
   pass

class footer(HtmlElement):
    pass

class form(HtmlElement):
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

class form_error(Base):
    __attrs__ = {
        'name': str
        }

    def _to_list(self, l):
        l.extend(('<form:error name="', self.attr('name'), '" />'))

class frame(HtmlElementNoChild):
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

class frameset(HtmlElement):
    __attrs__ = {
        'rows': str,
        'cols': str,
        }

class h1(HtmlElement):
   pass

class h2(HtmlElement):
   pass

class h3(HtmlElement):
   pass

class h4(HtmlElement):
   pass

class h5(HtmlElement):
   pass

class h6(HtmlElement):
   pass

class head(HtmlElement):
    __attrs__ = {
        'profile': str,
        }

class header(HtmlElement):
    pass

class hr(HtmlElementNoChild):
    pass

class html(HtmlElement):
    __attrs__ = {
        'content': str,
        'scheme': str,
        'http-equiv': str,
        'xmlns': str,
        'xmlns:og': str,
        'xmlns:fb': str,
        }

class i(HtmlElement):
   pass

class iframe(HtmlElement):
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

class video(HtmlElement):
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

class img(HtmlElementNoChild):
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

class input(HtmlElementNoChild):
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

class ins(HtmlElement):
    __attrs__ = {
        'cite': str,
        'datetime': str,
        }

class kbd(HtmlElement):
    pass

class label(HtmlElement):
    __attrs__ = {
        'for': str,
        }

class legend(HtmlElement):
   pass

class li(HtmlElement):
   pass

class link(HtmlElementNoChild):
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

class main(HtmlElement):
    # we are not enforcing the w3 spec of one and only one main element on the
    # page
    __attrs__ = {
        'role': str,
    }

class map(HtmlElement):
    __attrs__ = {
        'name': str,
        }

class meta(HtmlElementNoChild):
    __attrs__ = {
        'content': str,
        'http-equiv': str,
        'name': str,
        'property': str,
        'scheme': str,
        'charset': str,
        }

class nav(HtmlElement):
    pass

class noframes(HtmlElement):
   pass

class noscript(HtmlElement):
   pass

class object(HtmlElement):
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

class ol(HtmlElement):
   pass

class optgroup(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'label': str,
        }

class option(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'label': str,
        'selected': str,
        'value': str,
        }

class p(HtmlElement):
   pass

class param(HtmlElement):
    __attrs__ = {
        'name': str,
        'type': str,
        'value': str,
        'valuetype': str,
        }

class pre(HtmlElement):
   pass

class progress(HtmlElement):
    __attrs__ = {
        'max': int,
        'value': int,
    }

class q(HtmlElement):
    __attrs__ = {
        'cite': str,
        }

class samp(HtmlElement):
   pass

class script(HtmlElement):
    __attrs__ = {
        'async': str,
        'charset': str,
        'defer': str,
        'src': str,
        'type': str,
        }

class section(HtmlElement):
    pass

class select(HtmlElement):
    __attrs__ = {
        'disabled': str,
        'multiple': str,
        'name': str,
        'size': str,
        'required': str,
        }

class small(HtmlElement):
   pass

class span(HtmlElement):
   pass

class strong(HtmlElement):
   pass

class style(HtmlElement):
    __attrs__ = {
        'media': str,
        'type': str,
        }

class sub(HtmlElement):
   pass

class sup(HtmlElement):
   pass

class table(HtmlElement):
    __attrs__ = {
        'border': str,
        'cellpadding': str,
        'cellspacing': str,
        'frame': str,
        'rules': str,
        'summary': str,
        'width': str,
        }

class tbody(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class td(HtmlElement):
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

class textarea(HtmlElement):
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

class tfoot(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class th(HtmlElement):
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

class thead(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class time(HtmlElement):
    __attrs__ = {
        'datetime': str,
        }

class title(HtmlElement):
   pass

class tr(HtmlElement):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class tt(HtmlElement):
    pass

class u(HtmlElement):
    pass

class ul(HtmlElement):
    pass

class var(HtmlElement):
    pass
