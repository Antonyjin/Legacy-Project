"""
UT-PY-012: Test name processing utilities (Name.lower migration)

Tests the Python implementation of name_lower that replicates
the OCaml Name.lower behavior from GeneWeb.

This validates the migration of name normalization logic from OCaml to Python,
ensuring consistency with GeneWeb's name processing.

OCaml References:
- source_geneweb/lib/util/name.ml: Name.lower implementation (lines 36-51)
- source_geneweb/lib/util/name.mli: Function signature and documentation

Issue: MIG-001 - Migrate name_lower function
"""

import pytest
import sys
from pathlib import Path

# Add tests/python to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.name_utils import (
    name_lower,
    strip_lower,
    contains_only_ascii,
    is_normalized_name,
)


@pytest.mark.unit
class TestBasicNameLower:
    """Test basic name_lower functionality"""

    def test_simple_lowercase(self):
        """Simple uppercase to lowercase"""
        assert name_lower("MARTIN") == "martin"
        assert name_lower("SMITH") == "smith"
        assert name_lower("JONES") == "jones"

    def test_mixed_case(self):
        """Mixed case should all become lowercase"""
        assert name_lower("Martin") == "martin"
        assert name_lower("SmItH") == "smith"
        assert name_lower("JoNeS") == "jones"

    def test_already_lowercase(self):
        """Already lowercase names should remain unchanged"""
        assert name_lower("martin") == "martin"
        assert name_lower("smith") == "smith"

    def test_empty_string(self):
        """Empty string should return empty string"""
        assert name_lower("") == ""

    def test_single_char(self):
        """Single character names"""
        assert name_lower("A") == "a"
        assert name_lower("Z") == "z"
        assert name_lower("a") == "a"


@pytest.mark.unit
class TestAccentRemoval:
    """Test accent and diacritic removal via unidecode"""

    def test_french_accents(self):
        """French accented characters"""
        assert name_lower("René") == "rene"
        assert name_lower("François") == "francois"
        assert name_lower("Château") == "chateau"
        assert name_lower("Élise") == "elise"
        assert name_lower("Céline") == "celine"

    def test_german_umlauts(self):
        """German umlaut characters"""
        assert name_lower("Müller") == "muller"
        assert name_lower("Schröder") == "schroder"
        assert name_lower("Köhler") == "kohler"

    def test_spanish_accents(self):
        """Spanish accented characters"""
        assert name_lower("José") == "jose"
        assert name_lower("María") == "maria"
        assert name_lower("Ángel") == "angel"
        assert name_lower("Núñez") == "nunez"

    def test_scandinavian_chars(self):
        """Scandinavian special characters"""
        assert name_lower("Åström") == "astrom"
        assert name_lower("Øberg") == "oberg"
        assert name_lower("Ødegård") == "odegard"

    def test_multiple_accents(self):
        """Names with multiple accented characters"""
        assert name_lower("Françoise") == "francoise"
        assert name_lower("José María") == "jose maria"


@pytest.mark.unit
class TestNonLatinScripts:
    """Test non-Latin script transliteration"""

    def test_cyrillic(self):
        """Cyrillic (Russian) characters"""
        assert name_lower("Владимир") == "vladimir"
        assert name_lower("Иван") == "ivan"
        assert name_lower("Петров") == "petrov"

    def test_greek(self):
        """Greek characters"""
        assert name_lower("Αλέξανδρος") == "alexandros"
        assert name_lower("Νικόλαος") == "nikolaos"

    def test_arabic(self):
        """Arabic characters (transliterated)"""
        # Arabic names are transliterated to Latin
        result = name_lower("محمد")
        assert isinstance(result, str)
        assert result  # Should produce some transliteration

    def test_mixed_scripts(self):
        """Mixed Latin and non-Latin"""
        result = name_lower("Jean Владимир")
        assert "jean" in result
        assert "vladimir" in result


@pytest.mark.unit
class TestSpecialCharacters:
    """Test special character handling"""

    def test_hyphen_becomes_space(self):
        """Hyphens should become spaces"""
        assert name_lower("Jean-François") == "jean francois"
        assert name_lower("Anne-Marie") == "anne marie"
        assert name_lower("Smith-Jones") == "smith jones"

    def test_apostrophe_becomes_space(self):
        """Apostrophes should become spaces"""
        assert name_lower("O'Brien") == "o brien"
        assert name_lower("D'Angelo") == "d angelo"
        assert name_lower("O'Connor") == "o connor"

    def test_dot_is_preserved(self):
        """Dots should be preserved (for Jr., Sr., etc.)"""
        assert name_lower("Smith.Jr") == "smith.jr"
        assert name_lower("John.Sr") == "john.sr"
        assert name_lower("Dr.Martin") == "dr.martin"

    def test_numbers_preserved(self):
        """Numbers should be preserved"""
        assert name_lower("Louis16") == "louis16"
        assert name_lower("Henri4") == "henri4"
        assert name_lower("123") == "123"

    def test_underscores_become_spaces(self):
        """Underscores should become spaces"""
        assert name_lower("First_Last") == "first last"

    def test_multiple_special_chars(self):
        """Multiple special characters in sequence"""
        assert name_lower("Jean--François") == "jean francois"
        assert name_lower("O''Brien") == "o brien"


@pytest.mark.unit
class TestSpaceNormalization:
    """Test space handling and normalization"""

    def test_leading_spaces_removed(self):
        """Leading spaces should be removed"""
        assert name_lower("  Martin") == "martin"
        assert name_lower("   Smith") == "smith"

    def test_trailing_spaces_removed(self):
        """Trailing spaces should be removed"""
        assert name_lower("Martin  ") == "martin"
        assert name_lower("Smith   ") == "smith"

    def test_multiple_spaces_collapsed(self):
        """Multiple spaces should collapse to single space"""
        assert name_lower("Jean  François") == "jean francois"
        assert name_lower("De   La   Cruz") == "de la cruz"
        assert name_lower("Test    Multiple     Spaces") == "test multiple spaces"

    def test_space_before_and_after(self):
        """Spaces at both ends"""
        assert name_lower("  Jean François  ") == "jean francois"


@pytest.mark.unit
class TestComplexNames:
    """Test complex real-world names"""

    def test_spanish_compound_names(self):
        """Spanish compound surnames"""
        assert name_lower("DE LA CRUZ") == "de la cruz"
        assert name_lower("Del Río") == "del rio"
        assert name_lower("García López") == "garcia lopez"

    def test_french_particles(self):
        """French names with particles"""
        assert name_lower("De Gaulle") == "de gaulle"
        assert name_lower("Du Pont") == "du pont"
        assert name_lower("Le Blanc") == "le blanc"

    def test_dutch_van_names(self):
        """Dutch van/van der names"""
        assert name_lower("Van Gogh") == "van gogh"
        assert name_lower("Van der Berg") == "van der berg"

    def test_irish_names(self):
        """Irish O' and Mc names"""
        assert name_lower("O'Sullivan") == "o sullivan"
        assert name_lower("McDonald") == "mcdonald"
        assert name_lower("MacLeod") == "macleod"

    def test_scottish_names(self):
        """Scottish Mc/Mac names"""
        assert name_lower("McGregor") == "mcgregor"
        assert name_lower("MacKenzie") == "mackenzie"

    def test_long_compound_name(self):
        """Very long compound names"""
        name = "Jean-François-Marie De La Croix Du Château"
        result = name_lower(name)
        assert "jean" in result
        assert "francois" in result
        assert "marie" in result
        assert "de la croix" in result
        assert "du chateau" in result


@pytest.mark.unit
class TestStripLower:
    """Test strip_lower function (composition of lower + strip spaces)"""

    def test_basic_strip_lower(self):
        """Basic strip_lower removes all spaces"""
        assert strip_lower("Jean François") == "jeanfrancois"
        assert strip_lower("DE LA CRUZ") == "delacruz"

    def test_strip_lower_with_special_chars(self):
        """strip_lower with special characters"""
        assert strip_lower("Jean-François") == "jeanfrancois"
        assert strip_lower("O'Brien") == "obrien"

    def test_strip_lower_accents(self):
        """strip_lower removes accents and spaces"""
        assert strip_lower("José María") == "josemaria"
        assert strip_lower("Müller Schmidt") == "mullerschmidt"

    def test_strip_lower_preserves_dots(self):
        """strip_lower preserves dots"""
        assert strip_lower("Smith.Jr") == "smith.jr"


@pytest.mark.unit
class TestContainsOnlyAscii:
    """Test contains_only_ascii helper"""

    def test_pure_ascii(self):
        """Pure ASCII names"""
        assert contains_only_ascii("Smith") is True
        assert contains_only_ascii("O'Brien") is True
        assert contains_only_ascii("123") is True

    def test_with_accents(self):
        """Names with accents are not pure ASCII"""
        assert contains_only_ascii("René") is False
        assert contains_only_ascii("José") is False
        assert contains_only_ascii("Müller") is False

    def test_non_latin(self):
        """Non-Latin scripts are not ASCII"""
        assert contains_only_ascii("Владимир") is False
        assert contains_only_ascii("Αλέξανδρος") is False

    def test_empty(self):
        """Empty string is ASCII"""
        assert contains_only_ascii("") is True


@pytest.mark.unit
class TestIsNormalizedName:
    """Test is_normalized_name helper"""

    def test_normalized_names(self):
        """Already normalized names"""
        assert is_normalized_name("jean francois") is True
        assert is_normalized_name("smith") is True
        assert is_normalized_name("de la cruz") is True

    def test_uppercase_not_normalized(self):
        """Uppercase names are not normalized"""
        assert is_normalized_name("SMITH") is False
        assert is_normalized_name("Jean François") is False

    def test_accents_not_normalized(self):
        """Names with accents are not normalized"""
        assert is_normalized_name("rené") is False
        assert is_normalized_name("josé") is False

    def test_multiple_spaces_not_normalized(self):
        """Multiple spaces are not normalized"""
        assert is_normalized_name("jean  francois") is False

    def test_leading_trailing_spaces_not_normalized(self):
        """Leading/trailing spaces are not normalized"""
        assert is_normalized_name("  smith") is False
        assert is_normalized_name("smith  ") is False

    def test_dots_allowed(self):
        """Dots are allowed in normalized names"""
        assert is_normalized_name("smith.jr") is True

    def test_empty_is_normalized(self):
        """Empty string is considered normalized"""
        assert is_normalized_name("") is True


@pytest.mark.unit
class TestOCamlBehaviorConsistency:
    """Test consistency with OCaml Name.lower behavior"""

    def test_alphanumeric_and_dot_preserved(self):
        """Only alphanumeric and dots are preserved"""
        result = name_lower("Test123.Jr")
        assert result == "test123.jr"

    def test_special_chars_become_spaces(self):
        """Non-alphanumeric (except dot) become spaces"""
        result = name_lower("Test@#$Name")
        assert "test" in result
        assert "name" in result
        assert "@" not in result
        assert "#" not in result

    def test_no_double_spaces(self):
        """Multiple special chars don't create multiple spaces"""
        result = name_lower("Test###Name")
        assert "test  name" not in result  # No double spaces
        assert result == "test name"

    def test_utf8_transliteration(self):
        """UTF-8 characters are transliterated"""
        result = name_lower("Café")
        assert "cafe" == result
        assert "é" not in result


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_only_special_chars(self):
        """Only special characters should return empty"""
        assert name_lower("@#$%") == ""
        assert name_lower("---") == ""

    def test_only_spaces(self):
        """Only spaces should return empty"""
        assert name_lower("   ") == ""

    def test_very_long_name(self):
        """Very long names should work"""
        long_name = "A" * 1000
        result = name_lower(long_name)
        assert result == "a" * 1000

    def test_single_dot(self):
        """Single dot is preserved"""
        assert name_lower(".") == "."

    def test_numbers_only(self):
        """Numbers only"""
        assert name_lower("12345") == "12345"

    def test_mixed_everything(self):
        """Mixed letters, numbers, special chars, UTF-8"""
        result = name_lower("Jean123-François456@Test")
        assert "jean123" in result
        assert "francois456" in result
        assert "test" in result


@pytest.mark.unit
class TestRealWorldGeneWebNames:
    """Test with real-world GeneWeb database names"""

    def test_british_royal_family(self):
        """Names from GeneWeb test database (British royals)"""
        assert name_lower("Windsor") == "windsor"
        assert name_lower("Mountbatten-Windsor") == "mountbatten windsor"
        assert name_lower("Charles") == "charles"
        assert name_lower("Elizabeth") == "elizabeth"

    def test_french_names(self):
        """Common French names"""
        assert name_lower("Dupont") == "dupont"
        assert name_lower("Lefèvre") == "lefevre"
        assert name_lower("François") == "francois"

    def test_german_names(self):
        """Common German names"""
        assert name_lower("Müller") == "muller"
        assert name_lower("Schröder") == "schroder"
        assert name_lower("Weiß") == "weiss"

    def test_genealogy_suffixes(self):
        """Genealogical suffixes with dots"""
        assert name_lower("John.Jr") == "john.jr"
        assert name_lower("Robert.Sr") == "robert.sr"
        assert name_lower("William.III") == "william.iii"
