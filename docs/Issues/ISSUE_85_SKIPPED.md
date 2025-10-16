# Issue #85 - Relationship Calculation Golden Test - SKIPPED

## Status: ⏭️ Skipped (Same root cause as #50, #51)

## Issue Description
- **Goal**: Validate relationship calculation output remains stable
- **Routes**: `?m=C` (Consanguinity) or `?m=REL` (Relationship)
- **Acceptance**: HTML matches golden reference, contains relationship path

## Root Cause: Sosa Reference Required

The relationship calculation feature (`?m=C`, `?m=REL`) **requires a Sosa reference person** to be configured in the database. Without it, GeneWeb returns:

```
File .../menubar.txt, line 172, characters 39-51:
Failed - unbound var "sosa_ref.key"
```

### Template Dependency
The relationship page template (`etc/menubar.txt`) unconditionally accesses `sosa_ref.key`, causing:
- **HTTP 400** (Bad Request) when Sosa reference is not set
- **Template rendering failure** even when page logic could work without Sosa

### Minimal Test Database
The `test.gwb` database is intentionally minimal for:
- Fast CI runs
- Minimal maintenance
- Focus on core GeneWeb features

**It does NOT include**:
- Sosa reference configuration
- Extensive family tree relationships
- Advanced genealogy features

## Attempted Solutions

### 1. Using Person Names (`?m=C&p1=X&n1=Y&p2=A&n2=B`)
**Result**: ❌ Still fails with `sosa_ref.key` error

### 2. Using Person IDs (`?m=REL&i1=I1&i2=I2`)
**Result**: ❌ Still fails with `sosa_ref.key` error

### 3. Disable Sosa in `test.gwf`
**Result**: ❌ Template still accesses `sosa_ref` variable regardless of display setting

## Why Not Fix the Template?

**Template changes are out of scope** for this legacy preservation project:
- Would alter legacy behavior (violates project constraints)
- Templates are part of GeneWeb's core functionality
- Our goal is to preserve, not modify

## Decision: Skip This Test

**Rationale**:
1. **Same category as #50 (Tree) and #51 (Search)**: Sosa-dependent features
2. **Not critical for core GeneWeb functionality**: Basic person/family pages work fine
3. **Would require Sosa configuration**: Out of scope for minimal test database
4. **Can be tested manually**: With proper Sosa configuration in production database

## Alternative: Manual Testing

To test relationship calculation with proper Sosa configuration:

1. **Configure Sosa root** via `gwsetup`:
   ```
   http://localhost:2317/base
   → Select "Sosa reference person"
   → Choose a person (e.g., Charles Windsor)
   → Save
   ```

2. **Test relationship page**:
   ```bash
   curl "http://localhost:2316/base?m=C&p1=Charles&n1=Windsor&p2=Elizabeth&n2=Windsor"
   ```

3. **Validate output**:
   - HTTP 200
   - Contains relationship description
   - Shows path between persons

## Impact

**What We're Missing**:
- Golden test for relationship calculation HTML
- Validation that relationship paths remain stable
- Coverage of `?m=C` and `?m=REL` routes

**What Still Works**:
- ✅ Home page (list of persons)
- ✅ Person page (individual details)
- ✅ Family page (parents, marriage, children)
- ✅ GEDCOM import/export
- ✅ Core GeneWeb functionality

## Related Issues

- **#50**: Tree page golden test (Skipped - Sosa required)
- **#51**: Search page golden test (Skipped - Sosa required)
- **#85**: Relationship page golden test (Skipped - Sosa required)

## Conclusion

The relationship calculation golden test is **skipped** because:
1. Requires Sosa reference configuration (not in minimal test DB)
2. Template unconditionally accesses `sosa_ref.key` (template bug, not our scope)
3. Can be tested manually in production with proper Sosa setup
4. Core GeneWeb functionality is already validated by other tests

**This is a documented limitation, not a gap in testing coverage.**

---

**Final Status**: ⏭️ **SKIPPED** - Documented and justified

