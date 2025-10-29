# Python Integration Tests

## Current Status

**87 tests implemented** ⚠️ (32 passing, 54 failing, 1 failed)

| Test Suite | Tests | Status |
|------------|-------|--------|
| IT-PY-001: Server Lifecycle | 12 | ✅ Passing |
| IT-PY-002: API Routes | 9 | ✅ Passing |
| IT-PY-003: Database Access | 7 | ✅ Passing |
| IT-PY-004: HTML Generation | 10 | ❌ **Failing** (process management) |
| IT-PY-005: GEDCOM Roundtrip | 6 | ✅ Passing |
| IT-PY-006: Localization | 9 | ❌ **Failing** (process management) |
| IT-PY-007: Authentication | 9 | ❌ **Failing** (process management) |
| IT-PY-008: Error Handling | 13 | ❌ **Failing** (process management) |
| IT-PY-009: Performance | 11 | ❌ **Failing** (process management) |
| **Total** | **87** | **32 Passing, 54 Failing** |

## Overview

Integration tests validate **interactions between GeneWeb components**:
- `gwd` daemon (HTTP server)
- Database files (`.gwb` format)
- Template system (HTML generation)
- Network stack (HTTP protocol)
- Process management (startup/shutdown)

## Why Integration Tests?

| Test Type | What It Tests | Example |
|-----------|---------------|---------|
| **Unit Test** | Single behavior in isolation | HTTP parameter parsing |
| **Integration Test** | Component interactions | `gwd` + database + HTTP |
| **Functional Test** | End-to-end user workflows | Search → Results → Person page |

**Integration tests sit in the middle** - they validate that components work together correctly.

## Test Structure

### IT-PY-001: HTTP Server Lifecycle

**File**: `test_server_lifecycle.py`

**What it tests**: GeneWeb daemon (`gwd`) process management

**Components tested**:
```
┌─────────────┐
│ Python Test │
└──────┬──────┘
       │ subprocess.Popen()
       ▼
┌─────────────┐
│ gwd process │ ◄─ Start, stop, monitor
└──────┬──────┘
       │ Binds to port
       ▼
┌─────────────┐
│  HTTP :2317*│ ◄─ Test connections
└──────┬──────┘
       │ Reads database
       ▼
┌─────────────┐
│ bases/*.gwb │
└─────────────┘
```

## Running the Tests

### Prerequisites

1. **GeneWeb binaries** must exist in `GeneWeb/gw/`:
   ```bash
   ls GeneWeb/gw/gwd  # Should exist
   ```

2. **Test database** must exist:
   ```bash
   ls GeneWeb/bases/test.gwb/  # Should contain database files
   ```

3. **Python virtual environment + dependencies** (recommended):
   ```bash
   # Create and activate venv
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```
   ```bash
   pip install -r requirements.txt
   ```

### Execute Tests

```bash
# All integration tests
pytest tests/python/integration/ -v

# Specific test file
pytest tests/python/integration/test_server_lifecycle.py -v

# Exclude slow tests
pytest tests/python/integration/ -v -m "not slow"

# Specific test class
pytest tests/python/integration/test_server_lifecycle.py::TestServerStartup -v
```

### Environment Variables

Tests use deterministic settings (see `conftest.py`):

```bash
export LC_ALL=C.UTF-8   # Consistent locale
export TZ=UTC           # Consistent timezone
```

## Test Coverage

### ✅ Implemented Tests

#### IT-PY-001: HTTP Server Lifecycle

**File**: `test_server_lifecycle.py`

| Test | What It Validates | Acceptance Criteria |
|------|-------------------|---------------------|
| **Server Startup** | `gwd` starts and binds to port | Process alive, responds to HTTP |
| **Server Responds** | HTTP 200 on requests | Valid HTML, correct content |
| **Server Shutdown** | Graceful (SIGTERM) and force (SIGKILL) | Process terminates, port released |
| **Multiple Servers** | Independent instances on different ports | No interference between servers |
| **Concurrent Requests** | Handles multiple simultaneous requests | ≥80% success rate (OCaml limitation) |
| **Rapid Requests** | Handles fast sequential requests | All requests succeed |

#### IT-PY-002: API Routes

**File**: `test_api_route.py`

Tests all major GeneWeb API routes return expected responses:
- Home page (/)
- Person page (?p=X&n=Y)
- Family page (?m=F)
- Search (?m=S)
- Calendar (?m=CAL)
- Statistics (?m=STAT)
- Tree pages (?m=A, ?m=D)

#### IT-PY-003: Database Access ✅

**File**: `test_database_access.py` (7 tests)

**What it tests**: Database operations via HTTP API

**Components tested**:
```
┌─────────────┐
│ Python Test │
└──────┬──────┘
       │ HTTP GET
       ▼
┌─────────────┐
│ gwd (HTTP)  │ ◄─ Serves requests
└──────┬──────┘
       │ Reads data
       ▼
┌─────────────┐
│ test.gwb    │ ◄─ OCaml database format
│ (188 people)│
└─────────────┘
```

**Tests**:
1. `test_person_data_retrieval` - Fetch person from database
2. `test_multiple_persons_exist` - Query different individuals
3. `test_person_data_persistence` - Data consistency across requests
4. `test_family_relationships_exist` - Parent/spouse links
5. `test_search_uses_database` - Search queries access data
6. `test_database_handles_unknown_person` - 404 for missing persons
7. `test_database_encoding_support` - UTF-8 characters

**Known Issues**:
- **OCaml `gwd` daemonizes**: Parent process exits immediately after forking
  - **Solution**: Check HTTP response, not process status
  - **Cleanup**: Use `pkill` to kill all child processes on port
- **HTML volatility**: Don't compare HTML byte-by-byte
  - **Solution**: Check semantic data (names, dates, places) instead

#### IT-PY-004: HTML Generation

**File**: `test_html_generation.py`

Tests HTML template rendering:
- Valid HTML structure
- Content rendering
- Person page data binding
- Date rendering
- Statistics data
- Calendar information
- HTML encoding
- Search results
- Family names

#### IT-PY-005: GEDCOM Roundtrip

**File**: `test_gedcom_roundtrip.py`

Tests GEDCOM export/import:
- GEDCOM file creation via `gwb2ged`
- Valid GEDCOM format (HEAD, TRLR, INDI records)
- Person records preservation
- Date information
- UTF-8 encoding
- Family relationships

#### IT-PY-006: Localization

**File**: `test_localization.py`

Tests multi-language support:
- English pages (lang=en)
- French pages (lang=fr)
- French translation content
- Language parameter effectiveness
- Person page language support
- Search language support
- Statistics language support
- Calendar language support
- Unknown language fallback

#### IT-PY-007: Authentication

**File**: `test_authentication.py`

Tests authentication and access control:
- Public page access
- Public person page access
- Search accessibility
- Statistics accessibility
- Wizard mode parameter recognition
- Base access
- Multiple public requests
- Session handling
- Concurrent public access

#### IT-PY-008: Error Handling

**File**: `test_error_handling.py`

Tests graceful error handling:
- Missing person handling
- Malformed name parameters
- Empty parameters
- Invalid query parameters
- Very long parameters
- Unicode characters
- SQL injection attempts
- XSS attempts
- Server stability after errors
- Rapid invalid requests
- Missing base name handling
- Timeout recovery
- Concurrent error requests

#### IT-PY-009: Performance

**File**: `test_performance.py`

Tests performance characteristics:
- Home page load time (<2s)
- Person page load time (<2s)
- Search page load time (<3s)
- Statistics page load time (<3s)
- Calendar page load time (<2s)
- Repeated request consistency
- Rapid sequential requests
- Concurrent request performance
- Response size validation
- Large response handling
- Sustained load handling

## 🚨 Critical Process Management Issues

### **54 Tests Failing Due to OCaml Daemonization**

**Problem**: Most integration tests fail with:
```
RuntimeError: gwd exited unexpectedly while starting
```

**Root Cause**: OCaml `gwd` daemonizes (parent process exits immediately after forking), but tests check `proc.poll()` which returns 0 (successful exit) instead of `None` (still running).

**Solution Applied in IT-PY-003**: 
- Replace `proc.poll()` checks with HTTP readiness checks
- Use `pkill` for reliable cleanup of all child processes
- Check `is_running()` method instead of process status

**Files Needing Fix**:
- `test_html_generation.py` (10 tests) - **IT-PY-004**
- `test_authentication.py` (9 tests) - **IT-PY-007** 
- `test_error_handling.py` (13 tests) - **IT-PY-008**
- `test_localization.py` (9 tests) - **IT-PY-006**
- `test_performance.py` (11 tests) - **IT-PY-009**

**Fix Pattern**:
```python
# ❌ Wrong (fails with daemonization)
if self.proc.poll() is not None:
    raise RuntimeError("gwd exited unexpectedly while starting")

# ✅ Correct (works with daemonization)
if not self.is_running():
    raise RuntimeError("gwd not responding to HTTP requests")
```

## Known Issues & Limitations

### 1. OCaml Concurrency Limits

**Problem**: `gwd` may drop connections under heavy concurrent load (10+ simultaneous requests).

**Symptoms**:
```
requests.exceptions.ConnectionError: ('Connection aborted.', 
  RemoteDisconnected('Remote end closed connection without response'))
```

**Why**: OCaml `gwd` uses single-threaded event loop with limited connection pooling.

**Solution in Tests**: Accept ≥80% success rate for concurrent request tests.

**Migration Goal**: Python version should handle 100% of concurrent requests.

**Example**:
```python
def test_server_handles_concurrent_requests(self, geneweb_dir):
    # OCaml gwd has concurrency limits - accept 80% success rate
    assert success_rate >= 0.8, f"Success rate {success_rate:.0%} too low"
```

### 2. Port Conflicts

**Problem**: Tests may fail if port 23180-23181 are already in use.

**Symptoms**:
```
OSError: [Errno 48] Address already in use
```

**Solutions**:
```bash
# Check if port is in use
lsof -i :23180

# Kill existing gwd
pkill -f "gwd.*-p 23180"

# Or run tests with different port
pytest --base-port 24000
```

**In Tests**: We kill existing processes before starting:
```python
# Implemented in GeneWebServer.start()
subprocess.run(["pkill", "-f", f"gwd.*-p {port}"], check=False)
```

### 3. File Handle Leaks

**Problem**: `gwd` log files may not close properly if tests crash.

**Symptoms**:
```
ResourceWarning: unclosed file <_io.FileIO name='/tmp/gwd_test.log'>
```

**Solution in Tests**: Explicitly close files in cleanup:
```python
def stop(self, graceful: bool = True):
    if self.log_file and not self.log_file.closed:
        self.log_file.close()  # ← Close before killing process
    self.process.kill()
```

**Manual Cleanup**:
```bash
# Remove orphaned log files
rm -f /tmp/gwd_test.log
```

### 4. Process Zombies

**Problem**: Killed `gwd` processes may become zombies if not properly reaped.

**Symptoms**:
```bash
ps aux | grep gwd
# Shows: gwd <defunct>
```

**Solution in Tests**: Use `process.wait()` after `kill()`:
```python
self.process.kill()
self.process.wait()  # ← Reap zombie process
```

### 5. Database Lock Files

**Problem**: `.lck` files may persist if tests crash.

**Symptoms**:
```
gwd: database is locked
```

**Solution**:
```bash
# Remove lock files
rm -f GeneWeb/bases/test.lck
rm -f GeneWeb/bases/test.gwb/*.lck
```

**Not in Tests**: Lock files are database-level, not test-level.

## GeneWebServer Helper Class

The `GeneWebServer` class manages `gwd` lifecycle for tests:

### Usage

```python
# As context manager (recommended)
with GeneWebServer(geneweb_dir, port=23180) as server:
    response = requests.get("http://localhost:23180/test")
    assert response.status_code == 200
# Automatically stops on exit

# Manual control
server = GeneWebServer(geneweb_dir, port=23180)
server.start()
try:
    # ... tests ...
finally:
    server.stop()
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `start(timeout=5)` | Start `gwd` and wait for ready | `True` if started |
| `is_running()` | Check if server responds | `True` if responding |
| `stop(graceful=True)` | Stop server (SIGTERM or SIGKILL) | `True` if graceful |

### Parameters

```python
GeneWebServer(
    geneweb_dir: str,      # Path to GeneWeb/ directory
    port: int = 23180,     # Port to bind (default: 23180)
    base_name: str = "test" # Database name (default: "test")
)
```

### Implementation Details

**Startup**:
```python
gwd -hd ./gw -bd ./bases -p 23180 -lang en
```

**Ready Check**:
- Polls `http://localhost:{port}/{base}` every 0.2s
- Timeout after 5 seconds
- Returns `True` if HTTP 200, `False` otherwise

**Shutdown**:
- Graceful: `SIGTERM` → wait 3s → `SIGKILL` if needed
- Force: `SIGKILL` immediately

## Debugging Failed Tests

### 1. Check gwd Logs

```python
# Logs are in /tmp/gwd_test.log
tail -f /tmp/gwd_test.log
```

### 2. Run Tests with Verbose Output

```bash
pytest tests/python/integration/ -vv --tb=short
```

### 3. Run Single Test

```bash
pytest tests/python/integration/test_server_lifecycle.py::TestServerStartup::test_server_starts -vv
```

### 4. Check for Orphaned Processes

```bash
ps aux | grep gwd
# Kill if needed:
pkill -f gwd
```

### 5. Verify Database

```bash
ls -la GeneWeb/bases/test.gwb/
# Should show: base, base.acc, fnames.*, names.*, snames.*, strings.*
```

## Success Criteria

✅ **All tests pass** against OCaml GeneWeb  
✅ **Tests are deterministic** (no flaky tests)  
✅ **Fast execution** (<1s per test file)  
✅ **Clear failure messages** (easy debugging)  
✅ **Proper cleanup** (no orphaned processes/files)

### Example Validation

**Before Migration (OCaml)**:
```
test_server_handles_concurrent_requests: 80% success rate ⚠️
(OCaml limitation)
```

**After Migration (Python)**:
```
test_server_handles_concurrent_requests: 100% success rate ✅
(Python improvement)
```

## Related Documentation

- **Test Policy**: `wiki/03-Quality-Test-Policy.md`
- **ADR-004**: Python Testing Strategy (`wiki/06-Governance-ADR-004-Python-Testing.md`)
- **Unit Tests**: `tests/python/unit/README.md`
- **Functional Tests**: `tests/python/functional/README.md`
- **CI Workflow**: `.github/workflows/ci.yml`

## Common Questions

**Q: Why start/stop gwd for each test?**  
A: Isolation. Each test gets a clean server state. This prevents test pollution.

**Q: Why accept 80% success rate for concurrent requests?**  
A: OCaml gwd has documented concurrency limits. We're testing the reality, not the ideal.

**Q: What if a test fails in CI but passes locally?**  
A: Check for port conflicts, timing issues, or resource limits in CI environment.

**Q: Why not mock the server?**  
A: Integration tests validate REAL interactions. Mocks would hide OCaml limitations.

**Q: How do I add a new integration test?**  
A: 
1. Create test class in `test_server_lifecycle.py` or new file
2. Use `@pytest.mark.integration` and `@pytest.mark.requires_gwd`
3. Use `GeneWebServer` helper for server management
4. Document any OCaml limitations discovered

