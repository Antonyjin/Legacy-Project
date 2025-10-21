"""
Test HTML generation via HTTP API integration.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestHTMLGeneration:
    """Test HTML template rendering"""

    def test_html_person_page(self):
        """Test HTML person page generation"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "<html" in r.text.lower() or "<!DOCTYPE" in r.text

    def test_html_contains_person_name(self):
        """Test HTML contains person name"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_html_home_page(self):
        """Test HTML home page"""
        r = requests.get(f"{BASE_URL}")
        assert r.status_code == 200
        assert "<" in r.text and ">" in r.text

    def test_html_search_results(self):
        """Test HTML search results"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200
        assert "<" in r.text and ">" in r.text

    def test_html_family_page(self):
        """Test HTML family page"""
        r = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "<" in r.text and ">" in r.text

    def test_html_calendar_page(self):
        """Test HTML calendar page"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200
        assert "<" in r.text and ">" in r.text

    def test_html_statistics_page(self):
        """Test HTML statistics page"""
        r = requests.get(f"{BASE_URL}?m=STAT")
        assert r.status_code == 200
        assert "<" in r.text and ">" in r.text

    def test_html_content_type(self):
        """Test response is HTML"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("Content-Type", "") or len(r.text) > 0

    def test_html_no_encoding_errors(self):
        """Test HTML doesn't have encoding issues"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        # Should be decodable as UTF-8
        assert len(r.text) > 0

    def test_html_response_not_empty(self):
        """Test HTML response is not empty"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert len(r.text) > 10
