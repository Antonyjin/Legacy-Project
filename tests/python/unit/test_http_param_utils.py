# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
#!/usr/bin/env python3
"""
Unit tests for HTTP parameter parsing (MIG-004, MIG-009)

Test File: UT-PY-015
Issues:
  - MIG-004 - Migrate HTTP parameter parsing
  - MIG-009 - Migrate URL encoding functions
OCaml Reference:
  - source_geneweb/lib/util/mutil.ml:930-979 (encode function)
  - source_geneweb/lib/util/mutil.ml:982-1039 (decode function)
  - source_geneweb/bin/gwd/gwd.ml:174-180 (extract_assoc function)

Purpose:
    Validate the Python implementation of OCaml HTTP parameter parsing functions:
    - Mutil.encode: URL encoding with percent encoding and space-to-plus
    - Mutil.decode: URL decoding with percent encoding and plus-to-space
    - gwd.extract_assoc: Parameter extraction from key-value list

Coverage:
    - URL encoding (percent encoding, space to plus)
    - URL decoding (percent encoding, plus to space)
    - Special characters
    - UTF-8 encoding
    - Parameter extraction
    - Edge cases (empty, missing, duplicates)
    - Roundtrip (encode then decode)

Author: Python Migration Team
Date: 2025-10-29
"""

import sys
from pathlib import Path

# Add tests directory to path for imports
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(test_dir))

import pytest
from utils.http_params import extract_all_params, extract_param, parse_query_string, url_decode, url_encode


class TestURLEncoding:
    """Test URL encoding (percent encoding + space to plus)."""

    def test_no_encoding_needed(self):
        """Simple alphanumeric strings unchanged."""
        assert url_encode("hello") == "hello"
        assert url_encode("HelloWorld") == "HelloWorld"
        assert url_encode("test123") == "test123"

    def test_space_to_plus(self):
        """Spaces converted to plus signs."""
        assert url_encode("Hello World") == "Hello+World"
        assert url_encode("Jean François") == "Jean+Fran%C3%A7ois"
        assert url_encode("multiple  spaces") == "multiple++spaces"

    def test_special_characters(self):
        """Special characters percent-encoded."""
        assert url_encode("O'Brien") == "O%27Brien"
        assert url_encode("price = $100") == "price+%3D+%24100"
        assert url_encode("a&b") == "a%26b"
        assert url_encode("a#b") == "a%23b"
        assert url_encode("a@b") == "a%40b"
        assert url_encode("a:b") == "a%3Ab"

    def test_utf8_encoding(self):
        """UTF-8 characters percent-encoded."""
        assert url_encode("Jean-François") == "Jean-Fran%C3%A7ois"
        assert url_encode("é") == "%C3%A9"
        assert url_encode("à") == "%C3%A0"
        assert url_encode("Müller") == "M%C3%BCller"
        assert url_encode("北京") == "%E5%8C%97%E4%BA%AC"

    def test_control_characters(self):
        """Control characters encoded."""
        # Newline
        assert url_encode("line1\nline2") == "line1%0Aline2"
        # Tab
        assert url_encode("tab\there") == "tab%09here"
        # Carriage return
        assert url_encode("text\r") == "text%0D"

    def test_reserved_characters(self):
        """Reserved URL characters encoded."""
        # Query string reserved chars
        assert url_encode("a?b") == "a%3Fb"  # ?
        assert url_encode("a/b") == "a%2Fb"  # /
        assert url_encode("a=b") == "a%3Db"  # =
        assert url_encode("a&b") == "a%26b"  # &
        # Path reserved chars
        assert url_encode("a;b") == "a%3Bb"  # ;
        # Fragment reserved chars
        assert url_encode("a#b") == "a%23b"  # #

    def test_empty_string(self):
        """Empty string returns empty."""
        assert url_encode("") == ""

    def test_leading_trailing_spaces(self):
        """Leading/trailing spaces encoded."""
        assert url_encode("  hello  ") == "++hello++"
        assert url_encode(" test ") == "+test+"

    def test_multiple_special_chars(self):
        """Multiple special characters all encoded."""
        assert url_encode("file://path?query=value#fragment") == "file%3A%2F%2Fpath%3Fquery%3Dvalue%23fragment"
        assert url_encode("a<b>c\"d'e") == "a%3Cb%3Ec%22d%27e"

    def test_unicode_combinations(self):
        """Complex Unicode strings encoded."""
        assert url_encode("Café №1") == "Caf%C3%A9+%E2%84%961"
        assert url_encode("日本語") == "%E6%97%A5%E6%9C%AC%E8%AA%9E"
        assert url_encode("Résumé & CV") == "R%C3%A9sum%C3%A9+%26+CV"


class TestURLDecoding:
    """Test URL decoding (percent encoding)."""

    def test_no_encoding(self):
        """String without encoding unchanged."""
        assert url_decode("hello") == "hello"
        assert url_decode("HelloWorld") == "HelloWorld"

    def test_plus_to_space(self):
        """Plus signs converted to spaces."""
        assert url_decode("hello+world") == "hello world"
        assert url_decode("Jean+Fran%C3%A7ois") == "Jean François"

    def test_percent_encoding(self):
        """Percent-encoded characters decoded."""
        assert url_decode("hello%20world") == "hello world"
        assert url_decode("O%27Brien") == "O'Brien"
        assert url_decode("50%25") == "50%"

    def test_utf8_encoding(self):
        """UTF-8 encoded characters decoded correctly."""
        assert url_decode("Jean-Fran%C3%A7ois") == "Jean-François"
        assert url_decode("%C3%A9") == "é"
        assert url_decode("%C3%A0") == "à"
        assert url_decode("M%C3%BCller") == "Müller"

    def test_special_characters(self):
        """Special characters decoded."""
        assert url_decode("100%25") == "100%"
        assert url_decode("a%2Bb") == "a+b"
        assert url_decode("a%3Db") == "a=b"
        assert url_decode("a%26b") == "a&b"

    def test_empty_string(self):
        """Empty string returns empty."""
        assert url_decode("") == ""

    def test_strip_spaces(self):
        """Leading/trailing spaces stripped by default."""
        assert url_decode("%20hello%20") == "hello"
        assert url_decode("+hello+") == "hello"
        assert url_decode("+++") == ""

    def test_no_strip_spaces(self):
        """Spaces preserved when strip_spaces=False."""
        assert url_decode("%20hello%20", strip_spaces=False) == " hello "
        assert url_decode("+hello+", strip_spaces=False) == " hello "
        assert url_decode("+++", strip_spaces=False) == "   "


class TestExtractParam:
    """Test parameter extraction from key-value list."""

    def test_extract_existing_param(self):
        """Extract existing parameter."""
        params = [('p', 'jean'), ('n', 'martin'), ('oc', '0')]
        value, remaining = extract_param('p', params)
        assert value == 'jean'
        assert remaining == [('n', 'martin'), ('oc', '0')]

    def test_extract_middle_param(self):
        """Extract parameter from middle of list."""
        params = [('a', '1'), ('b', '2'), ('c', '3')]
        value, remaining = extract_param('b', params)
        assert value == '2'
        assert remaining == [('a', '1'), ('c', '3')]

    def test_extract_last_param(self):
        """Extract last parameter."""
        params = [('a', '1'), ('b', '2'), ('c', '3')]
        value, remaining = extract_param('c', params)
        assert value == '3'
        assert remaining == [('a', '1'), ('b', '2')]

    def test_extract_missing_param(self):
        """Missing parameter returns empty string and original list."""
        params = [('a', '1'), ('b', '2')]
        value, remaining = extract_param('missing', params)
        assert value == ''
        assert remaining == [('a', '1'), ('b', '2')]

    def test_extract_from_empty_list(self):
        """Empty list returns empty string and empty list."""
        value, remaining = extract_param('key', [])
        assert value == ''
        assert remaining == []

    def test_extract_with_url_encoding(self):
        """Extracted value is URL-decoded."""
        params = [('name', 'Jean+Fran%C3%A7ois')]
        value, remaining = extract_param('name', params)
        assert value == 'Jean François'
        assert remaining == []

    def test_extract_first_duplicate(self):
        """Only first occurrence extracted."""
        params = [('a', '1'), ('b', '2'), ('a', '3')]
        value, remaining = extract_param('a', params)
        assert value == '1'
        assert remaining == [('b', '2'), ('a', '3')]

    def test_extract_empty_value(self):
        """Empty value extracted correctly."""
        params = [('a', ''), ('b', '2')]
        value, remaining = extract_param('a', params)
        assert value == ''
        assert remaining == [('b', '2')]


class TestParseQueryString:
    """Test query string parsing."""

    def test_simple_query(self):
        """Parse simple query string."""
        params = parse_query_string("p=jean&n=martin&oc=0")
        assert params == [('p', 'jean'), ('n', 'martin'), ('oc', '0')]

    def test_encoded_query(self):
        """Parse query string with encoded values."""
        params = parse_query_string("name=John+Doe&age=30")
        assert params == [('name', 'John+Doe'), ('age', '30')]

    def test_empty_query(self):
        """Empty query string returns empty list."""
        assert parse_query_string("") == []

    def test_single_param(self):
        """Single parameter."""
        params = parse_query_string("key=value")
        assert params == [('key', 'value')]

    def test_param_without_value(self):
        """Parameter without '=' gets empty value."""
        params = parse_query_string("key_only")
        assert params == [('key_only', '')]

    def test_empty_values(self):
        """Parameters with empty values."""
        params = parse_query_string("a=1&b=&c=3")
        assert params == [('a', '1'), ('b', ''), ('c', '3')]

    def test_multiple_equals(self):
        """Value with '=' character."""
        params = parse_query_string("formula=a=b")
        assert params == [('formula', 'a=b')]


class TestExtractAllParams:
    """Test extracting all parameters to dictionary."""

    def test_simple_extraction(self):
        """Extract all parameters."""
        params = [('p', 'jean'), ('n', 'martin'), ('oc', '0')]
        result = extract_all_params(params)
        assert result == {'p': 'jean', 'n': 'martin', 'oc': '0'}

    def test_with_decoding(self):
        """All values are decoded."""
        params = [('name', 'Jean+Fran%C3%A7ois'), ('city', 'New+York')]
        result = extract_all_params(params)
        assert result == {'name': 'Jean François', 'city': 'New York'}

    def test_duplicate_keys(self):
        """First occurrence wins for duplicates."""
        params = [('a', '1'), ('b', '2'), ('a', '3')]
        result = extract_all_params(params)
        assert result == {'a': '1', 'b': '2'}

    def test_empty_params(self):
        """Empty list returns empty dict."""
        assert extract_all_params([]) == {}


class TestOCamlBehaviorConsistency:
    """Test that Python implementation matches OCaml behavior exactly."""

    def test_decode_ocaml_examples(self):
        """Test examples from OCaml codebase."""
        # From gwd.ml usage
        assert url_decode("jean") == "jean"
        assert url_decode("martin") == "martin"
        assert url_decode("0") == "0"

    def test_extract_assoc_ocaml_pattern(self):
        """
        Test OCaml extract_assoc pattern:
        let x, env = extract_assoc "b" env in
        """
        env = [('b', 'test'), ('lang', 'fr'), ('w', 'welcome')]

        # Extract "b"
        x, env = extract_param('b', env)
        assert x == 'test'
        assert ('b', 'test') not in env

        # Extract "lang"
        lang, env = extract_param('lang', env)
        assert lang == 'fr'
        assert ('lang', 'fr') not in env

        # Extract "w"
        w, env = extract_param('w', env)
        assert w == 'welcome'
        assert env == []

    def test_decode_strips_spaces(self):
        """OCaml decode strips leading/trailing spaces by default."""
        # From OCaml: strip_heading_and_trailing_spaces
        assert url_decode("%20test%20") == "test"
        assert url_decode("+test+") == "test"


class TestSpecialCharactersAndEdgeCases:
    """Test special characters and edge cases."""

    def test_non_latin_characters(self):
        """Non-Latin scripts decoded correctly."""
        # Cyrillic
        assert url_decode("%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80") == "Владимир"

        # Greek
        assert url_decode("%CE%93%CE%B5%CF%8E%CF%81%CE%B3%CE%B9%CE%BF%CF%82") == "Γεώργιος"

    def test_punctuation(self):
        """Punctuation characters."""
        assert url_decode("hello%2C+world%21") == "hello, world!"
        assert url_decode("question%3F") == "question?"
        assert url_decode("hash%23tag") == "hash#tag"

    def test_numbers_and_symbols(self):
        """Numbers and mathematical symbols."""
        assert url_decode("100%25") == "100%"
        assert url_decode("5%2B5%3D10") == "5+5=10"
        assert url_decode("a%2Fb") == "a/b"

    def test_mixed_encoding(self):
        """Mix of plus, percent, and plain characters."""
        assert url_decode("Jean+Fran%C3%A7ois+Martin") == "Jean François Martin"
        assert url_decode("New+York%2C+NY") == "New York, NY"


class TestIntegrationWithOCamlPatterns:
    """Test integration patterns used in OCaml GeneWeb."""

    def test_person_lookup_pattern(self):
        """
        Pattern from gwd.ml for person lookup:
        ?p=firstname&n=surname&oc=occurrence
        """
        query = "p=Jean+Fran%C3%A7ois&n=MARTIN&oc=0"
        params = parse_query_string(query)

        p, params = extract_param('p', params)
        n, params = extract_param('n', params)
        oc, params = extract_param('oc', params)

        assert p == "Jean François"
        assert n == "MARTIN"
        assert oc == "0"

    def test_language_parameter(self):
        """
        Language parameter from gwd.ml:
        let lang, env = extract_assoc "lang" env in
        """
        params = [('lang', 'fr'), ('b', 'test')]
        lang, params = extract_param('lang', params)
        assert lang == 'fr'
        assert params == [('b', 'test')]

    def test_base_parameter(self):
        """
        Base parameter from gwd.ml:
        let x, env = extract_assoc "b" env in
        """
        params = [('b', 'genealogy_db'), ('w', 'welcome')]
        b, params = extract_param('b', params)
        assert b == 'genealogy_db'

    def test_sequential_extraction(self):
        """Sequential parameter extraction (OCaml pattern)."""
        params = [
            ('b', 'test'),
            ('w', 'welcome'),
            ('lang', 'fr'),
            ('opt', 'no_menu'),
            ('threshold', '10')
        ]

        # Extract in order (as done in gwd.ml)
        b, params = extract_param('b', params)
        w, params = extract_param('w', params)
        lang, params = extract_param('lang', params)
        opt, params = extract_param('opt', params)
        threshold, params = extract_param('threshold', params)

        assert b == 'test'
        assert w == 'welcome'
        assert lang == 'fr'
        assert opt == 'no_menu'
        assert threshold == '10'
        assert params == []


class TestRoundtripEncoding:
    """Test roundtrip encoding/decoding (encode then decode)."""

    def test_simple_roundtrip(self):
        """Encode then decode returns original."""
        original = "Hello World"
        encoded = url_encode(original)
        decoded = url_decode(encoded)
        assert decoded == original

    def test_special_chars_roundtrip(self):
        """Special characters roundtrip correctly."""
        test_cases = [
            "O'Brien",
            "price = $100",
            "file#1: name",
            "a&b=c",
            "test?query=value"
        ]
        for original in test_cases:
            encoded = url_encode(original)
            decoded = url_decode(encoded)
            assert decoded == original, f"Roundtrip failed for: {original}"

    def test_utf8_roundtrip(self):
        """UTF-8 characters roundtrip correctly."""
        test_cases = [
            "Jean-François",
            "Müller",
            "北京",
            "Café №1",
            "Résumé & CV"
        ]
        for original in test_cases:
            encoded = url_encode(original)
            decoded = url_decode(encoded)
            assert decoded == original, f"Roundtrip failed for: {original}"

    def test_empty_string_roundtrip(self):
        """Empty string roundtrip."""
        original = ""
        encoded = url_encode(original)
        decoded = url_decode(encoded)
        assert decoded == original

    def test_spaces_roundtrip(self):
        """Multiple spaces roundtrip correctly."""
        test_cases = [
            "  leading",
            "trailing  ",
            "  both  ",
            "multiple  spaces  here"
        ]
        for original in test_cases:
            encoded = url_encode(original)
            decoded = url_decode(encoded, strip_spaces=False)
            # Note: decode strips spaces by default, so test with strip_spaces=False
            assert decoded == original, f"Roundtrip failed for: {original}"


class TestRealWorldQueryStrings:
    """Test with real-world GeneWeb query strings."""

    def test_person_page(self):
        """Person page query string."""
        query = "p=Jean&n=MARTIN&oc=0"
        params = parse_query_string(query)
        result = extract_all_params(params)
        assert result == {'p': 'Jean', 'n': 'MARTIN', 'oc': '0'}

    def test_search_query(self):
        """Search query with special characters."""
        query = "p=O%27Brien&n=Smith"
        params = parse_query_string(query)
        result = extract_all_params(params)
        assert result == {'p': "O'Brien", 'n': 'Smith'}

    def test_french_names(self):
        """French names with accents."""
        query = "p=Fran%C3%A7ois&n=Garc%C3%ADa"
        params = parse_query_string(query)
        result = extract_all_params(params)
        assert result == {'p': 'François', 'n': 'García'}

    def test_encoded_query_construction(self):
        """Build query string with url_encode."""
        # Encode parameter values
        firstname = url_encode("Jean-François")
        surname = url_encode("O'Brien")
        query = f"p={firstname}&n={surname}"
        # Parse and decode
        params = parse_query_string(query)
        result = extract_all_params(params)
        assert result == {'p': 'Jean-François', 'n': "O'Brien"}

    def test_complex_query(self):
        """Complex query with multiple parameters."""
        query = "b=test&w=welcome&lang=fr&p=Jean&n=MARTIN&oc=0&m=D"
        params = parse_query_string(query)
        result = extract_all_params(params)
        assert result == {
            'b': 'test',
            'w': 'welcome',
            'lang': 'fr',
            'p': 'Jean',
            'n': 'MARTIN',
            'oc': '0',
            'm': 'D'
        }


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
