# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
#!/usr/bin/env python3
"""
Unit tests for string utility functions (MIG-007)

Test File: UT-PY-014
Issue: MIG-007 - Migrate string utility functions
OCaml Reference: source_geneweb/lib/util/name.ml

Functions tested:
    - strip_c: Remove all occurrences of a character
    - purge: Remove all forbidden characters
    - contains_forbidden_char: Check for forbidden characters

Purpose:
    Validate the Python implementation of OCaml string utility functions,
    ensuring behavioral equivalence with the original OCaml code.

Coverage:
    - Basic character removal (strip_c)
    - Forbidden character removal (purge)
    - Forbidden character detection (contains_forbidden_char)
    - Edge cases (empty strings, no matches, all matches)
    - OCaml behavior consistency
"""

import sys
from pathlib import Path

# Add tests directory to path for imports
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(test_dir))

import pytest

# Import directly from string_utils to avoid circular dependencies
from utils.string_utils import FORBIDDEN_CHAR, contains_forbidden_char, purge, strip_c


class TestStripC:
    """Test strip_c function - remove all occurrences of a character."""

    def test_remove_single_character(self):
        """Remove single occurrence of character."""
        assert strip_c("hello", "l") == "heo"

    def test_remove_multiple_occurrences(self):
        """Remove multiple occurrences of character."""
        assert strip_c("hello world", "l") == "heo word"
        assert strip_c("aaaa", "a") == ""

    def test_remove_space(self):
        """Remove space characters."""
        assert strip_c("hello world", " ") == "helloworld"
        assert strip_c("  spaced  ", " ") == "spaced"

    def test_remove_special_characters(self):
        """Remove special characters."""
        assert strip_c("test@example.com", "@") == "testexample.com"
        assert strip_c("a-b-c", "-") == "abc"
        assert strip_c("file.name.txt", ".") == "filenametxt"

    def test_no_match(self):
        """String without the character remains unchanged."""
        assert strip_c("hello world", "x") == "hello world"
        assert strip_c("test", "z") == "test"

    def test_empty_string(self):
        """Empty string returns empty string."""
        assert strip_c("", "a") == ""
        assert strip_c("", " ") == ""

    def test_all_characters_match(self):
        """All characters match."""
        assert strip_c("aaaa", "a") == ""
        assert strip_c("   ", " ") == ""

    def test_unicode_characters(self):
        """Unicode characters are preserved when not removed."""
        assert strip_c("café", "é") == "caf"
        assert strip_c("café", "a") == "cfé"
        assert strip_c("你好", "你") == "好"

    def test_only_one_character(self):
        """String with only one character."""
        assert strip_c("a", "a") == ""
        assert strip_c("a", "b") == "a"

    def test_invalid_argument(self):
        """Multiple characters should raise ValueError."""
        with pytest.raises(ValueError, match="single character"):
            strip_c("hello", "ab")

        with pytest.raises(ValueError, match="single character"):
            strip_c("hello", "")


class TestPurge:
    """Test purge function - remove all forbidden characters."""

    def test_remove_single_forbidden_char(self):
        """Remove single forbidden character."""
        assert purge("user@example") == "userexample"
        assert purge("price=100") == "price100"
        assert purge("file#1") == "file1"
        assert purge("name:test") == "nametest"
        assert purge("cost$50") == "cost50"

    def test_remove_multiple_forbidden_chars(self):
        """Remove multiple forbidden characters."""
        assert purge("user@example.com:port#8080") == "userexample.comport8080"
        assert purge("price=$100") == "price100"
        assert purge("file#1:name=test") == "file1nametest"

    def test_no_forbidden_chars(self):
        """String without forbidden characters remains unchanged."""
        assert purge("normal text") == "normal text"
        assert purge("hello world") == "hello world"
        assert purge("test123") == "test123"

    def test_empty_string(self):
        """Empty string returns empty string."""
        assert purge("") == ""

    def test_only_forbidden_chars(self):
        """String with only forbidden characters."""
        assert purge("@#$=") == ""
        assert purge(":") == ""

    def test_mixed_forbidden_and_normal(self):
        """Mixed forbidden and normal characters."""
        assert purge("user@domain.com") == "userdomain.com"
        assert purge("price = $100") == "price  100"
        assert purge("file#1: name") == "file1 name"

    def test_all_forbidden_chars(self):
        """Test all forbidden characters."""
        for char in FORBIDDEN_CHAR:
            assert purge(f"test{char}value") == "testvalue"

    def test_unicode_preserved(self):
        """Unicode characters are preserved."""
        assert purge("café@example") == "caféexample"
        assert purge("价格=$100") == "价格100"


class TestContainsForbiddenChar:
    """Test contains_forbidden_char function - check for forbidden characters."""

    def test_contains_single_forbidden_char(self):
        """String contains one forbidden character."""
        assert contains_forbidden_char("user@example") is True
        assert contains_forbidden_char("price=100") is True
        assert contains_forbidden_char("file#1") is True
        assert contains_forbidden_char("name:test") is True
        assert contains_forbidden_char("cost$50") is True

    def test_contains_multiple_forbidden_chars(self):
        """String contains multiple forbidden characters."""
        assert contains_forbidden_char("user@example:port") is True
        assert contains_forbidden_char("price=$100") is True
        assert contains_forbidden_char("file#1:name=test") is True

    def test_no_forbidden_chars(self):
        """String without forbidden characters returns False."""
        assert contains_forbidden_char("normal text") is False
        assert contains_forbidden_char("hello world") is False
        assert contains_forbidden_char("test123") is False
        assert contains_forbidden_char("café") is False

    def test_empty_string(self):
        """Empty string returns False."""
        assert contains_forbidden_char("") is False

    def test_only_forbidden_chars(self):
        """String with only forbidden characters returns True."""
        assert contains_forbidden_char("@") is True
        assert contains_forbidden_char("@#$=") is True
        assert contains_forbidden_char(":") is True

    def test_forbidden_char_at_start(self):
        """Forbidden character at start of string."""
        assert contains_forbidden_char("@user") is True
        assert contains_forbidden_char(":name") is True
        assert contains_forbidden_char("#file") is True

    def test_forbidden_char_at_end(self):
        """Forbidden character at end of string."""
        assert contains_forbidden_char("user@") is True
        assert contains_forbidden_char("name:") is True
        assert contains_forbidden_char("price$") is True

    def test_forbidden_char_in_middle(self):
        """Forbidden character in middle of string."""
        assert contains_forbidden_char("user@example") is True
        assert contains_forbidden_char("price=100") is True
        assert contains_forbidden_char("file#1") is True

    def test_all_forbidden_chars(self):
        """Test all forbidden characters individually."""
        for char in FORBIDDEN_CHAR:
            assert contains_forbidden_char(f"test{char}value") is True


class TestOCamlCompatibility:
    """Test that Python implementation matches OCaml behavior."""

    def test_strip_c_matches_ocaml(self):
        """strip_c behavior matches OCaml implementation."""
        # OCaml: strip_c "hello world" 'l' = "heo word"
        assert strip_c("hello world", "l") == "heo word"

        # OCaml: strip_c "test" 'x' = "test"
        assert strip_c("test", "x") == "test"

    def test_purge_matches_ocaml(self):
        """purge behavior matches OCaml implementation."""
        # OCaml: purge removes all chars from forbidden_char list
        # forbidden_char = [':', '@', '#', '=', '$']
        assert purge("user@example") == "userexample"
        assert purge("file:name#test") == "filenametest"
        assert purge("price=$100") == "price100"

    def test_contains_forbidden_char_matches_ocaml(self):
        """contains_forbidden_char behavior matches OCaml implementation."""
        # OCaml: List.exists (String.contains s) forbidden_char
        assert contains_forbidden_char("user@example") is True
        assert contains_forbidden_char("normal text") is False
        assert contains_forbidden_char("") is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_strip_c_very_long_string(self):
        """strip_c with very long string."""
        long_string = "a" * 1000 + "b" * 1000
        assert strip_c(long_string, "a") == "b" * 1000
        assert strip_c(long_string, "b") == "a" * 1000

    def test_purge_very_long_string(self):
        """purge with very long string."""
        long_string = "test@" * 1000 + "end"
        result = purge(long_string)
        assert "@" not in result
        assert result.endswith("end")

    def test_contains_forbidden_char_very_long_string(self):
        """contains_forbidden_char with very long string."""
        long_string = "a" * 10000 + "@" + "b" * 10000
        assert contains_forbidden_char(long_string) is True

        long_string_no_forbidden = "a" * 20000
        assert contains_forbidden_char(long_string_no_forbidden) is False

    def test_strip_c_unicode_boundary(self):
        """strip_c with Unicode boundary cases."""
        # Remove emoji
        assert strip_c("hello😀world", "😀") == "helloworld"

        # Remove combining characters
        assert strip_c("café", "é") == "caf"

    def test_purge_preserves_valid_special_chars(self):
        """purge only removes forbidden chars, preserves others."""
        # Valid special characters that should be preserved
        assert purge("file-name.txt") == "file-name.txt"
        assert purge("test(123)") == "test(123)"
        assert purge("user+tag") == "user+tag"

    def test_strip_c_newline_and_tabs(self):
        """strip_c can remove newlines and tabs."""
        assert strip_c("line1\nline2", "\n") == "line1line2"
        assert strip_c("tab\there", "\t") == "tabhere"
