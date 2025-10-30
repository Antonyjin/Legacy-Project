# Branch Protection Setup (GitHub)

This repo uses GitHub Actions CI. To block merges when CI fails, add a protection rule on `main`.

## Prerequisite
- Ensure `.github/workflows/ci.yml` is on `main` and has run at least once. GitHub only lists checks that have run on the protected branch.
  - Actions → select the CI workflow → Run workflow on `main`, or push a trivial commit to `main`.

## Steps
1. GitHub → Settings → Branches → Add branch protection rule
2. Branch name pattern: `main`
3. Enable:
   - Require a pull request before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Require conversation resolution before merging
   - Block force pushes
   - Do not allow bypassing the above settings (optional)
4. Under “Status checks”, add (after they’ve run on `main` at least once):
   - `Quality Gates (format + lint + types + security)`
   - `Tests + Coverage (macOS)`
5. Save changes

## Notes
- If the checks list is empty, the workflow hasn’t run on `main` yet. Trigger it, then return and add the checks.
- You can later tighten requirements (e.g., add code owners, linear history) if needed.
