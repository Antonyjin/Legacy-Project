# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""Date validation utilities for GeneWeb genealogy software."""


def leap_year(year: int) -> bool:
    if year % 100 == 0:
        return (year // 100) % 4 == 0
    else:
        return year % 4 == 0


def nb_days_in_month(month: int, year: int) -> int:
    if month == 2 and leap_year(year):
        return 29
    if month < 1 or month > 12:
        return 0
    days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return days_per_month[month - 1]


