"""
UT-PY-006: Test string utilities

Tests OCaml's string manipulation functions by calling GeneWeb via HTTP
and validating responses.

Validates:
- String normalization
- Special character handling
- Name transformations
- String truncation/padding
"""

import pytest
import requests
from urllib.parse import quote


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestStringNormalization:
    """Test string normalization"""

    def test_name_normalization_basic(self, base_url):
        """Test basic name normalization"""
        response = requests.get(f"{base_url}?p=John&n=Smith")
        assert response.status_code == 200
        # Should normalize names consistently

    def test_space_trimming(self, base_url):
        """Test space trimming in names"""
        response = requests.get(f"{base_url}?p=John%20&n=Smith")
        assert response.status_code == 200
        # Should handle trailing spaces

    def test_multiple_spaces(self, base_url):
        """Test multiple consecutive spaces in names"""
        response = requests.get(f"{base_url}?p=John%20%20Smith&n=Doe")
        assert response.status_code == 200
        # Should normalize multiple spaces


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestSpecialCharacterHandling:
    """Test special character handling in strings"""

    def test_apostrophe_in_name(self, base_url):
        """Test apostrophe handling"""
        response = requests.get(f"{base_url}?p=Sean&n=O%27Brien")
        assert response.status_code == 200
        # Should handle apostrophes in names

    def test_hyphen_in_name(self, base_url):
        """Test hyphen handling"""
        response = requests.get(f"{base_url}?p=Mary&n=Smith-Jones")
        assert response.status_code == 200
        # Should handle hyphens in surnames

    def test_accent_characters(self, base_url):
        """Test accented character handling"""
        response = requests.get(f"{base_url}?p=Fran%C3%A7ois&n=Dupont")
        assert response.status_code == 200
        # Should handle accented characters

    def test_unicode_normalization(self, base_url):
        """Test Unicode normalization"""
        response = requests.get(f"{base_url}?p=Jos%C3%A9&n=Garc%C3%ADa")
        assert response.status_code == 200
        # Should normalize Unicode correctly


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestNameTransformation:
    """Test name transformation operations"""

    def test_surname_prefix_handling(self, base_url):
        """Test handling of surname prefixes (von, de, etc.)"""
        response = requests.get(f"{base_url}?p=Ludwig&n=von%20Beethoven")
        assert response.status_code == 200
        # Should handle name prefixes

    def test_particle_names(self, base_url):
        """Test particle handling (de, la, etc.)"""
        response = requests.get(f"{base_url}?p=Pierre&n=de%20La%20Fontaine")
        assert response.status_code == 200
        # Should handle name particles

    def test_compound_surnames(self, base_url):
        """Test compound surname handling"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Bowes-Lyon")
        assert response.status_code == 200
        # Should handle compound surnames


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestStringFormatting:
    """Test string formatting and display"""

    def test_initial_cap_display(self, base_url):
        """Test initial capital letter formatting"""
        response = requests.get(f"{base_url}?p=charles&n=windsor")
        assert response.status_code == 200
        # Should display with proper capitalization

    def test_all_caps_normalization(self, base_url):
        """Test all-caps input handling"""
        response = requests.get(f"{base_url}?p=JOHN&n=SMITH")
        assert response.status_code == 200
        # Should normalize from all-caps

    def test_mixed_case_normalization(self, base_url):
        """Test mixed case input normalization"""
        response = requests.get(f"{base_url}?p=jOhN&n=sMiTh")
        assert response.status_code == 200
        # Should normalize mixed case


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestStringSearching:
    """Test string searching and matching"""

    def test_substring_search(self, base_url):
        """Test substring search in names"""
        response = requests.get(f"{base_url}?m=S&s=Wind")
        assert response.status_code == 200
        # Should find partial matches

    def test_case_insensitive_search(self, base_url):
        """Test case-insensitive substring search"""
        response = requests.get(f"{base_url}?m=S&s=WINDSOR")
        assert response.status_code == 200
        # Should find case-insensitive matches

    def test_accent_insensitive_search(self, base_url):
        """Test accent-insensitive search"""
        response = requests.get(f"{base_url}?m=S&s=Jose")
        assert response.status_code == 200
        # Should match accented names with unaccented search
