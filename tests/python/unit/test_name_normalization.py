"""
Unit Tests for Name Normalization (Python Implementation)

These tests will validate the Python implementation of name processing functions
to ensure they behave identically to the OCaml versions.

Issue: UT-PY-003
Related OCaml: lib/util/name.ml
"""

import pytest


# ============================================================================
# FUNCTIONS TO IMPLEMENT (Python versions of OCaml Name module)
# ============================================================================

def name_lower(name: str) -> str:
    """
    Convert name to lowercase with normalization.
    
    OCaml equivalent: Name.lower
    
    Rules:
    - Convert to lowercase
    - Replace non-alphanumeric (except '.') with spaces
    - Use unidecode for accents
    """
    # TODO: Implement this function
    # For now, simple placeholder
    return name.lower().replace('-', ' ')


def name_strip(name: str) -> str:
    """
    Remove all spaces from name.
    
    OCaml equivalent: Name.strip
    """
    return name.replace(' ', '')


def name_strip_lower(name: str) -> str:
    """
    Strip spaces then lowercase.
    
    OCaml equivalent: Name.strip_lower
    """
    return name_strip(name_lower(name))


def name_concat(first_name: str, surname: str) -> str:
    """
    Concatenate first name and surname with a space.
    
    OCaml equivalent: Name.concat
    """
    return f"{first_name} {surname}"


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestNameLower:
    """Test name_lower function"""
    
    def test_simple_name(self):
        assert name_lower("John") == "john"
    
    def test_hyphenated_name(self):
        # OCaml converts hyphens to spaces
        assert name_lower("Jean-Paul") == "jean paul"
    
    def test_apostrophe(self):
        assert name_lower("O'Brien") == "o'brien"
    
    def test_all_caps(self):
        assert name_lower("SMITH") == "smith"
    
    def test_empty_string(self):
        assert name_lower("") == ""


class TestNameStrip:
    """Test name_strip function"""
    
    def test_two_words(self):
        assert name_strip("John Doe") == "JohnDoe"
    
    def test_three_words(self):
        assert name_strip("Jean Paul Sartre") == "JeanPaulSartre"
    
    def test_no_spaces(self):
        assert name_strip("NoSpaces") == "NoSpaces"
    
    def test_multiple_spaces(self):
        assert name_strip("Multiple    Spaces") == "MultipleSpaces"
    
    def test_empty_string(self):
        assert name_strip("") == ""


class TestNameStripLower:
    """Test name_strip_lower function"""
    
    def test_two_words(self):
        assert name_strip_lower("John Doe") == "johndoe"
    
    def test_hyphenated(self):
        # Hyphens converted to spaces, then stripped
        assert name_strip_lower("Jean-Paul") == "jeanpaul"
    
    def test_all_caps(self):
        assert name_strip_lower("SMITH") == "smith"
    
    def test_with_particle(self):
        assert name_strip_lower("Von Neumann") == "vonneumann"


class TestNameConcat:
    """Test name_concat function"""
    
    def test_simple_names(self):
        assert name_concat("John", "Smith") == "John Smith"
    
    def test_hyphenated_first_name(self):
        assert name_concat("Jean-Paul", "Sartre") == "Jean-Paul Sartre"
    
    def test_empty_names(self):
        assert name_concat("", "") == " "
    
    def test_empty_surname(self):
        assert name_concat("John", "") == "John "


# ============================================================================
# PARAMETRIZED TESTS (Test multiple inputs at once)
# ============================================================================

@pytest.mark.parametrize("input_name,expected", [
    ("john", "john"),
    ("JOHN", "john"),
    ("John", "john"),
    ("Jean-Paul", "jean paul"),
    ("O'Brien", "o'brien"),
    ("", ""),
])
def test_name_lower_parametrized(input_name, expected):
    """Test name_lower with multiple inputs"""
    assert name_lower(input_name) == expected


@pytest.mark.parametrize("input_name,expected", [
    ("John Doe", "JohnDoe"),
    ("No Spaces", "NoSpaces"),
    ("   ", ""),
    ("A B C", "ABC"),
])
def test_name_strip_parametrized(input_name, expected):
    """Test name_strip with multiple inputs"""
    assert name_strip(input_name) == expected


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and special characters"""
    
    def test_unicode_characters(self):
        # TODO: Implement proper unicode handling
        # assert name_lower("José") == "jose"
        pass
    
    def test_numbers_in_name(self):
        assert name_lower("Henry VIII") == "henry viii"
    
    def test_very_long_name(self):
        long_name = "A" * 1000
        assert len(name_strip(long_name)) == 1000


# ============================================================================
# COMPARISON WITH OCAML (Golden Master)
# ============================================================================

class TestOCamlEquivalence:
    """
    These tests will compare Python output with OCaml output.
    
    To run these tests:
    1. Generate OCaml outputs: dune exec test_ocaml_names.exe
    2. Run Python tests: pytest test_name_normalization.py
    3. Compare outputs
    """
    
    @pytest.mark.skip(reason="Requires OCaml baseline")
    def test_golden_master_name_lower(self):
        """Compare Python output with OCaml output"""
        # TODO: Load OCaml golden output
        # TODO: Compare with Python output
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

