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

- **macOS** (prebuilt binaries included) or **Linux** (download binaries)
- Basic terminal/command-line knowledge
- A web browser

### 📦 Getting Started

#### 1. Clone the repository

```bash
git clone https://github.com/Antonyjin/Legacy-Project.git
cd Legacy-Project
```

#### 2. Launch GeneWeb

**macOS:**
```bash
cd GeneWeb
./geneweb.sh
```

**Linux:**
```bash
# Download Linux binaries first
wget https://github.com/geneweb/geneweb/releases/download/v7.1-beta/geneweb-7.1-beta-linux-x86_64.tar.gz
tar -xzf geneweb-7.1-beta-linux-x86_64.tar.gz -C gw-linux
cd GeneWeb
gw-linux/gw/gwd -hd ./gw -bd ./bases -p 2317 -lang en
```

#### 3. Access the application

The script will automatically open your browser to:
- **GeneWeb home**: http://localhost:2317/test
- **Admin interface (gwsetup)**: http://localhost:2316

#### 4. Explore the test database

The `test.gwb` database contains British Royal Family data (35 persons).

**Try these pages:**
- Home: http://localhost:2317/test
- Person page: http://localhost:2317/test?p=Charles&n=Windsor
- Family page: http://localhost:2317/test?m=F&p=charles&n=windsor
- Calendar: http://localhost:2317/test?m=CAL
- First names: http://localhost:2317/test?m=P
- Surnames: http://localhost:2317/test?m=N

### 🧪 Running Tests

#### Golden Tests (Regression Detection)

Golden tests validate that OCaml behavior remains unchanged:

```bash
# From project root
export LC_ALL=C.UTF-8 TZ=UTC
./scripts/golden/run_golden.sh validate
```

**What this tests:**
- GEDCOM export consistency
- HTML rendering stability (7 page types)
- Data normalization (whitespace, timestamps, random IDs)

#### Integration Tests (Smoke Checks)

Automated smoke tests run in CI on every push:

```bash
# Runs automatically in CI
# See: .github/workflows/ci.yml
```

**What CI tests:**
- Home page HTTP 200 + marker
- Person page fields validation
- FR localization
- Logging validation
- GEDCOM export

### 📚 Documentation

#### For Quick Testing & Understanding
1. **This README** - Quick start
2. **[Wiki Home](https://github.com/Antonyjin/Legacy-Project/wiki)** - Full documentation
3. **[Product Runbook](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Runbook)** - How to run GeneWeb
4. **[OCaml Overview](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-OCaml-Overview)** - Understanding the codebase

#### For Deep Dives
- **[Test Policy](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Policy)** - QA strategy
- **[Test Protocols](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Protocols)** - Test types (UT/FT/Golden/IT)
- **[Architecture](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Architecture)** - System design
- **[Deployment Guide](https://github.com/Antonyjin/Legacy-Project/wiki/05-Deployment-Quick-Deploy)** - Production deployment

### 🔍 Understanding the Codebase

#### Directory Structure

```
Legacy-Project/
├── GeneWeb/                    # Main OCaml application
│   ├── gw/                     # Binaries (gwd, gwsetup, ged2gwb, gwb2ged)
│   ├── bases/                  # Databases (test.gwb, base.gwb)
│   ├── geneweb.sh             # Launcher script
│   └── START.htm              # Landing page
├── scripts/                    # Test and utility scripts
│   └── golden/                # Golden test harness
│       ├── run_golden.sh      # Main golden test script
│       └── test_gedcom_import.sh  # GEDCOM roundtrip test
├── tests/                      # Test artifacts
│   └── golden/                # Golden references
│       └── goldens/v1/        # Versioned golden snapshots
├── wiki/                       # Documentation (separate repo)
├── docs/                       # Additional documentation
│   └── Issues/                # Issue-specific docs
└── .github/workflows/         # CI/CD pipelines
```

#### Key OCaml Binaries

| Binary | Purpose | Example Usage |
|--------|---------|---------------|
| `gwd` | Web daemon (serves pages) | `gwd -hd ./gw -bd ./bases -p 2317` |
| `gwsetup` | Admin interface | `gwsetup -gd ./gw -lang en` |
| `ged2gwb` | GEDCOM → GeneWeb import | `ged2gwb input.ged -o bases/mybase` |
| `gwb2ged` | GeneWeb → GEDCOM export | `gwb2ged bases/mybase.gwb -o output.ged` |
| `gwu` | Text export utility | `gwu bases/mybase.gwb > dump.gw` |

### 🧪 Test Types

We have **4 distinct test categories**:

1. **Unit Tests (UT)** - Isolated code units (to be implemented)
2. **Functional Tests (FT)** - End-to-end user workflows (to be implemented)
3. **Golden Tests** - Regression detection via output snapshots (✅ implemented)
4. **Integration Tests (IT)** - Runtime smoke checks (✅ implemented)

See [Test Protocols](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Protocols) for details.

### 🐛 Troubleshooting

#### Port already in use
```bash
# Change ports in geneweb.sh or kill existing processes
lsof -ti:2317 | xargs kill -9  # macOS/Linux
```

#### "cannot execute binary file" on Linux
- The bundled binaries are for macOS
- Download Linux binaries from [GeneWeb releases](https://github.com/geneweb/geneweb/releases)

#### "Failed - unbound var sosa_ref.key"
- Tree and search pages require Sosa reference configuration
- Use gwsetup to configure a Sosa root person
- See [ISSUE_50_SKIPPED.md](docs/Issues/ISSUE_50_SKIPPED.md) for details

#### Golden tests failing with whitespace differences
```bash
# Regenerate goldens if changes are intentional
./scripts/golden/run_golden.sh create
```

### 🎓 Learning Path

**Day 1: Understand the basics**
1. Read this README
2. Launch GeneWeb with `geneweb.sh`
3. Explore the test database pages
4. Read [OCaml Overview](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-OCaml-Overview)

**Day 2: Understand the tests**
1. Run golden tests: `./scripts/golden/run_golden.sh validate`
2. Review [Test Protocols](https://github.com/Antonyjin/Legacy-Project/wiki/03-Quality-Test-Protocols)
3. Check CI results on GitHub Actions

**Day 3: Understand the architecture**
1. Read [Architecture](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Architecture)
2. Read [Runbook](https://github.com/Antonyjin/Legacy-Project/wiki/02-Product-Runbook)
3. Import your own GEDCOM file

### 📊 Current Test Coverage

- ✅ **Golden Tests**: 7 page types + GEDCOM export + import roundtrip
- ✅ **Integration Tests**: 5 smoke checks (home, person, FR, logging, export)
- 🔲 **Functional Tests**: To be implemented
- 🔲 **Unit Tests**: To be implemented

### 🤝 Contributing

1. Create a feature branch: `git checkout -b feature-name`
2. Make changes and test locally
3. Run golden tests: `./scripts/golden/run_golden.sh validate`
4. Commit with conventional commits: `feat:`, `fix:`, `docs:`, etc.
5. Push and create a PR

### 📞 Support

- **Wiki**: https://github.com/Antonyjin/Legacy-Project/wiki
- **Issues**: https://github.com/Antonyjin/Legacy-Project/issues
- **Upstream GeneWeb**: https://geneweb.tuxfamily.org/

### 📅 Timeline

**Defense window**: October 20–24, 2025

### 📜 License

GeneWeb is distributed under the GNU General Public License. See [LICENSE.txt](GeneWeb/LICENSE.txt).

---

**Quick Command Reference:**

```bash
# Start GeneWeb
cd GeneWeb && ./geneweb.sh

# Run golden tests
./scripts/golden/run_golden.sh validate

# Export GEDCOM
GeneWeb/gw/gwb2ged GeneWeb/bases/test.gwb -o export.ged

# Import GEDCOM
GeneWeb/gw/ged2gwb input.ged -o GeneWeb/bases/newbase

# Check CI status
# Visit: https://github.com/Antonyjin/Legacy-Project/actions
```

**Need help?** Start with the [Wiki Home](https://github.com/Antonyjin/Legacy-Project/wiki) or ask in Issues! 🚀
