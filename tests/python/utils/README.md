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

## Testing

All utility modules have comprehensive unit tests:

```bash
# Test name utilities
pytest tests/python/unit/test_name_processing.py -v     # name_lower
pytest tests/python/unit/test_name_strip.py -v          # name_strip

# Test number formatter
pytest tests/python/unit/test_number_formatting.py -v

# Test all utils
pytest tests/python/unit/test_name_processing.py tests/python/unit/test_name_strip.py tests/python/unit/test_number_formatting.py -v

# Run with coverage
pytest tests/python/unit/test_name_processing.py tests/python/unit/test_name_strip.py tests/python/unit/test_number_formatting.py --cov=tests/python/utils --cov-report=html
```

**Test Coverage**:

- 59 unit tests for `name_utils.py` (name_lower)
- 40 unit tests for `name_utils.py` (name_strip)
- 52 unit tests for `number_formatter.py`
- **Total: 151 utility tests**

## Usage in Tests

Import utilities in your test files:

````python
# In tests/python/unit/ or tests/python/integration/
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.number_formatter import format_number_with_separator
from utils.name_utils import name_lower, strip_lower

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
```## Implementation Notes

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
