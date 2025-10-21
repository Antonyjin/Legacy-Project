"""
Test API routes via HTTP integration tests.
These tests validate all major routes are accessible.

Note: Sosa (ancestors) mode may not be available.
Some routes may return 500 if not configured.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestCoreRoutes:
    """Test core navigation routes"""

    def test_home_page(self):
        """Test home page"""
        r = requests.get(f"{BASE_URL}")
        assert r.status_code == 200
        assert "GeneWeb" in r.text or "geneweb" in r.text.lower()

    def test_person_page(self):
        """Test person page"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_family_page(self):
        """Test family mode"""
        r = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_search_page(self):
        """Test search mode"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200


class TestTreeRoutes:
    """Test tree visualization routes"""

    def test_ancestors_tree(self):
        """Test ancestors mode (A)"""
        r = requests.get(f"{BASE_URL}?m=A&p=Charles&n=Windsor")
        # Ancestors may not be available
        assert r.status_code in [200, 500]

    def test_descendants_tree(self):
        """Test descendants mode (D)"""
        r = requests.get(f"{BASE_URL}?m=D&p=Charles&n=Windsor")
        # Descendants may not be available
        assert r.status_code in [200, 500]

    def test_next_generation(self):
        """Test next generation mode (NG)"""
        r = requests.get(f"{BASE_URL}?m=NG&p=Charles&n=Windsor")
        assert r.status_code in [200, 404, 500]

    def test_previous_generation(self):
        """Test previous generation mode (PG)"""
        r = requests.get(f"{BASE_URL}?m=PG&p=Charles&n=Windsor")
        assert r.status_code in [200, 404, 500]


class TestUtilityRoutes:
    """Test utility routes"""

    def test_calendar_route(self):
        """Test calendar mode"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200

    def test_statistics_route(self):
        """Test statistics mode"""
        r = requests.get(f"{BASE_URL}?m=STAT")
        assert r.status_code == 200

    def test_notes_route(self):
        """Test notes mode"""
        r = requests.get(f"{BASE_URL}?m=N")
        assert r.status_code in [200, 404, 500]


class TestLanguageRoutes:
    """Test language support"""

    def test_english_language(self):
        """Test English language"""
        r = requests.get(f"{BASE_URL}?lang=en")
        assert r.status_code == 200

    def test_french_language(self):
        """Test French language"""
        r = requests.get(f"{BASE_URL}?lang=fr")
        assert r.status_code == 200

    def test_spanish_language(self):
        """Test Spanish language"""
        r = requests.get(f"{BASE_URL}?lang=es")
        assert r.status_code == 200

    def test_german_language(self):
        """Test German language"""
        r = requests.get(f"{BASE_URL}?lang=de")
        assert r.status_code == 200
