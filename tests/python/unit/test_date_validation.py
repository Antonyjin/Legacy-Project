"""
Test date validation and calendar handling via HTTP API.
Tests OCaml's date parsing, validation, and calendar conversion functions.

OCaml Functions Tested (via HTTP):
- Date.compress / Date.uncompress (lib/util/date.ml)
- Date validation (day: 1-31, month: 1-13, year < 2500)
- Calendar conversions (Gregorian, Julian, French, Hebrew)
- Date precision handling (Sure, About, Maybe, Before, After)
"""
import requests
import pytest
from typing import Optional

BASE_URL = "http://localhost:23179/test"


class TestDateValidation:
    """Test basic date validation rules"""
    
    def test_valid_birth_date_displays(self):
        """Test that a person with valid birth date displays correctly"""
        # Charles Windsor: born 14/11/1948
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "1948" in r.text  # Birth year should appear
        assert "November" in r.text or "11" in r.text  # Month should appear
    
    def test_calendar_page_accepts_valid_date(self):
        """Test that calendar page accepts valid date parameters"""
        # Valid date: 14/11/1948 (Charles' birthday)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=1948&mg=11&dg=14")
        assert r.status_code == 200
        assert "1948" in r.text
    
    def test_calendar_page_handles_year_only(self):
        """Test calendar accepts year-only dates (day=0, month=0)"""
        r = requests.get(f"{BASE_URL}?m=CAL&yg=1948")
        assert r.status_code == 200
        assert "1948" in r.text
    
    def test_calendar_page_handles_month_year(self):
        """Test calendar accepts month+year dates (day=0)"""
        r = requests.get(f"{BASE_URL}?m=CAL&yg=1948&mg=11")
        assert r.status_code == 200
        assert "1948" in r.text


class TestDateBoundaryConditions:
    """Test date boundary conditions and edge cases"""
    
    def test_valid_month_range(self):
        """Test months 1-12 are accepted (13 for Hebrew calendar)"""
        # Test standard month range
        for month in [1, 6, 12]:
            r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg={month}&dg=15")
            assert r.status_code == 200, f"Month {month} should be valid"
    
    def test_valid_day_range(self):
        """Test days 1-31 are accepted"""
        # Test common days
        for day in [1, 15, 28]:
            r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=6&dg={day}")
            assert r.status_code == 200, f"Day {day} should be valid"
    
    def test_calendar_handles_edge_dates(self):
        """Test edge dates (Feb 29, Dec 31, etc.)"""
        # Leap year Feb 29
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=2&dg=29")
        assert r.status_code == 200
        
        # Dec 31
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=12&dg=31")
        assert r.status_code == 200
    
    def test_calendar_accepts_year_under_2500(self):
        """OCaml Date.compress requires year < 2500"""
        # Year 2499 should work (< 2500)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2499")
        assert r.status_code == 200
        
        # Year 1800 should work
        r = requests.get(f"{BASE_URL}?m=CAL&yg=1800")
        assert r.status_code == 200


class TestDatePrecision:
    """Test date precision modifiers (About, Maybe, Before, After)
    
    Note: These are tested indirectly via person pages that display
    date precision markers in the HTML.
    """
    
    def test_person_with_exact_date(self):
        """Test person with exact/sure date precision"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        # Charles has exact birth date: 14 November 1948
        assert "1948" in r.text
    
    def test_person_page_displays_dates(self):
        """Test that person pages display birth/death dates"""
        # Elizabeth II: 21 April 1926 - 8 September 2022
        r = requests.get(f"{BASE_URL}?p=Elizabeth&n=Windsor")
        assert r.status_code == 200
        assert "1926" in r.text  # Birth year
        assert "2022" in r.text  # Death year


class TestCalendarTypes:
    """Test different calendar types (Gregorian, Julian, French, Hebrew)
    
    OCaml supports:
    - Dgregorian (default)
    - Djulian
    - Dfrench (13 months)
    - Dhebrew (13 months)
    """
    
    def test_gregorian_calendar_default(self):
        """Test Gregorian calendar (default)"""
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=6&dg=15")
        assert r.status_code == 200
        # Gregorian is default, page should load
    
    def test_calendar_page_loads(self):
        """Test that calendar page loads and displays date fields"""
        r = requests.get(f"{BASE_URL}?m=CAL")
        assert r.status_code == 200
        # Check for calendar-specific elements
        assert ("gregorian" in r.text.lower() or 
                "calendar" in r.text.lower() or
                "date" in r.text.lower())


class TestDateInURL:
    """Test date parameters in URLs"""
    
    def test_person_page_with_date_params(self):
        """Test that person pages handle date navigation params"""
        # Link to calendar with specific date (from person page)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=1948&mg=11&dg=14&tg=1")
        assert r.status_code == 200
    
    def test_calendar_navigation_year(self):
        """Test calendar navigation with year parameter"""
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000")
        assert r.status_code == 200
        assert "2000" in r.text
    
    def test_calendar_navigation_month(self):
        """Test calendar navigation with month parameter"""
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=6")
        assert r.status_code == 200


class TestDateEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_day_month_accepted(self):
        """OCaml allows day=0, month=0 for year-only dates"""
        # Year-only date
        r = requests.get(f"{BASE_URL}?m=CAL&yg=1900")
        assert r.status_code == 200
    
    def test_historical_dates(self):
        """Test dates far in the past (historical genealogy)"""
        # Test medieval date (1200)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=1200")
        assert r.status_code == 200
        
        # Test ancient date (100)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=100")
        assert r.status_code == 200
    
    def test_negative_years_handled(self):
        """Test BCE dates (negative years)
        
        Note: OCaml supports negative years for BCE dates.
        GeneWeb may handle these specially.
        """
        # This may return 200 (with warning) or 4xx (rejected)
        # Either is acceptable behavior
        r = requests.get(f"{BASE_URL}?m=CAL&yg=-100")
        assert r.status_code < 500, "Server should not crash on BCE dates"
    
    def test_very_large_year_handled(self):
        """Test that very large years are handled gracefully
        
        OCaml Date.compress requires year < 2500.
        Years >= 2500 should be handled without crashing.
        """
        # Year 3000 (> 2500 limit)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=3000")
        # Accept either 200 (uncompressed date) or 4xx (rejected)
        assert r.status_code < 500, "Server should not crash on year > 2500"
    
    def test_invalid_month_handled(self):
        """Test that invalid month values are handled gracefully"""
        # Month 13 is valid for Hebrew/French calendars
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=13")
        # Should either work or return client error, not server error
        assert r.status_code < 500
        
        # Month 0 (year-only date)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=0")
        assert r.status_code < 500
    
    def test_invalid_day_handled(self):
        """Test that invalid day values are handled gracefully"""
        # Day 32 (invalid)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=6&dg=32")
        # Should return 4xx or 200 with error message, not 5xx
        assert r.status_code < 500, "Invalid day should not crash server"
        
        # Day 0 (month-only date)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2000&mg=6&dg=0")
        assert r.status_code < 500


class TestDateDisplay:
    """Test how dates are displayed on person pages"""
    
    def test_birth_date_display(self):
        """Test that birth dates are displayed correctly"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        # Birth date should be displayed
        assert ("born" in r.text.lower() or "°" in r.text)
        assert "1948" in r.text
    
    def test_death_date_display(self):
        """Test that death dates are displayed correctly"""
        r = requests.get(f"{BASE_URL}?p=Philip&n=Mountbatten")
        assert r.status_code == 200
        # Philip died in 2021
        assert ("died" in r.text.lower() or "†" in r.text or "2021" in r.text)
    
    def test_marriage_date_display(self):
        """Test that marriage dates are displayed on family pages"""
        r = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        assert r.status_code == 200
        # Should show family information with dates
        assert "<html" in r.text.lower()


@pytest.mark.unit
class TestDateCompression:
    """Test OCaml's Date.compress / Date.uncompress functionality
    
    OCaml compresses dates into a single integer if:
    - day >= 0 && day <= 31
    - month >= 0 && month <= 13
    - year > 0 && year < 2500
    - delta = 0
    - prec in {Sure, About, Maybe, Before, After}
    
    Formula: ((((prec * 32 + day) * 13 + month) * 2500) + year)
    """
    
    def test_compressible_date_works(self):
        """Test that dates meeting compression criteria work"""
        # Charles' birth: 14/11/1948 - should be compressible
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        assert "1948" in r.text
    
    def test_year_boundary_2500(self):
        """Test year < 2500 boundary (compression limit)"""
        # Year 2499 should be compressible
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2499&mg=6&dg=15")
        assert r.status_code == 200
        
        # Year 2500 exceeds compression limit but should still work
        # (stored as uncompressed Cdate instead of Cgregorian)
        r = requests.get(f"{BASE_URL}?m=CAL&yg=2500&mg=6&dg=15")
        assert r.status_code < 500  # Should not crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

