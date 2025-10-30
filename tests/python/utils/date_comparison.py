# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Date Comparison Utilities

Migrated from OCaml: source_geneweb/lib/util/date.ml (lines 147-210)

This module provides date comparison functions with precision handling.
Supports strict and non-strict comparison modes.

Public Functions:
- compare_dmy: Compare two dmy structures (raises NotComparable)
- compare_dmy_opt: Compare two dmy structures (returns Optional[int])
- compare_date: Compare two date structures

Types:
- Precision: Date precision (Sure, About, Maybe, Before, After)
- Calendar: Calendar type (Gregorian, Julian, French, Hebrew)
- Dmy: Date structure (day, month, year, precision, delta)
- Date: Union of Dgreg (Gregorian date) or Dtext (text date)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class Precision(Enum):
    """Date precision levels (from OCaml adef.ml)"""
    SURE = "sure"
    ABOUT = "about"
    MAYBE = "maybe"
    BEFORE = "before"
    AFTER = "after"
    # Note: OrYear and YearInt not migrated (complex, rarely used)


class Calendar(Enum):
    """Calendar types (from OCaml adef.ml)"""
    GREGORIAN = "gregorian"
    JULIAN = "julian"
    FRENCH = "french"
    HEBREW = "hebrew"


@dataclass(frozen=True)
class Dmy:
    """Date structure (from OCaml adef.ml)

    Fields:
    - day: Day of month (0 = unknown)
    - month: Month (0 = unknown, 1-12)
    - year: Year
    - prec: Precision level
    - delta: Delta value (for year ranges)
    """
    day: int
    month: int
    year: int
    prec: Precision
    delta: int


@dataclass(frozen=True)
class Dgreg:
    """Gregorian date with calendar type"""
    dmy: Dmy
    calendar: Calendar


@dataclass(frozen=True)
class Dtext:
    """Text-based date (unparsed string)"""
    text: str


# Date is either Dgreg or Dtext
Date = Union[Dgreg, Dtext]


class NotComparable(Exception):
    """Exception raised when dates cannot be compared in strict mode"""


def compare_dmy_opt(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> Optional[int]:
    """Compare two dmy structures, return None if not comparable.

    OCaml: date.ml:147 (compare_dmy_opt)

    Args:
        dmy1: First date structure
        dmy2: Second date structure
        strict: If True, consider precision (may return None)
                If False, compare as points on timeline

    Returns:
        -1 if dmy1 < dmy2
         0 if dmy1 == dmy2
         1 if dmy1 > dmy2
         None if not comparable (strict mode only)
    """

    def eval_strict(dmy1: Dmy, dmy2: Dmy, x: int) -> Optional[int]:
        """OCaml: date.ml:191 (eval_strict helper)"""
        if strict:
            # In strict mode, check if precisions make comparison invalid
            if x == -1 and (dmy1.prec == Precision.AFTER or dmy2.prec == Precision.BEFORE):
                return None
            if x == 1 and (dmy1.prec == Precision.BEFORE or dmy2.prec == Precision.AFTER):
                return None
            return x
        else:
            return x

    def compare_prec(dmy1: Dmy, dmy2: Dmy) -> Optional[int]:
        """OCaml: date.ml:178 (compare_prec helper)

        OCaml pattern matching:
        | (Sure | About | Maybe), (Sure | About | Maybe) -> Some 0
        | After, After | Before, Before -> Some 0
        | _, After | Before, _ -> Some (-1)
        | After, _ | _, Before -> Some 1
        | _ -> Some 0
        """
        p1, p2 = dmy1.prec, dmy2.prec

        # (Sure | About | Maybe), (Sure | About | Maybe) -> 0
        if p1 in (Precision.SURE, Precision.ABOUT, Precision.MAYBE) and \
           p2 in (Precision.SURE, Precision.ABOUT, Precision.MAYBE):
            return 0

        # After, After | Before, Before -> 0
        if (p1 == Precision.AFTER and p2 == Precision.AFTER) or \
           (p1 == Precision.BEFORE and p2 == Precision.BEFORE):
            return 0

        # _, After | Before, _ -> -1
        if p2 == Precision.AFTER or p1 == Precision.BEFORE:
            return -1

        # After, _ | _, Before -> 1
        if p1 == Precision.AFTER or p2 == Precision.BEFORE:
            return 1

        # _ -> 0
        return 0

    def compare_month_or_day(is_day: bool, dmy1: Dmy, dmy2: Dmy) -> Optional[int]:
        """OCaml: date.ml:152 (compare_month_or_day helper)"""

        def compare_with_unknown_value(unknown: Dmy, known: Dmy) -> Optional[int]:
            """OCaml: date.ml:154 (nested helper)"""
            if unknown.prec == Precision.AFTER:
                return 1
            elif unknown.prec == Precision.BEFORE:
                return -1
            else:
                # In strict mode, unknown value makes comparison invalid
                if strict:
                    return None
                else:
                    return compare_prec(unknown, known)

        # Select day or month for comparison
        if is_day:
            x, y = dmy1.day, dmy2.day
            next_comparison = compare_prec
        else:
            x, y = dmy1.month, dmy2.month
            def next_comparison_func(d1, d2):
                return compare_month_or_day(True, d1, d2)
            next_comparison = next_comparison_func

        # Handle unknown values (0)
        if x == 0 and y == 0:
            return compare_prec(dmy1, dmy2)
        elif x == 0:
            return compare_with_unknown_value(dmy1, dmy2)
        elif y == 0:
            # Swap and negate result
            result = compare_with_unknown_value(dmy2, dmy1)
            return -result if result is not None else None
        else:
            # Both known: compare values
            if x < y:
                return eval_strict(dmy1, dmy2, -1)
            elif x > y:
                return eval_strict(dmy1, dmy2, 1)
            else:
                return next_comparison(dmy1, dmy2)

    # Main comparison: start with year
    if dmy1.year < dmy2.year:
        return eval_strict(dmy1, dmy2, -1)
    elif dmy1.year > dmy2.year:
        return eval_strict(dmy1, dmy2, 1)
    else:
        # Years equal: compare month/day
        return compare_month_or_day(False, dmy1, dmy2)


def compare_dmy(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> int:
    """Compare two dmy structures, raise NotComparable if not comparable.

    OCaml: date.ml:199 (compare_dmy)

    Args:
        dmy1: First date structure
        dmy2: Second date structure
        strict: If True, consider precision (may raise NotComparable)

    Returns:
        -1 if dmy1 < dmy2
         0 if dmy1 == dmy2
         1 if dmy1 > dmy2

    Raises:
        NotComparable: If dates cannot be compared in strict mode
    """
    result = compare_dmy_opt(dmy1, dmy2, strict)
    if result is None:
        raise NotComparable(f"Cannot compare {dmy1} and {dmy2} in strict mode")
    return result


def compare_date(d1: Date, d2: Date, strict: bool = False) -> int:
    """Compare two date structures.

    OCaml: date.ml:204 (compare_date)

    Args:
        d1: First date
        d2: Second date
        strict: If True, consider precision and Dtext incomparability

    Returns:
        -1 if d1 < d2
         0 if d1 == d2
         1 if d1 > d2

    Raises:
        NotComparable: If dates cannot be compared in strict mode
    """
    if isinstance(d1, Dgreg) and isinstance(d2, Dgreg):
        return compare_dmy(d1.dmy, d2.dmy, strict)
    elif isinstance(d1, Dgreg) and isinstance(d2, Dtext):
        if strict:
            raise NotComparable("Cannot compare Dgreg and Dtext in strict mode")
        return 1  # Dgreg > Dtext
    elif isinstance(d1, Dtext) and isinstance(d2, Dgreg):
        if strict:
            raise NotComparable("Cannot compare Dtext and Dgreg in strict mode")
        return -1  # Dtext < Dgreg
    else:  # Both Dtext
        if strict:
            raise NotComparable("Cannot compare two Dtext in strict mode")
        return 0
