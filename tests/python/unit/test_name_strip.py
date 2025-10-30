# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
#!/usr/bin/env python3
"""
Unit tests for name_strip function (MIG-002)

Test File: UT-PY-013
Issue: MIG-002 - Migrate name_strip function
OCaml Reference: source_geneweb/lib/util/name.ml:138

Purpose:
    Validate the Python implementation of OCaml Name.strip function,
    which removes all space characters from a string.

Coverage:
    - Basic space removal
    - Names with various types of spaces
    - Edge cases (empty, no spaces, only spaces)
    - Unicode preservation
    - OCaml behavior consistency

Author: Python Migration Team
Date: 2025-10-29
"""

import sys
from pathlib import Path

# Add tests directory to path for imports
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(test_dir))

import pytest  # noqa: E402
from utils.name_utils import name_strip  # noqa: E402


class TestBasicNameStrip:
    """Test basic space removal functionality."""

    def test_simple_space(self):
        """Single space between words."""
        assert name_strip("Jean François") == "JeanFrançois"

    def test_multiple_spaces(self):
        """Multiple spaces between words."""
        assert name_strip("Jean  François") == "JeanFrançois"
        assert name_strip("A  B  C") == "ABC"

    def test_leading_space(self):
        """Leading space is removed."""
        assert name_strip(" Jean") == "Jean"
        assert name_strip("  Multiple") == "Multiple"

    def test_trailing_space(self):
        """Trailing space is removed."""
        assert name_strip("Jean ") == "Jean"
        assert name_strip("Multiple  ") == "Multiple"

    def test_leading_and_trailing(self):
        """Both leading and trailing spaces."""
        assert name_strip("  Jean François  ") == "JeanFrançois"
        assert name_strip("   Spaced   ") == "Spaced"


class TestCommonNames:
    """Test with common real-world names."""

    def test_french_names(self):
        """French names with spaces."""
        assert name_strip("Jean François") == "JeanFrançois"
        assert name_strip("Marie Claire") == "MarieClaire"
        assert name_strip("Pierre Paul") == "PierrePaul"

    def test_compound_surnames(self):
        """Surnames with multiple parts."""
        assert name_strip("DE LA CRUZ") == "DELACRUZ"
        assert name_strip("Van Der Berg") == "VanDerBerg"
        assert name_strip("Von Neumann") == "VonNeumann"
        assert name_strip("Da Silva") == "DaSilva"

    def test_irish_scottish_names(self):
        """Irish and Scottish names with apostrophes."""
        assert name_strip("O'Brien Smith") == "O'BrienSmith"
        assert name_strip("Mc Donald") == "McDonald"
        assert name_strip("Mac Arthur") == "MacArthur"

    def test_hyphenated_names(self):
        """Names with hyphens and spaces."""
        assert name_strip("Jean-Paul Martin") == "Jean-PaulMartin"
        assert name_strip("Anne-Marie Dubois") == "Anne-MarieDubois"


class TestUnicodeCharacters:
    """Test that Unicode characters are preserved."""

    def test_accented_names(self):
        """Names with accents keep their accents."""
        assert name_strip("José María") == "JoséMaría"
        assert name_strip("François René") == "FrançoisRené"
        assert name_strip("Müller Schmidt") == "MüllerSchmidt"

    def test_cyrillic_names(self):
        """Cyrillic script names."""
        assert name_strip("Владимир Путин") == "ВладимирПутин"
        assert name_strip("Иван Иванов") == "ИванИванов"

    def test_greek_names(self):
        """Greek script names."""
        assert name_strip("Γεώργιος Παπαδόπουλος") == "ΓεώργιοςΠαπαδόπουλος"

    def test_arabic_names(self):
        """Arabic script names."""
        assert name_strip("محمد علي") == "محمدعلي"

    def test_chinese_names(self):
        """Chinese characters (no spaces typically, but test anyway)."""
        assert name_strip("李 明") == "李明"
        assert name_strip("王 小 明") == "王小明"


class TestSpecialCharacters:
    """Test names with special characters and punctuation."""

    def test_dots(self):
        """Names with dots (periods)."""
        assert name_strip("John F. Kennedy") == "JohnF.Kennedy"
        assert name_strip("A. B. Smith") == "A.B.Smith"
        assert name_strip("Martin Luther King Jr.") == "MartinLutherKingJr."

    def test_commas(self):
        """Names with commas."""
        assert name_strip("Smith, John") == "Smith,John"
        assert name_strip("Doe, Jane Mary") == "Doe,JaneMary"

    def test_apostrophes(self):
        """Names with apostrophes (already tested but explicit)."""
        assert name_strip("O'Neil Patrick") == "O'NeilPatrick"
        assert name_strip("D'Angelo Maria") == "D'AngeloMaria"

    def test_numbers(self):
        """Names with numbers."""
        assert name_strip("Louis XIV") == "LouisXIV"
        assert name_strip("Elizabeth II") == "ElizabethII"
        assert name_strip("John Smith III") == "JohnSmithIII"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Empty string returns empty."""
        assert name_strip("") == ""

    def test_no_spaces(self):
        """String without spaces unchanged."""
        assert name_strip("NoSpaces") == "NoSpaces"
        assert name_strip("SingleWord") == "SingleWord"

    def test_only_spaces(self):
        """String with only spaces returns empty."""
        assert name_strip(" ") == ""
        assert name_strip("   ") == ""
        assert name_strip("     ") == ""

    def test_single_character(self):
        """Single character strings."""
        assert name_strip("A") == "A"
        assert name_strip(" A") == "A"
        assert name_strip("A ") == "A"
        assert name_strip(" A ") == "A"

    def test_very_long_name(self):
        """Very long name with multiple spaces."""
        long_name = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
        expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        assert name_strip(long_name) == expected


class TestWhitespaceTypes:
    """Test that only space character is removed, not other whitespace."""

    def test_tabs_preserved(self):
        """Tabs are not removed (only spaces)."""
        assert name_strip("Jean\tFrançois") == "Jean\tFrançois"

    def test_newlines_preserved(self):
        """Newlines are not removed (only spaces)."""
        assert name_strip("Jean\nFrançois") == "Jean\nFrançois"

    def test_mixed_whitespace(self):
        """Mix of spaces and other whitespace."""
        # Only spaces removed
        assert name_strip("Jean \t François") == "Jean\tFrançois"
        assert name_strip("Name \n Surname") == "Name\nSurname"


class TestCasePreservation:
    """Test that case is preserved (unlike name_lower)."""

    def test_uppercase(self):
        """Uppercase preserved."""
        assert name_strip("JOHN SMITH") == "JOHNSMITH"
        assert name_strip("MARIE CURIE") == "MARIECURIE"

    def test_lowercase(self):
        """Lowercase preserved."""
        assert name_strip("john smith") == "johnsmith"
        assert name_strip("marie curie") == "mariecurie"

    def test_mixed_case(self):
        """Mixed case preserved."""
        assert name_strip("JoHn SmItH") == "JoHnSmItH"
        assert name_strip("MaRiE CuRiE") == "MaRiECuRiE"


class TestOCamlBehaviorConsistency:
    """Test that Python implementation matches OCaml behavior exactly."""

    def test_ocaml_example_basic(self):
        """Basic example from OCaml implementation."""
        # OCaml: strip "hello world" = "helloworld"
        assert name_strip("hello world") == "helloworld"

    def test_ocaml_example_multiple(self):
        """Multiple spaces example."""
        # OCaml: strip "hello   world" = "helloworld"
        assert name_strip("hello   world") == "helloworld"

    def test_ocaml_example_edges(self):
        """Edge spaces example."""
        # OCaml: strip " hello world " = "helloworld"
        assert name_strip(" hello world ") == "helloworld"

    def test_ocaml_strip_c_behavior(self):
        """
        OCaml implementation: strip s = strip_c s ' '
        strip_c removes all occurrences of a specific character.
        """
        # Only space character should be removed
        test_cases = [
            ("a b c", "abc"),
            (" abc ", "abc"),
            ("  a  b  c  ", "abc"),
            ("", ""),
            ("no-spaces", "no-spaces"),
        ]
        for input_str, expected in test_cases:
            assert name_strip(input_str) == expected


class TestCompositionWithOtherFunctions:
    """Test name_strip in composition with other name utilities."""

    def test_strip_then_lower(self):
        """Apply strip then lower (reverse of strip_lower)."""
        from utils.name_utils import name_lower

        name = "Jean François"
        stripped = name_strip(name)  # "JeanFrançois"
        result = name_lower(stripped)  # "jeanfrancois"
        assert result == "jeanfrancois"

    def test_with_compound_operations(self):
        """Multiple operations in sequence."""
        from utils.name_utils import name_lower, strip_lower

        # Different orderings
        name = "Jean François MARTIN"

        # strip(lower(name))
        result1 = name_strip(name_lower(name))

        # strip_lower(name) - built-in composition
        result2 = strip_lower(name)

        assert result1 == result2 == "jeanfrancoismartin"


class TestRealWorldExamples:
    """Test with real-world genealogy data examples."""

    def test_genealogy_names(self):
        """Common genealogy name patterns."""
        assert name_strip("John Smith Jr.") == "JohnSmithJr."
        assert name_strip("Mary Anne Wilson") == "MaryAnneWilson"
        assert name_strip("Robert De Niro") == "RobertDeNiro"

    def test_nobility_titles(self):
        """Names with nobility indicators."""
        assert name_strip("Sir John Smith") == "SirJohnSmith"
        assert name_strip("Lady Mary Anne") == "LadyMaryAnne"
        assert name_strip("Baron von Schmidt") == "BaronvonSchmidt"

    def test_professional_suffixes(self):
        """Names with professional suffixes."""
        assert name_strip("Dr. Martin King") == "Dr.MartinKing"
        assert name_strip("Prof. Marie Curie") == "Prof.MarieCurie"


# Performance and stress tests
class TestPerformance:
    """Test performance with large inputs."""

    def test_very_long_string(self):
        """Test with very long string."""
        # 1000 words separated by spaces
        long_name = " ".join([f"Word{i}" for i in range(1000)])
        result = name_strip(long_name)

        # Should have no spaces
        assert ' ' not in result
        # Should contain all words
        assert result.startswith("Word0")
        assert result.endswith("Word999")

    def test_many_consecutive_spaces(self):
        """Test with many consecutive spaces."""
        name = "Word" + (" " * 1000) + "Another"
        result = name_strip(name)
        assert result == "WordAnother"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
