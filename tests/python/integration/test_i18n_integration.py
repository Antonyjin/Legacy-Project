"""Test localization integration via HTTP API."""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"

class TestI18NIntegration:
    """Test i18n across all pages"""

    def test_english_home(self):
        r = requests.get(f"{BASE_URL}?lang=en")
        assert r.status_code == 200

    def test_french_home(self):
        r = requests.get(f"{BASE_URL}?lang=fr")
        assert r.status_code == 200
        assert any(w in r.text for w in ["Accueil", "Personne", "Famille"])

    def test_spanish_home(self):
        r = requests.get(f"{BASE_URL}?lang=es")
        assert r.status_code == 200

    def test_language_in_search(self):
        r_en = requests.get(f"{BASE_URL}?m=S&s=Windsor&lang=en")
        r_fr = requests.get(f"{BASE_URL}?m=S&s=Windsor&lang=fr")
        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_language_fallback(self):
        r = requests.get(f"{BASE_URL}?lang=xx")
        assert r.status_code == 200

    def test_language_in_person_page(self):
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&lang=fr")
        assert r.status_code == 200

    def test_language_in_calendar(self):
        r = requests.get(f"{BASE_URL}?m=CAL&lang=fr")
        assert r.status_code == 200

    def test_language_in_statistics(self):
        r = requests.get(f"{BASE_URL}?m=STAT&lang=fr")
        assert r.status_code == 200

    def test_multiple_languages_supported(self):
        langs = ["en", "fr", "es", "de", "it"]
        for lang in langs:
            r = requests.get(f"{BASE_URL}?lang={lang}")
            assert r.status_code == 200, f"Language {lang} failed"

    def test_language_persistence(self):
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&lang=fr&m=F")
        assert r.status_code == 200
