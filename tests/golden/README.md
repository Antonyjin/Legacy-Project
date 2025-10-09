Golden tests (legacy behavior lock)

Overview
- Capture current outputs from legacy GeneWeb and compare against frozen references (goldens).
- Surfaces covered here:
  - GEDCOM export from an existing base (`test.gwb`)
  - HTML home page rendered by `gwd` on that base (English and French)

Directories
- goldens/v1/            # stored references (versioned)
- reports/               # validation diffs and artifacts
- tmp/                   # temporary files during test runs
- ../../GeneWeb/bases/   # uses `test.gwb` shipped in this repo

Usage
1) Create mode (first run — generate references)
   ```bash
   export LC_ALL=C.UTF-8 TZ=UTC
   ./scripts/golden/run_golden.sh create
   ```

2) Validate mode (subsequent runs — compare to references)
   ```bash
   export LC_ALL=C.UTF-8 TZ=UTC
   ./scripts/golden/run_golden.sh validate
   ```

Outputs
- goldens/v1/expected_export.ged.norm    # normalized GEDCOM export
- goldens/v1/expected_home.html.norm     # home page (English)
- goldens/v1/expected_home_fr.html.norm  # home page (French)
- reports/diff.txt (only on validate when differences exist)

Normalization
The script automatically normalizes volatile data to prevent false failures:
- **GEDCOM**: Removes timestamps (DATE/TIME fields)
- **HTML**: Removes random IDs (`?i=123` → `?i=RANDOM`), query times (`q_time = 0.007` → `q_time = TIME`)
- **Whitespace**: Trims trailing spaces and collapses multiple spaces

Notes
- If behavior is intentionally changed, re-run in create mode and commit the updated goldens with a short note in your PR.
- CI automatically runs validate mode on every push/PR.
- Linux users: download GeneWeb Linux binaries and run similarly; or configure the CI Linux job to validate on Ubuntu.

