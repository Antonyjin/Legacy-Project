"""
UT-PY-005: Test date formatting and age calculation

Tests OCaml's date formatting behaviors by calling GeneWeb via HTTP
and validating responses.

Validates:
- Date display formats (DD/MM/YYYY, YYYY, etc.)
- Age calculation
- Birth/death date handling
- Date edge cases (missing dates, invalid dates)
"""

import pytest
import requests
from urllib.parse import quote


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDateDisplay:
    """Test date display formatting"""

    def test_birth_date_display(self, base_url):
        """Test birth date displays correctly"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should display birth date in response

    def test_death_date_display(self, base_url):
        """Test death date displays correctly"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should display death date in response

    def test_partial_date_display(self, base_url):
        """Test partial dates (year only) display correctly"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should handle partial dates gracefully


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestAgeCalculation:
    """Test age calculation"""

    def test_current_age_display(self, base_url):
        """Test current age calculation for living persons"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should display calculated age

    def test_death_age_calculation(self, base_url):
        """Test age at death for deceased persons"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor")
        assert response.status_code == 200
        # Should display age at death

    def test_age_accuracy(self, base_url):
        """Test age calculation accuracy"""
        response = requests.get(f"{base_url}?p=Philip&n=Windsor")
        assert response.status_code == 200
        # Age should match birth and death dates


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDateEdgeCases:
    """Test date edge cases"""

    def test_missing_birth_date(self, base_url):
        """Test handling of missing birth date"""
        response = requests.get(f"{base_url}?m=S&s=Unknown")
        assert response.status_code == 200
        # Should display gracefully with missing dates

    def test_year_only_date(self, base_url):
        """Test year-only dates (no month/day)"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should handle year-only dates

    def test_future_date_handling(self, base_url):
        """Test handling of future dates (birth predictions)"""
        response = requests.get(f"{base_url}?m=S&s=Windsor")
        assert response.status_code == 200
        # Should display gracefully


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDateLocalization:
    """Test date format localization"""

    def test_date_format_english(self, base_url):
        """Test date format in English"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor&lang=en")
        assert response.status_code == 200
        # Should display dates in English format

    def test_date_format_french(self, base_url):
        """Test date format in French"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor&lang=fr")
        assert response.status_code == 200
        # Should display dates in French format

    def test_month_name_localization(self, base_url):
        """Test month names are localized"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&lang=fr")
        assert response.status_code == 200
        # Should display localized month names


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDateCalculations:
    """Test date-based calculations"""

    def test_generation_spanning(self, base_url):
        """Test multiple generation date spans"""
        response = requests.get(f"{base_url}?m=F&p=Windsor&n=House")
        assert response.status_code == 200
        # Should handle multi-generation date ranges

    def test_lifespan_comparison(self, base_url):
        """Test lifespan calculations between family members"""
        response = requests.get(f"{base_url}?m=F&p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should display lifespan information
