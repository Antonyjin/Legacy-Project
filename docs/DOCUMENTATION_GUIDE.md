# Documentation Guide

## Philosophy
**Keep it simple. Avoid redundancy. Update once, reference everywhere.**

## What to Document (Priority Order)

### 1. ✅ **Wiki** (Single Source of Truth)
**Location**: `wiki/`

**Update when**:
- Adding new features
- Changing how things work
- New test coverage
- Operational procedures change

**Key pages**:
- `02-Product-Runbook.md` - How to run/operate
- `03-Quality-Test-Protocols.md` - What tests exist
- `03-Quality-Test-Policy.md` - Testing strategy

**Example**: When adding a golden test, update `03-Quality-Test-Protocols.md` to list it.

### 2. ✅ **README Files** (Quick Start)
**Location**: `README.md`, `tests/golden/README.md`, etc.

**Update when**:
- Setup process changes
- New dependencies added
- Quick start instructions change

**Keep brief**: Link to wiki for details.

### 3. ✅ **Commit Messages** (What Changed)
**Format**:
```
type: brief description (#issue)

- Bullet points of changes
- What was added/fixed/changed
- Testing notes if relevant
```

**Examples**:
```bash
feat: Add family page golden test (#91)

- Add family_charles route to run_golden.sh
- Create golden reference (50KB normalized)
- Update wiki test protocols
- Tested locally: PASSED
```

```bash
fix: Skip tree/search tests - require Sosa config (#50 #51)

- Document Sosa requirement in runbook
- Update CI to skip these routes
- Add detailed skip rationale docs
- Tests: 100% feasible coverage (5/7 effective)
```

### 4. ✅ **GitHub Issue Comments** (When Closing)
**Keep brief**:
```markdown
Implemented in commit abc123.

Changes:
- [What was done]

Tested: PASSED
```

**That's it!** No need for lengthy explanations.

## What NOT to Document

### ❌ Individual Issue Completion Documents
**Don't create**: `ISSUE_XX_COMPLETED.md` for every issue

**Why not**:
- Redundant with commit messages
- Time-consuming
- Gets out of sync
- Nobody reads them

**Exception**: Complex meta-issues or major milestones

### ❌ Close Comment Templates
**Don't create**: `ISSUE_XX_CLOSE_COMMENT.md`

**Why not**: Just write the comment directly on GitHub

### ❌ Duplicate Information
**Don't**: Copy same info to multiple places

**Do**: Write once in wiki, reference from elsewhere

## Current Documentation Structure

```
docs/
├── DOCUMENTATION_GUIDE.md          # This file
└── Issues/
    ├── INTEGRATION_TEST_STATUS.md  # Meta-summary (keep)
    ├── ISSUE_50_SKIPPED.md         # Explains skip decision (keep)
    ├── ISSUE_51_SKIPPED.md         # Explains skip decision (keep)
    └── TEST_DATABASE_INFO.md       # Database reference (keep)

wiki/
├── 01-Legacy-*.md                  # Project context
├── 02-Product-*.md                 # How to run/operate
├── 03-Quality-*.md                 # Testing strategy
├── 04-Standards-*.md               # Coding standards
├── 05-Deployment-*.md              # Deployment guides
└── 06-Governance-*.md              # ADRs, methodology

tests/golden/
└── README.md                       # How to use golden tests

GeneWeb/
└── README.md                       # How to run GeneWeb
```

## Documentation Workflow

### When Implementing a Feature:

1. **Write code** with clear comments
2. **Update wiki** if behavior changes
3. **Update README** if setup changes
4. **Commit** with descriptive message
5. **Close issue** with brief GitHub comment

**Time**: ~5 minutes total

### When Closing an Issue:

**On GitHub**:
```markdown
Implemented in commit [hash].

✅ [What was done]
✅ Wiki updated: [page]
✅ Tested: PASSED

Closes #XX
```

**Time**: ~2 minutes

## Examples

### Good Documentation Flow:

**Scenario**: Add new golden test for family page

1. **Code**: Update `run_golden.sh`, create golden
2. **Wiki**: Update `03-Quality-Test-Protocols.md` to list new test
3. **README**: Update `tests/golden/README.md` with new route
4. **Commit**:
   ```
   feat: Add family page golden test (#91)
   
   - Add family_charles route
   - Create golden reference (50KB)
   - Update wiki and README
   - Tested: PASSED
   ```
5. **GitHub**: Close #91 with "Implemented in commit abc123. Tested: PASSED."

**Total time**: 5 minutes  
**Result**: Clear, concise, no redundancy

### Bad Documentation Flow (Don't Do This):

1. ❌ Create `ISSUE_91_DETAILED_ANALYSIS.md`
2. ❌ Create `ISSUE_91_IMPLEMENTATION_PLAN.md`
3. ❌ Create `ISSUE_91_TESTING_REPORT.md`
4. ❌ Create `ISSUE_91_COMPLETED.md`
5. ❌ Write 10-page document explaining everything

**Total time**: 2 hours  
**Result**: Nobody reads it, gets outdated, waste of time

## Meta-Documentation (Exceptions)

**Do create** summary documents for:
- ✅ Test coverage summaries (`INTEGRATION_TEST_STATUS.md`)
- ✅ Complex decisions that need explanation (`ISSUE_50_SKIPPED.md`)
- ✅ Database/data references (`TEST_DATABASE_INFO.md`)
- ✅ Major milestones (100% coverage achieved)

**These are valuable** because they:
- Track overall progress
- Explain complex decisions
- Provide reference information
- Are consulted regularly

## Quick Reference

| Scenario | Action | Time |
|----------|--------|------|
| Add feature | Update wiki + commit message | 5 min |
| Close issue | Brief GitHub comment | 2 min |
| Major milestone | Create summary doc | 15 min |
| Complex decision | Create explanation doc | 20 min |
| Regular issue | ❌ No completion doc | 0 min |

## Remember

**Good documentation is**:
- ✅ Concise
- ✅ Up-to-date
- ✅ Easy to find
- ✅ Single source of truth

**Bad documentation is**:
- ❌ Redundant
- ❌ Lengthy
- ❌ Scattered
- ❌ Out of sync

**When in doubt**: Update the wiki, write a good commit message, move on.

---

**This guide saves you hours of documentation time while maintaining quality!**

