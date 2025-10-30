# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
#!/usr/bin/env python3
"""
Unit tests for Roman numeral conversion (MIG-003)

Test File: UT-PY-014
Issue: MIG-003 - Migrate roman_of_arabian function
OCaml Reference: source_geneweb/lib/util/mutil.ml:328-365

Purpose:
    Validate the Python implementation of OCaml Mutil.roman_of_arabian and
    Mutil.arabian_of_roman functions for Roman numeral conversion.

Coverage:
    - Basic conversions (1-10)
    - Subtractive notation (4, 9, 40, 90, etc.)
    - OCaml test cases from util_test.ml
    - Boundary conditions (1, 3999)
    - Special years (genealogy use cases)
    - Round-trip conversion (arabian → roman → arabian)

Author: Python Migration Team
Date: 2025-10-29
"""

import sys
from pathlib import Path

# Add tests directory to path for imports
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(test_dir))

import pytest
from utils.roman_numerals import arabian_of_roman, roman_of_arabian


class TestBasicRomanConversion:
    """Test basic Roman numeral conversions (1-10)."""

    def test_one(self):
        """1 = I"""
        assert roman_of_arabian(1) == "I"

    def test_two(self):
        """2 = II"""
        assert roman_of_arabian(2) == "II"

    def test_three(self):
        """3 = III"""
        assert roman_of_arabian(3) == "III"

    def test_four(self):
        """4 = IV (subtractive)"""
        assert roman_of_arabian(4) == "IV"

    def test_five(self):
        """5 = V"""
        assert roman_of_arabian(5) == "V"

    def test_six(self):
        """6 = VI"""
        assert roman_of_arabian(6) == "VI"

    def test_seven(self):
        """7 = VII"""
        assert roman_of_arabian(7) == "VII"

    def test_eight(self):
        """8 = VIII"""
        assert roman_of_arabian(8) == "VIII"

    def test_nine(self):
        """9 = IX (subtractive)"""
        assert roman_of_arabian(9) == "IX"

    def test_ten(self):
        """10 = X"""
        assert roman_of_arabian(10) == "X"


class TestSubtractiveNotation:
    """Test subtractive notation cases."""

    def test_four(self):
        """IV = 4"""
        assert roman_of_arabian(4) == "IV"

    def test_nine(self):
        """IX = 9"""
        assert roman_of_arabian(9) == "IX"

    def test_forty(self):
        """XL = 40"""
        assert roman_of_arabian(40) == "XL"

    def test_ninety(self):
        """XC = 90"""
        assert roman_of_arabian(90) == "XC"

    def test_four_hundred(self):
        """CD = 400"""
        assert roman_of_arabian(400) == "CD"

    def test_nine_hundred(self):
        """CM = 900"""
        assert roman_of_arabian(900) == "CM"

    def test_fourteen(self):
        """XIV = 14"""
        assert roman_of_arabian(14) == "XIV"

    def test_nineteen(self):
        """XIX = 19"""
        assert roman_of_arabian(19) == "XIX"

    def test_forty_four(self):
        """XLIV = 44"""
        assert roman_of_arabian(44) == "XLIV"

    def test_ninety_nine(self):
        """XCIX = 99"""
        assert roman_of_arabian(99) == "XCIX"


class TestOCamlTestCases:
    """Test cases from OCaml util_test.ml."""

    def test_39(self):
        """39 = XXXIX (from OCaml tests)"""
        assert roman_of_arabian(39) == "XXXIX"

    def test_246(self):
        """246 = CCXLVI (from OCaml tests)"""
        assert roman_of_arabian(246) == "CCXLVI"

    def test_421(self):
        """421 = CDXXI (from OCaml tests)"""
        assert roman_of_arabian(421) == "CDXXI"

    def test_160(self):
        """160 = CLX (from OCaml tests)"""
        assert roman_of_arabian(160) == "CLX"


class TestSignificantYears:
    """Test years commonly used in genealogy."""

    def test_1000(self):
        """Year 1000 = M"""
        assert roman_of_arabian(1000) == "M"

    def test_1492(self):
        """Year 1492 = MCDXCII"""
        assert roman_of_arabian(1492) == "MCDXCII"

    def test_1789(self):
        """Year 1789 = MDCCLXXXIX"""
        assert roman_of_arabian(1789) == "MDCCLXXXIX"

    def test_1914(self):
        """Year 1914 = MCMXIV"""
        assert roman_of_arabian(1914) == "MCMXIV"

    def test_1944(self):
        """Year 1944 = MCMXLIV"""
        assert roman_of_arabian(1944) == "MCMXLIV"

    def test_1994(self):
        """Year 1994 = MCMXCIV"""
        assert roman_of_arabian(1994) == "MCMXCIV"

    def test_2000(self):
        """Year 2000 = MM"""
        assert roman_of_arabian(2000) == "MM"

    def test_2024(self):
        """Year 2024 = MMXXIV"""
        assert roman_of_arabian(2024) == "MMXXIV"


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_zero(self):
        """0 returns empty string"""
        assert roman_of_arabian(0) == ""

    def test_one_minimum(self):
        """1 is minimum valid Roman numeral"""
        assert roman_of_arabian(1) == "I"

    def test_3999_maximum(self):
        """3999 is maximum standard Roman numeral"""
        assert roman_of_arabian(3999) == "MMMCMXCIX"

    def test_100(self):
        """100 = C"""
        assert roman_of_arabian(100) == "C"

    def test_500(self):
        """500 = D"""
        assert roman_of_arabian(500) == "D"

    def test_1000(self):
        """1000 = M"""
        assert roman_of_arabian(1000) == "M"

    def test_3000(self):
        """3000 = MMM"""
        assert roman_of_arabian(3000) == "MMM"


class TestRoundNumbers:
    """Test round numbers (tens, hundreds)."""

    def test_multiples_of_ten(self):
        """Test 10, 20, 30, ..., 100"""
        test_cases = [
            (10, "X"),
            (20, "XX"),
            (30, "XXX"),
            (40, "XL"),
            (50, "L"),
            (60, "LX"),
            (70, "LXX"),
            (80, "LXXX"),
            (90, "XC"),
            (100, "C"),
        ]
        for num, expected in test_cases:
            assert roman_of_arabian(num) == expected

    def test_multiples_of_hundred(self):
        """Test 100, 200, 300, ..., 1000"""
        test_cases = [
            (100, "C"),
            (200, "CC"),
            (300, "CCC"),
            (400, "CD"),
            (500, "D"),
            (600, "DC"),
            (700, "DCC"),
            (800, "DCCC"),
            (900, "CM"),
            (1000, "M"),
        ]
        for num, expected in test_cases:
            assert roman_of_arabian(num) == expected


class TestComplexNumbers:
    """Test complex multi-digit numbers."""

    def test_444(self):
        """444 = CDXLIV (all subtractive)"""
        assert roman_of_arabian(444) == "CDXLIV"

    def test_888(self):
        """888 = DCCCXXXIII (all additive)"""
        assert roman_of_arabian(888) == "DCCCLXXXVIII"

    def test_999(self):
        """999 = CMXCIX (maximum subtractive)"""
        assert roman_of_arabian(999) == "CMXCIX"

    def test_1234(self):
        """1234 = MCCXXXIV"""
        assert roman_of_arabian(1234) == "MCCXXXIV"

    def test_2468(self):
        """2468 = MMCDLXVIII"""
        assert roman_of_arabian(2468) == "MMCDLXVIII"

    def test_3579(self):
        """3579 = MMMDLXXIX"""
        assert roman_of_arabian(3579) == "MMMDLXXIX"


class TestRomanToArabian:
    """Test conversion from Roman to Arabian."""

    def test_basic_conversions(self):
        """Test basic Roman to Arabian conversions."""
        test_cases = [
            ("I", 1),
            ("II", 2),
            ("III", 3),
            ("IV", 4),
            ("V", 5),
            ("VI", 6),
            ("VII", 7),
            ("VIII", 8),
            ("IX", 9),
            ("X", 10),
        ]
        for roman, expected in test_cases:
            assert arabian_of_roman(roman) == expected

    def test_ocaml_test_cases(self):
        """Test cases from OCaml util_test.ml."""
        test_cases = [
            ("XXXIX", 39),
            ("CCXLVI", 246),
            ("CDXXI", 421),
            ("CLX", 160),
        ]
        for roman, expected in test_cases:
            assert arabian_of_roman(roman) == expected

    def test_complex_numbers(self):
        """Test complex Roman numerals."""
        test_cases = [
            ("MCMXCIV", 1994),
            ("MMMCMXCIX", 3999),
            ("CDXLIV", 444),
            ("CMXCIX", 999),
        ]
        for roman, expected in test_cases:
            assert arabian_of_roman(roman) == expected

    def test_invalid_roman(self):
        """Test invalid Roman numerals raise ValueError."""
        with pytest.raises(ValueError):
            arabian_of_roman("")

        with pytest.raises(ValueError):
            arabian_of_roman("ABC")


class TestRoundTrip:
    """Test round-trip conversion (arabian → roman → arabian)."""

    def test_round_trip_1_to_100(self):
        """Test round-trip for 1-100."""
        for n in range(1, 101):
            roman = roman_of_arabian(n)
            back = arabian_of_roman(roman)
            assert back == n, f"Round-trip failed for {n}: {roman} -> {back}"

    def test_round_trip_100_to_1000(self):
        """Test round-trip for 100-1000 (every 10)."""
        for n in range(100, 1001, 10):
            roman = roman_of_arabian(n)
            back = arabian_of_roman(roman)
            assert back == n, f"Round-trip failed for {n}: {roman} -> {back}"

    def test_round_trip_1000_to_3999(self):
        """Test round-trip for 1000-3999 (every 100)."""
        for n in range(1000, 4000, 100):
            roman = roman_of_arabian(n)
            back = arabian_of_roman(roman)
            assert back == n, f"Round-trip failed for {n}: {roman} -> {back}"

    def test_round_trip_special_cases(self):
        """Test round-trip for special cases."""
        special_cases = [1, 4, 9, 39, 99, 246, 421, 888, 1994, 3999]
        for n in special_cases:
            roman = roman_of_arabian(n)
            back = arabian_of_roman(roman)
            assert back == n, f"Round-trip failed for {n}: {roman} -> {back}"


class TestOCamlBehaviorConsistency:
    """Verify exact OCaml behavior consistency."""

    def test_build_function_logic(self):
        """
        Test the 'build' helper function logic.
        OCaml build function handles digits 0-9 with three symbols.
        """
        # Units position (I, V, X)
        assert roman_of_arabian(0) == ""
        assert roman_of_arabian(1) == "I"
        assert roman_of_arabian(2) == "II"
        assert roman_of_arabian(3) == "III"
        assert roman_of_arabian(4) == "IV"
        assert roman_of_arabian(5) == "V"
        assert roman_of_arabian(6) == "VI"
        assert roman_of_arabian(7) == "VII"
        assert roman_of_arabian(8) == "VIII"
        assert roman_of_arabian(9) == "IX"

    def test_digit_positions(self):
        """
        Test that each digit position uses correct symbols.
        OCaml: build "M" "M" "M" (thousands)
               build "C" "D" "M" (hundreds)
               build "X" "L" "C" (tens)
               build "I" "V" "X" (units)
        """
        # Thousands: M, M, M
        assert roman_of_arabian(1000) == "M"
        assert roman_of_arabian(2000) == "MM"
        assert roman_of_arabian(3000) == "MMM"

        # Hundreds: C, D, M
        assert roman_of_arabian(100) == "C"
        assert roman_of_arabian(500) == "D"
        assert roman_of_arabian(400) == "CD"
        assert roman_of_arabian(900) == "CM"

        # Tens: X, L, C
        assert roman_of_arabian(10) == "X"
        assert roman_of_arabian(50) == "L"
        assert roman_of_arabian(40) == "XL"
        assert roman_of_arabian(90) == "XC"

        # Units: I, V, X
        assert roman_of_arabian(1) == "I"
        assert roman_of_arabian(5) == "V"
        assert roman_of_arabian(4) == "IV"
        assert roman_of_arabian(9) == "IX"

    def test_modulo_operations(self):
        """
        Test modulo operations match OCaml.
        OCaml: (n / 1000 mod 10), (n / 100 mod 10), etc.
        """
        # 1234: thousands=1, hundreds=2, tens=3, units=4
        assert roman_of_arabian(1234) == "MCCXXXIV"

        # 3999: thousands=3, hundreds=9, tens=9, units=9
        assert roman_of_arabian(3999) == "MMMCMXCIX"

        # 2468: thousands=2, hundreds=4, tens=6, units=8
        assert roman_of_arabian(2468) == "MMCDLXVIII"


class TestGeneWebUsage:
    """Test cases matching GeneWeb's actual usage patterns."""

    def test_year_range_check(self):
        """
        GeneWeb checks: y >= 1 && y < 4000
        From dateDisplay.ml:129
        """
        # Valid range
        assert roman_of_arabian(1) == "I"
        assert roman_of_arabian(1999) == "MCMXCIX"
        assert roman_of_arabian(3999) == "MMMCMXCIX"

        # Boundary
        assert roman_of_arabian(0) == ""  # Below range returns empty

    def test_common_genealogy_years(self):
        """Test years commonly seen in genealogy databases."""
        test_cases = [
            (1500, "MD"),
            (1600, "MDC"),
            (1700, "MDCC"),
            (1800, "MDCCC"),
            (1850, "MDCCCL"),
            (1900, "MCM"),
            (1950, "MCML"),
            (2000, "MM"),
        ]
        for year, expected in test_cases:
            assert roman_of_arabian(year) == expected


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
