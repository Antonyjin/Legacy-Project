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

### ✅ FT-PY-010: i18n

**File**: `test_i18n.py` (4 tests)

**User Story**: As a user, I want to use the application in multiple languages.

**Test Scenario**:
1. Switch between languages
2. Verify translations display correctly
3. Check date format changes
4. Test multiple language support

**Tests**:
1. `test_i18n_language_switch_works` - Language switching works
2. `test_i18n_translations_displayed` - Translations shown correctly
3. `test_i18n_date_format_changes` - Date format adapts to language
4. `test_i18n_multiple_languages_supported` - Multiple languages work
### ✅ FT-PY-009: Privacy

**File**: `test_privacy.py` (4 tests)

**User Story**: As a user, I want privacy rules to protect sensitive data.

**Test Scenario**:
1. Test privacy rules hide private data
2. Verify public mode restrictions
3. Check access control works
4. Verify living person rules

**Tests**:
1. `test_privacy_rules_hide_private_data` - Private data is hidden
2. `test_privacy_public_mode_restrictions` - Public mode restricts access
3. `test_privacy_access_control_works` - Access control functions
4. `test_privacy_living_person_rules` - Living person rules applied
### ✅ FT-PY-008: Wizard

**File**: `test_wizard.py` (4 tests)

**User Story**: As a user, I want to add, edit, and delete persons in wizard mode.

**Test Scenario**:
1. Access wizard mode
2. Add a new person
3. Edit existing person
4. Verify changes persist

**Tests**:
1. `test_wizard_mode_accessible` - Wizard mode loads correctly
2. `test_wizard_add_person_works` - Adding person works
3. `test_wizard_edit_person_works` - Editing person works
4. `test_wizard_changes_persist` - Changes are saved
### ✅ FT-PY-007: GEDCOM

**File**: `test_gedcom.py` (5 tests)

**User Story**: As a user, I want to import and export GEDCOM files.

**Test Scenario**:
1. Export database to GEDCOM format
2. Import GEDCOM file
3. Verify data preservation in roundtrip
4. Test special character handling
5. Validate GEDCOM format

**Tests**:
1. `test_gedcom_export_works` - GEDCOM export succeeds
2. `test_gedcom_import_works` - GEDCOM import succeeds
3. `test_gedcom_roundtrip_data_preserved` - Data preserved in roundtrip
4. `test_gedcom_handles_special_chars` - Special characters handled
5. `test_gedcom_validates_format` - Format validation works
### ✅ FT-PY-006: Statistics

**File**: `test_statistics.py` (4 tests)

**User Story**: As a user, I want to view database statistics.

**Test Scenario**:
1. Navigate to statistics page
2. View individual/family counts
3. Verify statistics are accurate
4. Check data formatting

**Tests**:
1. `test_statistics_page_loads` - Statistics page displays correctly
2. `test_statistics_count_display` - Counts are displayed
3. `test_statistics_data_correct` - Statistics are accurate
4. `test_statistics_formats_properly` - Data formatted correctly

### 🔄 Planned Tests

- **FT-PY-002**: Person search workflow
- **FT-PY-003**: GEDCOM import/export workflow
- **FT-PY-004**: Data modification workflow
- **FT-PY-005**: Calendar navigation workflow
- **FT-PY-006**: Multi-language workflow
- **FT-PY-007**: Calendar navigation workflow
- **FT-PY-008**: Data modification workflow
- **FT-PY-009**: Error recovery workflow
- **FT-PY-010**: Performance under load workflow
- **FT-PY-011**: Additional feature workflows
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

### ✅ FT-PY-003: Person Page Display

**File**: `test_person_page.py` (5 tests)

**User Story**: As a user, I want to view a person's profile with all their information.

**Test Scenario**:
1. Navigate to person page
2. View person's name and dates
3. View family relationships
4. View life events
5. Verify all fields display correctly

**Tests**:
1. `test_person_page_loads_successfully` - Person page displays correctly
2. `test_person_name_displayed` - Name and surname shown properly
3. `test_person_dates_displayed` - Birth/death dates shown
4. `test_person_family_relationships_shown` - Parents, spouse, children displayed
5. `test_person_missing_data_handled` - Missing data handled gracefully

### ✅ FT-PY-004: Relationship Calculation

**File**: `test_relationship.py` (5 tests)

**User Story**: As a user, I want to find the relationship between two people.

**Tests**:
1. `test_relationship_page_loads` - Relationship calculation page loads
2. `test_direct_relationship_calculated` - Parent-child relationship found
3. `test_indirect_relationship_calculated` - Cousin relationships found
4. `test_no_relationship_handled` - Unrelated persons handled
5. `test_relationship_display_formatted` - Relationship displayed clearly

### ✅ FT-PY-005: Calendar

**File**: `test_calendar.py` (4 tests)

**User Story**: As a user, I want to view birthdays in a calendar format.

**Test Scenario**:
1. Navigate to calendar page
2. View birthdays by month/year
3. Filter birthdays by month
4. Navigate through calendar months

**Tests**:
1. `test_calendar_page_loads` - Calendar page displays correctly
2. `test_calendar_displays_birthdays` - Birthdays shown in calendar
3. `test_calendar_filters_by_month` - Month filtering works
4. `test_calendar_navigation_works` - Month navigation works

### 🔄 Planned Tests

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
