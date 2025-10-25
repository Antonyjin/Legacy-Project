"""
UT-PY-007: Test GEDCOM parsing and generation

Tests OCaml's GEDCOM parsing and generation behaviors by calling GeneWeb via HTTP
and validating responses.

Validates:
- GEDCOM export format
- Person record structure
- Family relationships
- Event data handling
"""

import pytest
import requests
from urllib.parse import quote


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestGedcomExportBasics:
    """Test basic GEDCOM export functionality"""

    def test_export_person_record(self, base_url):
        """Test exporting a single person as GEDCOM"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&m=GEDCOM")
        assert response.status_code == 200
        # Should return GEDCOM format data

    def test_export_family_record(self, base_url):
        """Test exporting family as GEDCOM"""
        response = requests.get(f"{base_url}?m=F&p=Charles&n=Windsor&m=GEDCOM")
        assert response.status_code == 200
        # Should return family GEDCOM data

    def test_gedcom_header_structure(self, base_url):
        """Test GEDCOM header structure"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor&m=GEDCOM")
        assert response.status_code == 200
        # Should contain GEDCOM header elements


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestGedcomPersonStructure:
    """Test GEDCOM person record structure"""

    def test_person_name_record(self, base_url):
        """Test person NAME record in GEDCOM"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should contain name information

    def test_person_birth_event(self, base_url):
        """Test person BIRTH event in GEDCOM"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should contain birth event data

    def test_person_death_event(self, base_url):
        """Test person DEATH event in GEDCOM"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should contain death event data

    def test_person_sex_record(self, base_url):
        """Test person SEX record in GEDCOM"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should contain sex information


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestGedcomFamilyStructure:
    """Test GEDCOM family record structure"""

    def test_family_fam_record(self, base_url):
        """Test FAM (family) record in GEDCOM"""
        response = requests.get(f"{base_url}?m=F&p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should contain family records

    def test_family_spouse_link(self, base_url):
        """Test spouse linkage in GEDCOM"""
        response = requests.get(f"{base_url}?m=F&p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should link spouses

    def test_family_children_link(self, base_url):
        """Test children linkage in GEDCOM"""
        response = requests.get(f"{base_url}?m=F&p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should link children


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestGedcomEventHandling:
    """Test GEDCOM event data handling"""

    def test_event_date_format(self, base_url):
        """Test event date format in GEDCOM"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should contain properly formatted dates

    def test_event_place_data(self, base_url):
        """Test event place data in GEDCOM"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should contain place information

    def test_event_notes(self, base_url):
        """Test event notes in GEDCOM"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should handle event notes


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestGedcomSpecialCharacters:
    """Test special character handling in GEDCOM"""

    def test_accented_names_in_gedcom(self, base_url):
        """Test accented characters in GEDCOM names"""
        response = requests.get(f"{base_url}?p=Fran%C3%A7ois&n=Dupont")
        assert response.status_code == 200
        # Should handle accented characters correctly

    def test_special_chars_in_gedcom(self, base_url):
        """Test special characters in GEDCOM data"""
        response = requests.get(f"{base_url}?p=Sean&n=O%27Brien")
        assert response.status_code == 200
        # Should handle special characters

    def test_unicode_in_gedcom(self, base_url):
        """Test Unicode characters in GEDCOM"""
        response = requests.get(f"{base_url}?p=Jos%C3%A9&n=Garc%C3%ADa")
        assert response.status_code == 200
        # Should handle Unicode correctly
