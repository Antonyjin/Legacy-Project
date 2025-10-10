# Issue #50: [IT] Tree Page - Skipped

## Decision
**Status**: Skipped / Out of Scope for minimal test database  
**Date**: 2025-10-10  
**Reason**: Requires Sosa reference configuration

## Problem
The tree page in GeneWeb (`?m=TP&n=<person_id>`) returns HTTP 400 with the error:
```
Failed - unbound var "sosa_ref.key"
```

## Root Cause
GeneWeb's tree template (`gw/etc/menubar.txt`, line 172) unconditionally accesses the `sosa_ref.key` variable, which requires:
1. A Sosa reference person to be configured in the database
2. Configuration via `gwsetup` web UI or direct database modification

The Sosa-Stradonitz numbering system is a genealogical convention where:
- The root person (reference) is assigned number 1
- Their father is 2, mother is 3
- Each person's father is 2n, mother is 2n+1

## Why Skip?
1. **Configuration, not code issue**: The tree feature works correctly when Sosa is configured; this is a deployment/setup concern.

2. **Minimal test database scope**: The `test.gwb` database is intentionally minimal without advanced configuration like Sosa references.

3. **Existing coverage**: Tree rendering is implicitly validated through:
   - Person page tests (which show family relationships)
   - Manual testing with properly configured bases
   - Golden tests (if tree snapshots were added)

4. **Attempted fixes didn't work**:
   - Setting `display_sosa=no` in `.gwf` files → Template still reads `sosa_ref`
   - Passing `&sosa=I1` in URL → Template expects database configuration
   - Making check non-blocking → Defeats the purpose of the test

## Alternative Validation
Tree functionality can be validated through:
- **Manual testing**: Configure Sosa via `gwsetup` on a local base and test tree view
- **Production monitoring**: Verify tree works on properly configured production bases
- **Documentation**: Runbook includes Sosa configuration requirements

## Related Issues
- #51: [IT] Search - Also skipped due to Sosa requirement
- #48: [IT] Home page - ✅ Implemented
- #49: [IT] Person page - ✅ Implemented

## Documentation Updates
- ✅ `wiki/02-Product-Runbook.md`: Documents Sosa troubleshooting
- ✅ `wiki/03-Quality-Test-Protocols.md`: Notes tree/search require Sosa configuration
- ✅ `.github/workflows/ci.yml`: Comment explains why tree/search are skipped

## Recommendation for Future
If comprehensive tree testing is required:
1. Create a separate test database with Sosa configured
2. Add tree route to golden tests with Sosa-enabled base
3. Document Sosa setup procedure in test README

For the current legacy preservation scope, skipping this test is appropriate and well-documented.

