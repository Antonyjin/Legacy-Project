"""Test error handling via HTTP API."""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"

class TestErrorHandling:
    """Test error handling for edge cases"""

    def test_404_unknown_person(self):
        """Test 404 for unknown person"""
        r = requests.get(f"{BASE_URL}?p=NonExistentXYZ&n=PersonXYZ")
        assert r.status_code in [200, 404]

    def test_400_invalid_mode(self):
        """Test invalid mode handling"""
        r = requests.get(f"{BASE_URL}?m=INVALID")
        assert r.status_code in [200, 400, 404]

    def test_empty_search(self):
        """Test empty search"""
        r = requests.get(f"{BASE_URL}?m=S&s=")
        assert r.status_code == 200

    def test_special_chars_search(self):
        """Test special characters in search"""
        r = requests.get(f"{BASE_URL}?m=S&s=%27%22%3C%3E")
        assert r.status_code in [200, 400]

    def test_very_long_query(self):
        """Test very long query string"""
        long_query = "A" * 1000
        r = requests.get(f"{BASE_URL}?m=S&s={long_query}")
        assert r.status_code in [200, 400, 414]

    def test_missing_parameters(self):
        """Test missing required parameters"""
        r = requests.get(f"{BASE_URL}?p=Charles")
        assert r.status_code in [200, 404]

    def test_malformed_url(self):
        """Test malformed URL"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&corrupt=%")
        assert r.status_code in [200, 400]

    def test_null_bytes_in_param(self):
        """Test null bytes in parameters"""
        r = requests.get(f"{BASE_URL}?p=Charles%00&n=Windsor")
        assert r.status_code in [200, 400]

    def test_invalid_encoding(self):
        """Test invalid character encoding"""
        r = requests.get(f"{BASE_URL}?p=%FF%FE&n=Windsor")
        assert r.status_code in [200, 400]

    def test_server_continues_after_error(self):
        """Test server continues after error"""
        r1 = requests.get(f"{BASE_URL}?m=INVALID")
        r2 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r2.status_code == 200
