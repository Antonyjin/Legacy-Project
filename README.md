# GeneWeb Legacy Restoration Project

[![CI Status](https://github.com/Antonyjin/Legacy-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/Antonyjin/Legacy-Project/actions/workflows/ci.yml)

## 🎯 Mission

Restore, secure, test, and deploy the legacy OCaml genealogy software **GeneWeb** (1995-2008) without altering its core behavior.

## 🚀 Quick Start

### What is GeneWeb?

GeneWeb is an open-source genealogy application written in OCaml that:
- Imports/exports GEDCOM files (genealogical data format)
- Stores data in proprietary `.gwb` binary databases
- Serves family tree web pages via the `gwd` daemon
- Provides admin UI via `gwsetup` daemon

### Prerequisites

- **macOS** or **Linux** (x86_64)
- **Python 3.11+** (for running tests)
- Basic terminal/command-line knowledge
- A web browser

### 📦 Getting Started

There are **two ways** to use GeneWeb depending on your needs:

---

#### Option A: Quick Start for Testing (Recommended)

**This is what CI uses and what you need for running Python tests:**

```bash
# 1. Clone the repository
git clone https://github.com/Antonyjin/Legacy-Project.git
cd Legacy-Project

# 2. Start gwd on test port (23179)
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
cd ..

# 3. Verify it's running
curl http://localhost:23179/test
# Should return HTML with "GeneWeb"

# 4. Run Python tests
pip install -r requirements.txt
pytest tests/python/ -v

# 5. Stop gwd when done
pkill -f gwd
```

**Access test database:**
- 🌐 **Main app**: http://localhost:23179/test
- 👤 **Person page**: http://localhost:23179/test?p=Charles&n=Windsor
- 📊 **Statistics**: http://localhost:23179/test?m=STAT

**Database**: `test.gwb` contains British Royal Family data (188 persons)

---

#### Option B: Manual Launch for Exploration

**If you want to explore GeneWeb manually (not for testing):**

**macOS/Linux - Manual Start (Recommended):**
```bash
cd Legacy-Project/GeneWeb

# Start gwd (web server) on port 2317
./gw/gwd -hd ./gw -bd ./bases -p 2317 -lang en &

# Start gwsetup (admin interface) on port 2316 - optional
./gw/gwsetup -gd ./gw -lang en &

# Access application
echo "Main app: http://localhost:2317/test"
echo "Admin: http://localhost:2316"
```

**macOS - Using geneweb.sh (Alternative):**
```bash
cd GeneWeb
./geneweb.sh
# Note: This legacy script may have path issues. Use manual start above if it fails.
```

**Access application:**
- 🌐 **Main app**: http://localhost:2317/test  
- ⚙️ **Admin panel**: http://localhost:2316
- 📄 **Landing page**: Open `GeneWeb/START.htm` in browser

**Stop servers:**
```bash
pkill -f gwd
pkill -f gwsetup
```

---

#### Exploring the Database

**Try these pages** (adjust port as needed: 23179 for testing, 2317 for manual):

- 🏠 Home: `http://localhost:23179/test`
- 👤 Person: `http://localhost:23179/test?p=Charles&n=Windsor`
- 👨‍👩‍👧‍👦 Family: `http://localhost:23179/test?m=F&p=charles&n=windsor`
- 📅 Calendar: `http://localhost:23179/test?m=CAL`
- 📝 First names: `http://localhost:23179/test?m=P`
- 📋 Surnames: `http://localhost:23179/test?m=N`
- 📊 Statistics: `http://localhost:23179/test?m=STAT`

### 🧪 Running Tests

#### Prerequisites for Testing

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or manually install:
pip install pytest pytest-cov requests
```

#### Python Tests (Unit + Integration + Functional)

We have comprehensive Python tests that validate OCaml behavior:

```bash
# From project root (Legacy-Project/)

# Run all Python tests (85 tests)
pytest tests/python/ -v

# Run with coverage
pytest tests/python/ --cov=tests/python --cov-report=html

# Run specific test type
pytest tests/python/unit/ -v          # Unit tests (57 tests) - ✅ CI BLOCKING
pytest tests/python/integration/ -v   # Integration tests (28 tests) - ✅ CI BLOCKING
pytest tests/python/functional/ -v    # Functional tests - ⚠️ In development

# Run by marker
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m functional  # Functional tests only
```

**Test Status:**
- ✅ **Unit Tests (57)**: Test OCaml functions via HTTP black-box testing - **CI BLOCKS ON FAILURE**
- ✅ **Integration Tests (28)**: Test gwd lifecycle, port conflicts, concurrency - **CI BLOCKS ON FAILURE**
- ⚠️ **Functional Tests**: End-to-end user workflows - **In development, failures allowed**

**Current Coverage:** 85 tests passing

#### Golden Tests (Currently Disabled)

Golden tests validate that OCaml output remains unchanged. They are temporarily disabled during migration and will be re-enabled in Week 2-3.

```bash
# From project root
export LC_ALL=C.UTF-8 TZ=UTC
chmod +x ./scripts/golden/run_golden.sh
./scripts/golden/run_golden.sh validate
```

**What this tests:**
- GEDCOM export consistency
- HTML rendering stability (10 page types)
- Data normalization (whitespace, timestamps, random IDs)

**Note:** Golden tests are currently disabled in CI (see `.github/workflows/ci.yml`) and will be re-enabled after Python migration starts.

### 📚 Documentation

#### For Quick Testing & Understanding
1. **This README** - Quick start
2. **[Wiki Home](https://github.com/Antonyjin/Legacy-Project/wiki)** - Full documentation
3. **[Product Runbook](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Runbook)** - How to run GeneWeb
4. **[OCaml Overview](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-OCaml-Overview)** - Understanding the codebase
5. **[CI Workflow Guide](docs/CI_WORKFLOW_GUIDE.md)** - Understanding CI setup

#### For Deep Dives
- **[Test Policy](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Policy)** - QA strategy
- **[Test Protocols](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Protocols)** - Test types (UT/IT/FT)
- **[Architecture](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Architecture)** - System design

#### Test-Specific Documentation
- **[Unit Test README](tests/python/unit/README.md)** - Python unit testing strategy
- **[Integration Test README](tests/python/integration/README.md)** - Integration testing guide

### 🔍 Understanding the Codebase

#### Directory Structure

```
Legacy-Project/
├── GeneWeb/                    # Main OCaml application (prebuilt binaries)
│   ├── gw/                     # Binaries (gwd, gwsetup, ged2gwb, gwb2ged)
│   ├── bases/                  # Databases (test.gwb with 188 persons)
│   ├── geneweb.sh             # Launcher script (macOS)
│   └── START.htm              # Landing page
├── scripts/                    # Test and utility scripts
│   └── golden/                # Golden test harness (currently disabled)
│       ├── run_golden.sh      # Main golden test script
│       └── test_gedcom_import.sh  # GEDCOM roundtrip test
├── tests/                      # Python tests
│   ├── python/
│   │   ├── unit/              # 57 unit tests ✅
│   │   ├── integration/       # 28 integration tests ✅
│   │   └── functional/        # Functional tests (in dev) ⚠️
│   └── golden/                # Golden references (disabled)
│       └── goldens/v1/        # Versioned golden snapshots
├── docs/                       # Project documentation
│   └── CI_WORKFLOW_GUIDE.md   # CI setup guide
├── .github/workflows/         # CI/CD pipelines
│   └── ci.yml                 # Main CI workflow
├── pytest.ini                 # Pytest configuration
├── .coveragerc                # Coverage configuration
└── requirements.txt           # Python dependencies
```

#### Key OCaml Binaries

| Binary | Purpose | Example Usage |
|--------|---------|---------------|
| `gwd` | Web daemon (serves pages) | `gwd -hd ./gw -bd ./bases -p 2317 -lang en` |
| `gwsetup` | Admin interface | `gwsetup -gd ./gw -lang en` |
| `ged2gwb` | GEDCOM → GeneWeb import | `ged2gwb input.ged -o bases/mybase` |
| `gwb2ged` | GeneWeb → GEDCOM export | `gwb2ged bases/mybase.gwb -o output.ged` |
| `gwu` | Text export utility | `gwu bases/mybase.gwb > dump.gw` |

### 🧪 Test Types

We have **3 test categories** (4th coming soon):

1. ✅ **Unit Tests (57)** - Test OCaml functions via HTTP black-box testing - **Blocks CI**
2. ✅ **Integration Tests (28)** - Test gwd lifecycle, ports, concurrency - **Blocks CI**
3. ⚠️ **Functional Tests** - End-to-end user workflows - **In development**
4. 🔜 **Golden Tests** - Regression detection - **Temporarily disabled, will be re-enabled**

See [Test Protocols](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Protocols) and [CI Workflow Guide](docs/CI_WORKFLOW_GUIDE.md) for details.

### 🐛 Troubleshooting

#### Port already in use
```bash
# macOS/Linux - Find and kill processes
lsof -ti:2317 | xargs kill -9
lsof -ti:2316 | xargs kill -9

# Or use pkill
pkill -f gwd
pkill -f gwsetup
```

#### Python tests failing
```bash
# Make sure gwd is running on the correct port
ps aux | grep gwd

# Check if test database exists
ls -la GeneWeb/bases/test.gwb/

# Verify Python dependencies
pip list | grep pytest
```

#### "cannot execute binary file" on Linux
- The bundled binaries in `GeneWeb/` are for macOS only
- Download Linux binaries from [GeneWeb releases](https://github.com/geneweb/geneweb/releases)
- Follow the Linux setup instructions above

#### "Failed - unbound var sosa_ref.key"
- Tree and search pages require Sosa reference configuration
- Use gwsetup to configure a Sosa root person
- Access gwsetup at http://localhost:2316
- See [ISSUE_50_SKIPPED.md](docs/Issues/ISSUE_50_SKIPPED.md) for details

#### Golden tests failing with whitespace differences
```bash
# Regenerate goldens if changes are intentional
export LC_ALL=C.UTF-8 TZ=UTC
./scripts/golden/run_golden.sh create

# Note: Golden tests are currently disabled in CI
# They will be re-enabled during Week 2-3 migration phase
```

#### Python import errors
```bash
# Make sure you're in the project root
cd Legacy-Project

# Install dependencies
pip install -r requirements.txt

# Verify pytest works
pytest --version
```

### 🎓 Learning Path

**Day 1: Understand the basics**
1. Read this README
2. Launch GeneWeb with `./GeneWeb/geneweb.sh` (macOS) or follow Linux instructions
3. Explore the test database pages
4. Read [OCaml Overview](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-OCaml-Overview)

**Day 2: Understand the tests**
1. Install Python dependencies: `pip install -r requirements.txt`
2. Run Python tests: `pytest tests/python/ -v`
3. Review [Test Protocols](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Protocols)
4. Check [CI Workflow Guide](docs/CI_WORKFLOW_GUIDE.md)
5. Check CI results on GitHub Actions

**Day 3: Understand the architecture**
1. Read [Architecture](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Architecture)
2. Read [Runbook](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Runbook)
3. Try importing your own GEDCOM file

### 📊 Current Test Coverage

| Test Type | Status | Count | CI Blocking |
|-----------|--------|-------|-------------|
| **Python Unit Tests** | ✅ Complete | 57 tests | ✅ Yes |
| **Python Integration Tests** | ✅ Complete | 28 tests | ✅ Yes |
| **Python Functional Tests** | ⚠️ In Development | 0 tests | ⏳ Not yet |
| **Golden Tests** | 🔄 Disabled | 12 tests | 🚫 Disabled until migration |
| **TOTAL** | | **85 tests passing** | |

**Python Test Infrastructure** (Issue #97): ✅ **COMPLETE**
- pytest configuration (`pytest.ini`)
- Coverage setup (`.coveragerc`, target >80%)
- Shared fixtures (`tests/python/conftest.py`)
- Test directory structure with READMEs
- 85 passing tests with full CI integration

**CI Quality Gates** (Issue #117): ✅ **ACTIVE**
- ✅ Unit Tests (UT) block CI on failure
- ✅ Integration Tests (IT) block CI on failure
- ⚠️ Functional Tests (FT) allow failures during development
- 📊 Coverage tracked but not yet enforcing threshold

### 🤝 Contributing

1. Create a feature branch: `git checkout -b feature-name`
2. Make changes and test locally
3. Run all tests: `pytest tests/python/ -v`
4. Commit with conventional commits: `feat:`, `fix:`, `docs:`, etc.
5. Push and create a PR
6. CI will automatically run all tests

**Branch Protection Rules:**
- ✅ Unit tests must pass
- ✅ Integration tests must pass
- ⚠️ Functional tests may fail (in development)

### 📞 Support

- **Wiki**: https://github.com/Antonyjin/Legacy-Project/wiki
- **Issues**: https://github.com/Antonyjin/Legacy-Project/issues
- **Upstream GeneWeb**: https://geneweb.tuxfamily.org/
- **CI Status**: https://github.com/Antonyjin/Legacy-Project/actions

### 📜 License

GeneWeb is distributed under the GNU General Public License. See [LICENSE.txt](GeneWeb/LICENSE.txt).

---

## Quick Command Reference

```bash
# ==========================================
# Start GeneWeb - FOR TESTING (Port 23179)
# ==========================================

# Start gwd (what CI uses)
cd Legacy-Project/GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
cd ..

# Verify it's running
curl http://localhost:23179/test

# Stop
pkill -f gwd

# ==========================================
# Start GeneWeb - FOR MANUAL USE (Port 2317)
# ==========================================

# Recommended manual start
cd Legacy-Project/GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 2317 -lang en &
./gw/gwsetup -gd ./gw -lang en &

# Alternative: Use legacy script (may have issues)
./geneweb.sh

# Stop
pkill -f gwd
pkill -f gwsetup

# ==========================================
# Python Tests (from project root)
# ==========================================

# IMPORTANT: Start gwd on port 23179 first (see above)

# Install dependencies
pip install -r requirements.txt

# Run all tests (85 tests)
pytest tests/python/ -v

# Run by type
pytest tests/python/unit/ -v              # Unit tests (57)
pytest tests/python/integration/ -v       # Integration tests (28)
pytest -m unit                            # Unit marker
pytest -m integration                     # Integration marker

# With coverage
pytest tests/python/ --cov=tests/python --cov-report=html

# Specific test file
pytest tests/python/unit/test_http_params.py -v

# ==========================================
# Golden Tests (disabled, for reference)
# ==========================================

# Validate (when re-enabled)
export LC_ALL=C.UTF-8 TZ=UTC
./scripts/golden/run_golden.sh validate

# Regenerate goldens
./scripts/golden/run_golden.sh create

# ==========================================
# GEDCOM Import/Export
# ==========================================

# Export GEDCOM
GeneWeb/gw/gwb2ged GeneWeb/bases/test.gwb -o export.ged

# Import GEDCOM
GeneWeb/gw/ged2gwb input.ged -o GeneWeb/bases/newbase

# ==========================================
# Check Status
# ==========================================

# Check if gwd is running
ps aux | grep gwd

# Check CI status
# Visit: https://github.com/Antonyjin/Legacy-Project/actions

# Check test database
ls -la GeneWeb/bases/test.gwb/

# Check Python installation
python --version  # Should be 3.11+
pytest --version
```

**Need help?** Start with the [Wiki Home](https://github.com/Antonyjin/Legacy-Project/wiki), check [CI Workflow Guide](docs/CI_WORKFLOW_GUIDE.md), or ask in Issues! 🚀

