# ADR-004: Migration Strategy

**Status**: Accepted  
**Date**: 2025-10-31  
**Deciders**: Antonyjin  
**Consequences**: High impact on project timeline and test coverage

## Context

The GeneWeb project is a legacy OCaml application (1995-2008) that needs to be modernized. We must maintain full backward compatibility while gradually migrating functionality to Python. This requires a clear strategy for:

1. **Which functions to migrate**: Priority-based selection
2. **How to migrate**: Black-box testing approach vs direct translation
3. **Validation**: Ensuring migrated code produces identical output
4. **Timeline**: Phased approach vs big-bang rewrite

## Problem

- Legacy OCaml codebase is difficult to maintain and extend
- No Python developers familiar with genealogy algorithms
- Risk of breaking functionality during migration
- Need to maintain production availability during transition

## Decision

We adopt a **phased, test-driven migration strategy** with the following principles:

### 1. Black-Box Testing Approach
- Treat OCaml binaries as "golden reference"
- Test migrated Python functions against OCaml output
- No need to understand exact OCaml implementation details
- Enables parallel development by teams unfamiliar with OCaml

### 2. Priority-Based Selection
- **Tier 1 (Immediate)**: Core name/date processing functions
  - `name_lower()` - Normalize names
  - `date_validate()` - Validate dates
  - `sosa_kinship()` - Calculate family relationships
  
- **Tier 2 (Month 2-3)**: Data I/O functions
  - GEDCOM import/export
  - Database query optimization
  
- **Tier 3 (Month 4+)**: Advanced features
  - Search algorithms
  - Report generation
  - Statistics calculation

### 3. Proxy Server Pattern
- New Python Flask proxy server acts as API gateway
- Can route requests to OCaml backend (default) or Python backend
- Allows A/B testing and gradual rollout
- Enables feature-flag based backend selection

### 4. Test-Driven Implementation
- Unit tests written before migration (black-box style)
- Tests validate output against OCaml golden references
- Integration tests verify end-to-end functionality
- Golden Master tests detect regressions

### 5. Staged Rollout
- **Phase 1**: All requests → OCaml backend
- **Phase 2**: Optional routes → Python backend (feature flag)
- **Phase 3**: Critical routes → Python backend
- **Phase 4**: Complete migration (OCaml fallback only)

## Consequences

### Positive
- ✅ Low risk of breaking production
- ✅ Enables parallel testing and development
- ✅ Clear validation criteria (black-box matching)
- ✅ Easy rollback if Python version has issues
- ✅ Reduces team ramp-up time (no OCaml knowledge needed)

### Negative
- ❌ Initial slower pace than direct rewrite
- ❌ Maintaining dual implementations (OCaml + Python)
- ❌ Higher testing overhead
- ❌ Performance parity may require optimization work

### Trade-offs
- **Safety vs Speed**: We prioritize safety over speed
- **Test Coverage vs Implementation Speed**: Heavy testing upfront
- **Code Duplication vs Maintenance**: Two implementations during transition

## Implementation Details

### Test Structure
```
tests/
├── unit/              # Black-box unit tests
│   ├── test_name_lower.py
│   ├── test_date_validate.py
│   └── test_sosa_kinship.py
├── integration/       # End-to-end tests
│   ├── test_gedcom_roundtrip.py
│   └── test_database_operations.py
└── golden/           # Regression tests
    ├── goldens/v1/
    │   ├── name_lower.golden
    │   ├── date_validate.golden
    │   └── sosa_kinship.golden
```

### Backend Toggle Implementation
```python
# python_app/app.py
@app.route('/test', methods=['GET'])
def handle_test():
    backend = os.getenv('BACKEND', 'ocaml')
    
    if backend == 'python':
        return python_backend.handle_test()
    else:
        return ocaml_backend.handle_test()
```

### Testing Workflow
```bash
# 1. Verify OCaml reference produces expected output
curl http://localhost:23179/test?p=Charles&n=Windsor > ocaml.html

# 2. Run Python version and compare
BACKEND=python python -m python_app.app
curl http://localhost:2318/test?p=Charles&n=Windsor > python.html

# 3. Compare outputs
diff ocaml.html python.html  # Should be identical

# 4. Run regression tests
pytest tests/golden/ -v
```

## Alternatives Considered

### Alternative 1: Complete Rewrite
- **Pros**: Clean break from OCaml, modern codebase
- **Cons**: High risk, long timeline, complete testing needed
- **Rejected**: Too risky for production system

### Alternative 2: Direct OCaml Translation
- **Pros**: Faster implementation
- **Cons**: Requires OCaml expertise, harder to validate
- **Rejected**: Team lacks OCaml knowledge

### Alternative 3: Strangler Fig Pattern
- **Pros**: Gradual migration with clear boundaries
- **Cons**: Complex routing logic, duplicate code
- **Selected**: This is our chosen approach

## Related Decisions

- **ADR-005**: Testing approach (unit, integration, golden tests)
- **ADR-006**: Deployment platform selection
- **ADR-007**: CI/CD pipeline design

## References

- Strangler Fig Pattern: https://martinfowler.com/bliki/StranglerFigApplication.html
- Black-Box Testing: https://en.wikipedia.org/wiki/Black-box_testing
- Golden Master Testing: https://en.wikipedia.org/wiki/Golden_master_testing
