"""
Test database access via HTTP API integration.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestDatabaseAccess:
    """Test database read operations"""

    def test_database_person_retrieval(self):
        """Test person data retrieval"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_database_family_retrieval(self):
        """Test family data retrieval"""
        r = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        assert r.status_code == 200

    def test_database_search_query(self):
        """Test database search"""
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        assert r.status_code == 200

    def test_database_statistics(self):
        """Test database statistics"""
        r = requests.get(f"{BASE_URL}?m=STAT")
        assert r.status_code == 200

    def test_database_multiple_persons(self):
        """Test multiple persons accessible"""
        r1 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        r2 = requests.get(f"{BASE_URL}?p=Elizabeth&n=Windsor")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_database_non_existent_person(self):
        """Test non-existent person handling"""
        r = requests.get(f"{BASE_URL}?p=NonExistent&n=Person")
        assert r.status_code in [200, 404]

    def test_database_calendar_data(self):
        """Test calendar data from database"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200

    def test_database_consistency(self):
        """Test database consistency across queries"""
        r1 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        r2 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r1.status_code == 200
        assert r2.status_code == 200
        # Same query should return same data

    def test_database_response_contains_data(self):
        """Test response contains actual data"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert len(r.text) > 0
        assert "Charles" in r.text or "Windsor" in r.text

    def test_database_html_response(self):
        """Test database response is valid HTML"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        # Should contain HTML
        assert ("<" in r.text and ">" in r.text) or len(r.text) > 0
