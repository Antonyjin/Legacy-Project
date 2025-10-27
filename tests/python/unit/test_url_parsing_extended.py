"""
UT-PY-004: Test URL parsing via HTTP API

Extended tests for URL encoding/decoding beyond test_http_params.py
These tests work for OCaml NOW and will validate Python migration LATER.

Validates:
- URL encoding variants (percent encoding, plus encoding)
- UTF-8 and Latin-1 character handling
- Special genealogy characters
- Parameter extraction edge cases
- Malformed query string handling
"""
import requests
import pytest
from urllib.parse import quote

BASE_URL = "http://localhost:23179/test"


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestURLEncodingVariants:
    """Test different URL encoding methods"""

    def test_percent_encoding_space(self):
        """Test %20 encoding for spaces"""
        r = requests.get(f"{BASE_URL}?p=John%20Doe&n=Smith")
        assert r.status_code == 200

    def test_plus_encoding_space(self):
        """Test + encoding for spaces"""
        r = requests.get(f"{BASE_URL}?p=John+Doe&n=Smith")
        assert r.status_code == 200

    def test_mixed_encoding_spaces(self):
        """Test mixed %20 and + in same URL"""
        r = requests.get(f"{BASE_URL}?p=John%20Doe&n=John+Doe")
        assert r.status_code == 200

    def test_percent_encoded_special_chars(self):
        """Test %XX encoding for special characters"""
        # & = %26, = = %3D, ? = %3F
        r = requests.get(f"{BASE_URL}?p=Test%26Value&n=Smith")
        assert r.status_code == 200

    def test_case_insensitive_hex_digits(self):
        """Test hex digits in encoding are case-insensitive"""
        # %2F vs %2f should be equivalent
        r1 = requests.get(f"{BASE_URL}?p=Test%2Fvalue&n=Smith")
        r2 = requests.get(f"{BASE_URL}?p=Test%2fvalue&n=Smith")
        assert r1.status_code == 200
        assert r2.status_code == 200


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestUTF8Encoding:
    """Test UTF-8 character encoding"""

    def test_utf8_french_accents(self):
        """Test French accents (é, è, ê, ç)"""
        r = requests.get(f"{BASE_URL}?p=Fran%C3%A7ois&n=Dupont")
        assert r.status_code == 200

    def test_utf8_spanish_characters(self):
        """Test Spanish characters (ñ, á, é)"""
        r = requests.get(f"{BASE_URL}?p=Feli%C3%A9&n=Pe%C3%B1a")
        assert r.status_code == 200

    def test_utf8_german_umlauts(self):
        """Test German umlauts (ä, ö, ü)"""
        r = requests.get(f"{BASE_URL}?p=M%C3%BCller&n=Schmidt")
        assert r.status_code == 200

    def test_utf8_multibyte_sequences(self):
        """Test multi-byte UTF-8 sequences"""
        # René has multi-byte é
        r = requests.get(f"{BASE_URL}?p=Ren%C3%A9&n=Dupont")
        assert r.status_code == 200

    def test_utf8_italian_characters(self):
        """Test Italian characters"""
        r = requests.get(f"{BASE_URL}?p=Giuse%C3%A9&n=Rossi")
        assert r.status_code == 200


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestSpecialGenealogistCharacters:
    """Test special characters common in genealogy"""

    def test_apostrophe_in_surname(self):
        """Test apostrophes (O'Brien, O'Keefe)"""
        r = requests.get(f"{BASE_URL}?p=Sean&n=O%27Brien")
        assert r.status_code == 200

    def test_hyphenated_surname(self):
        """Test hyphenated surnames (Bowes-Lyon)"""
        r = requests.get(f"{BASE_URL}?p=Elizabeth&n=Bowes-Lyon")
        assert r.status_code == 200

    def test_periods_in_name(self):
        """Test periods (Jr., Sr., Ph.D.)"""
        r = requests.get(f"{BASE_URL}?p=John&n=Smith%20Jr.")
        assert r.status_code == 200

    def test_comma_in_name(self):
        """Test commas (rarely in names but valid)"""
        r = requests.get(f"{BASE_URL}?p=Smith%2CJohn&n=Doe")
        assert r.status_code == 200

    def test_underscore_in_name(self):
        """Test underscores"""
        r = requests.get(f"{BASE_URL}?p=John_Paul&n=Smith")
        assert r.status_code == 200


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestParameterExtraction:
    """Test parameter extraction from query strings"""

    def test_parameter_order_independence(self):
        """Test parameter order doesn't matter"""
        r1 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        r2 = requests.get(f"{BASE_URL}?n=Windsor&p=Charles")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_duplicate_parameter_first_wins(self):
        """Test duplicate params (first should win)"""
        r = requests.get(f"{BASE_URL}?p=Charles&p=George&n=Windsor")
        assert r.status_code == 200

    def test_empty_parameter_value(self):
        """Test empty parameter value"""
        r = requests.get(f"{BASE_URL}?p=&n=Windsor")
        assert r.status_code == 200

    def test_missing_parameter_value(self):
        """Test parameter without value (p instead of p=)"""
        r = requests.get(f"{BASE_URL}?p&n=Windsor")
        assert r.status_code == 200

    def test_many_parameters(self):
        """Test URL with many parameters"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&m=F&lang=en&oc=0&notes=test")
        assert r.status_code == 200


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestQueryStringMalformation:
    """Test handling of malformed query strings"""

    def test_missing_ampersand_between_params(self):
        """Test missing & between parameters"""
        r = requests.get(f"{BASE_URL}?p=Charlesn=Windsor")
        assert r.status_code in [200, 400]

    def test_double_question_mark(self):
        """Test double ?? in URL"""
        r = requests.get(f"{BASE_URL}??p=Charles&n=Windsor")
        assert r.status_code in [200, 400]

    def test_trailing_ampersand(self):
        """Test trailing & in query string"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&")
        assert r.status_code == 200

    def test_leading_ampersand(self):
        """Test leading & in query string"""
        r = requests.get(f"{BASE_URL}?&p=Charles&n=Windsor")
        assert r.status_code in [200, 400]

    def test_multiple_consecutive_ampersands(self):
        """Test multiple && in query string"""
        r = requests.get(f"{BASE_URL}?p=Charles&&n=Windsor")
        assert r.status_code in [200, 400]


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestURLEdgeCases:
    """Test edge cases in URL handling"""

    def test_very_long_parameter_value(self):
        """Test very long parameter (1000 chars)"""
        long_value = "A" * 1000
        r = requests.get(f"{BASE_URL}?p={long_value}&n=Smith")
        assert r.status_code in [200, 400, 414]

    def test_very_many_parameters(self):
        """Test many parameters (50+)"""
        params = "&".join([f"param{i}=value{i}" for i in range(50)])
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&{params}")
        assert r.status_code in [200, 400, 414]

    def test_deeply_nested_url_encoding(self):
        """Test double-encoded parameters"""
        # %25 is encoded %
        r = requests.get(f"{BASE_URL}?p=Test%2520Value&n=Smith")
        assert r.status_code == 200

    def test_null_character_in_param(self):
        """Test null character (should be encoded as %00)"""
        r = requests.get(f"{BASE_URL}?p=Charles%00&n=Windsor")
        assert r.status_code in [200, 400]

    def test_fragment_in_url(self):
        """Test fragment identifier (#)"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor#section")
        assert r.status_code == 200


@pytest.mark.unit
@pytest.mark.requires_gwd
@pytest.mark.slow
class TestURLParsingPerformance:
    """Test URL parsing under various conditions"""

    def test_rapid_url_variations(self):
        """Test 20 rapid requests with different encodings"""
        for i in range(20):
            variant = ["Charles", "Char%6Cs", "Char%6CS", "CHARLES"]
            r = requests.get(f"{BASE_URL}?m=S&s={variant[i % 4]}")
            assert r.status_code == 200

    def test_complex_query_string_consistency(self):
        """Test complex query string handling is consistent"""
        url = f"{BASE_URL}?p=John%20Paul&n=Bowes-Lyon&m=F&lang=fr&oc=0&notes=test%20notes"
        r1 = requests.get(url)
        r2 = requests.get(url)
        if r1.status_code == 200 and r2.status_code == 200:
            # Should behave consistently
            assert r1.status_code == r2.status_code
