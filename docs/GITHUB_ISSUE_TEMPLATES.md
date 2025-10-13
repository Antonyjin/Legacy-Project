# GitHub Issue Comment Templates

Quick templates for closing issues. Copy, customize, paste.

## Regular Feature/Test Implementation

```markdown
Implemented in commit [hash].

Changes:
- [What was added/changed]
- [Documentation updated]

Tested: PASSED
```

**Example**:
```markdown
Implemented in commit abc123.

Changes:
- Added family page golden test to run_golden.sh
- Updated wiki test protocols

Tested: PASSED (50KB golden created)
```

---

## Skipped/Won't Fix

```markdown
Closing as out of scope.

Reason: [Brief explanation]

Documentation: See [file] for details.

Alternative: [How to achieve this manually if needed]
```

**Example**:
```markdown
Closing as out of scope for minimal test database.

Reason: Tree/search pages require Sosa reference configuration via gwsetup.

Documentation: See docs/Issues/ISSUE_50_SKIPPED.md and wiki/02-Product-Runbook.md

Alternative: Configure Sosa root manually via gwsetup for production use.
```

---

## Bug Fix

```markdown
Fixed in commit [hash].

Issue: [What was broken]
Fix: [What was changed]

Tested: PASSED
```

**Example**:
```markdown
Fixed in commit def456.

Issue: CI failing with "Exec format error" on Ubuntu
Fix: Switched CI runner to macos-latest (matches bundled binaries)

Tested: PASSED (CI green)
```

---

## Meta-Issue/Epic Progress Update

```markdown
Progress update:

✅ Completed:
- [Item 1]
- [Item 2]

🔄 In Progress:
- [Item 3]

📋 Remaining:
- [Item 4]

Current status: [X/Y] complete ([Z]%)
```

**Example**:
```markdown
Progress update:

✅ Completed:
- Home page golden test
- Person page golden test
- Family page golden test

🔄 In Progress:
- Ancestor list golden test

📋 Remaining:
- Descendant list golden test
- Statistics page golden test

Current status: 3/6 complete (50%)
```

---

## Duplicate/Invalid

```markdown
Duplicate of #[number] / Invalid

[Brief explanation]
```

**Example**:
```markdown
Duplicate of #48

This functionality is already covered by the home page integration test.
```

---

## Blocked/Waiting

```markdown
Blocked by #[number]

Reason: [Why blocked]

Will resume after: [Condition]
```

**Example**:
```markdown
Blocked by #40

Reason: Need golden test framework established first

Will resume after: Golden test script is implemented and working
```

---

## Quick Reference

| Situation | Template | Time |
|-----------|----------|------|
| Implemented | Regular Feature | 1 min |
| Skipped | Won't Fix | 2 min |
| Fixed bug | Bug Fix | 1 min |
| Epic update | Progress Update | 3 min |
| Duplicate | Duplicate/Invalid | 30 sec |
| Blocked | Blocked/Waiting | 1 min |

---

**Remember**: Keep it brief. Link to commits/docs for details.

