"""Tests for date validation utilities (MIG-005).

Tests the leap_year and nb_days_in_month functions migrated from OCaml's Date module
(source_geneweb/lib/util/date.ml).

OCaml Reference:
- leap_year: date.ml:86
- nb_days_in_month: date.ml:88-93
"""

import pytest
from utils.date_validation import leap_year, nb_days_in_month


class TestLeapYear:
    """Test leap_year function (date.ml:86).
    
    OCaml implementation:
        let leap_year a = if a mod 100 = 0 then a / 100 mod 4 = 0 else a mod 4 = 0
    """
    
    def test_regular_leap_year(self):
        """Test regular leap years (divisible by 4, not by 100)"""
        assert leap_year(2004) is True
        assert leap_year(2008) is True
        assert leap_year(2012) is True
        assert leap_year(2016) is True
        assert leap_year(2020) is True
        assert leap_year(2024) is True
    
    def test_non_leap_year(self):
        """Test non-leap years (not divisible by 4)"""
        assert leap_year(2001) is False
        assert leap_year(2002) is False
        assert leap_year(2003) is False
        assert leap_year(2005) is False
        assert leap_year(2021) is False
        assert leap_year(2022) is False
        assert leap_year(2023) is False
    
    def test_century_not_leap(self):
        """Test century years that are NOT leap years (divisible by 100, not by 400)"""
        assert leap_year(1700) is False
        assert leap_year(1800) is False
        assert leap_year(1900) is False
        assert leap_year(2100) is False
        assert leap_year(2200) is False
        assert leap_year(2300) is False
    
    def test_century_leap(self):
        """Test century years that ARE leap years (divisible by 400)"""
        assert leap_year(1600) is True
        assert leap_year(2000) is True
        assert leap_year(2400) is True
    
    def test_genealogy_relevant_years(self):
        """Test years commonly found in genealogy databases"""
        # 19th century
        assert leap_year(1804) is True  # Napoleon emperor
        assert leap_year(1848) is True  # Revolutions
        assert leap_year(1870) is False # Franco-Prussian War
        assert leap_year(1892) is True
        
        # 20th century
        assert leap_year(1914) is False # WWI start
        assert leap_year(1918) is False # WWI end
        assert leap_year(1939) is False # WWII start
        assert leap_year(1944) is True  # D-Day
        assert leap_year(1945) is False # WWII end
        assert leap_year(1968) is True  # May 68
        assert leap_year(1989) is False # Berlin Wall
        
        # 21st century
        assert leap_year(2000) is True  # Millennium
        assert leap_year(2010) is False
        assert leap_year(2020) is True  # COVID-19


class TestNbDaysInMonth:
    """Test nb_days_in_month function (date.ml:88-93).
    
    OCaml implementation:
        let nb_days_in_month m a =
          if m = 2 && leap_year a then 29
          else if m >= 1 && m <= 12 then
            [| 31; 28; 31; 30; 31; 30; 31; 31; 30; 31; 30; 31 |].(m - 1)
          else 0
    """
    
    def test_31_day_months(self):
        """Test months with 31 days (Jan, Mar, May, Jul, Aug, Oct, Dec)"""
        year = 2023
        assert nb_days_in_month(1, year) == 31  # January
        assert nb_days_in_month(3, year) == 31  # March
        assert nb_days_in_month(5, year) == 31  # May
        assert nb_days_in_month(7, year) == 31  # July
        assert nb_days_in_month(8, year) == 31  # August
        assert nb_days_in_month(10, year) == 31 # October
        assert nb_days_in_month(12, year) == 31 # December
    
    def test_30_day_months(self):
        """Test months with 30 days (Apr, Jun, Sep, Nov)"""
        year = 2023
        assert nb_days_in_month(4, year) == 30  # April
        assert nb_days_in_month(6, year) == 30  # June
        assert nb_days_in_month(9, year) == 30  # September
        assert nb_days_in_month(11, year) == 30 # November
    
    def test_february_non_leap_year(self):
        """Test February in non-leap years (28 days)"""
        assert nb_days_in_month(2, 2001) == 28
        assert nb_days_in_month(2, 2002) == 28
        assert nb_days_in_month(2, 2003) == 28
        assert nb_days_in_month(2, 2021) == 28
        assert nb_days_in_month(2, 2022) == 28
        assert nb_days_in_month(2, 2023) == 28
    
    def test_february_leap_year(self):
        """Test February in leap years (29 days)"""
        assert nb_days_in_month(2, 2000) == 29  # Century leap year
        assert nb_days_in_month(2, 2004) == 29
        assert nb_days_in_month(2, 2008) == 29
        assert nb_days_in_month(2, 2012) == 29
        assert nb_days_in_month(2, 2016) == 29
        assert nb_days_in_month(2, 2020) == 29
        assert nb_days_in_month(2, 2024) == 29
    
    def test_february_century_years(self):
        """Test February in century years (special leap year rules)"""
        assert nb_days_in_month(2, 1700) == 28  # Not leap
        assert nb_days_in_month(2, 1800) == 28  # Not leap
        assert nb_days_in_month(2, 1900) == 28  # Not leap
        assert nb_days_in_month(2, 2000) == 29  # Leap!
        assert nb_days_in_month(2, 2100) == 28  # Not leap
        assert nb_days_in_month(2, 2400) == 29  # Leap!
    
    def test_invalid_month_zero(self):
        """Test invalid month 0 (used in GeneWeb for unknown month)"""
        assert nb_days_in_month(0, 2023) == 0
        assert nb_days_in_month(0, 2000) == 0
    
    def test_invalid_month_too_high(self):
        """Test invalid months > 12"""
        assert nb_days_in_month(13, 2023) == 0
        assert nb_days_in_month(14, 2023) == 0
        assert nb_days_in_month(100, 2023) == 0
    
    def test_invalid_month_negative(self):
        """Test invalid negative months"""
        assert nb_days_in_month(-1, 2023) == 0
        assert nb_days_in_month(-12, 2023) == 0


class TestOCamlBehaviorConsistency:
    """Test consistency with OCaml behavior patterns."""
    
    def test_leap_year_ocaml_examples(self):
        """Test leap year cases from OCaml test files"""
        # From source_geneweb/test/calendar_test.ml patterns
        assert leap_year(2000) is True   # Common test case
        assert leap_year(1996) is True   # 90s leap year
        assert leap_year(2020) is True   # Recent leap year
        assert leap_year(1900) is False  # Century non-leap
    
    def test_february_validation_pattern(self):
        """Test February validation pattern used in GeneWeb"""
        # Valid dates in February
        assert nb_days_in_month(2, 2020) >= 29
        assert nb_days_in_month(2, 2021) >= 28
        
        # February 29 only exists in leap years
        assert nb_days_in_month(2, 2020) == 29
        assert nb_days_in_month(2, 2021) < 29
    
    def test_month_boundary_validation(self):
        """Test month boundary conditions (0, 1-12, 13+)"""
        # Valid months
        for month in range(1, 13):
            days = nb_days_in_month(month, 2023)
            assert days > 0, f"Month {month} should have > 0 days"
            assert days <= 31, f"Month {month} should have <= 31 days"
        
        # Invalid months
        assert nb_days_in_month(0, 2023) == 0
        assert nb_days_in_month(13, 2023) == 0


class TestGenealogicalYears:
    """Test years commonly encountered in genealogy."""
    
    def test_19th_century_leap_years(self):
        """Test 19th century leap years"""
        # Sample genealogically-relevant years
        assert leap_year(1800) is False  # Century non-leap
        assert leap_year(1804) is True
        assert leap_year(1848) is True
        assert leap_year(1892) is True
        assert leap_year(1896) is True
    
    def test_20th_century_leap_years(self):
        """Test 20th century leap years"""
        assert leap_year(1900) is False  # Century non-leap
        assert leap_year(1904) is True
        assert leap_year(1944) is True
        assert leap_year(1968) is True
        assert leap_year(1996) is True
    
    def test_historical_february_days(self):
        """Test February in historical years"""
        # Non-leap February in history
        assert nb_days_in_month(2, 1789) == 28  # French Revolution
        assert nb_days_in_month(2, 1865) == 28  # US Civil War
        
        # Leap February in history
        assert nb_days_in_month(2, 1776) == 29  # US Independence
        assert nb_days_in_month(2, 1804) == 29  # Napoleon emperor


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_year_zero_and_negative(self):
        """Test year 0 and negative years (historical BC dates)"""
        # Year 0 in proleptic Gregorian calendar
        assert leap_year(0) is True  # Year 0 would be 1 BC, divisible by 400
        
        # Negative years (BC dates)
        # Note: OCaml doesn't specify BC behavior, but we handle it
        assert leap_year(-4) is True   # 5 BC
        assert leap_year(-100) is False # 101 BC
    
    def test_very_large_years(self):
        """Test very large year numbers"""
        assert leap_year(10000) is True  # Divisible by 400
        assert leap_year(10001) is False
        assert leap_year(99996) is True  # Divisible by 4
    
    def test_all_months_in_leap_year(self):
        """Test that only February changes in leap years"""
        leap = 2020
        non_leap = 2021
        
        for month in [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            # All months except February have same days regardless of leap year
            assert nb_days_in_month(month, leap) == nb_days_in_month(month, non_leap)
        
        # Only February differs
        assert nb_days_in_month(2, leap) != nb_days_in_month(2, non_leap)
        assert nb_days_in_month(2, leap) == 29
        assert nb_days_in_month(2, non_leap) == 28


class TestRoundTripValidation:
    """Test round-trip validation patterns."""
    
    def test_leap_year_february_consistency(self):
        """Test that leap_year and nb_days_in_month are consistent"""
        for year in range(1900, 2101):
            if leap_year(year):
                assert nb_days_in_month(2, year) == 29, f"{year} is leap but Feb != 29"
            else:
                assert nb_days_in_month(2, year) == 28, f"{year} not leap but Feb != 28"
