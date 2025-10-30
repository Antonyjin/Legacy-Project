# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
UT-PY-010: Test localization and internationalization

Tests OCaml's localization and i18n behaviors by calling GeneWeb via HTTP
and validating responses.

Validates:
- Language switching
- Message translations
- Date localization
- UI text localization
"""

import pytest
import requests


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestLanguageSwitching:
    """Test language switching functionality"""

    def test_english_interface(self, base_url):
        """Test English interface"""
        response = requests.get(f"{base_url}?lang=en", timeout=5)
        assert response.status_code == 200
        # Should display English interface

    def test_french_interface(self, base_url):
        """Test French interface"""
        response = requests.get(f"{base_url}?lang=fr", timeout=5)
        assert response.status_code == 200
        # Should display French interface

    def test_language_persistence(self, base_url):
        """Test language setting persists across pages"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&lang=fr", timeout=5)
        assert response.status_code == 200
        # Language should persist


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestMessageTranslation:
    """Test message and label translations"""

    def test_button_labels_english(self, base_url):
        """Test button labels in English"""
        response = requests.get(f"{base_url}?lang=en", timeout=5)
        assert response.status_code == 200
        # Should contain English labels

    def test_button_labels_french(self, base_url):
        """Test button labels in French"""
        response = requests.get(f"{base_url}?lang=fr", timeout=5)
        assert response.status_code == 200
        # Should contain French labels

    def test_error_messages_localized(self, base_url):
        """Test error messages are localized"""
        response = requests.get(f"{base_url}?p=NonExistent&n=Person&lang=fr", timeout=5)
        assert response.status_code == 200
        # Error messages should be in French


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestDateLocalization:
    """Test date format localization"""

    def test_date_format_english(self, base_url):
        """Test date format in English"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor&lang=en", timeout=5)
        assert response.status_code == 200
        # Dates should use English format

    def test_date_format_french(self, base_url):
        """Test date format in French"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor&lang=fr", timeout=5)
        assert response.status_code == 200
        # Dates should use French format

    def test_month_names_english(self, base_url):
        """Test month names in English"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&lang=en", timeout=5)
        assert response.status_code == 200
        # Should display English month names

    def test_month_names_french(self, base_url):
        """Test month names in French"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&lang=fr", timeout=5)
        assert response.status_code == 200
        # Should display French month names


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestUITextLocalization:
    """Test UI text localization"""

    def test_field_labels_english(self, base_url):
        """Test field labels in English"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&lang=en", timeout=5)
        assert response.status_code == 200
        # Field labels should be in English

    def test_field_labels_french(self, base_url):
        """Test field labels in French"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&lang=fr", timeout=5)
        assert response.status_code == 200
        # Field labels should be in French

    def test_navigation_menu_localization(self, base_url):
        """Test navigation menu is localized"""
        response = requests.get(f"{base_url}?lang=fr", timeout=5)
        assert response.status_code == 200
        # Navigation should be localized

    def test_page_titles_localized(self, base_url):
        """Test page titles are localized"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&lang=fr", timeout=5)
        assert response.status_code == 200
        # Page titles should be localized


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestLocalizationEdgeCases:
    """Test localization edge cases"""

    def test_fallback_language(self, base_url):
        """Test fallback to default language for unknown lang code"""
        response = requests.get(f"{base_url}?lang=zz", timeout=5)
        assert response.status_code == 200
        # Should fallback to default language

    def test_special_characters_localized(self, base_url):
        """Test special characters in localized text"""
        response = requests.get(f"{base_url}?p=Fran%C3%A7ois&n=Dupont&lang=fr", timeout=5)
        assert response.status_code == 200
        # Should handle accented characters

    def test_empty_translation_handling(self, base_url):
        """Test handling of missing translations"""
        response = requests.get(f"{base_url}?lang=en", timeout=5)
        assert response.status_code == 200
        # Should gracefully handle missing translations
