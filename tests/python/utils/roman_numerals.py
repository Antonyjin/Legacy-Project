# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Roman numeral conversion utilities - Migration from OCaml Mutil module.

This module replicates the OCaml roman numeral conversion functions from GeneWeb,
specifically migrating Mutil.roman_of_arabian.

OCaml Reference:
- source_geneweb/lib/util/mutil.ml: roman_of_arabian implementation (lines 328-346)
- source_geneweb/test/util_test.ml: Test cases for roman numerals

Issue: MIG-003 - Migrate roman_of_arabian function
"""


def roman_of_arabian(n: int) -> str:
    """
    Convert an integer to Roman numerals.

    This function replicates the OCaml Mutil.roman_of_arabian behavior.

    OCaml Reference: source_geneweb/lib/util/mutil.ml:328-346

    Algorithm (from OCaml):
    The function uses a "build" helper that converts a single digit (0-9)
    to Roman numerals using three letters (one, five, ten):

    - 0: ""
    - 1: one
    - 2: one + one
    - 3: one + one + one
    - 4: one + five (subtractive notation)
    - 5: five
    - 6: five + one
    - 7: five + one + one
    - 8: five + one + one + one
    - 9: one + ten (subtractive notation)

    Then applies this to each digit position:
    - Thousands: M, M, M (up to MMM = 3000)
    - Hundreds: C, D, M
    - Tens: X, L, C
    - Units: I, V, X

    Args:
        n: The integer to convert (typically 1-3999, but algorithm works for wider range)

    Returns:
        Roman numeral representation

    Examples:
        >>> roman_of_arabian(1)
        'I'
        >>> roman_of_arabian(4)
        'IV'
        >>> roman_of_arabian(9)
        'IX'
        >>> roman_of_arabian(39)
        'XXXIX'
        >>> roman_of_arabian(246)
        'CCXLVI'
        >>> roman_of_arabian(421)
        'CDXXI'
        >>> roman_of_arabian(160)
        'CLX'
        >>> roman_of_arabian(1994)
        'MCMXCIV'
        >>> roman_of_arabian(3999)
        'MMMCMXCIX'

    Notes:
        - The function handles the full range 1-3999 correctly
        - Uses subtractive notation (IV for 4, IX for 9, etc.)
        - Returns empty string for 0
        - Negative numbers are not typically used in genealogy
        - Numbers > 3999 work but may not follow classical Roman notation

    Usage in GeneWeb:
        - Used in dateDisplay.ml for displaying years in Roman numerals
        - Used in templ.ml for template rendering
        - Range check: y >= 1 && y < 4000 before calling
    """
    def build(one: str, five: str, ten: str, digit: int) -> str:
        """
        Helper function to build Roman numeral for a single digit (0-9).

        Args:
            one: Symbol for 1 in this position (I, X, C, or M)
            five: Symbol for 5 in this position (V, L, D, or M)
            ten: Symbol for 10 in this position (X, C, M, or M)
            digit: The digit value (0-9)

        Returns:
            Roman numeral representation of the digit
        """
        if digit == 0:
            return ""
        elif digit == 1:
            return one
        elif digit == 2:
            return one + one
        elif digit == 3:
            return one + one + one
        elif digit == 4:
            return one + five
        elif digit == 5:
            return five
        elif digit == 6:
            return five + one
        elif digit == 7:
            return five + one + one
        elif digit == 8:
            return five + one + one + one
        else:  # digit == 9
            return one + ten

    # Build Roman numeral from each digit position
    # Thousands (M = 1000)
    thousands = build("M", "M", "M", (n // 1000) % 10)

    # Hundreds (C = 100, D = 500, M = 1000)
    hundreds = build("C", "D", "M", (n // 100) % 10)

    # Tens (X = 10, L = 50, C = 100)
    tens = build("X", "L", "C", (n // 10) % 10)

    # Units (I = 1, V = 5, X = 10)
    units = build("I", "V", "X", n % 10)

    return thousands + hundreds + tens + units


def arabian_of_roman(s: str) -> int:
    """
    Convert Roman numerals to an integer.

    This function replicates the OCaml Mutil.arabian_of_roman behavior.

    OCaml Reference: source_geneweb/lib/util/mutil.ml:346-365

    Algorithm (from OCaml):
    The function uses a "decode_digit" helper that processes one digit position
    by reading characters and accumulating the value:

    - Counts consecutive 'one' characters (e.g., III = 3)
    - If 'five' follows, it's either 5 or subtractive (e.g., IV = 5 - 1 = 4)
    - If 'ten' follows, it's subtractive (e.g., IX = 10 - 1 = 9)

    Processes each position: thousands → hundreds → tens → units

    Args:
        s: Roman numeral string (uppercase)

    Returns:
        Integer value

    Raises:
        ValueError: If the string is not a valid Roman numeral

    Examples:
        >>> arabian_of_roman("I")
        1
        >>> arabian_of_roman("IV")
        4
        >>> arabian_of_roman("IX")
        9
        >>> arabian_of_roman("XXXIX")
        39
        >>> arabian_of_roman("CCXLVI")
        246
        >>> arabian_of_roman("CDXXI")
        421
        >>> arabian_of_roman("CLX")
        160
        >>> arabian_of_roman("MCMXCIV")
        1994
        >>> arabian_of_roman("MMMCMXCIX")
        3999

    Notes:
        - The function validates that the entire string is consumed
        - Invalid Roman numerals raise ValueError
        - Empty string raises ValueError
    """
    def decode_digit(one: str, five: str, ten: str, r: int, i: int) -> tuple[int, int]:
        """
        Decode one digit position from Roman numeral.

        Args:
            one: Character for 1 in this position (I, X, C, or M)
            five: Character for 5 in this position (V, L, D, or M)
            ten: Character for 10 in this position (X, C, M, or M)
            r: Accumulated result so far
            i: Current index in string

        Returns:
            Tuple of (new_result, new_index)
        """
        def loop(cnt: int, idx: int) -> tuple[int, int]:
            """Inner loop matching OCaml's recursive structure."""
            if idx >= len(s):
                # End of string
                return (10 * r + cnt, idx)
            elif s[idx] == one:
                # Another 'one' character
                return loop(cnt + 1, idx + 1)
            elif s[idx] == five:
                if cnt == 0:
                    # Just 'five', continue reading (e.g., VI = V + I)
                    return loop(5, idx + 1)
                else:
                    # Subtractive: 'one' before 'five' (e.g., IV = 5 - 1)
                    return (10 * r + 5 - cnt, idx + 1)
            elif s[idx] == ten:
                # Subtractive: 'one' before 'ten' (e.g., IX = 10 - 1)
                return (10 * r + 10 - cnt, idx + 1)
            else:
                # Different character, return accumulated count
                return (10 * r + cnt, idx)

        return loop(0, i)

    if not s:
        raise ValueError("Empty Roman numeral string")

    # Decode each position
    r, i = decode_digit('M', 'M', 'M', 0, 0)  # Thousands
    r, i = decode_digit('C', 'D', 'M', r, i)  # Hundreds
    r, i = decode_digit('X', 'L', 'C', r, i)  # Tens
    r, i = decode_digit('I', 'V', 'X', r, i)  # Units

    # Validate that entire string was consumed
    if i != len(s):
        raise ValueError(f"Invalid Roman numeral: {s}")

    return r
