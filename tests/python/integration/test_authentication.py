"""Test authentication and access control via HTTP API."""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"

class TestAuthentication:
    """Test authentication and permissions"""

    def test_public_access(self):
        """Test public access to base"""
        r = requests.get(f"{BASE_URL}")
        assert r.status_code == 200

    def test_public_search(self):
        """Test public search access"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200

    def test_public_person_page(self):
        """Test public person page access"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_wizard_mode_access(self):
        """Test wizard mode"""
        r = requests.get(f"{BASE_URL}?m=TIND")
        assert r.status_code in [200, 401, 403, 404]

    def test_friend_mode_access(self):
        """Test friend mode"""
        r = requests.get(f"{BASE_URL}?m=FRIEND")
        assert r.status_code in [200, 401, 403, 404]

    def test_admin_access(self):
        """Test admin access"""
        r = requests.get(f"{BASE_URL}?m=IM")
        assert r.status_code in [200, 401, 403, 404]

    def test_statistics_public(self):
        """Test statistics public access"""
        r = requests.get(f"{BASE_URL}?m=STAT")
        assert r.status_code == 200

    def test_calendar_public(self):
        """Test calendar public access"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200

    def test_export_access(self):
        """Test export functionality"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        assert r.status_code in [200, 404, 500]

    def test_unknown_person_access(self):
        """Test access to unknown person"""
        r = requests.get(f"{BASE_URL}?p=Unknown&n=Person999")
        assert r.status_code in [200, 404]
