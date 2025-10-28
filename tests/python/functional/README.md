# Python Functional Tests

## Overview

Functional tests validate **complete end-to-end user workflows** through the GeneWeb application. These tests simulate real user interactions and verify that the entire system works together correctly.

## Why Functional Tests?

| Test Type | What It Tests | Example |
|-----------|---------------|---------|
| **Unit Test** | Single behavior in isolation | HTTP parameter parsing |
| **Integration Test** | Component interactions | `gwd` + database + HTTP |
| **Functional Test** | End-to-end user workflows | Navigate home → person → family → parent |

**Functional tests validate complete user journeys** - they ensure users can accomplish their goals.

## Test Structure

### FT-PY-001: Tree Navigation ✅

**File**: `test_tree_navigation.py`

**User Story**: As a user, I want to navigate through the family tree to explore relationships.

**Test Scenario**:
1. Load home page
2. Click on a person
3. View their family (parents, children, spouse)
4. Navigate to parent
5. Verify breadcrumbs/navigation

**Tests**:
1. `test_home_page_loads_successfully` - Home page displays correctly
2. `test_click_on_person_loads_person_page` - Person page loads when clicked
3. `test_family_relationships_displayed_correctly` - Family info is shown
4. `test_navigate_to_parent_works` - Parent navigation works
5. `test_breadcrumbs_navigation_elements_present` - Navigation elements exist
6. `test_complete_navigation_workflow` - End-to-end workflow
7. `test_navigation_handles_missing_persons_gracefully` - Error handling
8. `test_navigation_preserves_url_parameters` - URL parameter handling

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
# All functional tests
pytest tests/python/functional/ -v

# Specific test file
pytest tests/python/functional/test_tree_navigation.py -v

# Specific test
pytest tests/python/functional/test_tree_navigation.py::TestTreeNavigation::test_home_page_loads_successfully -v

# With markers
pytest -m functional
```

### Environment Variables

Tests use deterministic settings (see `conftest.py`):

```bash
export LC_ALL=C.UTF-8   # Consistent locale
export TZ=UTC           # Consistent timezone
```

## Test Coverage

### ✅ Implemented Tests

#### FT-PY-001: Tree Navigation

**File**: `test_tree_navigation.py` (8 tests)

**What it tests**: Complete user navigation workflow

**Components tested**:
```
┌─────────────┐
│ User        │ ◄─ Simulates user actions
└──────┬──────┘
       │ HTTP requests
       ▼
┌─────────────┐
│ gwd (HTTP)  │ ◄─ Serves pages
└──────┬──────┘
       │ Reads data
       ▼
┌─────────────┐
│ test.gwb    │ ◄─ OCaml database format
│ (188 people)│
└─────────────┘
```

**Tests**:
1. `test_home_page_loads_successfully` - Home page displays correctly
2. `test_click_on_person_loads_person_page` - Person page loads when clicked
3. `test_family_relationships_displayed_correctly` - Family info is shown
4. `test_navigate_to_parent_works` - Parent navigation works
5. `test_breadcrumbs_navigation_elements_present` - Navigation elements exist
6. `test_complete_navigation_workflow` - End-to-end workflow
7. `test_navigation_handles_missing_persons_gracefully` - Error handling
8. `test_navigation_preserves_url_parameters` - URL parameter handling

**Known Issues**:
- **OCaml `gwd` daemonizes**: Parent process exits immediately after forking
  - **Solution**: Check HTTP response, not process status
  - **Cleanup**: Use `pkill` to kill all child processes on port
- **Test data dependency**: Tests rely on specific test data (Charles Windsor, Elizabeth, Philip)
  - **Solution**: Use known test persons from the test database

### ✅ FT-PY-002: Person Search

**File**: `test_person_search.py` (6 tests)

**User Story**: As a user, I want to search for a person by name and view results.

**Test Scenario**:
1. Enter search query in search form
2. Submit search
3. View search results page
4. Verify results are relevant
5. Click on a result to view person page

**Tests**:
1. `test_search_form_loads_successfully` - Search form displays correctly
2. `test_search_returns_results` - Search query returns matching results
3. `test_search_filters_correctly` - Search filters by name properly
4. `test_search_result_click_navigates` - Clicking result loads person page
5. `test_search_handles_no_results` - Empty/no results handled gracefully
6. `test_search_with_special_characters` - Special chars in search work

### 🔄 Planned Tests

- **FT-PY-003**: Person page display workflow
- **FT-PY-004**: Relationship calculation workflow
- **FT-PY-005**: Birthday calendar workflow
- **FT-PY-006**: Statistics page workflow
- **FT-PY-007**: GEDCOM import/export workflow
- **FT-PY-008**: Data modification workflow
- **FT-PY-009**: Privacy settings workflow
- **FT-PY-010**: Multi-language workflow

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

### 2. Test Data Dependency

**Problem**: Functional tests rely on specific test data being present.

**Current Dependencies**:
- Charles Windsor (test person)
- Elizabeth Windsor (mother)
- Philip Mountbatten (father)
- Diana Spencer (spouse)

**Solution**: Use consistent test data or create test fixtures.

### 3. Process Management

**Problem**: OCaml `gwd` daemonizes, making process management tricky.

**Solution**: Use HTTP readiness checks instead of process status checks.

## Debugging Guide

### Common Issues

1. **Server won't start**:
   ```bash
   # Check if port is in use
   lsof -i :23184
   
   # Kill existing processes
   pkill -f "gwd.*-p 23184"
   ```

2. **Tests fail with connection errors**:
   ```bash
   # Check server logs
   cat gwd_ft_23184.log
   
   # Verify server is running
   curl http://localhost:23184/test
   ```

3. **Missing test data**:
   ```bash
   # Verify test database exists
   ls GeneWeb/bases/test.gwb/
   
   # Check database contents
   ./GeneWeb/gw/gwc -c GeneWeb/bases/test.gwb
   ```

### Test Development Tips

1. **Start with simple workflows**: Begin with basic navigation before complex scenarios
2. **Use known test data**: Rely on consistent test persons from the database
3. **Test error cases**: Verify graceful handling of missing persons, invalid parameters
4. **Verify content**: Check that expected content appears in responses
5. **Test parameter handling**: Ensure URL parameters work correctly

## Migration Strategy

Functional tests serve as **Golden Master tests** for migration validation:

```
OCaml System → Run FT Tests → Capture Expected Behavior
     ↓
Python System → Run SAME FT Tests → Compare Behavior
     ↓
✅ Identical = Migration Success
❌ Different = Regression Detected
```

This ensures the Python migration maintains the same user experience as the OCaml system.
