# Python Integration Tests

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

3. **Python dependencies**:
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

### ✅ Implemented (IT-PY-001)

| Test | What It Validates | Acceptance Criteria |
|------|-------------------|---------------------|
| **Server Startup** | `gwd` starts and binds to port | Process alive, responds to HTTP |
| **Server Responds** | HTTP 200 on requests | Valid HTML, correct content |
| **Server Shutdown** | Graceful (SIGTERM) and force (SIGKILL) | Process terminates, port released |
| **Multiple Servers** | Independent instances on different ports | No interference between servers |
| **Concurrent Requests** | Handles multiple simultaneous requests | ≥80% success rate (OCaml limitation) |
| **Rapid Requests** | Handles fast sequential requests | All requests succeed |

### 🔄 Planned (IT-PY-002 to IT-PY-010)

- **IT-PY-002**: API Routes (all major endpoints return 200)
- **IT-PY-003**: Database Access (read persons, families)
- **IT-PY-004**: HTML Generation (verify template rendering)
- **IT-PY-005**: Localization (i18n, lang=fr/en)
- **IT-PY-006**: GEDCOM Export (file creation, content validation)
- **IT-PY-007**: GEDCOM Import (roundtrip integrity)
- **IT-PY-008**: Logging System (verify log entries)
- **IT-PY-009**: Authentication (admin access, permissions)
- **IT-PY-010**: Performance Benchmarks (response times)

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

