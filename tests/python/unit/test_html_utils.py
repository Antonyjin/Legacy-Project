# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
#!/usr/bin/env python3
"""
Unit tests for HTML escaping/unescaping (MIG-010)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.html_utils import escape_html, unescape_html


class TestEscape:
    def test_basic(self):
        assert escape_html('<>&') == '&lt;&gt;&amp;'
        # both quotes escaped (double then single)
        assert escape_html("\"'\"") == '&quot;&#x27;&quot;'

    def test_text_passthrough(self):
        assert escape_html('plain text') == 'plain text'
        assert escape_html('') == ''
        assert escape_html(None) == ''

    def test_quote_toggle(self):
        # when quote=False, quotes are not escaped
        assert escape_html("\"'\"", quote=False) == "\"'\""

    def test_mixed(self):
        # Genealogy example: Person name with special characters and potential XSS
        s = "Jean-François & Marie <script>alert('xss')</script>"
        out = escape_html(s)
        assert '&lt;script&gt;' in out and '&amp;' in out and '&#x27;' in out
        assert 'Jean-François' in out  # Name preserved

    def test_genealogy_names(self):
        """Test escaping with genealogy-specific names."""
        # Names with ampersands (e.g., "Smith & Johnson")
        assert '&amp;' in escape_html("Smith & Johnson Family")
        # Names with quotes (e.g., "O'Brien", "d'Albert")
        assert '&#x27;' in escape_html("O'Brien")
        assert '&quot;' in escape_html('Family "Genealogy" Book')

    def test_roundtrip_stability(self):
        # Genealogy data example: Date with HTML-like characters
        s = 'Born on <14 Nov 1948> in "London"'
        once = escape_html(s)
        # Escaping twice would double-escape. Verify escape(unescape(x)) == x
        assert escape_html(unescape_html(once)) == once


class TestUnescape:
    def test_named_entities(self):
        assert unescape_html('&lt;&gt;&amp;') == '<>&'
        assert unescape_html('&quot;&#x27;') == "\"'"

    def test_numeric(self):
        assert unescape_html('&#60;&#62;') == '<>'
        assert unescape_html('&#x3C;&#x3E;') == '<>'

    def test_roundtrip(self):
        # Genealogy example: Person notes with special characters
        s = 'Résumé & "Genealogical Notes" <birth: 1948>'
        esc = escape_html(s)
        assert unescape_html(esc) == s

    def test_empty(self):
        assert unescape_html('') == ''
