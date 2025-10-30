# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""Date validation utilities for GeneWeb genealogy software.

This module provides date validation functions migrated from OCaml's Date module
(source_geneweb/lib/util/date.ml). These functions handle leap year calculations
and day-of-month validation for the Gregorian calendar.

OCaml Reference:
- leap_year: date.ml:86
- nb_days_in_month: date.ml:88-93
"""


def leap_year(year: int) -> bool:
    """Check if a year is a leap year (Gregorian calendar).

    A year is a leap year if:
    - It's divisible by 4 AND
    - Either it's NOT divisible by 100, OR it IS divisible by 400

    This follows the Gregorian calendar leap year rules:
    - Years divisible by 4 are leap years
    - EXCEPT years divisible by 100 are NOT leap years
    - EXCEPT years divisible by 400 ARE leap years

    Examples:
        >>> leap_year(2000)  # Divisible by 400
        True
        >>> leap_year(2004)  # Divisible by 4
        True
        >>> leap_year(1900)  # Divisible by 100 but not 400
        False
        >>> leap_year(2001)  # Not divisible by 4
        False

    Args:
        year: The year to check (any integer)

    Returns:
        True if the year is a leap year, False otherwise

    OCaml Reference:
        let leap_year a = if a mod 100 = 0 then a / 100 mod 4 = 0 else a mod 4 = 0
        (date.ml:86)
    """
    if year % 100 == 0:
        # Century years: only leap if divisible by 400
        # e.g., 1600, 2000, 2400 are leap; 1700, 1800, 1900, 2100 are not
        return (year // 100) % 4 == 0
    else:
        # Non-century years: leap if divisible by 4
        # e.g., 2004, 2008, 2012, 2016, 2020, 2024
        return year % 4 == 0


def nb_days_in_month(month: int, year: int) -> int:
    """Return the number of days in a given month and year (Gregorian calendar).

    Takes leap years into account for February. Returns 0 for invalid month numbers.

    Month numbering: 1 = January, 2 = February, ..., 12 = December

    Examples:
        >>> nb_days_in_month(2, 2000)  # February in leap year
        29
        >>> nb_days_in_month(2, 2001)  # February in non-leap year
        28
        >>> nb_days_in_month(4, 2023)  # April (30 days)
        30
        >>> nb_days_in_month(1, 2023)  # January (31 days)
        31
        >>> nb_days_in_month(13, 2023)  # Invalid month
        0
        >>> nb_days_in_month(0, 2023)  # Invalid month
        0

    Args:
        month: Month number (1-12, where 1 = January)
        year: Year (used for leap year calculation)

    Returns:
        Number of days in the month (28-31), or 0 if month is invalid

    OCaml Reference:
        let nb_days_in_month m a =
          if m = 2 && leap_year a then 29
          else if m >= 1 && m <= 12 then
            [| 31; 28; 31; 30; 31; 30; 31; 31; 30; 31; 30; 31 |].(m - 1)
          else 0
        (date.ml:88-93)
    """
    # Special case: February in a leap year
    if month == 2 and leap_year(year):
        return 29

    # Validate month range
    if month < 1 or month > 12:
        return 0

    # Days per month (non-leap year)
    # Index 0 = January (31), Index 1 = February (28), etc.
    days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    return days_per_month[month - 1]
