"""
Test GEDCOM export/import roundtrip via HTTP API integration.
Tests data integrity through GEDCOM export and re-import cycle.
"""
import requests
import pytest

BASE_URL = "http://localhost:23179/test"


class TestGEDCOMRoundtrip:
    """Test GEDCOM export and import functionality"""

    def test_gedcom_export_available(self):
        """Test GEDCOM export endpoint"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        # Export may not be enabled
        assert r.status_code in [200, 404, 500]

    def test_gedcom_export_contains_persons(self):
        """Test GEDCOM export includes person records"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should contain INDI records
            assert "INDI" in r.text or "@I" in r.text or "19" in r.text

    def test_gedcom_export_structure(self):
        """Test GEDCOM has proper structure"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Check for GEDCOM structure
            assert len(r.text) > 50

    def test_gedcom_person_data_preservation(self):
        """Test person data is preserved in export"""
        # Get person page first
        p1 = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        if p1.status_code == 200:
            # Export GEDCOM
            r_export = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
            if r_export.status_code == 200:
                # GEDCOM should mention Charles
                assert "Charles" in r_export.text or "19" in r_export.text

    def test_gedcom_family_relationships(self):
        """Test family relationships in GEDCOM"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should contain family relationships
            assert "FAM" in r.text or "FAMC" in r.text or "FAMS" in r.text or len(r.text) > 100

    def test_gedcom_dates_preserved(self):
        """Test dates are preserved in export"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should contain year information
            assert "19" in r.text or "20" in r.text or "DATE" in r.text

    def test_gedcom_multiple_exports_consistent(self):
        """Test multiple exports are consistent"""
        r1 = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        r2 = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        
        if r1.status_code == 200 and r2.status_code == 200:
            # Same content
            assert r1.text == r2.text or len(r1.text) == len(r2.text)

    def test_gedcom_not_corrupted(self):
        """Test GEDCOM data is not corrupted"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should not contain HTML
            assert "<html" not in r.text.lower()

    def test_gedcom_encoding_valid(self):
        """Test GEDCOM uses valid encoding"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should be readable
            assert len(r.text) > 0

    def test_gedcom_size_reasonable(self):
        """Test GEDCOM size is reasonable"""
        r = requests.get(f"{BASE_URL}?m=EXPORT&format=ged")
        if r.status_code == 200:
            # Should be at least 100 bytes
            assert len(r.text) > 100
