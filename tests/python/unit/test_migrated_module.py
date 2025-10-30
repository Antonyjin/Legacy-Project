# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
#!/usr/bin/env python3
"""
Unit tests for python_app.migrated module (MIG-INF-002)

Issue: #226 - Expose migrated utils in python_app/migrated/ with tests

Purpose:
    Validate that python_app.migrated correctly exposes all migrated utility
    functions from tests/python/utils/ and that they work correctly when
    imported via the migrated module.

Coverage:
    - Module can be imported
    - All exported functions are accessible
    - Functions work correctly (sample tests for each category)
    - __all__ exports match actual exports
    - Functions match their original implementations
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the migrated module
from python_app import migrated


class TestMigratedModuleImports:
    """Test that python_app.migrated can be imported and all exports are available."""

    def test_module_can_be_imported(self):
        """Test: python_app.migrated module can be imported"""
        assert migrated is not None
        assert hasattr(migrated, '__all__')

    def test_all_exports_are_accessible(self):
        """Test: All functions listed in __all__ are actually accessible"""
        # Get all exported names
        exported = migrated.__all__

        # Check each export is accessible
        missing = []
        for name in exported:
            if not hasattr(migrated, name):
                missing.append(name)

        assert len(missing) == 0, f"Missing exports: {missing}"

    def test_exports_count(self):
        """Test: Expected number of exports"""
        # Should have all migrated functions (30+ exports)
        assert len(migrated.__all__) >= 30, f"Expected at least 30 exports, got {len(migrated.__all__)}"


class TestMigratedNameUtilities:
    """Test name utility functions via python_app.migrated"""

    def test_name_lower(self):
        """Test: name_lower works via migrated module"""
        assert migrated.name_lower("Jean-François") == "jean francois"  # Hyphens become spaces
        assert migrated.name_lower("Mary O'Brien") == "mary o brien"  # Apostrophes become spaces too

    def test_name_strip(self):
        """Test: name_strip works via migrated module"""
        assert migrated.name_strip("  John  ") == "John"
        assert migrated.name_strip("  Mary  ") == "Mary"

    def test_strip_lower(self):
        """Test: strip_lower works via migrated module"""
        assert migrated.strip_lower("  SMITH  ") == "smith"
        assert migrated.strip_lower("  Windsor  ") == "windsor"


class TestMigratedStringUtilities:
    """Test string utility functions via python_app.migrated"""

    def test_strip_c(self):
        """Test: strip_c works via migrated module"""
        assert migrated.strip_c("test", "t") == "es"
        assert migrated.strip_c("genealogy", "g") == "enealoy"  # Removes all 'g' occurrences

    def test_purge(self):
        """Test: purge works via migrated module"""
        # purge only removes FORBIDDEN_CHAR (:, @, #, =, $), not spaces
        assert migrated.purge("test:value") == "testvalue"
        assert migrated.purge("genealogy") == "genealogy"

    def test_contains_forbidden_char(self):
        """Test: contains_forbidden_char works via migrated module"""
        # FORBIDDEN_CHAR includes :, @, #, =, $
        assert migrated.contains_forbidden_char("test:value") == True
        assert migrated.contains_forbidden_char("test@example") == True
        assert migrated.contains_forbidden_char("normal text") == False


class TestMigratedHTTPUtilities:
    """Test HTTP utility functions via python_app.migrated"""

    def test_url_encode(self):
        """Test: url_encode works via migrated module"""
        assert migrated.url_encode("test value") == "test+value"
        assert migrated.url_encode("Smith & Johnson") == "Smith+%26+Johnson"

    def test_url_decode(self):
        """Test: url_decode works via migrated module"""
        assert migrated.url_decode("test+value") == "test value"
        assert migrated.url_decode("Smith+%26+Johnson") == "Smith & Johnson"

    def test_extract_param(self):
        """Test: extract_param works via migrated module"""
        params = [("p", "Charles"), ("n", "Windsor"), ("lang", "en")]
        value, remaining = migrated.extract_param("p", params)
        assert value == "Charles"
        assert len(remaining) == 2


class TestMigratedHTMLUtilities:
    """Test HTML utility functions via python_app.migrated"""

    def test_escape_html(self):
        """Test: escape_html works via migrated module"""
        assert migrated.escape_html("<tag>") == "&lt;tag&gt;"
        assert migrated.escape_html("Smith & Johnson") == "Smith &amp; Johnson"
        assert migrated.escape_html("O'Brien") == "O&#x27;Brien"

    def test_unescape_html(self):
        """Test: unescape_html works via migrated module"""
        assert migrated.unescape_html("&lt;tag&gt;") == "<tag>"
        assert migrated.unescape_html("Smith &amp; Johnson") == "Smith & Johnson"
        assert migrated.unescape_html("O&#x27;Brien") == "O'Brien"


class TestMigratedNumberFormatting:
    """Test number formatting functions via python_app.migrated"""

    def test_format_number_with_separator(self):
        """Test: format_number_with_separator works via migrated module"""
        assert migrated.format_number_with_separator(12345, "en") == "12,345"
        assert migrated.format_number_with_separator(12345, "fr") == "12 345"


class TestMigratedRomanNumerals:
    """Test Roman numeral functions via python_app.migrated"""

    def test_roman_of_arabian(self):
        """Test: roman_of_arabian works via migrated module"""
        assert migrated.roman_of_arabian(188) == "CLXXXVIII"
        assert migrated.roman_of_arabian(2024) == "MMXXIV"

    def test_arabian_of_roman(self):
        """Test: arabian_of_roman works via migrated module"""
        assert migrated.arabian_of_roman("CLXXXVIII") == 188
        assert migrated.arabian_of_roman("MMXXIV") == 2024


class TestMigratedDateValidation:
    """Test date validation functions via python_app.migrated"""

    def test_leap_year(self):
        """Test: leap_year works via migrated module"""
        assert migrated.leap_year(2024) == True
        assert migrated.leap_year(2023) == False
        assert migrated.leap_year(2000) == True  # Century leap year
        assert migrated.leap_year(1900) == False  # Century non-leap year

    def test_nb_days_in_month(self):
        """Test: nb_days_in_month works via migrated module"""
        assert migrated.nb_days_in_month(2, 2024) == 29  # Leap year February
        assert migrated.nb_days_in_month(2, 2023) == 28  # Non-leap year February
        assert migrated.nb_days_in_month(4, 2024) == 30  # April


class TestMigratedDateComparison:
    """Test date comparison functions via python_app.migrated"""

    def test_compare_dmy(self):
        """Test: compare_dmy works via migrated module"""
        from python_app.migrated import Dmy, Precision

        # Create date objects (Dmy requires: day, month, year, prec, delta)
        date1 = Dmy(day=1, month=1, year=2024, prec=Precision.SURE, delta=0)
        date2 = Dmy(day=15, month=1, year=2024, prec=Precision.SURE, delta=0)
        date3 = Dmy(day=1, month=2, year=2024, prec=Precision.SURE, delta=0)

        # Test comparisons
        assert migrated.compare_dmy(date1, date2) < 0  # Earlier date
        assert migrated.compare_dmy(date2, date1) > 0  # Later date
        assert migrated.compare_dmy(date1, date1) == 0  # Same date


class TestMigratedModuleConsistency:
    """Test that python_app.migrated functions match original implementations"""

    def test_name_lower_matches_original(self):
        """Test: migrated name_lower matches original implementation"""
        import sys
        from pathlib import Path
        test_utils_path = Path(__file__).parent.parent.parent.parent / "tests" / "python"
        sys.path.insert(0, str(test_utils_path))
        from utils.name_utils import name_lower as original_name_lower

        test_cases = ["Jean", "SMITH", "O'Brien"]
        for case in test_cases:
            assert migrated.name_lower(case) == original_name_lower(case), \
                f"name_lower mismatch for '{case}'"

    def test_escape_html_matches_original(self):
        """Test: migrated escape_html matches original implementation"""
        import sys
        from pathlib import Path
        test_utils_path = Path(__file__).parent.parent.parent.parent / "tests" / "python"
        sys.path.insert(0, str(test_utils_path))
        from utils.html_utils import escape_html as original_escape_html

        test_cases = ["<tag>", "Smith & Johnson", "O'Brien"]
        for case in test_cases:
            assert migrated.escape_html(case) == original_escape_html(case), \
                f"escape_html mismatch for '{case}'"

    def test_url_encode_matches_original(self):
        """Test: migrated url_encode matches original implementation"""
        import sys
        from pathlib import Path
        test_utils_path = Path(__file__).parent.parent.parent.parent / "tests" / "python"
        sys.path.insert(0, str(test_utils_path))
        from utils.http_params import url_encode as original_url_encode

        test_cases = ["test value", "Smith & Johnson"]
        for case in test_cases:
            assert migrated.url_encode(case) == original_url_encode(case), \
                f"url_encode mismatch for '{case}'"


@pytest.mark.unit
class TestMigratedModuleAPI:
    """Test that python_app.migrated provides a stable API"""

    def test_api_stability(self):
        """Test: All expected functions are available via migrated module"""
        expected_functions = [
            # Name utilities
            "name_lower", "name_strip", "strip_lower",
            # String utilities
            "strip_c", "purge", "contains_forbidden_char",
            # HTTP utilities
            "url_encode", "url_decode", "extract_param", "parse_query_string",
            # HTML utilities
            "escape_html", "unescape_html",
            # Number formatting
            "format_number_with_separator",
            # Roman numerals
            "roman_of_arabian", "arabian_of_roman",
            # Date validation
            "leap_year", "nb_days_in_month",
            # Date comparison
            "compare_dmy", "compare_dmy_opt", "compare_date",
        ]

        for func_name in expected_functions:
            assert hasattr(migrated, func_name), \
                f"Expected function {func_name} not found in python_app.migrated"
