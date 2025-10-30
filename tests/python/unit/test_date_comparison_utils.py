# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
UT-PY-017: Date Comparison Tests

Tests date comparison functions migrated from OCaml.
OCaml Reference: source_geneweb/lib/util/date.ml (lines 147-210)

Test Coverage:
- Basic date comparisons (year, month, day)
- Strict vs non-strict modes
- Unknown values (0 for month/day)
- Precision handling (Sure, About, Maybe, Before, After)
- Dtext comparisons
- NotComparable exception
- Real OCaml usage patterns
"""

import sys
from pathlib import Path

# Add tests directory to path for imports
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(test_dir))

import pytest  # noqa: E402
from utils.date_comparison import (  # noqa: E402
    Calendar,
    Dgreg,
    Dmy,
    Dtext,
    NotComparable,
    Precision,
    compare_date,
    compare_dmy,
    compare_dmy_opt,
)


class TestBasicComparisons:
    """Test basic date comparisons without precision complexity"""

    def test_equal_dates(self):
        """OCaml: date.ml:147 - Equal dates return 0"""
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == 0

    def test_different_years(self):
        """OCaml: date.ml:149 - Year comparison"""
        d1 = Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == -1
        assert compare_dmy(d2, d1) == 1

    def test_different_months_same_year(self):
        """OCaml: date.ml:152 - Month comparison when years equal"""
        d1 = Dmy(day=1, month=3, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=1, month=6, year=1990, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == -1
        assert compare_dmy(d2, d1) == 1

    def test_different_days_same_month(self):
        """OCaml: date.ml:152 - Day comparison when year/month equal"""
        d1 = Dmy(day=10, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=20, month=6, year=1990, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == -1
        assert compare_dmy(d2, d1) == 1


class TestUnknownValues:
    """Test handling of unknown values (0 for month/day)"""

    def test_unknown_month_both(self):
        """OCaml: date.ml:168 - Both months unknown, falls to precision"""
        d1 = Dmy(day=15, month=0, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=20, month=0, year=1990, prec=Precision.SURE, delta=0)
        # When both months are 0, OCaml skips to compare_prec (ignores days)
        # Both have SURE precision -> equal
        assert compare_dmy(d1, d2) == 0

    def test_unknown_day_both(self):
        """OCaml: date.ml:168 - Both days unknown"""
        d1 = Dmy(day=0, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=0, month=6, year=1990, prec=Precision.SURE, delta=0)
        # Falls through to precision comparison
        assert compare_dmy(d1, d2) == 0

    def test_unknown_month_one_side_after(self):
        """OCaml: date.ml:154-157 - Unknown month with AFTER precision"""
        d1 = Dmy(day=1, month=0, year=1990, prec=Precision.AFTER, delta=0)
        d2 = Dmy(day=1, month=6, year=1990, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == 1  # AFTER means later

    def test_unknown_month_one_side_before(self):
        """OCaml: date.ml:154-157 - Unknown month with BEFORE precision"""
        d1 = Dmy(day=1, month=0, year=1990, prec=Precision.BEFORE, delta=0)
        d2 = Dmy(day=1, month=6, year=1990, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == -1  # BEFORE means earlier

    def test_unknown_day_strict_mode(self):
        """OCaml: date.ml:157 - Unknown day in strict mode returns None"""
        d1 = Dmy(day=0, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        assert compare_dmy_opt(d1, d2, strict=True) is None


class TestPrecisionHandling:
    """Test precision handling (Sure, About, Maybe, Before, After)"""

    def test_sure_about_maybe_equal(self):
        """OCaml: date.ml:180-181 - Sure/About/Maybe are equivalent"""
        d_sure = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d_about = Dmy(day=15, month=6, year=1990, prec=Precision.ABOUT, delta=0)
        d_maybe = Dmy(day=15, month=6, year=1990, prec=Precision.MAYBE, delta=0)

        assert compare_dmy(d_sure, d_about) == 0
        assert compare_dmy(d_sure, d_maybe) == 0
        assert compare_dmy(d_about, d_maybe) == 0

    def test_after_after_equal(self):
        """OCaml: date.ml:182 - Two AFTER precisions are equal when dates equal"""
        # NOTE: Precision only matters when day/month/year are EQUAL
        # If days differ (15 vs 20), the day comparison result is used
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)  # Same day!
        assert compare_dmy_opt(d1, d2) == 0

    def test_before_before_equal(self):
        """OCaml: date.ml:182 - Two BEFORE precisions are equal when dates equal"""
        # NOTE: Precision only matters when day/month/year are EQUAL
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.BEFORE, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.BEFORE, delta=0)  # Same day!
        assert compare_dmy_opt(d1, d2) == 0

    def test_after_vs_before(self):
        """OCaml: date.ml:185-186 - AFTER > BEFORE"""
        d_after = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)
        d_before = Dmy(day=15, month=6, year=1990, prec=Precision.BEFORE, delta=0)
        assert compare_dmy_opt(d_after, d_before) == 1
        assert compare_dmy_opt(d_before, d_after) == -1


class TestStrictMode:
    """Test strict mode behavior"""

    def test_strict_mode_after_invalidates_less_than(self):
        """OCaml: date.ml:192-193 - AFTER invalidates < in strict mode"""
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)
        d2 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
        # Non-strict: d1 < d2 (1990 < 2000)
        assert compare_dmy(d1, d2, strict=False) == -1
        # Strict: d1 is AFTER, so comparison invalid
        assert compare_dmy_opt(d1, d2, strict=True) is None

    def test_strict_mode_before_invalidates_greater_than(self):
        """OCaml: date.ml:194-195 - BEFORE invalidates > in strict mode"""
        d1 = Dmy(day=15, month=6, year=2000, prec=Precision.BEFORE, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        # Non-strict: d1 > d2 (2000 > 1990)
        assert compare_dmy(d1, d2, strict=False) == 1
        # Strict: d1 is BEFORE, so comparison invalid
        assert compare_dmy_opt(d1, d2, strict=True) is None

    def test_strict_mode_valid_comparison(self):
        """OCaml: date.ml:191 - Strict mode allows valid comparisons"""
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2, strict=True) == -1


class TestCompareDate:
    """Test compare_date function (Dgreg vs Dtext)"""

    def test_two_dgreg_dates(self):
        """OCaml: date.ml:206 - Compare two Dgreg dates"""
        dmy1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        dmy2 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
        d1 = Dgreg(dmy=dmy1, calendar=Calendar.GREGORIAN)
        d2 = Dgreg(dmy=dmy2, calendar=Calendar.GREGORIAN)
        assert compare_date(d1, d2) == -1

    def test_dgreg_vs_dtext_non_strict(self):
        """OCaml: date.ml:207 - Dgreg > Dtext in non-strict mode"""
        dmy = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d1 = Dgreg(dmy=dmy, calendar=Calendar.GREGORIAN)
        d2 = Dtext(text="circa 1990")
        assert compare_date(d1, d2, strict=False) == 1
        assert compare_date(d2, d1, strict=False) == -1

    def test_dgreg_vs_dtext_strict_raises(self):
        """OCaml: date.ml:207 - Dgreg vs Dtext raises in strict mode"""
        dmy = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d1 = Dgreg(dmy=dmy, calendar=Calendar.GREGORIAN)
        d2 = Dtext(text="circa 1990")
        with pytest.raises(NotComparable):
            compare_date(d1, d2, strict=True)

    def test_two_dtext_non_strict(self):
        """OCaml: date.ml:210 - Two Dtext are equal in non-strict mode"""
        d1 = Dtext(text="circa 1990")
        d2 = Dtext(text="around 2000")
        assert compare_date(d1, d2, strict=False) == 0

    def test_two_dtext_strict_raises(self):
        """OCaml: date.ml:210 - Two Dtext raise in strict mode"""
        d1 = Dtext(text="circa 1990")
        d2 = Dtext(text="around 2000")
        with pytest.raises(NotComparable):
            compare_date(d1, d2, strict=True)


class TestNotComparableException:
    """Test NotComparable exception raising"""

    def test_compare_dmy_raises_when_opt_returns_none(self):
        """OCaml: date.ml:200-202 - compare_dmy raises if opt returns None"""
        d1 = Dmy(day=0, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        with pytest.raises(NotComparable):
            compare_dmy(d1, d2, strict=True)

    def test_not_comparable_message(self):
        """Verify exception message contains date info"""
        d1 = Dmy(day=0, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        with pytest.raises(NotComparable) as exc_info:
            compare_dmy(d1, d2, strict=True)
        assert "Cannot compare" in str(exc_info.value)


class TestOCamlRealUsagePatterns:
    """Test patterns from actual OCaml codebase usage"""

    def test_birth_death_display_pattern(self):
        """OCaml: birthDeathDisplay.ml:15 - Compare with today's date"""
        # Date.compare_dmy d conf.today = 1
        future_date = Dmy(day=1, month=1, year=2030, prec=Precision.SURE, delta=0)
        today = Dmy(day=29, month=10, year=2025, prec=Precision.SURE, delta=0)
        assert compare_dmy(future_date, today) == 1

    def test_birth_death_leq_pattern(self):
        """OCaml: birthDeath.ml:57 - Less than or equal comparison"""
        # let leq (_, x, _) (_, y, _) = Date.compare_dmy x y <= 0
        d1 = Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) <= 0
        assert compare_dmy(d1, d1) <= 0

    def test_event_non_strict_pattern(self):
        """OCaml: event.ml:44 - Non-strict comparison with opt"""
        # match Date.compare_dmy_opt ~strict:false d1 d2
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.ABOUT, delta=0)
        d2 = Dmy(day=20, month=6, year=1990, prec=Precision.MAYBE, delta=0)
        result = compare_dmy_opt(d1, d2, strict=False)
        assert result is not None
        assert result == -1

    def test_check_item_strict_pattern(self):
        """OCaml: checkItem.ml:34 - Strict comparison with opt"""
        # match Date.compare_dmy_opt ~strict:true d1 d2
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)
        d2 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
        result = compare_dmy_opt(d1, d2, strict=True)
        # AFTER precision makes comparison invalid
        assert result is None


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_year_zero(self):
        """Handle year 0 (1 BCE in genealogy)"""
        d1 = Dmy(day=1, month=1, year=0, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=1, month=1, year=1, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == -1

    def test_negative_years(self):
        """Handle negative years (BCE dates)"""
        d1 = Dmy(day=1, month=1, year=-100, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=1, month=1, year=-50, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == -1

    def test_very_large_years(self):
        """Handle very large years"""
        d1 = Dmy(day=1, month=1, year=9999, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=1, month=1, year=10000, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == -1

    def test_all_unknown_values(self):
        """Day, month, year all zero/unknown"""
        d1 = Dmy(day=0, month=0, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=0, month=0, year=1990, prec=Precision.SURE, delta=0)
        assert compare_dmy(d1, d2) == 0

    def test_different_calendars_same_dmy(self):
        """OCaml ignores calendar in comparison (only uses dmy)"""
        dmy = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d1 = Dgreg(dmy=dmy, calendar=Calendar.GREGORIAN)
        d2 = Dgreg(dmy=dmy, calendar=Calendar.JULIAN)
        assert compare_date(d1, d2) == 0  # Only dmy compared

    def test_delta_ignored_in_comparison(self):
        """Delta field doesn't affect comparison"""
        d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=10)
        assert compare_dmy(d1, d2) == 0


class TestTypeImmutability:
    """Verify that dataclasses are frozen (immutable)"""

    def test_dmy_frozen(self):
        """Dmy should be immutable"""
        d = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        with pytest.raises(AttributeError):
            d.day = 20  # type: ignore

    def test_dgreg_frozen(self):
        """Dgreg should be immutable"""
        dmy = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
        d = Dgreg(dmy=dmy, calendar=Calendar.GREGORIAN)
        with pytest.raises(AttributeError):
            d.calendar = Calendar.JULIAN  # type: ignore

    def test_dtext_frozen(self):
        """Dtext should be immutable"""
        d = Dtext(text="circa 1990")
        with pytest.raises(AttributeError):
            d.text = "circa 2000"  # type: ignore
