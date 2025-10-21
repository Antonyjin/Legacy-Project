"""
Test string utilities via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestStringUtils:
    """Test string utility functions via search and display"""

    def test_search_with_spaces(self):
        """Test search handles spaces in names"""
        r = requests.get(f"{BASE_URL}?m=S&s=Charles%20Philip")
        assert r.status_code == 200

    def test_search_with_unicode(self):
        """Test search handles Unicode characters"""
        r = requests.get(f"{BASE_URL}?m=S&s=Fran%C3%A7ois")
        assert r.status_code == 200

    def test_search_with_hyphens(self):
        """Test search handles hyphenated names"""
        r = requests.get(f"{BASE_URL}?m=S&s=Bowes-Lyon")
        assert r.status_code == 200

    def test_search_trims_whitespace(self):
        """Test leading/trailing spaces are handled"""
        r = requests.get(f"{BASE_URL}?m=S&s=%20Windsor%20")
        assert r.status_code == 200

    def test_url_encoding_special_chars(self):
        """Test URL encoding of special characters"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&notes=%40test")
        assert r.status_code == 200

    def test_string_display_in_person_page(self):
        """Test strings display correctly on person pages"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "Charles" in r.text
        assert "Windsor" in r.text

    def test_empty_string_handling(self):
        """Test empty strings are handled gracefully"""
        r = requests.get(f"{BASE_URL}?m=S&s=")
        assert r.status_code == 200

    def test_very_long_string(self):
        """Test long strings don't crash server"""
        long_str = "A" * 500
        r = requests.get(f"{BASE_URL}?m=S&s={long_str}")
        assert r.status_code in [200, 400, 414]

    def test_newline_handling_in_params(self):
        """Test newlines in parameters"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&notes=test%0Aline2")
        assert r.status_code == 200

    def test_special_characters_in_search(self):
        """Test various special characters in search"""
        special_chars = ["%21", "%40", "%23", "%24", "%25", "%5E", "%26"]
        for char in special_chars:
            r = requests.get(f"{BASE_URL}?m=S&s=test{char}")
            assert r.status_code in [200, 400]
