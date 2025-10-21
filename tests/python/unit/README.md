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

| Approach | Pros | Cons |
|----------|------|------|
| **HTTP Testing (our choice)** | ✅ No OCaml code changes<br>✅ Tests survive migration<br>✅ Black-box validation | ⚠️ Requires running `gwd`<br>⚠️ Indirect (via HTTP) |
| **OCaml Unit Tests** | ✅ Direct testing<br>✅ Fast | ❌ Requires OCaml expertise<br>❌ Discarded after migration<br>❌ Modifies legacy code |

## Test Structure

### UT-PY-002: HTTP Parameter Parsing

**What we test**: OCaml's HTTP parameter parsing logic (see `source_geneweb/bin/gwd/request.ml`)

**Why these routes**:

```python
# Basic person lookup - tests p= and n= parameters
?p=Charles&n=Windsor
→ Tests: request.ml::person_is_std_key, gwd.ml::extract_assoc

# URL encoding - tests Mutil.decode
?p=René&n=Dupont  
→ Tests: Mutil.decode, UTF-8 handling

# Language selection - tests lang= parameter
?lang=fr
→ Tests: Language fallback logic, i18n system

# Search mode - tests m= parameter
?m=S&s=Windsor
→ Tests: Mode parsing, Name.lower (case-insensitive search)

# Empty/missing params - tests edge cases
?p=&n=Windsor
→ Tests: Graceful handling of malformed input
```

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

## OCaml Code Reference

The tests validate behaviors implemented in:

```
source_geneweb/
├── bin/gwd/
│   ├── gwd.ml              # extract_assoc, parse_digest
│   └── request.ml          # person_is_std_key, make_henv
├── lib/util/
│   ├── mutil.mli           # decode, normalize_utf_8
│   └── name.mli            # lower, crush_lower, strip
```

### Key OCaml Functions Tested (Indirectly)

| Test | OCaml Function | File |
|------|---------------|------|
| `test_parse_person_params` | `extract_assoc` | `gwd.ml:140-147` |
| `test_url_encoded_space` | `Mutil.decode` | `util.ml:150` |
| `test_lowercase_search` | `Name.lower` | `name.ml:80` |
| `test_lang_fr` | `Util.p_getenv` | `util.ml:200` |
| `test_hyphenated_surname` | `Name.strip` | `name.ml:120` |

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

