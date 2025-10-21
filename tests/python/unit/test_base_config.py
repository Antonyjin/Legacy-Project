"""
Test base configuration via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestBaseConfig:
    """Test base configuration through API responses"""

    def test_base_home_page(self):
        """Test base home page loads"""
        r = requests.get(f"{BASE_URL}/")
        assert r.status_code == 200

    def test_base_title_in_response(self):
        """Test base name appears in home page"""
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            # Should contain GeneWeb or database name
            assert "GeneWeb" in r.text or "geneweb" in r.text.lower()

    def test_base_search_enabled(self):
        """Test search functionality is enabled"""
        r = requests.get(f"{BASE_URL}?m=S&s=test")
        assert r.status_code == 200

    def test_base_person_page(self):
        """Test person page functionality"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_base_family_mode(self):
        """Test family mode is enabled"""
        r = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_base_statistics(self):
        """Test statistics page"""
        r = requests.get(f"{BASE_URL}?m=STAT")
        assert r.status_code == 200

    def test_base_calendar(self):
        """Test calendar page"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200

    def test_base_language_en(self):
        """Test English language setting"""
        r = requests.get(f"{BASE_URL}?lang=en")
        assert r.status_code == 200

    def test_base_language_fr(self):
        """Test French language setting"""
        r = requests.get(f"{BASE_URL}?lang=fr")
        assert r.status_code == 200

    def test_base_configuration_response_time(self):
        """Test base responds quickly"""
        import time
        start = time.time()
        r = requests.get(f"{BASE_URL}")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5  # Should respond within 5 seconds
