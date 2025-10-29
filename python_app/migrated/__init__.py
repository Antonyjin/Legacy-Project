"""
Migrated utility functions from tests/python/utils/

This module imports all migrated Python utility functions.
When BACKEND=python, these functions are used instead of OCaml equivalents.
"""

# Import all migrated utilities
import sys
from pathlib import Path

# Add tests/python to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests" / "python"))

# Import utility modules
from utils import (
    # Name utilities
    name_lower,
    name_strip,
    strip_lower,
    
    # String utilities
    strip_c,
    purge,
    contains_forbidden_char,
    FORBIDDEN_CHAR,
    
    # HTTP utilities
    url_encode,
    url_decode,
    extract_param,
    parse_query_string,
    extract_all_params,
    
    # HTML utilities
    escape_html,
    unescape_html,
    
    # Number formatting
    format_number_with_separator,
    LOCALE_SEPARATORS,
    
    # Roman numerals
    roman_of_arabian,
    arabian_of_roman,
    
    # Date validation
    leap_year,
    nb_days_in_month,
    
    # Date comparison
    Precision,
    Calendar,
    Dmy,
    Dgreg,
    Dtext,
    Date,
    compare_dmy,
    compare_dmy_opt,
    compare_date,
    NotComparable,
)

__all__ = [
    # Name utilities
    "name_lower",
    "name_strip",
    "strip_lower",
    # String utilities
    "strip_c",
    "purge",
    "contains_forbidden_char",
    "FORBIDDEN_CHAR",
    # HTTP utilities
    "url_encode",
    "url_decode",
    "extract_param",
    "parse_query_string",
    "extract_all_params",
    # HTML utilities
    "escape_html",
    "unescape_html",
    # Number formatting
    "format_number_with_separator",
    "LOCALE_SEPARATORS",
    # Roman numerals
    "roman_of_arabian",
    "arabian_of_roman",
    # Date validation
    "leap_year",
    "nb_days_in_month",
    # Date comparison
    "Precision",
    "Calendar",
    "Dmy",
    "Dgreg",
    "Dtext",
    "Date",
    "compare_dmy",
    "compare_dmy_opt",
    "compare_date",
    "NotComparable",
]

