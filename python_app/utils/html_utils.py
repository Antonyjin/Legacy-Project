# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
HTML escaping/unescaping utilities - Migration from GeneWeb.
"""

from html import escape as _py_escape
from html import unescape as _py_unescape


def escape_html(text: str, quote: bool = True) -> str:
    if text is None:
        return ''
    return _py_escape(text, quote=quote)


def unescape_html(text: str) -> str:
    if not text:
        return ''
    return _py_unescape(text)


