# GeneWeb Legacy Restoration Project - Roadmap

## Project Overview

The GeneWeb Legacy Restoration Project aims to restore, secure, test, and deploy the legacy OCaml genealogy software **GeneWeb** (1995-2008) without altering its core behavior. This document outlines the strategic roadmap for the project across phases.

## Vision

Transform a legacy 30-year-old OCaml genealogy system into a well-tested, documented, and containerized application suitable for modern deployment and maintenance.

## Project Phases

### Phase 1: Foundation & Testing Infrastructure ✅ COMPLETE

**Duration:** Weeks 1-3
**Status:** ✅ Complete

#### Objectives
- Establish Python test infrastructure for black-box testing
- Create comprehensive unit test suite (191 tests)
- Document project structure and architecture
- Setup CI/CD pipeline with GitHub Actions
- Implement code quality gates (Black, Pylint, Mypy)

#### Deliverables
- ✅ Python test framework with pytest
- ✅ 191 unit tests passing (CI blocking)
- ✅ 87 integration tests (32 passing, 54 process issues)
- ✅ Coverage tracking (>80% on unit tests)
- ✅ CI/CD workflow with multiple test types
- ✅ Code quality tools (Black, Pylint, Mypy, Bandit)
- ✅ Branch protection rules on main

#### Key Commits
- `db25185` - CI/CD foundation complete
- `1615418` - Branch protection setup
- `601c470` - Code quality tools configuration

### Phase 2: Deployment & Operations ✅ IN PROGRESS

**Duration:** Weeks 4-6
**Status:** 🟡 In Progress

#### Objectives
- Create Docker containerization strategy
- Document deployment procedures (local, Docker, production)
- Establish operational monitoring and health checks
- Create ADR documentation for major decisions
- Complete integration test fixes
- Enable golden tests validation

#### Current Status
- ✅ Docker Dockerfile created
- ✅ Docker Compose setup for gwd + proxy
- ✅ Deployment guide documentation
- ✅ ADR documents (004-007)
- ✅ CI/CD guide documentation
- ⚠️ Integration tests (process management issues)
- ⏳ Golden tests (awaiting re-enablement)

#### Key Commits
- `091ad20` - Deployment guide
- `b496103` - ADR-004: Migration Strategy
- `ac38adf` - ADR-005: Testing Approach
- `9007036` - ADR-006: Deployment Platform
- `0efdd4a` - ADR-007: CI/CD Pipeline

### Phase 3: Migration Planning ⏳ UPCOMING

**Duration:** Weeks 7-9
**Status:** 🔜 Not Started

#### Objectives
- Design OCaml → Python migration strategy
- Create Python proxy server foundation (MIG-INF-001)
- Implement black-box test approach for safe migration
- Plan incremental migration modules
- Establish feature parity validation

#### Planned Deliverables
- Python proxy server with BACKEND toggle
- Migration strategy documentation
- Feature parity test suite
- Safe migration procedures
- Incremental module decomposition plan

#### Current Progress
- ✅ Python proxy server (flask-based, MIG-INF-001)
- ⏳ Full feature parity tests (in development)
- ⏳ Migration modules roadmap

### Phase 4: Incremental Module Migration ⏳ UPCOMING

**Duration:** Weeks 10-16
**Status:** 🔜 Not Started

#### Objectives
- Migrate utilities and helpers first (safest)
- Migrate data types and structures
- Migrate business logic (incrementally)
- Migrate UI/web components
- Validate each module with black-box tests

#### Planned Modules
1. **Utilities** (low risk)
   - Date/calendar functions
   - String utilities
   - File utilities

2. **Data Types** (medium risk)
   - GEDCOM structures
   - Person/family records
   - Database models

3. **Business Logic** (medium-high risk)
   - Search functions
   - Relationship calculations
   - GEDCOM import/export

4. **Web Components** (high risk)
   - Route handlers
   - HTML generation
   - Templating

#### Testing Strategy
- Unit tests for each migrated function
- Black-box regression tests comparing OCaml ↔ Python
- Integration tests in proxy server
- Golden tests for HTML/GEDCOM output stability

### Phase 5: Validation & Optimization ⏳ UPCOMING

**Duration:** Weeks 17-20
**Status:** 🔜 Not Started

#### Objectives
- Complete golden test suite
- Performance benchmarking (OCaml vs Python)
- Security audit and hardening
- Documentation completion
- User acceptance testing

#### Planned Deliverables
- Full golden test coverage
- Performance reports
- Security assessment report
- Complete API documentation
- User guides and tutorials

### Phase 6: Production Release ⏳ UPCOMING

**Duration:** Weeks 21+
**Status:** 🔜 Not Started

#### Objectives
- Production deployment procedures
- Monitoring and alerting setup
- Disaster recovery planning
- Community documentation
- Release management

## Key Metrics

### Testing Coverage
- **Unit Tests:** 191 tests (✅ passing)
- **Integration Tests:** 87 tests (32 passing, 54 needs fix)
- **Functional Tests:** In development
- **Golden Tests:** Disabled (planned re-enablement Week 4-6)
- **Coverage Target:** >80% on critical paths

### Quality Gates
- ✅ Black: Code formatting
- ✅ Pylint: Code style and errors
- ✅ Mypy: Type checking
- ✅ Bandit: Security scanning
- 📊 Coverage: >80% on unit tests

### Performance Targets
- **Startup time:** <2 seconds (gwd)
- **Page load:** <500ms median
- **Query response:** <1 second (typical)
- **GEDCOM import:** <1GB file size supported

## Risk Management

### Critical Risks

1. **OCaml Behavior Preservation** (High)
   - **Risk:** Python migration changes behavior
   - **Mitigation:** Black-box testing, golden tests, feature parity validation

2. **Data Integrity** (High)
   - **Risk:** GEDCOM import/export data loss
   - **Mitigation:** Roundtrip testing, backup procedures, validation

3. **Performance Regression** (Medium)
   - **Risk:** Python slower than OCaml
   - **Mitigation:** Benchmarking, optimization, selective migration

4. **Integration Test Instability** (Medium)
   - **Risk:** Process management issues causing flaky tests
   - **Mitigation:** Fix process handling, add retries, improve health checks

### Medium Risks

1. **Legacy Code Dependencies** (Medium)
   - **Risk:** Hidden dependencies in OCaml codebase
   - **Mitigation:** Comprehensive testing, incremental approach

2. **Documentation Gaps** (Medium)
   - **Risk:** Incomplete documentation during migration
   - **Mitigation:** Document as we go, maintain wiki

## Success Criteria

### End of Phase 2 (Current)
- ✅ 191 unit tests passing
- ✅ 32+ integration tests passing
- ✅ Complete deployment documentation
- ✅ ADR documentation complete
- ✅ CI/CD pipeline stable

### End of Phase 3
- Python proxy server operational
- Migration strategy validated
- Feature parity framework established
- Safe migration procedures documented

### End of Phase 4
- At least 30% of codebase migrated
- All migrated modules fully tested
- Golden tests re-enabled
- Zero regression in migrated features

### End of Project
- 100% of features migrated or validated
- >95% test coverage
- Production deployment ready
- Complete documentation suite

## Timeline Summary

```
Phase 1: Foundation          [####] ✅ COMPLETE (Weeks 1-3)
Phase 2: Deployment          [##--] 🟡 IN PROGRESS (Weeks 4-6)
Phase 3: Migration Planning  [-----] ⏳ UPCOMING (Weeks 7-9)
Phase 4: Module Migration    [-----] ⏳ UPCOMING (Weeks 10-16)
Phase 5: Validation          [-----] ⏳ UPCOMING (Weeks 17-20)
Phase 6: Production Release  [-----] ⏳ UPCOMING (Weeks 21+)
```

## Dependencies & Prerequisites

- **Python 3.11+** - Test infrastructure and proxy server
- **Docker** - Containerization and deployment
- **OCaml compiler** - Understanding legacy code
- **Git/GitHub** - Version control and CI/CD
- **Linux/macOS** - Development environment

## Stakeholders

- **Project Lead:** Responsible for overall direction
- **QA Team:** Testing and validation
- **DevOps Team:** Deployment and infrastructure
- **Developers:** Code migration and implementation
- **Documentation Team:** Documentation and user guides

## Review Schedule

- **Weekly:** Progress on current phase
- **Bi-weekly:** Risk assessment and mitigation
- **Monthly:** Roadmap adjustment based on learnings
- **Phase-end:** Comprehensive review and next phase planning

---

**Last Updated:** October 2025
**Next Review:** End of Week 6 (Phase 2 completion)
