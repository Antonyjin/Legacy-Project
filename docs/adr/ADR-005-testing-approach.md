# ADR-005: Testing Approach

**Status**: Accepted  
**Date**: 2025-10-31  
**Deciders**: Antonyjin  
**Consequences**: Determines test coverage strategy and CI/CD validation

## Context

To ensure safe migration from OCaml to Python, we need a comprehensive testing strategy that:

1. Validates migrated code produces identical output to OCaml
2. Detects regressions early in development
3. Prevents breaking changes in CI/CD pipeline
4. Provides confidence for production deployment

## Problem

- How do we validate Python implementations match OCaml behavior exactly?
- What types of tests are needed for different components?
- How do we prevent regression during development?
- What's the minimum acceptable test coverage?

## Decision

We implement a **four-tier testing strategy** with clear purposes and CI blocking rules:

### Tier 1: Unit Tests (Black-Box Testing)

**Purpose**: Test individual functions against OCaml golden references

**Approach**:
- Treat OCaml as black box (don't read OCaml source)
- Test via HTTP API calls to gwd server
- Compare Python output to OCaml output
- Focus on input/output validation

**Example**:
```python
def test_name_lower():
    """Test name_lower matches OCaml behavior"""
    ocaml_result = call_gwd_function('name_lower', 'JOHN')
    python_result = call_python_function('name_lower', 'JOHN')
    assert ocaml_result == python_result
```

**Coverage Target**: >85% of code  
**CI Status**: ✅ **BLOCKING** - Failure blocks PR merge

### Tier 2: Integration Tests

**Purpose**: Test multi-component workflows and interactions

**Approach**:
- Test complete workflows (import → validate → export)
- Test concurrent operations
- Test database operations
- Test edge cases and error handling

**Example**:
```python
def test_gedcom_roundtrip():
    """Test import → validate → export produces valid GEDCOM"""
    # Import GEDCOM
    import_result = import_gedcom('input.ged')
    
    # Validate data
    validation = validate_imported_data(import_result)
    assert validation.errors == []
    
    # Export and verify
    export_result = export_to_gedcom(import_result)
    assert gedcom_valid(export_result)
```

**Coverage Target**: Key workflows  
**CI Status**: ✅ **BLOCKING** - Failure blocks PR merge

### Tier 3: Golden Master Tests

**Purpose**: Detect regressions by comparing against known-good output

**Approach**:
- Run OCaml with test inputs, save output as "golden"
- Run Python with same inputs, compare output
- Detect any differences (regressions)
- Update goldens when changes are intentional

**Example**:
```bash
# Generate golden (once)
./scripts/golden/run_golden.sh create

# Validate against golden
./scripts/golden/run_golden.sh validate
# Fails if any output differs from golden
```

**What's Tested**:
- GEDCOM export format and completeness
- HTML page rendering (10 page types)
- Data normalization (timestamps, IDs, etc.)
- Search results consistency

**CI Status**: ✅ **Non-blocking currently** (will enable in Phase 2)

### Tier 4: Smoke Tests

**Purpose**: Quick validation that system is working

**Approach**:
- Basic API connectivity tests
- Health checks (liveness, readiness)
- Database accessibility
- Core functionality still works

**Example**:
```bash
# Quick smoke test
curl http://localhost:2317/health
curl http://localhost:2317/test?p=Charles&n=Windsor
```

**CI Status**: ✅ **BLOCKING** - Failure indicates deployment issue

## Test Coverage Requirements

| Test Type | Coverage | Status |
|-----------|----------|--------|
| Unit Tests | >85% | ✅ ENFORCED |
| Integration Tests | Key workflows | ✅ REQUIRED |
| Golden Tests | 12 page types | ⏳ Phase 2 |
| Smoke Tests | Happy path | ✅ REQUIRED |

## Test Organization

```
tests/
├── python/
│   ├── unit/                    # 191 unit tests
│   │   ├── test_name_lower.py
│   │   ├── test_date_validate.py
│   │   └── conftest.py         # Shared fixtures
│   ├── integration/             # 87 integration tests
│   │   ├── test_gedcom_import.py
│   │   └── test_database_ops.py
│   └── functional/              # Functional workflows
│       └── test_user_workflows.py
├── golden/                      # Golden master tests
│   ├── run_golden.sh           # Test harness
│   └── goldens/v1/             # Golden outputs
│       ├── name_lower.golden
│       └── date_validate.golden
└── conftest.py                 # Project-wide fixtures
```

## CI/CD Integration

### CI Pipeline Rules
```yaml
# .github/workflows/ci.yml
- Unit tests MUST pass (blocks merge)
- Integration tests MUST pass (blocks merge)
- Golden tests NOT required yet (informational)
- Coverage report generated (target >80%)
```

### Running Tests Locally
```bash
# All tests
pytest tests/ -v

# Specific suite
pytest tests/python/unit/ -v

# With coverage
pytest tests/ --cov=python_app --cov-report=html

# Run and stop on first failure
pytest -x tests/
```

## Test Data

### Minimal Test Database
- `test.gwb` - British Royal Family (188 persons)
- Used for unit and integration tests
- Covers various data types and relationships

### Golden References
- Created once, committed to repo
- Updated only when intentional behavior changes
- Validated in each test run

## Consequences

### Positive
- ✅ High confidence in migrated code correctness
- ✅ Early detection of regressions
- ✅ Clear validation criteria
- ✅ Enables safe gradual rollout
- ✅ Team can contribute without OCaml knowledge

### Negative
- ❌ High upfront testing work (191 tests written)
- ❌ Tests must be maintained alongside code
- ❌ Slower CI/CD pipeline (tests take time)
- ❌ Duplicate code in OCaml and Python

## Phases

### Phase 1 (Current)
- Unit tests blocking CI
- Integration tests blocking CI
- Golden tests informational
- Coverage tracked but not enforced

### Phase 2 (Month 2)
- Golden tests blocking CI
- Coverage threshold enforced (>80%)
- Performance benchmarks added

### Phase 3 (Month 3+)
- Extended coverage targets (>90%)
- Security testing
- Performance regression detection

## Related Decisions

- **ADR-004**: Migration strategy (black-box testing)
- **ADR-006**: Deployment platform
- **ADR-007**: CI/CD design

## References

- Pytest Documentation: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/
- Golden Master Pattern: https://en.wikipedia.org/wiki/Golden_master_testing
