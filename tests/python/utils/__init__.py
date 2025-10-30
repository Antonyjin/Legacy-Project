# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Utility modules for Python tests
"""

from .date_comparison import (
    Calendar,
    Date,
    Dgreg,
    Dmy,
    Dtext,
    NotComparable,
    Precision,
    compare_date,
    compare_dmy,
    compare_dmy_opt,
)
from .date_validation import leap_year, nb_days_in_month
from .html_utils import escape_html, unescape_html
from .http_params import extract_all_params, extract_param, parse_query_string, url_decode, url_encode
from .name_utils import contains_only_ascii, is_normalized_name, name_lower, name_strip, strip_lower
from .number_formatter import LOCALE_SEPARATORS, format_number_with_separator
from .roman_numerals import arabian_of_roman, roman_of_arabian
from .string_utils import FORBIDDEN_CHAR, contains_forbidden_char, purge, strip_c

__all__ = [
    'format_number_with_separator',
    'LOCALE_SEPARATORS',
    'name_lower',
    'name_strip',
    'strip_lower',
    'contains_only_ascii',
    'is_normalized_name',
    'strip_c',
    'purge',
    'contains_forbidden_char',
    'FORBIDDEN_CHAR',
    'roman_of_arabian',
    'arabian_of_roman',
    'url_encode',
    'url_decode',
    'extract_param',
    'parse_query_string',
    'extract_all_params',
    'leap_year',
    'nb_days_in_month',
    # Date comparison types
    'Precision',
    'Calendar',
    'Dmy',
    'Dgreg',
    'Dtext',
    'Date',
    # Date comparison functions
    'compare_dmy',
    'compare_dmy_opt',
    'compare_date',
    'NotComparable',
    # HTML utilities
    'escape_html',
    'unescape_html',
]
