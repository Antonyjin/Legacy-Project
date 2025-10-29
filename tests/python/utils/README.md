# Python Test Utilities

This directory contains utility modules used by the Python test suite.

## Modules

### `name_utils.py`

Implements name processing utilities, replicating the OCaml Name module from GeneWeb.

**Issue**: MIG-001 - Migrate name_lower function

**OCaml References**:

- `source_geneweb/lib/util/name.ml`: `Name.lower` implementation (lines 36-51)
- `source_geneweb/lib/util/name.mli`: Function signatures and documentation

#### Functions

##### `name_lower(name: str) -> str`

Convert name to lowercase with Unicode transliteration.

Replicates OCaml `Name.lower` behavior:

- Uppercase letters → lowercase
- Accents removed (Unicode → ASCII via unidecode)
- Non-alphanumeric characters (except '.') → spaces (stripped)

**Parameters**:

- `name`: The name to process (can contain UTF-8, accents, etc.)

**Returns**: Normalized lowercase name with ASCII characters only

**Examples**:

```python
from utils.name_utils import name_lower

# Basic lowercase
name_lower("MARTIN")              # 'martin'
name_lower("Jean-François")       # 'jean francois'

# Accent removal
name_lower("René")                # 'rene'
name_lower("Müller")              # 'muller'
name_lower("José María")          # 'jose maria'

# Special characters
name_lower("O'Brien")             # 'o brien'
name_lower("Smith.Jr")            # 'smith.jr'  (dot preserved)

# Non-Latin scripts
name_lower("Владимир")            # 'vladimir' (Cyrillic)
name_lower("Αλέξανδρος")          # 'alexandros' (Greek)
```

##### `name_strip(name: str) -> str`

Remove all space characters from a name.

Replicates OCaml `Name.strip` behavior which removes all space characters.

**Issue**: MIG-002 - Migrate name_strip function

**OCaml Reference**: `source_geneweb/lib/util/name.ml:138`

**Parameters**:

- `name`: The name to process

**Returns**: Name with all spaces removed

**Examples**:

```python
from utils.name_utils import name_strip

# Basic space removal
name_strip("Jean François")      # 'JeanFrançois'
name_strip("DE LA CRUZ")         # 'DELACRUZ'

# Compound names
name_strip("Van Der Berg")       # 'VanDerBerg'
name_strip("Da Silva")           # 'DaSilva'

# Multiple spaces
name_strip("  Multiple   Spaces  ")  # 'MultipleSpaces'

# Special cases
name_strip("")                   # ''
name_strip("NoSpaces")           # 'NoSpaces'
name_strip("   ")                # ''
```

**Notes**:

- Only removes space characters (not tabs, newlines, etc.)
- Preserves case and all other characters (unlike `name_lower`)
- Used in GeneWeb name processing pipeline

##### `strip_lower(name: str) -> str`

Equivalent to `strip(lower(name))` - removes all spaces after normalization.

Used in GeneWeb for first comparison of names and surnames.

**Examples**:

```python
from utils.name_utils import strip_lower

strip_lower("Jean-François")     # 'jeanfrancois'
strip_lower("DE LA CRUZ")        # 'delacruz'
strip_lower("O'Brien")           # 'obrien'
```

##### `contains_only_ascii(name: str) -> bool`

Check if name contains only ASCII characters.

##### `is_normalized_name(name: str) -> bool`

Check if a name is already in normalized form (output of name_lower).

#### Supported Scripts

The module handles 33+ languages via `unidecode`:

- **Latin scripts**: French, German, Spanish, Italian, Portuguese, etc.
- **Cyrillic**: Russian, Ukrainian, Bulgarian
- **Greek**: Ancient and Modern Greek
- **Arabic**: Arabic names (transliterated)
- **Other**: Hebrew, Chinese, Japanese, Korean, etc.

### `number_formatter.py`

Implements number formatting with thousands separator support, replicating the OCaml behavior from GeneWeb.

**Issue**: MIG-008 - Migrate number formatting with thousands separator

**OCaml References**:

- `source_geneweb/lib/util/mutil.ml`: `string_of_int_sep` function
- `source_geneweb/lib/allnDisplay.ml`: `format_with_thousand_sep` function
- `GeneWeb/gw/lang/lexicon.txt`: `(thousand separator)` translations

#### Functions

##### `format_number_with_separator(num: int, locale: str = 'en') -> str`

Format an integer with thousands separator according to locale.

**Parameters**:

- `num`: The integer to format
- `locale`: The locale code (e.g., 'fr', 'en', 'de', 'fr_FR', 'en_US'). Defaults to 'en'.

**Returns**: Formatted string with thousands separator

**Examples**:

```python
from utils.number_formatter import format_number_with_separator

# English (comma separator)
format_number_with_separator(1000, 'en')       # '1,000'
format_number_with_separator(1000000, 'en')    # '1,000,000'

# French (space separator)
format_number_with_separator(1000, 'fr')       # '1 000'
format_number_with_separator(1000000, 'fr')    # '1 000 000'

# German (dot separator)
format_number_with_separator(1000, 'de')       # '1.000'
format_number_with_separator(1000000, 'de')    # '1.000.000'

# Locale aliases
format_number_with_separator(5000, 'en_US')    # '5,000'
format_number_with_separator(5000, 'fr_FR')    # '5 000'

# Negative numbers
format_number_with_separator(-1000, 'en')      # '-1,000'

# Small numbers (no separator)
format_number_with_separator(500, 'en')        # '500'
format_number_with_separator(0, 'en')          # '0'
```

##### `get_locale_separator(locale: str = 'en') -> str`

Get the thousands separator for a given locale.

**Parameters**:

- `locale`: The locale code (e.g., 'fr', 'en', 'de')

**Returns**: The thousands separator character(s) for the locale

**Examples**:

```python
from utils.number_formatter import get_locale_separator

get_locale_separator('en')     # ','
get_locale_separator('fr')     # ' '
get_locale_separator('de')     # '.'
get_locale_separator('ru')     # "'"
```

#### Supported Locales

The module supports 33 locales matching GeneWeb's lexicon.txt:

| Locale | Language   | Separator        | Example |
| ------ | ---------- | ---------------- | ------- |
| `en`   | English    | `,` (comma)      | 1,000   |
| `fr`   | French     | ` ` (space)      | 1 000   |
| `de`   | German     | `.` (dot)        | 1.000   |
| `es`   | Spanish    | `.` (dot)        | 1.000   |
| `it`   | Italian    | `.` (dot)        | 1.000   |
| `pt`   | Portuguese | `.` (dot)        | 1.000   |
| `ru`   | Russian    | `'` (apostrophe) | 1'000   |
| `he`   | Hebrew     | `,` (comma)      | 1,000   |
| `tr`   | Turkish    | `,` (comma)      | 1,000   |
| `zh`   | Chinese    | `.` (dot)        | 1.000   |
| ...    | ...        | ...              | ...     |

**Full list**: See `LOCALE_SEPARATORS` in `number_formatter.py`

#### Locale Aliases

For convenience, common locale codes are aliased:

- `en_US`, `en_GB` → `en`
- `fr_FR` → `fr`
- `de_DE` → `de`
- `es_ES` → `es`
- `it_IT` → `it`
- `pt_BR`, `pt_PT` → `pt`
- `zh_CN` → `zh`

### `roman_numerals.py`

Implements Roman numeral conversion utilities, replicating the OCaml behavior from GeneWeb.

**Issue**: MIG-003 - Migrate roman_of_arabian function

**OCaml References**:

- `source_geneweb/lib/util/mutil.ml`: `roman_of_arabian` and `arabian_of_roman` (lines 328-365)
- `source_geneweb/test/util_test.ml`: Roman numeral test cases
- `source_geneweb/lib/dateDisplay.ml`: Usage in date display (line 129)

#### Functions

##### `roman_of_arabian(n: int) -> str`

Convert an integer to Roman numerals.

**Parameters**:

- `n`: The integer to convert (typically 1-3999 for classical Roman notation)

**Returns**: Roman numeral representation

**Examples**:

```python
from utils.roman_numerals import roman_of_arabian

# Basic conversions
roman_of_arabian(1)          # 'I'
roman_of_arabian(4)          # 'IV'
roman_of_arabian(9)          # 'IX'
roman_of_arabian(10)         # 'X'

# OCaml test cases
roman_of_arabian(39)         # 'XXXIX'
roman_of_arabian(246)        # 'CCXLVI'
roman_of_arabian(421)        # 'CDXXI'
roman_of_arabian(160)        # 'CLX'

# Years (genealogy usage)
roman_of_arabian(1789)       # 'MDCCLXXXIX'
roman_of_arabian(1994)       # 'MCMXCIV'
roman_of_arabian(2024)       # 'MMXXIV'

# Boundary cases
roman_of_arabian(0)          # ''
roman_of_arabian(3999)       # 'MMMCMXCIX'
```

**Algorithm**:

The function uses a "build" helper that converts each digit (0-9) using three symbols:

- 0: ""
- 1-3: one, one+one, one+one+one
- 4: one+five (subtractive)
- 5: five
- 6-8: five+one, five+one+one, five+one+one+one
- 9: one+ten (subtractive)

Applied to each position:

- Thousands: M, M, M
- Hundreds: C, D, M
- Tens: X, L, C
- Units: I, V, X

##### `arabian_of_roman(s: str) -> int`

Convert Roman numerals to an integer.

**Parameters**:

- `s`: Roman numeral string (uppercase, e.g., 'XIV', 'MCMXCIV')

**Returns**: Integer value

**Raises**: `ValueError` if the string is not a valid Roman numeral

**Examples**:

```python
from utils.roman_numerals import arabian_of_roman

# Basic conversions
arabian_of_roman('I')        # 1
arabian_of_roman('IV')       # 4
arabian_of_roman('IX')       # 9
arabian_of_roman('X')        # 10

# OCaml test cases
arabian_of_roman('XXXIX')    # 39
arabian_of_roman('CCXLVI')   # 246
arabian_of_roman('CDXXI')    # 421
arabian_of_roman('CLX')      # 160

# Complex numbers
arabian_of_roman('MCMXCIV')  # 1994
arabian_of_roman('MMMCMXCIX')  # 3999

# Invalid input
arabian_of_roman('')         # ValueError
arabian_of_roman('ABC')      # ValueError
```

**Notes**:

- Round-trip conversion works perfectly: `arabian_of_roman(roman_of_arabian(n)) == n`
- Validation ensures the entire string is consumed
- Used in GeneWeb's GEDCOM import for person IDs

#### Usage in GeneWeb

Roman numerals are used for:

- **Year display**: Years 1-3999 shown in Roman numerals (dateDisplay.ml)
- **Template rendering**: `{% roman 1994 %}` → `MCMXCIV` (templ.ml)
- **GEDCOM import**: Person ID parsing (ged2gwb.ml)

**Range check** (from dateDisplay.ml:129):

```ocaml
if y >= 1 && y < 4000 then Mutil.roman_of_arabian y else string_of_int y
```

### `http_params.py`

Implements HTTP query parameter parsing utilities, replicating the OCaml behavior from GeneWeb.

**Issue**: MIG-004 - Migrate HTTP parameter parsing

**OCaml References**:

- `source_geneweb/lib/util/mutil.ml`: `decode` function (lines 982-1039)
- `source_geneweb/bin/gwd/gwd.ml`: `extract_assoc` function (lines 174-180)

#### Functions

##### `url_decode(s: str, strip_spaces: bool = True) -> str`

Decode URL-encoded string with percent encoding and plus-to-space conversion.

**Parameters**:

- `s`: The URL-encoded string to decode
- `strip_spaces`: If True, strip leading/trailing spaces (default: True)

**Returns**: Decoded string

**Examples**:

```python
from utils.http_params import url_decode

# Basic decoding
url_decode("Hello+World")          # 'Hello World'
url_decode("hello%20world")        # 'hello world'

# UTF-8 characters
url_decode("Jean-Fran%C3%A7ois")   # 'Jean-François'
url_decode("M%C3%BCller")          # 'Müller'

# Special characters
url_decode("O%27Brien")            # "O'Brien"
url_decode("100%25")               # "100%"

# Space stripping (default)
url_decode("%20test%20")           # 'test'
url_decode("%20test%20", strip_spaces=False)  # ' test '
```

**Notes**:

- Uses Python's `urllib.parse.unquote_plus` internally
- Matches OCaml `Mutil.decode` behavior exactly
- `strip_spaces=True` replicates OCaml's `strip_heading_and_trailing_spaces`

##### `extract_param(key: str, params: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]`

Extract a parameter from a list of key-value pairs.

**Parameters**:

- `key`: The parameter name to search for
- `params`: List of (key, value) tuples

**Returns**: Tuple of (decoded_value, remaining_params)

**Examples**:

```python
from utils.http_params import extract_param

# Basic extraction
params = [('p', 'jean'), ('n', 'martin'), ('oc', '0')]
value, remaining = extract_param('p', params)
# value = 'jean'
# remaining = [('n', 'martin'), ('oc', '0')]

# With URL encoding
params = [('name', 'Jean+Fran%C3%A7ois')]
value, remaining = extract_param('name', params)
# value = 'Jean François'

# Sequential extraction (OCaml pattern)
params = [('b', 'test'), ('lang', 'fr')]
b, params = extract_param('b', params)
lang, params = extract_param('lang', params)
# b = 'test', lang = 'fr', params = []
```

**Notes**:

- Replicates OCaml `gwd.extract_assoc` behavior
- Returns decoded value (calls `url_decode` internally)
- Only first occurrence extracted (if duplicates exist)
- Returns ("", original_list) if key not found

##### `parse_query_string(query: str) -> List[Tuple[str, str]]`

Parse a query string into a list of (key, value) tuples.

**Parameters**:

- `query`: Query string (e.g., "p=jean&n=martin&oc=0")

**Returns**: List of (key, value) tuples

**Examples**:

```python
from utils.http_params import parse_query_string

# Simple query
parse_query_string("p=jean&n=martin&oc=0")
# [('p', 'jean'), ('n', 'martin'), ('oc', '0')]

# With encoding (values not decoded yet)
parse_query_string("name=John+Doe&age=30")
# [('name', 'John+Doe'), ('age', '30')]
```

##### `extract_all_params(params: List[Tuple[str, str]]) -> dict`

Extract all parameters into a dictionary with decoded values.

**Parameters**:

- `params`: List of (key, value) tuples

**Returns**: Dictionary mapping keys to decoded values

**Examples**:

```python
from utils.http_params import extract_all_params

params = [('p', 'jean'), ('n', 'martin'), ('oc', '0')]
result = extract_all_params(params)
# {'p': 'jean', 'n': 'martin', 'oc': '0'}
```

#### Usage in GeneWeb

HTTP parameter parsing is used for:

- **Person lookup**: `?p=firstname&n=surname&oc=occurrence` (gwd.ml)
- **Base selection**: `let x, env = extract_assoc "b" env in` (gwd.ml:1204)
- **Language selection**: `let lang, env = extract_assoc "lang" env in` (gwd.ml:1233)
- **All query parameter handling** throughout the application

**OCaml Pattern** (from gwd.ml):

```ocaml
let b, env = extract_assoc "b" env in
let w, env = extract_assoc "w" env in
let lang, env = extract_assoc "lang" env in
```

**Python Equivalent**:

```python
b, env = extract_param('b', env)
w, env = extract_param('w', env)
lang, env = extract_param('lang', env)
```

### `date_validation.py`

Implements date validation utilities from the OCaml Date module.

**Issue**: MIG-005 - Migrate date validation

**OCaml References**:

- `source_geneweb/lib/util/date.ml`: Leap year and days-in-month calculations (lines 86-93)
- `source_geneweb/lib/util/date.mli`: Function signatures

#### Functions

##### `leap_year(year: int) -> bool`

Check if a year is a leap year (Gregorian calendar).

Implements the standard Gregorian calendar leap year rules:

- Years divisible by 4 are leap years
- **EXCEPT** years divisible by 100 are NOT leap years
- **EXCEPT** years divisible by 400 ARE leap years

**Parameters**:

- `year`: The year to check (any integer)

**Returns**: True if the year is a leap year, False otherwise

**Examples**:

```python
from utils.date_validation import leap_year

# Regular leap years (divisible by 4)
leap_year(2004)  # True
leap_year(2020)  # True
leap_year(2024)  # True

# Non-leap years
leap_year(2001)  # False
leap_year(2022)  # False
leap_year(2023)  # False

# Century years - special rules
leap_year(1900)  # False (divisible by 100, not 400)
leap_year(2000)  # True  (divisible by 400)
leap_year(2100)  # False (divisible by 100, not 400)
```

**OCaml Reference** (date.ml:86):

```ocaml
let leap_year a = if a mod 100 = 0 then a / 100 mod 4 = 0 else a mod 4 = 0
```

##### `nb_days_in_month(month: int, year: int) -> int`

Return the number of days in a given month and year (Gregorian calendar).

Takes leap years into account for February. Returns 0 for invalid months.

**Parameters**:

- `month`: Month number (1-12, where 1 = January)
- `year`: Year (used for leap year calculation)

**Returns**: Number of days in the month (28-31), or 0 if month is invalid

**Examples**:

```python
from utils.date_validation import nb_days_in_month

# 31-day months
nb_days_in_month(1, 2023)   # 31 (January)
nb_days_in_month(3, 2023)   # 31 (March)
nb_days_in_month(12, 2023)  # 31 (December)

# 30-day months
nb_days_in_month(4, 2023)   # 30 (April)
nb_days_in_month(6, 2023)   # 30 (June)

# February - depends on leap year
nb_days_in_month(2, 2020)   # 29 (leap year)
nb_days_in_month(2, 2021)   # 28 (non-leap)
nb_days_in_month(2, 2000)   # 29 (century leap year)
nb_days_in_month(2, 1900)   # 28 (century non-leap)

# Invalid months
nb_days_in_month(0, 2023)   # 0 (month 0 = unknown in GeneWeb)
nb_days_in_month(13, 2023)  # 0 (invalid month)
```

**OCaml Reference** (date.ml:88-93):

```ocaml
let nb_days_in_month m a =
  if m = 2 && leap_year a then 29
  else if m >= 1 && m <= 12 then
    [| 31; 28; 31; 30; 31; 30; 31; 31; 30; 31; 30; 31 |].(m - 1)
  else 0
```

#### Usage in GeneWeb

Date validation is used for:

- **Date compression**: Validating dates before compression in `Date.compress` (date.ml:15-32)
- **Input validation**: Checking user-entered dates in forms
- **GEDCOM import**: Validating dates during genealogy file imports
- **Calendar boundaries**: Ensuring dates are within valid ranges

**OCaml Pattern** (date.ml usage):

```ocaml
(* Check if date is compressible - requires valid day/month/year *)
let simple =
  match d.prec with
  | Sure | About | Maybe | Before | After ->
      d.day >= 0 && d.month >= 0 && d.year > 0 && d.year < 2500 && d.delta = 0
  | OrYear _ | YearInt _ -> false
```

**Python Equivalent**:

```python
# Validate date before processing
if is_valid_date(day, month, year) and 0 < year < 2500:
    # Process valid date
    max_days = nb_days_in_month(month, year)
    # ...
```

## Testing

All utility modules have comprehensive unit tests:

```bash
# Test name utilities
pytest tests/python/unit/test_name_processing.py -v     # name_lower
pytest tests/python/unit/test_name_strip.py -v          # name_strip

# Test number formatter
pytest tests/python/unit/test_number_formatting.py -v

# Test Roman numerals
pytest tests/python/unit/test_roman_numerals.py -v

# Test HTTP parameters
pytest tests/python/unit/test_http_param_utils.py -v

# Test date validation
pytest tests/python/unit/test_date_validation_utils.py -v

# Test all utils
pytest tests/python/unit/test_name_processing.py tests/python/unit/test_name_strip.py tests/python/unit/test_number_formatting.py tests/python/unit/test_roman_numerals.py tests/python/unit/test_http_param_utils.py tests/python/unit/test_date_validation_utils.py -v

# Run with coverage
pytest tests/python/unit/test_name_processing.py tests/python/unit/test_name_strip.py tests/python/unit/test_number_formatting.py tests/python/unit/test_roman_numerals.py tests/python/unit/test_http_param_utils.py tests/python/unit/test_date_validation_utils.py --cov=tests/python/utils --cov-report=html
```

**Test Coverage**:

- 59 unit tests for `name_utils.py` (name_lower)
- 40 unit tests for `name_utils.py` (name_strip)
- 52 unit tests for `number_formatter.py`
- 60 unit tests for `roman_numerals.py`
- 42 unit tests for `http_params.py`
- 23 unit tests for `date_validation.py`
- **Total: 276 utility tests**

## Usage in Tests

Import utilities in your test files:

````python
# In tests/python/unit/ or tests/python/integration/
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.number_formatter import format_number_with_separator
from utils.name_utils import name_lower, strip_lower
from utils.roman_numerals import roman_of_arabian
from utils.http_params import url_decode, extract_param
from utils.date_validation import leap_year, nb_days_in_month

def test_statistics_count():
    """Test formatting of statistics counts"""
    count = 15234
    formatted_en = format_number_with_separator(count, 'en')
    formatted_fr = format_number_with_separator(count, 'fr')

    assert formatted_en == '15,234'
    assert formatted_fr == '15 234'

def test_name_normalization():
    """Test name normalization for search"""
    # OCaml-compatible name processing
    assert name_lower("Jean-François") == "jean francois"
    assert strip_lower("O'Brien") == "obrien"

def test_year_display():
    """Test Roman numeral year display"""
    # As used in GeneWeb dateDisplay
    year = 1789
    if 1 <= year < 4000:
        assert roman_of_arabian(year) == "MDCCLXXXIX"

def test_query_parsing():
    """Test HTTP parameter parsing"""
    # As used in GeneWeb gwd.ml
    params = [('p', 'Jean+Fran%C3%A7ois'), ('n', 'MARTIN')]
    p, params = extract_param('p', params)
    n, params = extract_param('n', params)
    assert p == "Jean François"
    assert n == "MARTIN"

def test_date_validation():
    """Test date validation"""
    # As used in GeneWeb date processing
    assert leap_year(2000) is True  # Century leap year
    assert leap_year(1900) is False # Century non-leap
    assert nb_days_in_month(2, 2020) == 29  # Feb in leap year
    assert nb_days_in_month(2, 2021) == 28  # Feb in non-leap
```
    if 1 <= year < 4000:
        assert roman_of_arabian(year) == "MDCCLXXXIX"

def test_query_parsing():
    """Test HTTP parameter parsing"""
    # As used in GeneWeb gwd.ml
    params = [('p', 'Jean+Fran%C3%A7ois'), ('n', 'MARTIN')]
    p, params = extract_param('p', params)
    n, params = extract_param('n', params)
    assert p == "Jean François"
    assert n == "MARTIN"
```

### `date_comparison.py`

Implements date comparison functions with precision handling, replicating the OCaml Date module from GeneWeb.

**Issue**: MIG-006 - Migrate date comparison functions

**OCaml References**:
- `source_geneweb/lib/util/date.ml`: `compare_dmy_opt`, `compare_dmy`, `compare_date` (lines 147-210)
- `source_geneweb/lib/util/date.mli`: Public API signatures
- `source_geneweb/lib/def/adef.ml`: Type definitions (dmy, date, precision, calendar)

#### Types

##### `Precision` (Enum)

Date precision levels:
- `SURE`: Exact date known
- `ABOUT`: Approximate date (~)
- `MAYBE`: Uncertain date (?)
- `BEFORE`: Date is before the value (<)
- `AFTER`: Date is after the value (>)

**Note**: `OrYear` and `YearInt` (complex year ranges) are **not migrated** (rarely used, high complexity).

##### `Calendar` (Enum)

Calendar types:
- `GREGORIAN`: Gregorian calendar (default)
- `JULIAN`: Julian calendar
- `FRENCH`: French Republican calendar
- `HEBREW`: Hebrew calendar

##### `Dmy` (frozen dataclass)

Date structure with day, month, year components.

**Fields**:
- `day: int` - Day of month (0 = unknown)
- `month: int` - Month (0 = unknown, 1-12)
- `year: int` - Year (negative for BCE)
- `prec: Precision` - Precision level
- `delta: int` - Delta value (for year ranges)

**Example**:
```python
from utils.date_comparison import Dmy, Precision

# June 15, 1990 (exact)
d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)

# Unknown day in 1990 (before)
d2 = Dmy(day=0, month=0, year=1990, prec=Precision.BEFORE, delta=0)
```

##### `Dgreg` (frozen dataclass)

Gregorian date with calendar type.

**Fields**:
- `dmy: Dmy` - Date structure
- `calendar: Calendar` - Calendar type

##### `Dtext` (frozen dataclass)

Text-based date (unparsed string).

**Fields**:
- `text: str` - Date as text (e.g., "circa 1990")

##### `Date` (Union)

Union type: `Date = Union[Dgreg, Dtext]`

#### Functions

##### `compare_dmy_opt(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> Optional[int]`

Compare two dmy structures, return None if not comparable.

**OCaml**: `date.ml:147` (`compare_dmy_opt`)

**Parameters**:
- `dmy1`: First date structure
- `dmy2`: Second date structure
- `strict`: If True, consider precision (may return None). If False, compare as points on timeline.

**Returns**:
- `-1` if dmy1 < dmy2
- `0` if dmy1 == dmy2
- `1` if dmy1 > dmy2
- `None` if not comparable (strict mode only)

**Behavior**:
1. Compare years first
2. If years equal, compare months (0 = unknown)
3. If months equal, compare days (0 = unknown)
4. If all equal, compare precisions
5. Unknown values (0) handled with precision rules (BEFORE, AFTER)
6. Strict mode invalidates comparisons when precisions conflict

**Examples**:
```python
from utils.date_comparison import Dmy, Precision, compare_dmy_opt

# Basic comparison
d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
d2 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
compare_dmy_opt(d1, d2)  # -1 (1990 < 2000)

# Unknown month with precision
d1 = Dmy(day=1, month=0, year=1990, prec=Precision.AFTER, delta=0)
d2 = Dmy(day=1, month=6, year=1990, prec=Precision.SURE, delta=0)
compare_dmy_opt(d1, d2)  # 1 (AFTER means later)

# Strict mode invalidates comparison
d1 = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)
d2 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
compare_dmy_opt(d1, d2, strict=True)  # None (AFTER invalidates <)
```

##### `compare_dmy(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> int`

Compare two dmy structures, raise NotComparable if not comparable.

**OCaml**: `date.ml:199` (`compare_dmy`)

**Parameters**: Same as `compare_dmy_opt`

**Returns**: Same as `compare_dmy_opt` (but never None)

**Raises**: `NotComparable` if dates cannot be compared in strict mode

**Example**:
```python
from utils.date_comparison import Dmy, Precision, compare_dmy, NotComparable

d1 = Dmy(day=0, month=6, year=1990, prec=Precision.SURE, delta=0)
d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)

try:
    result = compare_dmy(d1, d2, strict=True)
except NotComparable as e:
    print(f"Cannot compare: {e}")
```

##### `compare_date(d1: Date, d2: Date, strict: bool = False) -> int`

Compare two date structures (Dgreg or Dtext).

**OCaml**: `date.ml:204` (`compare_date`)

**Parameters**:
- `d1`: First date (Dgreg or Dtext)
- `d2`: Second date (Dgreg or Dtext)
- `strict`: If True, Dtext comparisons raise NotComparable

**Returns**: Same as `compare_dmy`

**Raises**: `NotComparable` if strict mode and Dtext involved

**Behavior**:
- `Dgreg` vs `Dgreg`: Compare using `compare_dmy`
- `Dgreg` vs `Dtext`: Dgreg > Dtext (non-strict), NotComparable (strict)
- `Dtext` vs `Dtext`: Equal (non-strict), NotComparable (strict)

**Example**:
```python
from utils.date_comparison import Dmy, Dgreg, Dtext, Calendar, Precision, compare_date

dmy = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
d1 = Dgreg(dmy=dmy, calendar=Calendar.GREGORIAN)
d2 = Dtext(text="circa 1990")

compare_date(d1, d2, strict=False)  # 1 (Dgreg > Dtext)
# compare_date(d1, d2, strict=True)  # Raises NotComparable
```

#### Exception

##### `NotComparable`

Exception raised when dates cannot be compared in strict mode.

**OCaml**: `date.ml:197` (`exception Not_comparable`)

**Example**:
```python
from utils.date_comparison import NotComparable, compare_dmy

try:
    result = compare_dmy(dmy1, dmy2, strict=True)
except NotComparable as e:
    print(f"Comparison failed: {e}")
```

## Implementation Notes

### Name Processing (name_utils.py)

#### OCaml Compatibility

The Python implementation replicates the OCaml `Name.lower` behavior:

1. **Character processing**:
   - ASCII alphanumeric and dots: preserved (lowercased)
   - Other ASCII characters: become spaces
   - UTF-8 characters: transliterated via `unidecode` library

2. **Space handling**:
   - Multiple spaces collapsed to single space
   - Leading/trailing spaces stripped
   - Special characters between words → single space

3. **Dot preservation**: The dot '.' character is preserved for suffixes (Jr., Sr., etc.)

#### Algorithm

From OCaml `source_geneweb/lib/util/name.ml`:

```ocaml
let lower s =
  let rec copy special i len =
    if i = String.length s then Buff.get len
    else if Char.code s.[i] < 0x80 then
      match s.[i] with
      | ('a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '.') as c ->
          let len = if special then Buff.store len ' ' else len in
          let c = Char.lowercase_ascii c in
          copy false (i + 1) (Buff.store len c)
      | _ -> copy (len <> 0) (i + 1) len
    else
      let len = if special then Buff.store len ' ' else len in
      let t, j = unaccent_utf_8 true s i in
      copy false j (Buff.mstore len t)
  in
  copy false 0 0
````

Python equivalent uses `unidecode` for UTF-8 transliteration.

### Number Formatting (number_formatter.py)

#### OCaml Compatibility

The Python implementation replicates the OCaml behavior from `Mutil.string_of_int_sep`:

1. **Separator placement**: Every 3 digits from right to left
2. **Small numbers**: Numbers < 1000 have no separator
3. **Negative numbers**: Sign is preserved before the number
4. **Locale-specific**: Separator varies by locale (matching lexicon.txt)

### Algorithm

The formatting algorithm mirrors the OCaml logic:

```ocaml
(* OCaml: source_geneweb/lib/util/mutil.ml *)
let string_of_int_sep sep x =
  (* ... *)
  if i < len - 1 && (len - 1 - i) mod 3 = 0 then (
    String.blit sep 0 s (j + 1) slen;
    (i + 1, j + 1 + slen))
  (* ... *)
```

```python
# Python: tests/python/utils/number_formatter.py
for i, digit in enumerate(reversed(num_str)):
    if i > 0 and i % 3 == 0:
        result.append(separator)
    result.append(digit)
```

Both insert separators when `(position from right) mod 3 = 0`.

## Contributing

When adding new utility modules:

1. Create the module in `tests/python/utils/`
2. Add comprehensive unit tests in `tests/python/unit/test_<module_name>.py`
3. Export public API in `tests/python/utils/__init__.py`
4. Document in this README
5. Reference relevant OCaml code if applicable

## Related Documentation

- [Unit Test README](../unit/README.md) - Unit testing strategy
- [Integration Test README](../integration/README.md) - Integration testing guide
- [Test Policy](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Policy) - Overall QA strategy
