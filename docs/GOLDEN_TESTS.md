# Golden Master Tests

Golden tests freeze key GeneWeb outputs (HTML + GEDCOM) and validate that future runs match these references. They are used to ensure Python migration preserves OCaml behavior.

## Prerequisites
- GeneWeb runtime present under `GeneWeb/` (`gw/gwd`, `gw/gwb2ged`, and a base in `bases/`).
- Locale/timezone pinned for deterministic output:
  - `LC_ALL=C.UTF-8`
  - `TZ=UTC`

## Create references (local)
```bash
export LC_ALL=C.UTF-8 TZ=UTC
chmod +x scripts/golden/run_golden.sh
./scripts/golden/run_golden.sh create
# References are written to tests/golden/goldens/v1/
```
Commit the generated files.

## Validate (local/CI)
```bash
./scripts/golden/run_golden.sh validate
```
- Exits 0 on success, 1 on diff.
- Diffs are saved to `tests/golden/reports/diff.txt`.

## What is snapshotted
Routes in `scripts/golden/run_golden.sh` (EN/FR home, person, family, lists, calendar, trees, and extra search/list pages). The harness:
- Detects the base name (`test` or `base`).
- Normalizes volatile data: query time, random dice icons, age strings, non‑breaking spaces, and absolute paths inside HTML comments (`<!-- gw/etc/*.txt -->`).
- Exports GEDCOM and normalizes timestamps.

## CI integration
Golden validation is optional and runs when:
- Manually triggered: Actions → CI → Run workflow → `run_golden=true`.
- Relevant files change (paths filter): `GeneWeb/**`, `scripts/golden/**`, `tests/golden/**`, `python_app/routes/**`, `python_app/migrated/**`.
- A PR has the label `golden`.

CI never auto‑creates references. Creation is done locally and committed, then CI validates.

## Troubleshooting
- gwd not ready: The harness waits for startup; CI adds an extra delay. Ensure ports are free.
- etc_dir warnings: The CI/runner pre‑creates `bases/etc` so gwd can write `etc/<base>`.
- Path differences inside HTML comments: Normalized by the harness; recreate references only if content truly changed.

## Updating references
If a legitimate change affects output (template update, intentional wording change):
1) Update code/templates.
2) Recreate goldens locally: `run_golden.sh create`.
3) Review diffs, commit the new references, and mention in PR description.

## Stabilizing calendar goldens

GeneWeb calendar pages are time-dependent by default. To keep golden outputs stable in CI:

- We pin calendar routes to a fixed date using the proper parameter names:
  - Gregorian: `?m=CAL&yg=YYYY&mg=MM&dg=DD`
- The golden runner (`scripts/golden/run_golden.sh`) uses:
  - `calendar::?m=CAL&yg=2025&mg=10&dg=30`
  - `calendar_fixed::?m=CAL&yg=1999&mg=12&dg=15`

This avoids diffs caused by the current day of week, lunar phase, or Julian day.

### Adding new routes
- Prefer fixed parameters for any time-dependent page.
- Keep query strings exactly as served by GeneWeb (semicolon usage is allowed elsewhere, but calendar routes use `&`).
