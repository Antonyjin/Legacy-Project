# Code Quality Guide

## 📋 Overview

This project uses automated code quality tools to ensure consistent code style, detect errors early, and maintain high code quality standards.

**Tools Used**:
- **Ruff** - Fast Python linter (replaces flake8, isort, etc.)
- **Black** - Code formatter
- **Pylint** - Comprehensive linting
- **Mypy** - Static type checking
- **Bandit** - Security linting
- **pip-audit** - Dependency vulnerability scanning

**Configuration Files**:
- `.pylintrc` - Pylint settings
- `mypy.ini` - Mypy type checking config
- `pyproject.toml` - Black formatter config

---

## 🚀 Quick Start

### Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install quality tools (already in requirements.txt)
pip install ruff black pylint mypy bandit[toml] pip-audit

# Set Python path
export PYTHONPATH=$(pwd)
```

### Run All Quality Checks

```bash
# Run all checks (same as CI)
ruff check python_app tests/python
black --check python_app tests/python
pylint python_app tests/python
mypy python_app
pip-audit
bandit -r python_app
```

---

## 🔧 Individual Tools

### Ruff (Fast Static Checks)

**Purpose**: Catch common errors quickly before running slower tools.

```bash
# Check for issues
ruff check python_app tests/python

# Auto-fix issues (where possible)
ruff check --fix python_app tests/python
```

**What it checks**:
- Import sorting
- Unused imports/variables
- Syntax errors
- PEP 8 violations
- Complex code patterns

### Black (Code Formatter)

**Purpose**: Automatically format code to a consistent style.

```bash
# Check formatting (dry-run)
black --check python_app tests/python

# Auto-format code
black python_app tests/python

# Format specific file
black python_app/app.py
```

**Configuration**: `pyproject.toml`
- Line length: 100 characters
- Target Python: 3.11+

### Pylint (Strict Linting)

**Purpose**: Deep code analysis for quality, bugs, and style issues.

```bash
# Run pylint (parallel processing)
pylint -j 2 python_app tests/python

# Check specific file
pylint python_app/app.py

# Check specific directory
pylint python_app/routes/
```

**Configuration**: `.pylintrc`
- Max line length: 120
- Disabled warnings: Common acceptable patterns (docs, duplicate-code, etc.)
- Good names: Short variables common in tests/benchmarks (i, j, o, v, c, p1, p2, etc.)

**Common Disabled Warnings** (configured in `.pylintrc`):
- `C0114-C0116` - Missing docstrings (acceptable in tests/utilities)
- `R0801` - Duplicate code (intentional patterns across routes)
- `R0903` - Too few public methods (common in test classes)
- `W0511` - TODO comments (acceptable)
- `R1710` - Inconsistent return statements (common in fixtures)

### Mypy (Type Checking)

**Purpose**: Static type checking to catch type-related errors.

```bash
# Type check production code (excludes tests)
mypy python_app

# Type check with verbose output
mypy python_app --verbose

# Type check specific file
mypy python_app/app.py
```

**Configuration**: `mypy.ini`
- Python version: 3.11
- Ignores missing imports (for external libraries)
- Excludes tests (to avoid duplicate module name errors)
- Special handling for Flask and requests (dynamic attributes)

**Why tests are excluded**:
- Test files often have duplicate names (`test_localization.py` in both unit/ and integration/)
- Tests use more relaxed typing (dynamic fixtures, etc.)
- Focus type checking on production code

### Bandit (Security Linting)

**Purpose**: Find common security issues in Python code.

```bash
# Scan production code
bandit -r python_app

# Scan with quiet output (only errors)
bandit -q -r python_app

# Scan specific file
bandit python_app/ocaml_bridge.py
```

**What it checks**:
- Hardcoded passwords/secrets
- SQL injection risks
- Shell injection risks
- Use of insecure functions

### pip-audit (Dependency Security)

**Purpose**: Check installed packages for known vulnerabilities.

```bash
# Audit dependencies
pip-audit

# Audit with specific output format
pip-audit --format json
```

---

## 📝 Pre-commit Workflow

### Before Committing

1. **Format code with Black**:
   ```bash
   black python_app tests/python
   ```

2. **Fix Ruff issues**:
   ```bash
   ruff check --fix python_app tests/python
   ```

3. **Check Pylint** (fix critical issues):
   ```bash
   pylint python_app tests/python
   ```

4. **Type check with Mypy**:
   ```bash
   mypy python_app
   ```

5. **Run tests**:
   ```bash
   pytest tests/python/ -v
   ```

### Make Script (Optional)

Create a `Makefile` for convenience:

```makefile
.PHONY: quality
quality:
	ruff check python_app tests/python
	black --check python_app tests/python
	pylint python_app tests/python
	mypy python_app
	bandit -q -r python_app
	pip-audit
```

Then run: `make quality`

---

## ⚙️ Configuration Files

### `.pylintrc`

Located in project root. Key settings:
- `max-line-length = 120`
- `good-names = i,j,k,...,o,v,c,p1,p2` (short names for tests/benches)
- Disabled warnings for acceptable patterns

### `mypy.ini`

Located in project root. Key settings:
- `python_version = 3.11`
- `ignore_missing_imports = True` (for external libs)
- `exclude = tests/.*` (avoid duplicate module names)
- Special configs for `flask.*` and `requests.*`

### `pyproject.toml`

Located in project root. Contains Black configuration:
- `line-length = 100`
- `target-version = ["py311"]`
- Include/exclude patterns

---

## 🐛 Common Issues

### Pylint: Duplicate Code (R0801)

**Issue**: Pylint flags similar error handling patterns across routes.

**Solution**: Already disabled in `.pylintrc`. This duplication is intentional for clarity.

### Mypy: Duplicate Module Name

**Issue**: `test_localization.py` exists in both `tests/python/unit/` and `tests/python/integration/`.

**Solution**: Tests are excluded from mypy. Only `python_app/` is type-checked.

### Mypy: Flask/Requests Type Errors

**Issue**: Mypy can't see Flask's dynamic attributes (Blueprint, Response, etc.).

**Solution**: Special `[mypy-flask.*]` and `[mypy-requests.*]` configs in `mypy.ini` with `ignore_missing_imports = True`.

### Black: Line Too Long

**Issue**: Black suggests wrapping long lines.

**Solution**: Run `black` to auto-format, or manually wrap following Black's style guide.

### Ruff: Import Not Used

**Issue**: Ruff flags imports that aren't used.

**Solution**: Run `ruff check --fix` to auto-remove, or remove manually.

---

## 📊 CI Integration

All quality checks run in CI before tests:

1. **Quality Job** (Python 3.11 & 3.12):
   - Ruff → Black → Pylint → Mypy → Security
   - All steps are **blocking** (must pass)

2. **Tests Job** (only after quality passes):
   - Unit tests
   - Integration tests
   - Functional tests
   - Coverage ≥80%

**See**: [CI Workflow Guide](CI_WORKFLOW_GUIDE.md)

---

## 🔗 Related Documentation

- [CI Workflow Guide](CI_WORKFLOW_GUIDE.md) - How CI runs quality checks
- [README.md](../README.md) - Project overview
- [Python Proxy Server](PYTHON_PROXY_SERVER.md) - Proxy server docs

---

**Current Status**: ✅ All quality tools configured and passing in CI!

