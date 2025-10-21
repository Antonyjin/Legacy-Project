# CI/CD Workflow Guide

## 📋 Overview

**Platform**: GitHub Actions (free unlimited minutes on public repos)  
**Runner**: macOS-latest (required for prebuilt GeneWeb binaries)  
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

2. **OCaml/GeneWeb Tests**
   - **Smoke tests**: Start `gwd`, verify HTTP 200, check home page, person page, French localization, logging
   - **GEDCOM export test**: Export database, verify file exists and has content
   - **Golden tests**: Validate 10 HTML pages against frozen snapshots
   - **GEDCOM roundtrip**: Export → Import → Compare

3. **Python Tests** (NEW - added with Issue #97)
   - **Infrastructure test**: Verify pytest setup (must pass)
   - **Unit tests**: Test OCaml functions via HTTP (`continue-on-error: true` during Week 1)
   - **Integration tests**: Test component interactions (`continue-on-error: true` during Week 1-2)
   - **Functional tests**: Test end-to-end workflows (`continue-on-error: true` during Week 2-3)
   - **Coverage report**: Generate coverage report (target >80%)

4. **Artifacts Upload** (on failure)
   - Golden test diffs
   - Python coverage reports
   - Pytest logs

---

## 🎯 CI Evolution Timeline

### Week 1: Current State
- ✅ OCaml tests must pass (blocks merge)
- ✅ Python infrastructure test must pass
- ⏳ Python UT/IT/FT allowed to fail (`continue-on-error: true`)
- 📊 Coverage tracked but not enforced

### Week 2: Stabilization
- ✅ Python unit tests enforced (`continue-on-error: false`)
- ⏳ Python IT/FT allowed to fail
- 📊 Coverage visible in artifacts

### Week 3: Full Enforcement
- ✅ All tests must pass (OCaml + Python UT/IT/FT)
- ✅ Coverage >80% enforced
- 🚫 Merges blocked on failures

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

## 📊 What CI Tests

| Test Type | Count | Status | Enforced |
|-----------|-------|--------|----------|
| Smoke tests | 5 | ✅ Passing | Yes |
| Golden tests | 12 | ✅ Passing | Yes |
| Python infrastructure | 8 | ✅ Passing | Yes |
| Python unit tests | 0/9 | ⏳ TODO | No (Week 1) |
| Python integration tests | 0/10 | ⏳ TODO | No (Week 1-2) |
| Python functional tests | 0/10 | ⏳ TODO | No (Week 2-3) |

**Total**: 25 tests passing, 29 tests to implement

---

## 🚀 Next Steps

1. **Week 1**: Implement Python unit tests (UT-PY-002 to 010)
2. **Week 2**: Implement Python integration tests, enforce unit tests in CI
3. **Week 3**: Complete functional tests, enforce all tests, configure branch protection

---

## 📚 Related Files

- **CI Workflow**: `.github/workflows/ci.yml`
- **Test Policy**: `wiki/03-Quality-Test-Policy.md`
- **Test Protocols**: `wiki/03-Quality-Test-Protocols.md`
- **Pytest Guide**: `tests/python/README.md`

---

**Current Status**: ✅ CI configured with Python tests, infrastructure passing, ready for test implementation!
