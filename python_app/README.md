# Python Proxy Server

GeneWeb Python proxy server with backend toggle (OCaml/Python).

## Overview

This is the core infrastructure for the migration strategy (MIG-INF-001, Issue #225). It provides a Python Flask server that can toggle between OCaml and Python backend implementations.

## Benchmarks (MIG-INF-004)

Micro-benchmarks comparing OCaml `gwd` vs Python backend are available. See `docs/BENCHMARKS.md` or run:

```bash
python -m python_app.benchmarks.benchmark_runner
```

## Quick Start

### Installation (Using Virtual Environment)

**Create and activate a virtual environment** (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Verify installation:**
```bash
# Check Flask is installed
python -c "import flask; print(f'Flask {flask.__version__} installed')"
```

### Running the Server

```bash
# Make sure venv is activated (you should see (venv) in your prompt)
source venv/bin/activate  # On macOS/Linux

# OCaml backend (default) - proxies to OCaml gwd
BACKEND=ocaml python -m python_app.app

# Python backend - uses migrated functions
BACKEND=python python -m python_app.app

# With custom port
FLASK_PORT=2318 python -m python_app.app
```

**Note**: Make sure OCaml `gwd` is running if using `BACKEND=ocaml` (or the proxy will fail).

### Access the Server

- **Server URL**: http://localhost:2318/test (default)
- **Health Check**: http://localhost:2318/health
- **Debug Config**: http://localhost:2318/debug/config (if DEBUG=true)

## Configuration

Set via environment variables:

- `BACKEND`: `ocaml` or `python` (default: `ocaml`)
- `FLASK_HOST`: Flask host (default: `127.0.0.1`)
- `FLASK_PORT`: Flask port (default: `2318`)
- `GENEWEB_DIR`: Path to GeneWeb directory (default: `GeneWeb`)
- `GENEWEB_BASE`: Base name (default: `test`)
- `GENEWEB_LANG`: Default language (default: `en`)
- `OCAML_GWD_PORT`: OCaml gwd port (default: `2317`)
- `FLASK_DEBUG`: Enable debug mode (default: `false`)

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────┐
│  Python Flask App   │
│  (python_app/app)   │
└──────┬───────────────┘
       │
       ├─ BACKEND=python ──► tests/python/utils/ (migrated functions)
       │
       └─ BACKEND=ocaml ────► ocaml_bridge ──► OCaml gwd (subprocess)
```

## Structure

- `app.py`: Main Flask application
- `config.py`: Configuration and backend toggle
- `migrated/`: Imports from `tests/python/utils/` (migrated functions)
  - **Issue**: MIG-INF-002 (#226)
  - Exposes all migrated utility functions (name, string, HTTP, HTML, number, roman, date utilities)
  - Used when `BACKEND=python` to access Python implementations
  - Validated by `tests/python/unit/test_migrated_module.py` (24 tests)
- `routes/`: HTTP route handlers
  - `person.py`: Person detail pages
  - `family.py`: Family relationship pages
  - `search.py`: Search functionality
  - `stats.py`: Statistics pages
- `ocaml_bridge.py`: Subprocess calls to OCaml binaries

## Backend Toggle

### OCaml Backend (`BACKEND=ocaml`)

- Proxies all requests to OCaml `gwd` server
- Uses subprocess calls via `ocaml_bridge`
- OCaml `gwd` must be running on `OCAML_GWD_PORT` (default: 2317)

### Python Backend (`BACKEND=python`)

- Uses migrated functions from `tests/python/utils/`
- Processes requests with Python implementations
- Still uses OCaml for:
  - Database access (not yet migrated)
  - GEDCOM export/import (complex operations)
  - Complex algorithms (search, relationships)

## Current Status

**✅ Implemented:**
- Flask application structure
- Backend toggle mechanism
- Route handlers (person, family, search, stats)
- OCaml bridge (subprocess calls)
- Migrated function imports

**⏳ In Progress:**
- Full Python implementation of routes (currently proxies to OCaml)
- Database access layer (still using OCaml)
- Template rendering (still using OCaml HTML)

**🔮 Future Work:**
- Full Python implementation
- Template rendering in Python
- Database access in Python
- Dual-run validation (OCaml vs Python)

## Testing

**Prerequisites**: Make sure OCaml `gwd` is running if using `BACKEND=ocaml` or if routes need to proxy.

```bash
# Activate venv (if not already active)
source venv/bin/activate

# Start OCaml gwd (if using BACKEND=ocaml or proxy routes)
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 2317 -lang en &
cd ..

# Test health endpoint
curl http://localhost:2318/health

# Test home page
curl http://localhost:2318/test

# Test person page
curl "http://localhost:2318/test?p=Charles&n=Windsor"

# Test with Python backend
BACKEND=python python -m python_app.app
curl http://localhost:2318/health
```

## Related

- **Issue**: #225 (MIG-INF-001)
- **Migration Status**: `docs/MIGRATION_STATUS.md`
- **ADR-006**: Utility Function Migration Approach
- **ADR-007**: CI Quality Gates Strategy

