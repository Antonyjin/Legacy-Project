# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
String utility functions - Migration from OCaml Name module.
"""

FORBIDDEN_CHAR = [':', '@', '#', '=', '$']


def strip_c(s: str, c: str) -> str:
    if len(c) != 1:
        raise ValueError(f"strip_c requires a single character, got: {c}")
    return s.replace(c, '')


def purge(s: str) -> str:
    result = s
    for forbidden_char in FORBIDDEN_CHAR:
        result = strip_c(result, forbidden_char)
    return result


def contains_forbidden_char(s: str) -> bool:
    return any(char in s for char in FORBIDDEN_CHAR)


