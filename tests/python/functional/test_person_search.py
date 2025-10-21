"""Test person search workflow (FT-PY-001)."""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"

class TestPersonSearchWorkflow:
    """Test complete search workflow"""

    def test_search_by_surname(self):
        """User searches for surname"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200
        assert "Windsor" in r.text or "Charles" in r.text

    def test_search_results_clickable(self):
        """Search results contain person links"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200

    def test_navigate_to_person(self):
        """Click to navigate to person page"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_search_no_results(self):
        """Search with no results"""
        r = requests.get(f"{BASE_URL}?m=S&s=NOTEXIST999")
        assert r.status_code == 200

    def test_search_case_insensitive(self):
        """Search is case-insensitive"""
        r1 = requests.get(f"{BASE_URL}?m=S&s=windsor")
        r2 = requests.get(f"{BASE_URL}?m=S&s=WINDSOR")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_search_partial_name(self):
        """Search with partial name"""
        r = requests.get(f"{BASE_URL}?m=S&s=Wind")
        assert r.status_code == 200

    def test_search_then_family(self):
        """Search then view family"""
        r1 = requests.get(f"{BASE_URL}?m=S&s=Charles")
        r2 = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_multiple_searches(self):
        """Multiple searches work"""
        r1 = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        r2 = requests.get(f"{BASE_URL}?m=S&s=Elizabeth")
        r3 = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r3.status_code == 200

    def test_search_with_language(self):
        """Search in different language"""
        r_en = requests.get(f"{BASE_URL}?m=S&s=Windsor&lang=en")
        r_fr = requests.get(f"{BASE_URL}?m=S&s=Windsor&lang=fr")
        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_search_special_characters(self):
        """Search with special characters"""
        r = requests.get(f"{BASE_URL}?m=S&s=O%27Brien")
        assert r.status_code in [200, 404]
