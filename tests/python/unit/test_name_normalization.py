# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Test name normalization via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.
"""
import requests

BASE_URL = "http://localhost:23179/test"


class TestNameNormalization:
    """Test Name module via search/display behavior"""

    def test_name_search_case_insensitive(self):
        """Name.lower is used in search"""
        r = requests.get(f"{BASE_URL}?m=NG&n=WINDSOR", timeout=5)
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_name_search_lowercase(self):
        """Test lowercase search"""
        r = requests.get(f"{BASE_URL}?m=NG&n=windsor", timeout=5)
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_name_search_mixed_case(self):
        """Test mixed case search"""
        r = requests.get(f"{BASE_URL}?m=NG&n=Windsor", timeout=5)
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_name_strip_in_urls(self):
        """Name is properly handled in URL parameters"""
        r1 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor", timeout=5)
        r2 = requests.get(f"{BASE_URL}?p=Charles%20III&n=Windsor", timeout=5)
        assert r1.status_code == 200
        assert r2.status_code in [200, 404]

    def test_name_exact_search_works(self):
        """Test exact name search works"""
        r = requests.get(f"{BASE_URL}?m=NG&n=Windsor", timeout=5)
        assert r.status_code == 200
        assert "Windsor" in r.text

    def test_person_page_displays_name(self):
        """Test that person page displays name correctly"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor", timeout=5)
        assert r.status_code == 200
        assert "Charles" in r.text
        assert "Windsor" in r.text

    def test_search_returns_multiple_results(self):
        """Test that search with common name returns results"""
        r = requests.get(f"{BASE_URL}?m=NG&n=Windsor", timeout=5)
        assert r.status_code == 200
        assert "p=" in r.text and "Windsor" in r.text
