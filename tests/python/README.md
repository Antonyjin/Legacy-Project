# GeneWeb Python Tests

Python test suite for GeneWeb (OCaml) with migration validation strategy.

## 📁 Directory Structure

```
tests/python/
├── unit/                    # Unit tests (UT-PY-001 to 010)
│   ├── test_name_normalization.py
│   ├── test_url_parsing.py
│   ├── test_date_formatting.py
│   └── ...
├── integration/             # Integration tests (IT-PY-001 to 010)
│   ├── test_http_api.py
│   ├── test_database_access.py
│   └── ...
├── functional/              # Functional tests (FT-PY-001 to 010)
│   ├── test_tree_navigation.py
│   ├── test_person_search.py
│   └── ...
├── conftest.py             # Shared fixtures
├── pytest.log              # Test execution log
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start GeneWeb daemon:**
```bash
cd GeneWeb
./gwd.sh
```

3. **Verify test database is accessible:**
```bash
curl http://localhost:23179/test
```

### Running Tests

**All tests:**
```bash
pytest tests/python/ -v
```

**By category:**
```bash
pytest tests/python/unit/ -v           # Unit tests only
pytest tests/python/integration/ -v    # Integration tests only
pytest tests/python/functional/ -v     # Functional tests only
```

**Specific test file:**
```bash
pytest tests/python/unit/test_name_normalization.py -v
```

**With coverage:**
```bash
pytest tests/python/ --cov=tests/python --cov-report=html
```

**Parallel execution (faster):**
```bash
pytest tests/python/ -n auto
```

**Stop on first failure:**
```bash
pytest tests/python/ -x
```

## 🏷️ Test Markers

Tests are marked for easy filtering:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests (requires gwd)
pytest -m integration

# Run only functional tests
pytest -m functional

# Skip slow tests
pytest -m "not slow"
```

## 📊 Coverage

Generate coverage report:
```bash
pytest tests/python/ --cov=tests/python --cov-report=html
open tests/python/htmlcov/index.html
```

**Target:** >80% coverage

## 🧪 Test Strategy

### Unit Tests (UT)
- **Goal:** Test OCaml functions via HTTP API (black-box)
- **Speed:** Fast (<30s total)
- **Dependencies:** gwd daemon
- **Coverage:** Core functions (Name, Date, URL parsing, etc.)

### Integration Tests (IT)
- **Goal:** Test component interactions
- **Speed:** Medium (<60s total)
- **Dependencies:** gwd daemon + test database
- **Coverage:** HTTP API, Database, Templates, Logging

### Functional Tests (FT)
- **Goal:** End-to-end user workflows
- **Speed:** Slower (<120s total)
- **Dependencies:** Full system
- **Coverage:** Navigation, Search, GEDCOM, Privacy, etc.

## 🔧 Determinism

Tests require deterministic environment:

```bash
export LC_ALL=C.UTF-8
export TZ=UTC
```

## 🎯 Migration Validation

These tests validate OCaml **NOW** and Python **LATER**:

1. **Before Migration:** Tests pass against OCaml ✅
2. **During Migration:** Run tests against Python version
3. **Validation:** If tests pass → Migration successful! ✅

## 📝 Writing Tests

### Example Unit Test

```python
# tests/python/unit/test_example.py
import pytest
import requests

BASE_URL = "http://localhost:23179/test"

@pytest.mark.unit
@pytest.mark.requires_gwd
def test_person_access():
    """Test person page is accessible"""
    response = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
    assert response.status_code == 200
    assert "Charles" in response.text
```

### Test Naming Convention

- File: `test_<feature>.py`
- Class: `Test<Feature>`
- Function: `test_<specific_behavior>`

### Docstrings

Every test should have:
- **What** is being tested
- **Why** it's tested this way
- **OCaml source reference** (for unit tests)

## 🐛 Troubleshooting

### "gwd not running"
```bash
cd GeneWeb
./gwd.sh
```

### "Connection refused"
Check if port 23179 is in use:
```bash
lsof -i :23179
```

### "Database not found"
Verify test database exists:
```bash
ls -la GeneWeb/bases/test.gwb/
```

### Tests hanging
Set timeout:
```bash
pytest tests/python/ --timeout=30
```

## 📚 Related Documentation

- **Test Policy:** `wiki/03-Quality-Test-Policy.md`
- **Test Protocols:** `wiki/03-Quality-Test-Protocols.md`
- **ADR-004:** `wiki/06-Governance-ADR-004-Python-Testing.md`

## 🎯 Success Metrics

- ✅ All tests pass consistently (100% pass rate)
- ✅ Coverage >80%
- ✅ Tests complete in <3 minutes total
- ✅ Tests are isolated and order-independent
- ✅ CI integration successful

