# Python Unit Tests

## Overview

Python Unit Tests validate **OCaml's core behaviors** in isolation through **black-box HTTP testing**. These tests establish the "contract" that our Python migration must honor.

## Why HTTP Testing for Unit Tests?

### Decision Rationale

We chose **HTTP-based black-box testing** instead of OCaml unit tests because:

1. **No OCaml source modification needed** - Tests run against compiled binaries
2. **Migration validation ready** - Same tests will validate Python migration
3. **Clean separation** - Tests don't depend on OCaml internals
4. **Deterministic** - HTTP responses are reproducible and testable
5. **Future-proof** - When OCaml is replaced, tests continue to work

### Trade-offs

| Approach                      | Pros                                                                              | Cons                                                                                   |
| ----------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **HTTP Testing (our choice)** | ✅ No OCaml code changes<br>✅ Tests survive migration<br>✅ Black-box validation | ⚠️ Requires running `gwd`<br>⚠️ Indirect (via HTTP)                                    |
| **OCaml Unit Tests**          | ✅ Direct testing<br>✅ Fast                                                      | ❌ Requires OCaml expertise<br>❌ Discarded after migration<br>❌ Modifies legacy code |

## Test Structure

### UT-PY-002: HTTP Parameter Parsing

**File**: test_http_params.py | **Status**: ✅ Complete | **Issue**: #98

Tests HTTP parameter parsing, URL encoding, special characters, and edge cases.

- 25 test methods validating parameter extraction and decoding
- OCaml functions: `gwd.ml::extract_assoc`, `Mutil.decode`, `request.ml::person_is_std_key`

### UT-PY-003: Name Normalization

**File**: test_name_normalization.py | **Status**: ✅ Complete | **Issue**: #99

Tests name search case-insensitivity, display formatting, and special character handling.

- 6 test methods validating name normalization
- OCaml functions: `Name.lower`, `Name.crush_lower`, name display formatting

### UT-PY-004: Date Validation

**File**: test_date_validation.py | **Status**: ✅ Complete | **Issue**: #100

Tests date validation, calendar types, date boundaries, and compression logic.

- 26 test methods across 6 test classes
- OCaml functions: `Date.compress`, `Date.uncompress`, date validation (lib/util/date.ml)
- Tests: Gregorian/Julian/French/Hebrew calendars, BCE dates, year < 2500 boundary

### UT-PY-005: URL Parsing

**File**: test_url_parsing_extended.py | **PR**: #190 | **Issue**: #162

Tests URL encoding/decoding, UTF-8 handling, parameter extraction, and edge cases.

- 35 test methods across 7 test classes
- OCaml functions: `gwd.ml::extract_assoc`, `Mutil.ml::decode`, `Mutil.ml::iso_8859_1_of_utf_8`

### UT-PY-005: Date Formatting

**File**: test_date_formatting.py | **PR**: #191 | **Issue**: #163

Tests date display formats, age calculation, and date localization.

- 13 test methods across 5 test classes
- OCaml functions: `Mutil.date_of_string`, date display formatting, age calculation

### UT-PY-006: String Utils

**File**: test_string_utils.py | **PR**: #192 | **Issue**: #164

Tests string normalization, special character handling, and name transformations.

- 15 test methods across 5 test classes
- OCaml functions: `Name.lower`, `Name.strip`, `Mutil.normalize`, string utilities

### UT-PY-007: GEDCOM Parsing

**File**: test_gedcom_parsing.py | **PR**: #193 | **Issue**: #165

Tests GEDCOM export format, person/family structure, and event handling.

- 17 test methods across 5 test classes
- OCaml functions: GEDCOM export, event formatting, relationship linking

### UT-PY-008: Privacy & Access Control

**File**: test_privacy.py | **PR**: #194 | **Issue**: #166

Tests privacy mechanisms, access restrictions, and record visibility.

- 15 test methods across 5 test classes
- OCaml functions: privacy flags, access control, record filtering

### UT-PY-009: Database Configuration

**File**: test_base_config.py | **PR**: #195 | **Issue**: #167

Tests database metadata, configuration settings, and statistics.

- 15 test methods across 5 test classes
- OCaml functions: database info, configuration, statistics retrieval

### UT-PY-010: Localization & i18n

**File**: test_localization.py | **PR**: #196 | **Issue**: #168

Tests language switching, translations, and internationalization.

- 16 test methods across 5 test classes
- OCaml functions: language selection, message translation, date/UI localization

### UT-PY-011: Number Formatting

**File**: test_number_formatting.py | **Status**: ✅ Complete | **Issue**: MIG-008

Tests number formatting with thousands separator across 33 locales.

- 52 test methods across 10 test classes
- OCaml functions: `Mutil.string_of_int_sep`, `format_with_thousand_sep` (allnDisplay.ml)
- Locales: en (,), fr ( ), de (.), ru ('), and 29 others from lexicon.txt
- Tests: basic formatting, locale-specific separators, negative numbers, large numbers, edge cases

### UT-PY-012: Name Processing

**File**: test_name_processing.py | **Status**: ✅ Complete | **Issue**: MIG-001

Tests name normalization and lowercase conversion with Unicode transliteration.

- 59 test methods across 11 test classes
- OCaml functions: `Name.lower`, `Name.strip_lower` (name.ml:36-51)
- Transliteration: `unidecode` library for UTF-8 → ASCII conversion
- Tests: accent removal, non-Latin scripts (Cyrillic, Greek, Arabic), special characters, space normalization, real-world names

---

## How Unit Tests Map to OCaml Functions

### Why We Test These Specific Behaviors

#### 1. **Parameter Parsing** (`?p=X&n=Y`)

- **OCaml Function**: `gwd.ml::extract_assoc`, `request.ml::person_is_std_key`
- **Migration Impact**: Python must parse query strings identically
- **Risk**: Different parsing = broken person lookups = critical failure

#### 2. **URL Encoding** (`René`, `O'Brien`)

- **OCaml Function**: `Mutil.decode`, `Mutil.iso_8859_1_of_utf_8`
- **Migration Impact**: Python must handle UTF-8, Latin-1, and percent encoding
- **Risk**: Name encoding bugs = data corruption

#### 3. **Case Insensitivity** (`WINDSOR` = `windsor`)

- **OCaml Function**: `Name.lower`, `Name.crush_lower`
- **Migration Impact**: Python search must match OCaml's normalization
- **Risk**: Search breaks for users

#### 4. **Language Selection** (`?lang=fr`)

- **OCaml Function**: `Util.p_getenv`, language fallback logic
- **Migration Impact**: Python must support same i18n mechanism
- **Risk**: UI breaks for non-English users

#### 5. **Edge Cases** (empty params, long strings, special chars)

- **OCaml Behavior**: Graceful degradation, no crashes
- **Migration Impact**: Python must be equally robust
- **Risk**: Crashes, security vulnerabilities

#### 6. **Number Formatting** (`1000` → `1,000` / `1 000` / `1.000`)

- **OCaml Function**: `Mutil.string_of_int_sep`, `transl conf "(thousand separator)"`
- **Migration Impact**: Python must format numbers with locale-specific separators
- **Risk**: Wrong separators = poor UX for international users, inconsistent statistics display
- **Locales**: 33 languages with different separators (comma, space, dot, apostrophe)

#### 7. **Name Normalization** (`Jean-François` → `jean francois`)

- **OCaml Function**: `Name.lower`, `Name.strip_lower` (name.ml)
- **Migration Impact**: Python must normalize names identically for search/comparison
- **Risk**: Search breaks, duplicate person detection fails, name matching incorrect
- **Coverage**: French accents, German umlauts, Cyrillic, Greek, Arabic, special chars (hyphens, apostrophes)

## OCaml Code Reference

The tests validate behaviors implemented in:

```
source_geneweb/
├── bin/gwd/
│   ├── gwd.ml              # extract_assoc, parse_digest
│   └── request.ml          # person_is_std_key, make_henv
├── lib/
│   ├── allnDisplay.ml      # format_with_thousand_sep
│   └── util/
│       ├── mutil.ml        # string_of_int_sep, decode, normalize_utf_8
│       ├── name.ml         # lower, strip_lower, crush_lower, strip
│       ├── name.mli        # Function signatures
│       └── date.ml         # compress, uncompress
└── GeneWeb/gw/lang/
    └── lexicon.txt         # (thousand separator) translations
```

### Key OCaml Functions Tested (Indirectly)

| Test                                  | OCaml Function             | File                        |
| ------------------------------------- | -------------------------- | --------------------------- |
| `test_parse_person_params`            | `extract_assoc`            | `gwd.ml:140-147`            |
| `test_url_encoded_space`              | `Mutil.decode`             | `util.ml:150`               |
| `test_lowercase_search`               | `Name.lower`               | `name.ml:80`                |
| `test_compressible_date_works`        | `Date.compress`            | `lib/util/date.ml:15-32`    |
| `test_year_boundary_2500`             | `Date.compress`            | `lib/util/date.ml:19`       |
| `test_lang_fr`                        | `Util.p_getenv`            | `util.ml:200`               |
| `test_hyphenated_surname`             | `Name.strip`               | `name.ml:120`               |
| `test_format_one_thousand_english`    | `Mutil.string_of_int_sep`  | `lib/util/mutil.ml:576-599` |
| `test_french_space_separator`         | `format_with_thousand_sep` | `lib/allnDisplay.ml:21-22`  |
| `test_french_accents`                 | `Name.lower`               | `lib/util/name.ml:36-51`    |
| `test_strip_lower_with_special_chars` | `Name.strip_lower`         | `lib/util/name.mli`         |

## Running the Tests

### Prerequisites

1. **Start GeneWeb**:

   ```bash
   cd GeneWeb
   ./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
   ```

2. **Run tests**:

   ```bash
   # All unit tests
   pytest tests/python/unit/ -v

   # Just HTTP param tests
   pytest tests/python/unit/test_http_params.py -v

   # Specific test class
   pytest tests/python/unit/test_http_params.py::TestBasicParameterParsing -v
   ```

### Environment Variables

Tests use deterministic settings (see `conftest.py`):

```bash
export LC_ALL=C.UTF-8   # Consistent locale
export TZ=UTC           # Consistent timezone
```

## Success Criteria

✅ **All tests pass** against OCaml GeneWeb  
✅ **Tests are deterministic** (no flaky tests)  
✅ **Fast execution** (<1s per test file)  
✅ **Clear failure messages** (easy debugging)

## Related Documentation

- **Test Policy**: `wiki/03-Quality-Test-Policy.md`
- **ADR-004**: Python Testing Strategy (`wiki/06-Governance-ADR-004-Python-Testing.md`)
- **CI Workflow**: `.github/workflows/ci.yml`
- **Integration Tests**: `tests/python/integration/README.md`

## Questions?

**Q: Why not test OCaml functions directly?**  
A: We're migrating to Python, so OCaml-specific tests would be discarded. HTTP tests survive the migration.

**Q: Why test via HTTP if it's "unit" testing?**  
A: "Unit" means testing isolated behaviors (not implementation). HTTP is just the interface.

**Q: What if a test fails after migration?**  
A: That's the point! It means the Python version broke the contract. Fix the Python code.

**Q: Are these really unit tests or integration tests?**  
A: They're **behavioral unit tests** - validating specific behaviors in isolation, accessed via HTTP.
