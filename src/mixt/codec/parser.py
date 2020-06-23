import tokenize

from mixt import html
from mixt.exceptions import ParserStateError, ParserError, RequiredPropError, InvalidPropNameError
from mixt.internal.base import escape
from mixt.internal.html import __tags__
from mixt.internal.proptypes import BasePropTypes
from .html_tokenizer import HTMLTokenizer
from mixt.codec.state import State
from .pytokenize import Untokenizer


class PyxlParser(HTMLTokenizer):
    def __init__(self, row, col, str_function):
        super().__init__()
        self.start = self.end = (row, col)
        self.output = []
        self.open_tags = []
        self.remainder = None
        self.next_thing_is_python = False
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False
        self.str_function = str_function

    def delete_last_comma(self):
        for i in reversed(range(len(self.output))):
            stripped = self.output[i].rstrip()
            if stripped and not stripped[0] == '#':
                assert stripped[-1] == ',', (self.output, stripped, i)
                self.output[i] = self.output[i][:len(stripped)-1] + self.output[i][len(stripped):]
                return
        assert False, "couldn't find a comma"

    def handle_close_if(self):
        """Clean up after an unpaired if statement.
        Should be called at the beginning of any construct other than an else.
        """
        if self.last_thing_was_close_if_tag:
            self.delete_last_comma()
            self.output.append(' else None, ')
            self.last_thing_was_close_if_tag = False

    def start_element(self):
        """Mark the start of an element.
        This is to allow figuring out how many children exist.
        """
        if self.open_tags:
            self.open_tags[-1]['children'] += 1

    def feed(self, token):
        ttype, tvalue, tstart, tend, tline = token

        assert tstart[0] >= self.end[0], "row went backwards"
        if tstart[0] > self.end[0]:
            self.output.append("\n" * (tstart[0] - self.end[0]))

        # interpret jumps on the same line as a single space
        elif tstart[1] > self.end[1]:
            super().feed(" ")

        self.end = tstart

        if ttype != tokenize.INDENT:
            while tvalue and not self.done():
                c, tvalue = tvalue[0], tvalue[1:]
                if c == "\n":
                    self.end = (self.end[0]+1, 0)
                else:
                    self.end = (self.end[0], self.end[1]+1)
                try:
                    super().feed(c)
                except ParserStateError as exc:
                    raise ParserError("HTML Parsing error", self.end, exc)
        if self.done():
            self.remainder = (ttype, tvalue, self.end, tend, tline)
        else:
            self.end = tend

    def feed_python(self, tokens):
        self.handle_close_if()

        ttype, tvalue, tstart, tend, tline = tokens[0]
        assert tstart[0] >= self.end[0], "row went backwards"
        if tstart[0] > self.end[0]:
            self.output.append("\n" * (tstart[0] - self.end[0]))
        ttype, tvalue, tstart, tend, tline = tokens[-1]
        self.end = tend

        if self.state in [State.DATA, State.CDATA_SECTION]:
            self.next_thing_is_python = True
            self.emit_data()
            output = Untokenizer().untokenize(tokens)
            # If we have a generator comprehension, parenthesize it
            if has_bare_generator(tokens):
                self.output.append("(%s), " % output)
            else:
                self.output.append("%s, " % output)
            self.next_thing_is_python = False
            self.last_thing_was_python = True
            self.start_element()
        elif self.state in [State.BEFORE_ATTRIBUTE_VALUE,
                            State.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
                            State.ATTRIBUTE_VALUE_SINGLE_QUOTED,
                            State.ATTRIBUTE_VALUE_UNQUOTED]:
            super().feed_python(tokens)
        elif self.state in [State.BEFORE_ATTRIBUTE_NAME,
                            State.AFTER_ATTRIBUTE_NAME]:
            # will only allow **somedict kind of python
            super().feed_python(tokens)
        else:
            raise ParserError("Python not allowed here", tstart)

    def feed_position_only(self, token):
        """update with any whitespace we might have missed, and advance position to after the
        token"""
        ttype, tvalue, tstart, tend, tline = token
        self.feed((ttype, '', tstart, tstart, tline))
        self.end = tend

    def python_comment_allowed(self):
        """Returns true if we're in a state where a # starts a comment.

        <a # comment before attribute name
           class="bar"# comment after attribute value
           href="#notacomment">
            # comment in data
            Link text
        </a>
        """
        return self.state in (State.DATA, State.TAG_NAME,
                              State.BEFORE_ATTRIBUTE_NAME, State.AFTER_ATTRIBUTE_NAME,
                              State.BEFORE_ATTRIBUTE_VALUE, State.AFTER_ATTRIBUTE_VALUE,
                              State.COMMENT, State.DOCTYPE_CONTENTS, State.CDATA_SECTION)

    def python_mode_allowed(self):
        """Returns true if we're in a state where a { starts python mode.

        <!-- {this isn't python} -->
        """
        return self.state not in (State.COMMENT,)

    def feed_comment(self, token):
        ttype, tvalue, tstart, tend, tline = token
        self.feed((ttype, '', tstart, tstart, tline))
        self.output.append(tvalue)
        self.end = tend

    def get_remainder(self):
        return self.remainder

    def done(self):
        return len(self.open_tags) == 0 and self.state == State.DATA and self.output

    def get_token(self):
        return (tokenize.STRING, ''.join(self.output), self.start, self.end, '')

    def _handle_attr_value(self, attr_value):
        def format_parts():
            prev_was_python = False
            for i, part in enumerate(attr_value):
                if type(part) == list:
                    yield part
                    prev_was_python = True
                else:
                    next_is_python = bool(i+1 < len(attr_value) and type(attr_value[i+1]) == list)
                    part = self._normalize_data_whitespace(part, prev_was_python, next_is_python)
                    if part:
                        yield part
                    prev_was_python = False

        def format_part(part):
            """Allow numbers, bools, None and NotProvided to be passed without being stringified."""
            if part in {'True', 'False', 'None', 'NotProvided'}:
                return part
            if part.isdecimal():
                return part
            try:
                float(part)
            except:
                pass
            else:
                return part

            return repr(part)

        output = []

        if attr_value is True:
            # special case where we force the value to True for attributes without value
            output.append('True')
        else:
            attr_value = list(format_parts())
            if len(attr_value) == 1:
                part = attr_value[0]
                if type(part) == list:
                    output.append(Untokenizer().untokenize(part))
                else:
                    output.append(format_part(part))
            else:
                output.append('"".join((')
                for part in attr_value:
                    if type(part) == list:
                        output.append('{}('.format(self.str_function))
                        output.append(Untokenizer().untokenize(part))
                        output.append(')')
                    else:
                        output.append(format_part(part))
                    output.append(', ')
                output.append('))')

        return output

    @staticmethod
    def _normalize_data_whitespace(data, prev_was_py, next_is_py):
        if not data:
            return ''
        if '\n' in data and not data.strip():
            if prev_was_py and next_is_py:
                return ' '
            else:
                return ''
        if prev_was_py and data.startswith('\n'):
                data = " " + data.lstrip('\n')
        if next_is_py and data.endswith('\n'):
                data = data.rstrip('\n') + " "
        data = data.strip('\n')
        data = data.replace('\r', ' ')
        data = data.replace('\n', ' ')
        return data

    def handle_starttag(self, tag, attrs, kwargs_attrs=None, call=True):
        self.start_element()
        self.open_tags.append({'tag':tag, 'pos': self.end, 'attrs': attrs, 'children': 0})
        if tag == 'if':
            self.handle_close_if()

            if len(attrs) != 1:
                for attr in attrs:
                    if attr != 'cond':
                        raise ParserError("Invalid <if> tag: only allowed prop is `cond`", self.end, InvalidPropNameError('if', attr))
            if 'cond' not in attrs:
                raise ParserError("Invalid <if> tag", self.end, RequiredPropError('if', 'cond'))

            self.open_tags[-1]['open'] = len(self.output)  # track Fragment pos so it can be deleted
            self.output.append('html.Fragment()(')
            self.last_thing_was_python = False
            self.last_thing_was_close_if_tag = False
            return
        elif tag == 'else':
            if len(attrs) != 0:
                for attr in attrs:
                    raise ParserError("Invalid <else> tag: no allowed props", self.end, InvalidPropNameError('else', attr))
            if not self.last_thing_was_close_if_tag:
                raise ParserError("<else> tag must come right after </if>", self.end)

            self.delete_last_comma()
            self.output.append('else ')
            self.open_tags[-1]['open'] = len(self.output)
            self.output.append('html.Fragment()(')
            self.last_thing_was_python = False
            self.last_thing_was_close_if_tag = False
            return

        self.handle_close_if()

        tag_lower = tag.lower()
        if tag == tag_lower and tag_lower in __tags__:
            # allow only lower-cased tags in html
            self.output.append('html.%s(' % __tags__[tag_lower])
        elif hasattr(html, tag) and tag_lower not in __tags__:
            # or other in html but not html tags: just "special" tags
            self.output.append('html.%s(' % tag)
        else:
            self.output.append('%s(' % tag)

        first_attr = True
        for attr_name, attr_value in attrs.items():
            if first_attr: first_attr = False
            else: self.output.append(', ')

            try:
                safe_attr_name = BasePropTypes.__to_python__(attr_name)
            except NameError:
                raise ParserError(f"Invalid prop name {attr_name}", self.start)

            self.output.append(safe_attr_name)
            self.output.append('=')
            self.output.extend(self._handle_attr_value(attr_value))

        if kwargs_attrs:
            for kwargs_attr in kwargs_attrs:
                if first_attr: first_attr = False
                else: self.output.append(', ')

                handled_kwargs_attr = ''.join(self._handle_attr_value(kwargs_attr))
                left_striped_handled_kwargs_attr = handled_kwargs_attr.lstrip()

                if not left_striped_handled_kwargs_attr.startswith('**'):
                    line = kwargs_attr[0][0][2][0]
                    col = kwargs_attr[0][0][2][1] + len(handled_kwargs_attr) - len(left_striped_handled_kwargs_attr) + 1
                    raise ParserError("Only **kwargs style is allowed here", (line, col))

                self.output.append(handled_kwargs_attr)

        self.output.append(')')
        if call:
            # start call to __call__
            self.output.append('(')
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_endtag(self, tag_name, call=True):
        self.handle_close_if()

        if call:
            # finish call to __call__
            self.output.append(")")

        assert self.open_tags, "got </%s> but tag stack empty; parsing should be over!" % tag_name

        open_tag = self.open_tags.pop()
        if open_tag['tag'] != tag_name:
            raise ParserError(
                f"<{open_tag['tag']}> closed by </{tag_name}> on "
                f"[line={self.end[0]}, col={self.end[1]}]", open_tag['pos']
            )

        # If we are finishing an if or an else and it only had one child, we can safely
        # remove the x_frag that opened it.
        if tag_name in ('if', 'else') and call and open_tag['children'] == 1:
            self.output[-1] = ''
            self.delete_last_comma()
            self.output[open_tag['open']] = ''

        if open_tag['tag'] == 'if':
            self.output.append(' if ')
            # If another if/else appears in the condition, we need to parenthesize it.
            # Detect this in a bad but easy way that might have some false positives.
            start = len(self.output)
            self.output.append('(')
            self.output.extend(self._handle_attr_value(open_tag['attrs']['cond']))
            if 'else' in ''.join(self.output[start:]):
                self.output.append(')')
            else:
                self.output[start] = ''
            self.last_thing_was_close_if_tag = True
        else:
            self.last_thing_was_close_if_tag = False

        if len(self.open_tags):
            self.output.append(",")
        self.last_thing_was_python = False

    def handle_startendtag(self, tag_name, attrs, kwargs_attrs=None):
        self.handle_starttag(tag_name, attrs, kwargs_attrs, call=False)
        self.handle_endtag(tag_name, call=False)

    def handle_data(self, data):
        data = self._normalize_data_whitespace(
                data, self.last_thing_was_python, self.next_thing_is_python)
        if not data:
            return

        self.start_element()
        self.handle_close_if()

        # XXX XXX mimics old pyxl, but this is gross and likely wrong. I'm pretty sure we actually
        # want %r instead of this crazy quote substitution and "%s".
        data = data.replace('"', '\\"')
        if data != escape(data):
            self.output.append('html.Raw("%s"), ' % data)
        else:
            self.output.append('"%s", ' % data)

        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_comment(self, data):
        self.handle_startendtag("Comment", {"comment": [data.strip()]})
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_doctype(self, data):
        self.handle_startendtag("Doctype", {"doctype": [data]})
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_cdata(self, data):
        self.handle_startendtag("CData", {"cdata": [data]})
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

def has_bare_generator(tokens):
    nesting = 0
    for token in tokens:
        tvalue = token[1]
        if tvalue in "({[":
            nesting += 1
        if tvalue in ")}]":
            nesting -= 1
        if tvalue == "for" and nesting == 0:
            return True
    return False