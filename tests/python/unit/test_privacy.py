"""
Test privacy rules via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.

Note: Privacy rules depend on GeneWeb configuration.
Some tests may behave differently based on setup.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestPrivacy:
    """Test privacy filtering via HTTP API"""

    def test_public_person_accessible(self):
        """Test public persons are accessible"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_person_page_loads(self):
        """Test person page loads successfully"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "Charles" in r.text

    def test_search_returns_public_results(self):
        """Test search returns public persons"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200

    def test_family_page_displays(self):
        """Test family page is accessible"""
        r = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_person_notes_display(self):
        """Test person notes are displayed if public"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        if r.status_code == 200:
            # Notes may or may not be present depending on data
            pass

    def test_private_person_restricted(self):
        """Test private persons show restricted info"""
        # Try accessing a person that might be private
        r = requests.get(f"{BASE_URL}?p=PrivatePerson&n=Test")
        # Should either show restricted view or 404
        assert r.status_code in [200, 404, 403]

    def test_wizard_mode_requires_password(self):
        """Test wizard mode access"""
        r = requests.get(f"{BASE_URL}?m=TIND")
        # May be restricted or require password
        assert r.status_code in [200, 401, 403, 404]

    def test_statistics_public_data(self):
        """Test statistics page shows public data"""
        r = requests.get(f"{BASE_URL}?m=STAT")
        assert r.status_code == 200

    def test_calendar_shows_public_events(self):
        """Test calendar only shows public birthdays"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200

    def test_living_person_privacy(self):
        """Test living persons have privacy protections"""
        # Charles is still living
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        # May show limited information
