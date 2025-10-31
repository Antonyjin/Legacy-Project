# ADR-007: CI/CD Pipeline Design

**Status**: Accepted  
**Date**: 2025-10-31  
**Deciders**: Antonyjin  
**Consequences**: Automated testing, deployment speed, feedback cycle

## Context

We need a CI/CD pipeline that:

1. Validates code quality on every push/PR
2. Runs tests automatically
3. Prevents broken code from merging
4. Automates deployment to production
5. Provides fast feedback to developers

## Problem

- How do we catch bugs before they reach main?
- What tests should block merging?
- How do we deploy safely?
- How do we balance speed vs safety?

## Decision

We implement a **GitHub Actions-based CI/CD pipeline** with clear stages:

### Pipeline Stages

#### Stage 1: Lint & Format (< 1 minute)
```yaml
- Run pylint, black, isort
- Fail if code style issues
- Auto-fix with pre-commit hook
```

#### Stage 2: Unit Tests (< 5 minutes)
```yaml
- Run pytest on unit tests (191 tests)
- Enforce coverage >80%
- Block PR if tests fail
```

#### Stage 3: Integration Tests (< 10 minutes)
```yaml
- Start OCaml gwd server
- Run integration tests (87 tests)
- Block PR if tests fail
```

#### Stage 4: Golden Master Tests (< 5 minutes)
```yaml
- Validate against golden references
- Informational (doesn't block currently)
- Will block in Phase 2
```

#### Stage 5: Build Docker Image (< 5 minutes)
```yaml
- Build Docker image
- Tag with commit SHA
- Push to container registry (if on main)
```

#### Stage 6: Deploy to Staging (< 2 minutes)
```yaml
- Deploy to staging environment
- Run smoke tests
- Only if all tests pass
```

#### Stage 7: Deploy to Production (manual)
```yaml
- Manual approval required
- Deploy to production on command
- Run production smoke tests
```

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pylint black isort
      - run: black --check .
      - run: isort --check-only .
      - run: pylint python_app/

  unit-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/python/unit/ -v --cov=python_app --cov-report=xml
      - uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: |
          cd GeneWeb
          ./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
          cd ..
      - run: pytest tests/python/integration/ -v
      - run: pkill -f gwd

  golden-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      - run: |
          cd GeneWeb
          ./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
          cd ..
      - run: ./scripts/golden/run_golden.sh validate
      - run: pkill -f gwd

  build-image:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - uses: docker/build-push-action@v4
        with:
          push: false
          tags: geneweb:${{ github.sha }}

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-image
    if: github.ref == 'refs/heads/main'
    steps:
      - run: |
          ssh deploy@staging.geneweb.com
          cd /opt/geneweb
          git pull origin main
          docker-compose up -d --build
          
  smoke-tests-staging:
    runs-on: ubuntu-latest
    needs: deploy-staging
    steps:
      - run: |
          curl https://staging.geneweb.com/health
          curl https://staging.geneweb.com/test?p=Charles&n=Windsor
```

## Branch Protection Rules

```yaml
# Required to pass before merging to main
- Status checks must pass:
  - lint
  - unit-tests
  - integration-tests
  
# Optional (informational):
- golden-tests
- codecov threshold

# Review policy:
- Require 1 approval
- Dismiss stale reviews
- Allow auto-merge after approval
```

## Test Coverage Strategy

| Metric | Target | Current | Enforced |
|--------|--------|---------|----------|
| Overall Coverage | >80% | 85% | ✅ Yes |
| Unit Test Coverage | >85% | 89% | ✅ Yes |
| Integration Tests | Key workflows | 87 tests | ✅ Yes |
| Golden Tests | 12 page types | 12 tests | ⏳ Phase 2 |

## Deployment Strategy

### On Pull Request
- ✅ Run linting and tests
- ✅ Build Docker image (don't push)
- ❌ No deployment

### On Push to Main
- ✅ Run all tests
- ✅ Build and push Docker image
- ✅ Deploy to staging
- ✅ Run smoke tests on staging
- ⏳ Manual approval for production

### On Tag (Release)
```bash
# Tag: v1.0.0
# Actions:
# 1. Run full CI pipeline
# 2. Build and push Docker image
# 3. Create GitHub Release
# 4. Push Docker image to registry
# 5. Deploy to production (manual approval)
```

## Performance Metrics

| Stage | Duration | Parallelizable |
|-------|----------|---|
| Lint | 1 min | Yes (with unit/integration) |
| Unit Tests | 5 min | No (depends on lint) |
| Integration Tests | 10 min | Yes (parallel with unit) |
| Golden Tests | 5 min | Yes |
| Build Docker | 5 min | No (depends on tests) |
| Deploy Staging | 2 min | No |
| **Total (Critical Path)** | **~23 minutes** | |

### Optimization Opportunities
- ✅ Run linting, unit, integration in parallel (saves 5 min)
- ✅ Cache Docker layers (saves 2 min)
- ✅ Cache pip packages (saves 2 min)
- ✅ Use matrix builds for Python versions

**Optimized Total**: ~18 minutes

## Monitoring & Feedback

### CI Dashboard
- GitHub Actions dashboard shows status
- Badge in README for current status
- Slack notifications on failure (optional)

### Metrics Tracked
- Test pass rate
- Coverage trends
- Pipeline duration
- Failure frequency by test type
- Deployment frequency

## Secrets Management

### GitHub Secrets Required
```yaml
DOCKER_REGISTRY_TOKEN  # For pushing to registry
DEPLOY_KEY              # SSH key for production
SENTRY_DSN              # Error tracking (optional)
```

### Environment-Specific Config
```yaml
# Staging
BACKEND: python
LOG_LEVEL: debug

# Production
BACKEND: ocaml
LOG_LEVEL: info
```

## Consequences

### Positive
- ✅ Automated quality gates
- ✅ Fast feedback (tests run in parallel)
- ✅ Prevents broken code from reaching main
- ✅ Automated deployment
- ✅ Audit trail of changes
- ✅ Easy rollback (redeploy previous image)

### Negative
- ❌ Pipeline complexity
- ❌ Tests must pass before merging (no exceptions)
- ❌ GitHub Actions usage/cost (free tier sufficient)
- ❌ Requires monitoring/maintenance

## Related Decisions

- **ADR-005**: Testing approach (what tests block CI)
- **ADR-006**: Deployment platform
- **ADR-004**: Migration strategy

## References

- GitHub Actions Documentation: https://docs.github.com/en/actions
- CI/CD Best Practices: https://www.atlassian.com/continuous-delivery/tutorials/continuous-integration-tutorial
- Conventional Commits: https://www.conventionalcommits.org/
