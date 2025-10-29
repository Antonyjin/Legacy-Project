# Migration Status

This document tracks the progress of migrating OCaml functions to Python.

## Overview

**Strategy**: Incremental migration using the Strangler Fig pattern. Small, independent utility functions are migrated first, then validated using existing black-box tests (Golden/FT/IT/Python UT).

**Validation**: All migrated functions must pass:
- ✅ Python unit tests (black-box HTTP tests or direct tests)
- ✅ Integration tests (if applicable)
- ✅ Functional tests (if applicable)
- ✅ Golden Master tests (after full migration)

## Completed Migrations

### ✅ MIG-001: Migrate Name.lower (Issue #131)
- **Status**: ✅ Complete
- **Function**: `name_lower(name: str) -> str`
- **OCaml Reference**: `source_geneweb/lib/util/name.ml:36-51`
- **Python Implementation**: `tests/python/utils/name_utils.py`
- **Tests**: 59 unit tests in `tests/python/unit/test_name_processing.py`
- **Coverage**: Name normalization with Unicode transliteration

### ✅ MIG-002: Migrate Name.strip (Issue #132)
- **Status**: ✅ Complete
- **Function**: `name_strip(name: str) -> str`
- **OCaml Reference**: `source_geneweb/lib/util/name.ml:138`
- **Python Implementation**: `tests/python/utils/name_utils.py`
- **Tests**: 40 unit tests in `tests/python/unit/test_name_strip.py`
- **Coverage**: Space removal from names

### ✅ MIG-003: Migrate Number Formatting (Issue #133)
- **Status**: ✅ Complete
- **Function**: `format_number_with_separator(number: int, locale: str) -> str`
- **OCaml Reference**: `source_geneweb/lib/util/mutil.ml` (`string_of_int_sep`)
- **Python Implementation**: `tests/python/utils/number_formatter.py`
- **Tests**: 52 unit tests in `tests/python/unit/test_number_formatting.py`
- **Coverage**: Locale-specific number formatting (e.g., "15,234" in English, "15 234" in French)

### ✅ MIG-004: Migrate HTTP Parameter Parsing (Issue #134)
- **Status**: ✅ Complete
- **Functions**: `url_decode`, `extract_param`, `parse_query_string`, `extract_all_params`
- **OCaml Reference**: `source_geneweb/lib/util/mutil.ml:982-1039` (`decode`, `extract_assoc`)
- **Python Implementation**: `tests/python/utils/http_params.py`
- **Tests**: 42 unit tests (includes decoding) in `tests/python/unit/test_http_param_utils.py`
- **Coverage**: Query parameter parsing, URL decoding, parameter extraction

### ✅ MIG-005: Migrate Date Validation (Issue #135)
- **Status**: ✅ Complete
- **Functions**: `leap_year(year: int) -> bool`, `nb_days_in_month(month: int, year: int) -> int`
- **OCaml Reference**: `source_geneweb/lib/util/date.ml:86-93`
- **Python Implementation**: `tests/python/utils/date_validation.py`
- **Tests**: 23 unit tests in `tests/python/unit/test_date_validation.py`
- **Coverage**: Leap year calculation, days in month validation

### ✅ MIG-006: Migrate Date Comparison (Issue #136)
- **Status**: ✅ Complete
- **Functions**: `compare_dmy_opt`, `compare_dmy`, `compare_date`
- **OCaml Reference**: `source_geneweb/lib/util/date.ml:147-210`
- **Python Implementation**: `tests/python/utils/date_comparison.py`
- **Tests**: Comprehensive date comparison tests
- **Coverage**: Date comparison with precision handling (SURE, ABOUT, MAYBE, BEFORE, AFTER), calendar support

### ✅ MIG-007: Migrate String Utility Functions (Issue #138)
- **Status**: ✅ Complete
- **Functions**: `strip_c`, `purge`, `contains_forbidden_char`
- **OCaml Reference**: `source_geneweb/lib/util/name.ml:138-143`
- **Python Implementation**: `tests/python/utils/string_utils.py`
- **Tests**: 36 unit tests in `tests/python/unit/test_string_utils.py`
- **Coverage**: Character removal, name sanitization, forbidden character validation

### ✅ MIG-008: Migrate Roman Numerals (Issue #137)
- **Status**: ✅ Complete
- **Functions**: `roman_of_arabian`, `arabian_of_roman`
- **OCaml Reference**: `source_geneweb/lib/util/mutil.ml` (`roman_of_arabian`, `arabian_of_roman`)
- **Python Implementation**: `tests/python/utils/roman_numerals.py`
- **Tests**: 60 unit tests in `tests/python/unit/test_roman_numerals.py`
- **Coverage**: Arabic ↔ Roman numeral conversion (1-3999)

### ✅ MIG-009: Migrate URL Encoding Functions (Issue #140)
- **Status**: ✅ Complete
- **Function**: `url_encode(s: str) -> str`
- **OCaml Reference**: `source_geneweb/lib/util/mutil.ml:1041` (`encode`)
- **Python Implementation**: `tests/python/utils/http_params.py`
- **Tests**: 10 encoding tests + 5 roundtrip tests in `tests/python/unit/test_http_param_utils.py`
- **Coverage**: URL encoding for query parameters (spaces → `+`, special chars → `%XX`)

### ✅ MIG-010: Migrate HTML Escaping Functions (Issue #141)
- **Status**: ✅ Complete
- **Functions**: `escape_html`, `unescape_html`
- **OCaml Reference**: Used throughout GeneWeb when printing HTML output
- **Python Implementation**: `tests/python/utils/html_utils.py`
- **Tests**: 10 unit tests in `tests/python/unit/test_html_utils.py`
- **Coverage**: HTML entity escaping/unescaping (XSS prevention, safe rendering)

## Migration Statistics

- **Total Functions Migrated**: 10
- **Total Unit Tests**: 322+ (across all utilities)
- **Test Status**: ✅ All passing
- **Coverage**: High (comprehensive edge cases, OCaml compatibility)

## Next Steps

### Remaining Migration Candidates (Future Work)
- Complex date formatting functions
- GEDCOM parsing/generation
- Database query builders
- Template rendering utilities
- Advanced search algorithms

**Note**: These will be addressed in future migration phases after the foundational utilities are validated in production.

## Validation Strategy

Each migrated function is validated using:

1. **Python Unit Tests**: Direct testing of the Python implementation
2. **Black-box HTTP Tests**: Testing via HTTP requests to `gwd` (for functions exposed via API)
3. **Golden Master Tests**: Comparing OCaml vs Python output (after full feature migration)
4. **Integration Tests**: Validating integration with the rest of the system

## Testing Approach

- **Direct Tests**: For pure functions (e.g., `name_lower`, `roman_of_arabian`)
- **HTTP Tests**: For functions exposed via GeneWeb HTTP API (e.g., date validation, name normalization)
- **Golden Tests**: For full feature validation (currently disabled during migration)

## Documentation

- **Implementation Docs**: `tests/python/utils/README.md`
- **Migration Rationale**: `docs/MIGRATION_FUNCTION_SELECTION.md`
- **Individual Justification**: `docs/WHY_MIGRATE_EACH_FUNCTION.md`

## Related Issues

See GitHub issues with label `migration` for detailed tracking of each migration.

---

**Last Updated**: January 2025  
**Migration Phase**: Foundation utilities (10/10 complete)  
**Next Phase**: Complex algorithms and database operations

