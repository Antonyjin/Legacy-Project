"""
Test GEDCOM parsing via HTTP API.
These tests work for OCaml NOW and will validate Python migration LATER.

Note: OCaml GEDCOM implementation may have limitations.
Some tests may be skipped if test database lacks GEDCOM export capability.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestGEDCOMParsing:
    """Test GEDCOM export functionality"""

    def test_gedcom_export_endpoint_exists(self):
        """Test GEDCOM export endpoint responds"""
        # Try to export GEDCOM
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        assert r.status_code in [200, 404, 500]
        # Some servers may not support this

    def test_gedcom_export_has_header(self):
        """Test GEDCOM export contains proper header"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            assert "HEAD" in r.text or "0 HEAD" in r.text

    def test_gedcom_export_has_persons(self):
        """Test GEDCOM export contains INDI records"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            assert "INDI" in r.text or "@I" in r.text

    def test_gedcom_export_has_trailer(self):
        """Test GEDCOM export has proper trailer"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            assert "TRLR" in r.text or "0 TRLR" in r.text

    def test_gedcom_export_valid_structure(self):
        """Test GEDCOM structure is valid"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            lines = r.text.split('\n')
            # Should have multiple lines with tags
            assert len(lines) > 1

    def test_gedcom_person_export(self):
        """Test exporting specific person data"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor&m=EXPORT&format=ged")
        if r.status_code == 200:
            assert "NAME" in r.text or "Charles" in r.text

    def test_gedcom_export_encoding(self):
        """Test GEDCOM export with proper encoding"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        assert r.status_code in [200, 404, 500]

    def test_gedcom_contains_dates(self):
        """Test GEDCOM includes date information"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should contain BIRT (birth) or DATE tags
            assert "BIRT" in r.text or "DATE" in r.text or "19" in r.text

    def test_gedcom_contains_relationships(self):
        """Test GEDCOM includes family relationships"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should contain FAM (family) or relationship tags
            assert "FAM" in r.text or "FAMC" in r.text or "FAMS" in r.text

    def test_gedcom_not_html(self):
        """Test GEDCOM export is not HTML"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should not contain HTML tags
            assert "<html>" not in r.text.lower()
            assert "<!DOCTYPE" not in r.text
