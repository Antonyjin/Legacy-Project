# CI/CD Workflow Guide

## 📋 Overview

**Platform**: GitHub Actions (free unlimited minutes on public repos)  
**Runner**: ubuntu-latest  
**Location**: `.github/workflows/ci.yml`  
**Triggers**: Push to main/master, Pull Requests, Manual dispatch

---

## 🔄 How CI Works

### Current Workflow Steps

1. **Setup**
   - Checkout code
   - Install Python 3.11
   - Install dependencies from `requirements.txt`
   - Make executables executable

2. **OCaml/GeneWeb Smoke**
   - Start `gwd`, verify HTTP 200, check home page, person page, French localization
   - GEDCOM export: verify file exists and has content
   - Golden tests: optional (see Golden Tests section)

3. **Python Tests**
   - Infrastructure: Verify pytest setup (✅ BLOCKS CI)
   - Unit tests: OCaml behavior via HTTP/Python utils (✅ BLOCKS CI)
   - Integration tests: Component interactions (✅ BLOCKS CI)
   - Functional tests: End-to-end workflows (⚠️ allowed to fail during development)
   - Coverage report: Generated; threshold may not be enforced

4. **Artifacts Upload** (on failure)
   - Golden test diffs
   - Python coverage reports
   - Pytest logs

---

## 🎯 CI Quality Gates

### ✅ Quality Job (Runs First, Blocking)
Runs on Python 3.11 and 3.12 in parallel:

1. **Ruff** (fast static checks) - `ruff check python_app tests/python`
2. **Black** (code formatting) - `black --check python_app tests/python`
3. **Pylint** (strict linting) - `pylint -j 2 python_app tests/python`
   - Configuration: `.pylintrc`
   - Acceptable warnings disabled (docs, duplicate-code, etc.)
4. **Mypy** (type checking) - `mypy python_app`
   - Only checks production code (tests excluded due to duplicate module names)
   - Configuration: `mypy.ini`
5. **Security**:
   - **pip-audit** - Dependency vulnerability scanning
   - **Bandit** - Static Application Security Testing (SAST)

### ✅ Tests Job (Runs After Quality)
- ✅ Python infrastructure test (pytest must work)
- ✅ Unit tests (must pass)
- ✅ Integration tests (must pass)
- ⚠️ Functional tests (allowed to fail)
- 📊 Coverage report (informational unless otherwise configured)
- ✅ Python proxy server smoke test (non-blocking)

### Quality Tools Configuration

**Files**:
- `.pylintrc` - Pylint configuration (disabled warnings, good names)
- `mypy.ini` - Mypy configuration (Python version, exclusions, Flask/requests handling)
- `pyproject.toml` - Black formatter configuration
- `.github/workflows/ci.yml` - CI workflow definition

**Local Development**:
See [Code Quality Guide](CODE_QUALITY.md) for running quality checks locally.

---

## 🔧 Key Configuration

### Environment Variables
```
LC_ALL=C.UTF-8    # Deterministic locale
TZ=UTC            # Deterministic timezone
```

### Test Execution
- OCaml tests: Shell scripts (`run_golden.sh`, `test_gedcom_import.sh`)
- Python tests: pytest with markers (`-m unit`, `-m integration`, `-m functional`)

### Local vs CI Python Environments

- **Local development**: Always use a virtual environment
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On macOS/Linux
  # On Windows: venv\\Scripts\\activate
  pip install -r requirements.txt
  ```
- **CI runners**: Already isolated; the workflow installs dependencies into the runner environment directly. No venv creation is required in CI.

### Golden Tests

- Optional; CI never auto-creates references
- Run when any of the following:
  - Workflow input `run_golden=true`
  - Relevant paths change (GeneWeb/**, scripts/golden/**, tests/golden/**, python_app/routes/**, python_app/migrated/**)
  - PR has label `golden`
- See `docs/GOLDEN_TESTS.md` and ADR‑011 for determinism rules

### Functional Tests: Known CI Behaviors

- **GEDCOM routes**: Some GeneWeb distributions don't expose GEDCOM export/import via HTTP. Functional tests detect `HTTP 400/404` on `?m=GEDCOM` and `pytest.skip(...)` with a clear message. GEDCOM behavior is validated via CLI in golden/deployment scripts.
- **Wizard routes**: `?m=MOD_IND` and `?m=ADD_IND` require authentication. Functional tests skip when `HTTP 401` is returned to preserve read-only behavior in CI.
- **Statistics counts**: The individual count may be formatted differently depending on templates; tests assert presence of numeric data and semantic markers rather than exact strings.

---

## 🐛 When CI Fails

### View Results
1. Go to GitHub → Actions tab
2. Click on failed workflow run
3. Expand failed step to see logs
4. Download artifacts if needed (golden diffs, coverage, logs)

### Common Fixes
- **Golden test failure**: Review diff artifact, update goldens if intentional
- **Python test failure**: Check pytest logs artifact, fix test or code
- **gwd not starting**: Check smoke test logs for error messages

---

## 📊 What CI Enforces

- Quality checks: Ruff, Black, Pylint, Mypy, security scans
- Unit and integration tests must pass
- Functional tests are non-blocking during development
- Golden tests are optional and only run when requested or relevant

---

## 🚀 Notes

Branch protection should require quality and required test jobs. Golden tests should not be required.

---

## 📚 Related Files

- **CI Workflow**: `.github/workflows/ci.yml`
- **Test Policy**: `wiki/03-Quality-Test-Policy.md`
- **Test Protocols**: `wiki/03-Quality-Test-Protocols.md`
- **Pytest Guide**: `tests/python/README.md`

---

**Current Status**: ✅ CI configured with quality gates and Python tests; golden tests optional.
