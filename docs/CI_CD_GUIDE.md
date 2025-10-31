# CI/CD Guide

This guide explains the GeneWeb project's CI/CD pipeline, how it works, and how to use it.

## Overview

The project uses **GitHub Actions** for continuous integration and continuous deployment:

- **CI (Continuous Integration)**: Tests run automatically on every push and pull request
- **CD (Continuous Deployment)**: Code is automatically deployed to staging on successful tests
- **Manual Production Deployment**: Production requires manual approval

## What Runs When

### On Pull Request (PR)

```
Push to feature branch
        ↓
[Lint & Format Check] ← Must pass
        ↓
[Unit Tests] ← Must pass (blocks PR if fails)
        ↓
[Integration Tests] ← Must pass (blocks PR if fails)
        ↓
[Golden Master Tests] ← Informational (doesn't block yet)
        ↓
[Build Docker Image] ← For testing only, not pushed
```

**Result**: If all tests pass, PR can be merged after review approval.

### On Push to Main

```
Merge PR to main
        ↓
[All Tests Run] ← Same as PR
        ↓
[Build & Push Docker Image]
        ↓
[Deploy to Staging]
        ↓
[Smoke Tests on Staging]
        ↓
Manual: Deploy to Production (click button)
```

### On Tag (Release)

```
Git tag v1.0.0
        ↓
[All Tests Run]
        ↓
[Build Docker Image]
        ↓
[Create GitHub Release]
        ↓
[Push to Docker Registry]
        ↓
Manual: Deploy to Production
```

## Test Types & What They Check

### 1. Lint & Format (1 min)

**Checks**:
- Python code style (pylint)
- Code formatting (black)
- Import sorting (isort)

**Result**: ✅ Pass = clean code style

**Failure Example**:
```
E501 line too long (145/120 characters) (line-too-long)
C0304 final newline missing (missing-final-newline)
```

### 2. Unit Tests (5 min)

**Checks**:
- 191 individual function tests
- Each function tested in isolation
- OCaml behavior verified against Python
- Code coverage >85%

**Result**: ✅ Pass = functions work correctly

**Failure Example**:
```
FAILED tests/python/unit/test_name_lower.py::test_name_lower
AssertionError: 'john' != 'JOHN'
```

### 3. Integration Tests (10 min)

**Checks**:
- Multi-component workflows (GEDCOM import/export)
- Database operations
- Concurrent requests
- Error handling

**Result**: ✅ Pass = system works end-to-end

**Failure Example**:
```
FAILED tests/python/integration/test_gedcom_roundtrip.py
RuntimeError: gwd failed to start on port 23179
```

### 4. Golden Master Tests (5 min)

**Checks**:
- Output matches known-good reference ("golden")
- Detects any unexpected changes
- 12 golden references (HTML pages, GEDCOM exports)

**Status**: ℹ️ Currently informational (doesn't block)

**Example Output**:
```
Golden test: GEDCOM export
Expected lines: 245
Actual lines: 245
✓ PASSED
```

**If it fails**:
```
Golden test: GEDCOM export
Expected lines: 245
Actual lines: 243
✗ FAILED - Output differs

--- expected
+++ actual
@@ -15,3 +15,2 @@
 DATE 1 JAN 1950
```

## Reading CI Results

### GitHub Actions Dashboard

1. Go to **Actions** tab in repository
2. Click on the workflow run (shows commit message)
3. See test results by stage:
   - ✅ Green checkmark = passed
   - ❌ Red X = failed
   - ⏭️ Skipped = not run

### Checking Your PR

1. Create a pull request
2. GitHub automatically runs tests
3. See status below PR title:
   ```
   ✅ All checks passed - Ready to merge
   or
   ❌ Some checks failed - Fix and push again
   ```

### Understanding Test Failures

**Click on the failed check** to see details:

```
FAILED tests/python/unit/test_sosa_kinship.py::test_sosa_generation_number

Expected:
  Person 1 generation number: 0

Actual:
  Person 1 generation number: -1

Help: Check that sosa_kinship() handles root person correctly
```

## How to Fix CI Failures

### Lint/Format Failures

```bash
# Auto-fix style issues
black .
isort .

# Push fixed code
git add .
git commit -m "fix: Format code"
git push
```

### Unit Test Failures

```bash
# Run failing test locally
pytest tests/python/unit/test_name_lower.py::test_name_lower -v

# Debug: Add print statements
# Fix the bug
# Push fix
git add .
git commit -m "fix: Correct name_lower function"
git push
```

### Integration Test Failures

```bash
# Start gwd first
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
cd ..

# Run test
pytest tests/python/integration/test_gedcom_import.py -v

# Fix the issue
# Clean up
pkill -f gwd
```

### Golden Test Failures

If golden test fails, output might have changed intentionally:

```bash
# Review the diff
# If changes are correct, regenerate golden
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
cd ..

./scripts/golden/run_golden.sh create
pytest tests/golden/ -v

pkill -f gwd
```

## Branch Protection Rules

The `main` branch is protected:

- ✅ **Unit tests must pass**
- ✅ **Integration tests must pass**  
- ✅ **Code review approval required** (1 reviewer)
- ℹ️ **Golden tests** (informational)
- ℹ️ **Coverage tracking** (>80% target)

If any **required** check fails, you **cannot merge**. You must:

1. Fix the issue
2. Push the fix
3. Wait for tests to pass
4. Then merge

## Deployment Workflow

### Deploying to Staging

1. Create a pull request
2. All tests pass
3. Get code review approval
4. **Merge to main**
5. GitHub Actions automatically:
   - Builds Docker image
   - Pushes to staging
   - Runs smoke tests

### Deploying to Production

1. Ensure staging is working
2. Go to **Actions** tab
3. Find the workflow run for main
4. Click **Review deployments**
5. Approve for **Production**
6. Deployment starts
7. Monitor in Actions tab

## Creating a Release

### Step 1: Tag the Commit

```bash
# Make sure you're on main and everything is committed
git checkout main
git pull origin main

# Create a tag
git tag v1.0.0  # Follow semantic versioning

# Push tag
git push origin v1.0.0
```

### Step 2: GitHub Automatically

1. Detects the tag
2. Runs all tests
3. Creates a GitHub Release
4. Builds Docker image with tag `v1.0.0`
5. Pushes to Docker registry

### Step 3: Monitor

1. Go to **Actions** tab
2. See release workflow running
3. Go to **Releases** tab to see new release
4. Release includes:
   - Release notes (from git commits)
   - Docker image ready for deployment

## Understanding diff.txt

When golden tests fail, a `diff.txt` file might be generated showing:

```diff
--- expected (OCaml output)
+++ actual (Python output)
@@ -15,3 +15,2 @@
 DATE 1 JAN 1950
 NAME John Doe
-EXTRA LINE
+DIFFERENT LINE
```

**Legend**:
- `-` = Line in expected but missing in actual
- `+` = Line in actual but not in expected
- No prefix = Line matches

**Actions**:
- If differences are bugs: Fix code
- If differences are intentional: Update golden reference

## Performance

**Total CI time**: ~20-25 minutes

```
Lint:              1 min  ┐
Unit Tests:        5 min  ├─ Can run in parallel = 10 min total
Integration Tests: 10 min ┘
Golden Tests:      5 min  ┐
                          ├─ Can run in parallel with above
Build Docker:      5 min  ┘
├─ Deploy to Staging: 2 min
└─ Smoke Tests: 1 min
```

## Troubleshooting CI

### "Tests pass locally but fail in CI"

**Possible causes**:
- Different Python version (CI uses 3.11)
- Different OCaml version
- Environment variables not set
- Timing issues in CI runner

**Solution**: Check CI logs for exact error

### "Random test failures"

**Possible causes**:
- Port conflicts (if gwd not properly stopped)
- Timing-sensitive tests
- File system permissions

**Solution**: Run tests locally to reproduce

### "CI stuck / not running"

**Possible causes**:
- GitHub Actions quota exceeded
- Runner offline
- Workflow disabled

**Solution**: Check Actions tab for status

## Best Practices

1. **Run tests locally before pushing**
   ```bash
   pytest tests/ -v
   ```

2. **Read CI logs carefully**
   - Scroll to the error
   - Read the full error message
   - Don't ignore warnings

3. **One commit per feature**
   - Easier to identify issues
   - Cleaner history

4. **Write descriptive commit messages**
   ```
   fix: Correct date validation in date_validate()
   
   The function was not properly handling February dates
   in leap years. Added test case and fixed logic.
   ```

5. **Keep PRs focused**
   - One feature per PR
   - Easier to review
   - Easier to bisect if issues

## Key Contacts

- **CI Issues**: Check GitHub Issues (label: `ci`)
- **Deployment Help**: See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Test Help**: See [Testing documentation](docs/TESTING.md)

## Summary

| What | When | Time | Required |
|------|------|------|----------|
| Lint | Every push | 1 min | ✅ Yes |
| Unit Tests | Every push | 5 min | ✅ Yes |
| Integration Tests | Every push | 10 min | ✅ Yes |
| Golden Tests | Every push | 5 min | ℹ️ No |
| Deploy to Staging | Push to main | 2 min | ✅ Automatic |
| Deploy to Prod | Manual | 2 min | ⏳ Manual |

**Pro Tips**:
- Always check CI results before leaving your desk
- Fix CI failures immediately (don't accumulate)
- Use git tags for production releases
- Monitor staging before deploying to production
