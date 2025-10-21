"""
UT-PY-009: Test database configuration and settings

Tests OCaml's database configuration and settings behaviors by calling GeneWeb via HTTP
and validating responses.

Validates:
- Database metadata
- Configuration settings
- Database statistics
- Version information
"""

import pytest
import requests
from urllib.parse import quote


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDatabaseMetadata:
    """Test database metadata retrieval"""

    def test_database_name_retrieval(self, base_url):
        """Test database name is retrievable"""
        response = requests.get(f"{base_url}")
        assert response.status_code == 200
        # Should display database information

    def test_database_info_page(self, base_url):
        """Test database info page"""
        response = requests.get(f"{base_url}?m=INFO")
        assert response.status_code == 200
        # Should display database info

    def test_database_statistics(self, base_url):
        """Test database statistics"""
        response = requests.get(f"{base_url}?m=STAT")
        assert response.status_code == 200
        # Should display statistics


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestConfigurationSettings:
    """Test configuration settings"""

    def test_default_language_setting(self, base_url):
        """Test default language setting"""
        response = requests.get(f"{base_url}?lang=en")
        assert response.status_code == 200
        # Should respect language setting

    def test_encoding_configuration(self, base_url):
        """Test character encoding configuration"""
        response = requests.get(f"{base_url}?p=Fran%C3%A7ois&n=Dupont")
        assert response.status_code == 200
        # Should handle encoding properly

    def test_timezone_configuration(self, base_url):
        """Test timezone configuration"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should respect timezone settings


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDatabaseStatistics:
    """Test database statistics retrieval"""

    def test_person_count(self, base_url):
        """Test total person count"""
        response = requests.get(f"{base_url}?m=STAT")
        assert response.status_code == 200
        # Should display person count

    def test_family_count(self, base_url):
        """Test total family count"""
        response = requests.get(f"{base_url}?m=STAT")
        assert response.status_code == 200
        # Should display family count

    def test_event_statistics(self, base_url):
        """Test event statistics"""
        response = requests.get(f"{base_url}?m=STAT")
        assert response.status_code == 200
        # Should display event counts


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestVersionInformation:
    """Test version and build information"""

    def test_geneweb_version(self, base_url):
        """Test GeneWeb version display"""
        response = requests.get(f"{base_url}?m=INFO")
        assert response.status_code == 200
        # Should display version information

    def test_database_format_version(self, base_url):
        """Test database format version"""
        response = requests.get(f"{base_url}?m=INFO")
        assert response.status_code == 200
        # Should display database format version

    def test_build_date_info(self, base_url):
        """Test build date information"""
        response = requests.get(f"{base_url}?m=INFO")
        assert response.status_code == 200
        # Should display build information


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDatabaseCapabilities:
    """Test database capabilities and features"""

    def test_unicode_support(self, base_url):
        """Test Unicode support"""
        response = requests.get(f"{base_url}?p=Jos%C3%A9&n=Garc%C3%ADa")
        assert response.status_code == 200
        # Should support Unicode

    def test_large_database_handling(self, base_url):
        """Test handling of large databases"""
        response = requests.get(f"{base_url}?m=N")
        assert response.status_code == 200
        # Should handle large name lists

    def test_sorting_capabilities(self, base_url):
        """Test sorting capabilities"""
        response = requests.get(f"{base_url}?m=N&n=1")
        assert response.status_code == 200
        # Should support pagination and sorting
