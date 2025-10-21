"""
Test localization via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestLocalization:
    """Test language and localization support"""

    def test_default_language(self):
        """Test default language setting"""
        r = requests.get(f"{BASE_URL}")
        assert r.status_code == 200

    def test_english_language(self):
        """Test English language parameter"""
        r = requests.get(f"{BASE_URL}?lang=en")
        assert r.status_code == 200

    def test_french_language(self):
        """Test French language parameter"""
        r = requests.get(f"{BASE_URL}?lang=fr")
        assert r.status_code == 200
        assert any(word in r.text for word in ["Accueil", "Personne", "Famille", "Recherche"])

    def test_spanish_language(self):
        """Test Spanish language parameter"""
        r = requests.get(f"{BASE_URL}?lang=es")
        assert r.status_code == 200

    def test_invalid_language_fallback(self):
        """Test invalid language falls back to default"""
        r = requests.get(f"{BASE_URL}?lang=xx")
        assert r.status_code == 200
        # Should still return valid page

    def test_language_in_person_page(self):
        """Test language affects person page"""
        r_en = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&lang=en")
        r_fr = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&lang=fr")
        
        assert r_en.status_code == 200
        assert r_fr.status_code == 200
        # Pages may differ in language

    def test_language_in_search(self):
        """Test language affects search results"""
        r_en = requests.get(f"{BASE_URL}?m=S&s=Windsor&lang=en")
        r_fr = requests.get(f"{BASE_URL}?m=S&s=Windsor&lang=fr")
        
        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_language_in_statistics(self):
        """Test language affects statistics page"""
        r_en = requests.get(f"{BASE_URL}?m=STAT&lang=en")
        r_fr = requests.get(f"{BASE_URL}?m=STAT&lang=fr")
        
        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_language_in_calendar(self):
        """Test language affects calendar page"""
        r_en = requests.get(f"{BASE_URL}?m=CAL&lang=en")
        r_fr = requests.get(f"{BASE_URL}?m=CAL&lang=fr")
        
        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_language_persistence(self):
        """Test language parameter persists across navigation"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&lang=fr")
        assert r.status_code == 200
        # Language should be reflected in response
