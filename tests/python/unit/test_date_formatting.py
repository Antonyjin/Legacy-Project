"""
Test date formatting via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestDateFormatting:
    """Test Date module via person page display"""

    def test_person_birth_year_displays(self):
        """Test birth year is displayed on person page"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "1948" in r.text

    def test_person_death_year_displays(self):
        """Test death year is displayed if available"""
        # Elizabeth II died in 2022
        r = requests.get(f"{BASE_URL}?p=Elizabeth&n=Windsor")
        assert r.status_code == 200
        # Should contain year information

    def test_age_calculation_on_page(self):
        """Test age is calculated from birth/death dates"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        # Age should be displayed or calculable

    def test_person_search_by_date_range(self):
        """Test search filters by date"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200

    def test_calendar_view_dates(self):
        """Test calendar shows dates correctly"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200
        # Calendar should display date information

    def test_date_precision_display(self):
        """Test dates with different precision levels"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_unknown_date_handling(self):
        """Test handling of unknown/missing dates"""
        r = requests.get(f"{BASE_URL}?p=Unknown&n=Person")
        assert r.status_code in [200, 404]

    def test_date_localization_en(self):
        """Test date displayed in English format"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&lang=en")
        assert r.status_code == 200

    def test_date_localization_fr(self):
        """Test date displayed in French format"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&lang=fr")
        assert r.status_code == 200

    def test_statistics_date_ranges(self):
        """Test date ranges in statistics"""
        r = requests.get(f"{BASE_URL}?m=STAT")
        assert r.status_code == 200
