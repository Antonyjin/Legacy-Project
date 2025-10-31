# Python Proxy Server Documentation

## Overview

The Python proxy server (MIG-INF-001, Issue #225) is the core infrastructure for the Strangler Fig migration pattern. It provides a Flask-based web server that can toggle between OCaml and Python backend implementations.

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────┐
│  Python Flask App   │  ◄── Backend toggle (BACKEND env var)
│  (python_app/app)   │
└──────┬───────────────┘
       │
       ├─ BACKEND=python ──► python_app/migrated/ ──► tests/python/utils/
       │                     (Use migrated functions)
       │
       └─ BACKEND=ocaml ────► python_app/ocaml_bridge ──► OCaml gwd (subprocess)
                            (Proxy to OCaml server)
```

## Installation

### Using Virtual Environment (Recommended)

**Always use a virtual environment** to avoid conflicts with system Python packages:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print(f'Flask {flask.__version__} installed')"
```

**Or use the setup script:**
```bash
./python_app/setup_venv.sh
source venv/bin/activate
```

**Note**: Always activate the virtual environment before running the server or tests.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND` | `ocaml` | Backend to use: `ocaml` or `python` |
| `FLASK_HOST` | `127.0.0.1` | Flask server host |
| `FLASK_PORT` | `2318` | Flask server port |
| `GENEWEB_DIR` | `GeneWeb` | Path to GeneWeb directory |
| `GENEWEB_BASE` | `test` | Default database base name |
| `GENEWEB_LANG` | `en` | Default language |
| `OCAML_GWD_PORT` | `2317` | Port for OCaml gwd server |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |

### Example Usage

```bash
# OCaml backend (default) - proxies all requests to OCaml gwd
BACKEND=ocaml python -m python_app.app

# Python backend - uses migrated functions from tests/python/utils/
BACKEND=python python -m python_app.app

# Custom port
FLASK_PORT=5000 python -m python_app.app

# Debug mode
FLASK_DEBUG=true python -m python_app.app
```

## Routes

### Main Routes

| Route | Handler | Description |
|-------|---------|-------------|
| `/` | `index()` | Redirects to default base |
| `/<base_name>` | `home()` | Home page for a base |
| `/health` | `health()` | Health check endpoint |
| `/debug/config` | `debug_config()` | Configuration debug (if DEBUG=true) |

### Query Parameter Routes

All routes support query parameters like GeneWeb:

- **Home**: `http://localhost:2318/test`
- **Person**: `http://localhost:2318/test?p=Charles&n=Windsor`
- **Family**: `http://localhost:2318/test?m=F&p=charles&n=windsor`
- **Search**: `http://localhost:2318/test?m=S&v=query`
- **Statistics**: `http://localhost:2318/test?m=STAT`
- **Calendar**: `http://localhost:2318/test?m=CAL`
- **Language**: `http://localhost:2318/test?lang=fr`

### Route Handlers

Located in `python_app/routes/`:
- `person.py`: Person detail pages
- `family.py`: Family relationship pages
- `search.py`: Search functionality
- `stats.py`: Statistics pages

## Backend Toggle

### OCaml Backend (`BACKEND=ocaml`)

**Behavior**:
- All requests are proxied to OCaml `gwd` server
- Uses `ocaml_bridge.proxy_request()` to forward HTTP requests
- OCaml `gwd` must be running on `OCAML_GWD_PORT` (default: 2317)

**Use Case**: Direct compatibility mode, testing, baseline behavior

### Python Backend (`BACKEND=python`)

**Behavior**:
- Uses migrated functions from `tests/python/utils/`
- Processes requests with Python implementations:
  - Name normalization (`name_lower`, `name_strip`)
  - URL encoding/decoding (`url_encode`, `url_decode`)
  - HTML escaping (`escape_html`)
  - Number formatting (`format_number_with_separator`)
  - Date validation (`leap_year`, `nb_days_in_month`)
  - String utilities (`purge`, `strip_c`)
- Still uses OCaml for:
  - Database access (not yet migrated)
  - GEDCOM export/import (complex operations)
  - Template rendering (OCaml HTML)

**Use Case**: Testing migrated functions, dual-run validation, gradual migration

## Current Limitations

### What's Implemented ✅
- Flask server infrastructure
- Backend toggle mechanism
- Route handlers (person, family, search, stats)
- OCaml bridge (subprocess calls)
- Migrated function imports (all 10 utilities)

### What's Still Using OCaml ⏳
- **Database access**: All data retrieval still goes through OCaml `gwd`
- **Template rendering**: HTML pages are rendered by OCaml and proxied
- **GEDCOM operations**: Export/import use OCaml binaries
- **Complex algorithms**: Search, relationships, statistics

### Why?
- These require database layer migration (not yet implemented)
- GeneWeb HTML templates are OCaml-specific (would need Python templates)
- Some operations are complex and not yet prioritized for migration

## Testing

### Manual Testing

```bash
# 1. Start OCaml gwd (required for OCaml backend or proxy calls)
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 2317 -lang en &
cd ..

# 2. Start Python server
source venv/bin/activate
BACKEND=ocaml python -m python_app.app

# 3. Test endpoints
curl http://localhost:2318/health
curl http://localhost:2318/test
curl "http://localhost:2318/test?p=Charles&n=Windsor"
```

### Integration with Tests

The Python proxy server will be integrated into integration and functional tests in future phases to validate:
- Backend toggle functionality
- Python vs OCaml output parity
- Dual-run validation

## Development Workflow

### Adding a New Route

1. Create handler in `python_app/routes/new_route.py`
2. Import in `python_app/app.py`
3. Add routing logic in `home()` function
4. Use `Config.is_python_backend()` to check backend
5. Use migrated functions when `BACKEND=python`
6. Proxy to OCaml via `OCamlBridge` when needed

### Adding a New Migrated Function

1. Implement function in `tests/python/utils/new_module.py`
2. Add unit tests in `tests/python/unit/test_new_module.py`
3. Export in `tests/python/utils/__init__.py`
4. Import in `python_app/migrated/__init__.py`
5. Use in route handlers when `BACKEND=python`

## Troubleshooting

### Import Errors

```bash
# Make sure you're in project root
cd Legacy-Project

# Activate venv
source venv/bin/activate

# Verify imports
python -c "from python_app.config import Config; print('OK')"
```

### OCaml gwd Not Running

```bash
# Check if gwd is running
ps aux | grep gwd

# Start gwd if needed
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 2317 -lang en &
```

### Port Conflicts

```bash
# Check if port is in use
lsof -ti:2318

# Kill process if needed
pkill -f "python.*python_app"
```

## Related Documentation

- **Main README**: Project overview and quick start
- **python_app/README.md**: Server-specific documentation
- **Migration Status**: `docs/MIGRATION_STATUS.md`
- **ADR-006**: Utility Function Migration Approach
- **ADR-007**: CI Quality Gates Strategy
- **Issue #225**: [MIG-INF-001] Create Python proxy server

---

**Last Updated**: January 2025  
**Status**: ✅ Infrastructure complete, routes proxy to OCaml  
**Next Phase**: Implement Python database access and template rendering

# Python Proxy Server – Operational Notes

## Admin passthrough (/admin)
- Requests to `/admin[/...]` are proxied to GeneWeb gwsetup (port 2316 inside the network).
- The proxy rewrites links in returned HTML so navigation stays under `/admin`:
  - `href`, `action`, and `src` attributes are rewritten to add `/admin` when needed.
  - Absolute URLs like `http://geneweb:2316/gwsetup?...` become `/admin/gwsetup?...`.

## Semicolon query parameters
- GeneWeb uses semicolons (`;`) as separators (e.g., `lang=en;v=list.htm`).
- The proxy preserves the original `request.query_string` to avoid converting `;` to `&`.

## Redirect rewriting
- `Location` headers from gwsetup/gwd are rewritten so redirects go through the proxy:
  - Backend URLs like `http://geneweb:2317/test?...` become `/test?...` (relative).
  - Admin URLs like `http://geneweb:2316/gwsetup?...` become `/admin/gwsetup?...`.

## POST and file uploads
- The proxy forwards form-encoded POST bodies and file uploads to gwsetup.
- For GET, the query string is appended to the backend URL verbatim.

## Security and hardening
- All HTTP requests are internal (container network/localhost) and have timeouts.
- Subprocess calls use fixed argument lists with `shell=False`.
- Bandit suppressions are scoped and documented:
  - `# nosec B603/B607` for safe subprocess usage (no shell, fixed args).
  - `# nosec B310` for internal HTTP to GeneWeb.
- Avoids bare `except/pass`; failures fall back to returning original content.

## Ports and targets
- gwd (frontend) default test port: 23179 (mapped from 2317)
- gwsetup (admin) default test port: 23176 (mapped from 2316)
- Proxy listens on 23182 (Flask)

## Known limitations
- HTML rewriting is best-effort and targeted to `href`, `action`, and `src`.
- If upstream changes markup significantly, additional rewrite rules may be needed.

