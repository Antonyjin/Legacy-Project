# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Date Comparison Utilities (migrated for runtime use)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class Precision(Enum):
    SURE = "sure"
    ABOUT = "about"
    MAYBE = "maybe"
    BEFORE = "before"
    AFTER = "after"


class Calendar(Enum):
    GREGORIAN = "gregorian"
    JULIAN = "julian"
    FRENCH = "french"
    HEBREW = "hebrew"


@dataclass(frozen=True)
class Dmy:
    day: int
    month: int
    year: int
    prec: Precision
    delta: int


@dataclass(frozen=True)
class Dgreg:
    dmy: Dmy
    calendar: Calendar


@dataclass(frozen=True)
class Dtext:
    text: str


Date = Union[Dgreg, Dtext]


class NotComparable(Exception):
    pass


def compare_dmy_opt(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> Optional[int]:
    def eval_strict(d1: Dmy, d2: Dmy, x: int) -> Optional[int]:
        if strict:
            if x == -1 and (d1.prec == Precision.AFTER or d2.prec == Precision.BEFORE):
                return None
            if x == 1 and (d1.prec == Precision.BEFORE or d2.prec == Precision.AFTER):
                return None
            return x
        else:
            return x

    def compare_prec(d1: Dmy, d2: Dmy) -> Optional[int]:
        p1, p2 = d1.prec, d2.prec
        if p1 in (Precision.SURE, Precision.ABOUT, Precision.MAYBE) and \
           p2 in (Precision.SURE, Precision.ABOUT, Precision.MAYBE):
            return 0
        if (p1 == Precision.AFTER and p2 == Precision.AFTER) or \
           (p1 == Precision.BEFORE and p2 == Precision.BEFORE):
            return 0
        if p2 == Precision.AFTER or p1 == Precision.BEFORE:
            return -1
        if p1 == Precision.AFTER or p2 == Precision.BEFORE:
            return 1
        return 0

    def compare_month_or_day(is_day: bool, d1: Dmy, d2: Dmy) -> Optional[int]:
        def compare_with_unknown_value(unknown: Dmy, known: Dmy) -> Optional[int]:
            if unknown.prec == Precision.AFTER:
                return 1
            elif unknown.prec == Precision.BEFORE:
                return -1
            else:
                if strict:
                    return None
                else:
                    return compare_prec(unknown, known)

        if is_day:
            x, y = d1.day, d2.day
            next_comparison = compare_prec
        else:
            x, y = d1.month, d2.month
            def next_comparison_func(dd1, dd2):
                return compare_month_or_day(True, dd1, dd2)
            next_comparison = next_comparison_func

        if x == 0 and y == 0:
            return compare_prec(d1, d2)
        elif x == 0:
            return compare_with_unknown_value(d1, d2)
        elif y == 0:
            result = compare_with_unknown_value(d2, d1)
            return -result if result is not None else None
        else:
            if x < y:
                return eval_strict(d1, d2, -1)
            elif x > y:
                return eval_strict(d1, d2, 1)
            else:
                return next_comparison(d1, d2)

    if dmy1.year < dmy2.year:
        return eval_strict(dmy1, dmy2, -1)
    elif dmy1.year > dmy2.year:
        return eval_strict(dmy1, dmy2, 1)
    else:
        return compare_month_or_day(False, dmy1, dmy2)


def compare_dmy(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> int:
    result = compare_dmy_opt(dmy1, dmy2, strict)
    if result is None:
        raise NotComparable(f"Cannot compare {dmy1} and {dmy2} in strict mode")
    return result


def compare_date(d1: Date, d2: Date, strict: bool = False) -> int:
    if isinstance(d1, Dgreg) and isinstance(d2, Dgreg):
        return compare_dmy(d1.dmy, d2.dmy, strict)
    elif isinstance(d1, Dgreg) and isinstance(d2, Dtext):
        if strict:
            raise NotComparable("Cannot compare Dgreg and Dtext in strict mode")
        return 1
    elif isinstance(d1, Dtext) and isinstance(d2, Dgreg):
        if strict:
            raise NotComparable("Cannot compare Dtext and Dgreg in strict mode")
        return -1
    else:
        if strict:
            raise NotComparable("Cannot compare two Dtext in strict mode")
        return 0


