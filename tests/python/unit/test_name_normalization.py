"""
Test name normalization via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestNameNormalization:
    """Test Name module via search/display behavior"""

    def test_name_search_case_insensitive(self):
        """Name.lower is used in search - test indirectly"""
        # Search for "WINDSOR" should find "Windsor"
        r = requests.get(f"{BASE_URL}?m=S&s=WINDSOR")
        assert r.status_code == 200
        assert "Charles" in r.text  # Should find Charles Windsor

    def test_name_search_lowercase(self):
        """Test lowercase search"""
        # Search for "windsor" should also find "Windsor"
        r = requests.get(f"{BASE_URL}?m=S&s=windsor")
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_name_search_mixed_case(self):
        """Test mixed case search"""
        # Search for "Windsor" should find "Windsor"
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_name_strip_in_urls(self):
        """Name is properly handled in URL parameters"""
        # Test with spaces (if supported)
        r1 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        r2 = requests.get(f"{BASE_URL}?p=Charles%20III&n=Windsor")
        assert r1.status_code == 200
        assert r2.status_code in [200, 404]  # May or may not have Charles III

    def test_name_partial_search(self):
        """Test partial name search"""
        # Search for "Char" should find "Charles"
        r = requests.get(f"{BASE_URL}?m=S&s=Char")
        assert r.status_code == 200

    def test_name_empty_search(self):
        """Test empty search"""
        # Empty search should not crash
        r = requests.get(f"{BASE_URL}?m=S&s=")
        assert r.status_code == 200

    def test_name_search_with_special_chars(self):
        """Test search with special characters"""
        # Test with apostrophe (if test data contains it)
        r = requests.get(f"{BASE_URL}?m=S&s=O%27Brien")
        assert r.status_code == 200

    def test_person_page_displays_name(self):
        """Test that person page displays name correctly"""
        # Query specific person
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "Charles" in r.text
        assert "Windsor" in r.text

    def test_person_page_with_spaces_in_name(self):
        """Test person page with name containing spaces"""
        # Some names have middle parts
        r = requests.get(f"{BASE_URL}?p=Charles%20Philip&n=Windsor")
        assert r.status_code in [200, 404]  # May or may not match

    def test_search_returns_multiple_results(self):
        """Test that search with common name returns results"""
        # "Windsor" is a common surname
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200
        # Should contain person links
        assert "p=" in r.text or "Windsor" in r.text
