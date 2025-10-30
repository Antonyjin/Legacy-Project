# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
UT-PY-011: Test number formatting with thousands separator

Tests the Python implementation of number formatting that replicates
the OCaml behavior from Mutil.string_of_int_sep.

This validates the migration of number formatting logic from OCaml to Python,
ensuring consistency with GeneWeb's localized thousand separators.

OCaml References:
- source_geneweb/lib/util/mutil.ml: string_of_int_sep function
- source_geneweb/lib/allnDisplay.ml: format_with_thousand_sep
- GeneWeb/gw/lang/lexicon.txt: (thousand separator) translations

Issue: MIG-008 - Migrate number formatting with thousands separator
"""

import sys
from pathlib import Path

import pytest

# Add tests/python to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.number_formatter import LOCALE_SEPARATORS, format_number_with_separator, get_locale_separator


@pytest.mark.unit
class TestBasicNumberFormatting:
    """Test basic number formatting with different locales"""

    def test_format_zero(self):
        """Zero should be formatted as '0' regardless of locale"""
        assert format_number_with_separator(0, 'en') == '0'
        assert format_number_with_separator(0, 'fr') == '0'
        assert format_number_with_separator(0, 'de') == '0'

    def test_format_small_numbers(self):
        """Numbers under 1000 should not have separators"""
        assert format_number_with_separator(1, 'en') == '1'
        assert format_number_with_separator(99, 'en') == '99'
        assert format_number_with_separator(999, 'en') == '999'

        # Same behavior for all locales
        assert format_number_with_separator(500, 'fr') == '500'
        assert format_number_with_separator(500, 'de') == '500'

    def test_format_one_thousand_english(self):
        """1000 in English should use comma separator"""
        assert format_number_with_separator(1000, 'en') == '1,000'

    def test_format_one_thousand_french(self):
        """1000 in French should use space separator"""
        assert format_number_with_separator(1000, 'fr') == '1 000'

    def test_format_one_thousand_german(self):
        """1000 in German should use dot separator"""
        assert format_number_with_separator(1000, 'de') == '1.000'


@pytest.mark.unit
class TestLocaleSeparators:
    """Test locale-specific thousand separators"""

    def test_english_comma_separator(self):
        """English uses comma as thousand separator"""
        assert format_number_with_separator(10000, 'en') == '10,000'
        assert format_number_with_separator(100000, 'en') == '100,000'
        assert format_number_with_separator(1000000, 'en') == '1,000,000'

    def test_french_space_separator(self):
        """French uses space as thousand separator"""
        assert format_number_with_separator(10000, 'fr') == '10 000'
        assert format_number_with_separator(100000, 'fr') == '100 000'
        assert format_number_with_separator(1000000, 'fr') == '1 000 000'

    def test_german_dot_separator(self):
        """German uses dot as thousand separator"""
        assert format_number_with_separator(10000, 'de') == '10.000'
        assert format_number_with_separator(100000, 'de') == '100.000'
        assert format_number_with_separator(1000000, 'de') == '1.000.000'

    def test_spanish_dot_separator(self):
        """Spanish uses dot as thousand separator"""
        assert format_number_with_separator(5000, 'es') == '5.000'

    def test_italian_dot_separator(self):
        """Italian uses dot as thousand separator"""
        assert format_number_with_separator(5000, 'it') == '5.000'

    def test_hebrew_comma_separator(self):
        """Hebrew uses comma as thousand separator"""
        assert format_number_with_separator(5000, 'he') == '5,000'

    def test_turkish_comma_separator(self):
        """Turkish uses comma as thousand separator"""
        assert format_number_with_separator(5000, 'tr') == '5,000'

    def test_russian_apostrophe_separator(self):
        """Russian uses apostrophe as thousand separator"""
        assert format_number_with_separator(5000, 'ru') == "5'000"

    def test_latvian_apostrophe_separator(self):
        """Latvian uses apostrophe as thousand separator"""
        assert format_number_with_separator(5000, 'lv') == "5'000"


@pytest.mark.unit
class TestLocaleAliases:
    """Test locale aliases (e.g., en_US -> en)"""

    def test_en_us_alias(self):
        """en_US should map to 'en' locale"""
        assert format_number_with_separator(1000, 'en_US') == '1,000'

    def test_en_gb_alias(self):
        """en_GB should map to 'en' locale"""
        assert format_number_with_separator(1000, 'en_GB') == '1,000'

    def test_fr_fr_alias(self):
        """fr_FR should map to 'fr' locale"""
        assert format_number_with_separator(1000, 'fr_FR') == '1 000'

    def test_de_de_alias(self):
        """de_DE should map to 'de' locale"""
        assert format_number_with_separator(1000, 'de_DE') == '1.000'

    def test_es_es_alias(self):
        """es_ES should map to 'es' locale"""
        assert format_number_with_separator(1000, 'es_ES') == '1.000'


@pytest.mark.unit
class TestNegativeNumbers:
    """Test formatting of negative numbers"""

    def test_negative_small_number(self):
        """Negative numbers under 1000 should not have separators"""
        assert format_number_with_separator(-1, 'en') == '-1'
        assert format_number_with_separator(-99, 'en') == '-99'
        assert format_number_with_separator(-999, 'en') == '-999'

    def test_negative_thousand_english(self):
        """Negative thousand in English"""
        assert format_number_with_separator(-1000, 'en') == '-1,000'
        assert format_number_with_separator(-10000, 'en') == '-10,000'

    def test_negative_thousand_french(self):
        """Negative thousand in French"""
        assert format_number_with_separator(-1000, 'fr') == '-1 000'
        assert format_number_with_separator(-10000, 'fr') == '-10 000'

    def test_negative_thousand_german(self):
        """Negative thousand in German"""
        assert format_number_with_separator(-1000, 'de') == '-1.000'
        assert format_number_with_separator(-10000, 'de') == '-10.000'

    def test_negative_million(self):
        """Negative million across locales"""
        assert format_number_with_separator(-1000000, 'en') == '-1,000,000'
        assert format_number_with_separator(-1000000, 'fr') == '-1 000 000'
        assert format_number_with_separator(-1000000, 'de') == '-1.000.000'


@pytest.mark.unit
class TestLargeNumbers:
    """Test formatting of large numbers"""

    def test_ten_thousand(self):
        """Format 10,000 across locales"""
        assert format_number_with_separator(10000, 'en') == '10,000'
        assert format_number_with_separator(10000, 'fr') == '10 000'
        assert format_number_with_separator(10000, 'de') == '10.000'

    def test_hundred_thousand(self):
        """Format 100,000 across locales"""
        assert format_number_with_separator(100000, 'en') == '100,000'
        assert format_number_with_separator(100000, 'fr') == '100 000'
        assert format_number_with_separator(100000, 'de') == '100.000'

    def test_one_million(self):
        """Format 1,000,000 across locales"""
        assert format_number_with_separator(1000000, 'en') == '1,000,000'
        assert format_number_with_separator(1000000, 'fr') == '1 000 000'
        assert format_number_with_separator(1000000, 'de') == '1.000.000'

    def test_ten_million(self):
        """Format 10,000,000 across locales"""
        assert format_number_with_separator(10000000, 'en') == '10,000,000'
        assert format_number_with_separator(10000000, 'fr') == '10 000 000'
        assert format_number_with_separator(10000000, 'de') == '10.000.000'

    def test_billion(self):
        """Format 1,000,000,000 across locales"""
        assert format_number_with_separator(1000000000, 'en') == '1,000,000,000'
        assert format_number_with_separator(1000000000, 'fr') == '1 000 000 000'
        assert format_number_with_separator(1000000000, 'de') == '1.000.000.000'


@pytest.mark.unit
class TestGeneWebDataSizes:
    """Test realistic numbers from GeneWeb (persons count, etc.)"""

    def test_test_database_size(self):
        """Test database has 188 persons"""
        assert format_number_with_separator(188, 'en') == '188'
        assert format_number_with_separator(188, 'fr') == '188'

    def test_small_genealogy_database(self):
        """Small genealogy database: 1,500 persons"""
        assert format_number_with_separator(1500, 'en') == '1,500'
        assert format_number_with_separator(1500, 'fr') == '1 500'

    def test_medium_genealogy_database(self):
        """Medium genealogy database: 10,000 persons"""
        assert format_number_with_separator(10000, 'en') == '10,000'
        assert format_number_with_separator(10000, 'fr') == '10 000'

    def test_large_genealogy_database(self):
        """Large genealogy database: 500,000 persons"""
        assert format_number_with_separator(500000, 'en') == '500,000'
        assert format_number_with_separator(500000, 'fr') == '500 000'


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_unsupported_locale_raises_error(self):
        """Unsupported locale should raise ValueError"""
        with pytest.raises(ValueError, match="Unsupported locale"):
            format_number_with_separator(1000, 'xx')

    def test_unsupported_locale_detailed_message(self):
        """Error message should list supported locales"""
        with pytest.raises(ValueError, match="Supported locales:"):
            format_number_with_separator(1000, 'invalid')

    def test_default_locale_is_english(self):
        """Default locale should be English"""
        assert format_number_with_separator(1000) == '1,000'

    def test_all_supported_locales_work(self):
        """All locales in LOCALE_SEPARATORS should work"""
        for locale in LOCALE_SEPARATORS.keys():
            result = format_number_with_separator(1000, locale)
            assert isinstance(result, str)
            assert '1' in result
            assert '000' in result


@pytest.mark.unit
class TestGetLocaleSeparator:
    """Test get_locale_separator helper function"""

    def test_get_english_separator(self):
        """English separator is comma"""
        assert get_locale_separator('en') == ','

    def test_get_french_separator(self):
        """French separator is space"""
        assert get_locale_separator('fr') == ' '

    def test_get_german_separator(self):
        """German separator is dot"""
        assert get_locale_separator('de') == '.'

    def test_get_russian_separator(self):
        """Russian separator is apostrophe"""
        assert get_locale_separator('ru') == "'"

    def test_get_separator_with_alias(self):
        """Should handle locale aliases"""
        assert get_locale_separator('en_US') == ','
        assert get_locale_separator('fr_FR') == ' '

    def test_get_separator_unsupported_locale(self):
        """Should raise ValueError for unsupported locale"""
        with pytest.raises(ValueError):
            get_locale_separator('invalid')


@pytest.mark.unit
class TestOCamlBehaviorConsistency:
    """Test consistency with OCaml Mutil.string_of_int_sep behavior"""

    def test_separator_every_three_digits(self):
        """Separator should appear every 3 digits from right"""
        # 4 digits: one separator
        assert format_number_with_separator(1234, 'en') == '1,234'

        # 5 digits: one separator
        assert format_number_with_separator(12345, 'en') == '12,345'

        # 6 digits: one separator
        assert format_number_with_separator(123456, 'en') == '123,456'

        # 7 digits: two separators
        assert format_number_with_separator(1234567, 'en') == '1,234,567'

    def test_no_separator_at_start(self):
        """Separator should never appear at the start"""
        result = format_number_with_separator(1000000, 'en')
        assert not result.startswith(',')
        assert not result.startswith(' ')
        assert not result.startswith('.')

    def test_no_separator_at_end(self):
        """Separator should never appear at the end"""
        result = format_number_with_separator(1000000, 'en')
        assert not result.endswith(',')
        assert not result.endswith(' ')
        assert not result.endswith('.')

    def test_consistent_separator_spacing(self):
        """All separators should be evenly spaced (every 3 digits)"""
        result = format_number_with_separator(1234567890, 'en')
        assert result == '1,234,567,890'

        # Count separators
        assert result.count(',') == 3

    def test_digits_preserved(self):
        """All digits should be preserved in output"""
        num = 123456789
        result = format_number_with_separator(num, 'en')
        # Remove separators and verify digits match
        digits_only = result.replace(',', '')
        assert digits_only == str(num)


@pytest.mark.unit
class TestRealWorldScenarios:
    """Test real-world usage scenarios from GeneWeb"""

    def test_statistics_page_counts(self):
        """Format counts for statistics page"""
        # Total persons
        assert format_number_with_separator(15234, 'en') == '15,234'
        assert format_number_with_separator(15234, 'fr') == '15 234'

        # Total families
        assert format_number_with_separator(4567, 'en') == '4,567'
        assert format_number_with_separator(4567, 'fr') == '4 567'

    def test_surname_list_counts(self):
        """Format surname counts in surname list"""
        assert format_number_with_separator(2345, 'en') == '2,345'
        assert format_number_with_separator(2345, 'fr') == '2 345'

    def test_search_results_count(self):
        """Format search results count"""
        assert format_number_with_separator(789, 'en') == '789'
        assert format_number_with_separator(1789, 'en') == '1,789'

    def test_multilingual_interface(self):
        """Same number should format differently per language"""
        num = 50000

        english = format_number_with_separator(num, 'en')
        french = format_number_with_separator(num, 'fr')
        german = format_number_with_separator(num, 'de')

        assert english == '50,000'
        assert french == '50 000'
        assert german == '50.000'

        # All should be different
        assert english != french
        assert french != german
        assert english != german
