#!/usr/bin/env python

from typing import Any
import xml.sax.saxutils

xml_escape = xml.sax.saxutils.escape
xml_unescape = xml.sax.saxutils.unescape
escape_other = {
    '"': '&quot;',
    }
unescape_other = {
    '&quot;': '"',
    }

def escape(obj: Any) -> str:
    return xml_escape(str(obj), escape_other)

def unescape(obj: Any) -> str:
    return xml_unescape(str(obj), unescape_other)
