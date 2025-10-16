Golden tests (legacy behavior lock)

Overview
- Capture current outputs from legacy GeneWeb and compare against frozen references (goldens).
- Surfaces covered here:
  - GEDCOM export from an existing base (`test.gwb`)
  - GEDCOM import roundtrip (import → export → compare for data consistency)
  - HTML home page rendered by `gwd` on that base (English and French)
  - HTML person page (Charles Windsor) with key fields (name, person, id)
  - HTML family page (Charles Windsor's family) with parents, marriage info, children

Directories
- goldens/v1/            # stored references (versioned)
- reports/               # validation diffs and artifacts
- tmp/                   # temporary files during test runs
- ../../GeneWeb/bases/   # uses `test.gwb` shipped in this repo

Usage
1) Export/HTML Golden Tests
   a) Create mode (first run — generate references)
      ```bash
      export LC_ALL=C.UTF-8 TZ=UTC
      ./scripts/golden/run_golden.sh create
      ```

   b) Validate mode (subsequent runs — compare to references)
      ```bash
      export LC_ALL=C.UTF-8 TZ=UTC
      ./scripts/golden/run_golden.sh validate
      ```

2) GEDCOM Import Roundtrip Test
   a) Create mode (first run — generate reference)
      ```bash
      export LC_ALL=C.UTF-8 TZ=UTC
      ./scripts/golden/test_gedcom_import.sh create
      ```

   b) Validate mode (subsequent runs — compare to reference)
      ```bash
      export LC_ALL=C.UTF-8 TZ=UTC
      ./scripts/golden/test_gedcom_import.sh validate
      ```

Outputs
- goldens/v1/expected_export.ged.norm             # normalized GEDCOM export
- goldens/v1/expected_import_export.ged.norm      # GEDCOM import roundtrip reference
- goldens/v1/expected_home.html.norm              # home page (English)
- goldens/v1/expected_home_fr.html.norm           # home page (French)
- goldens/v1/expected_person_charles.html.norm    # person page (Charles Windsor)
- goldens/v1/expected_family_charles.html.norm    # family page (Charles Windsor's family)
- reports/diff.txt (only on validate when differences exist)
- reports/import_diff.txt (only on GEDCOM import test failures)

Normalization
The script automatically normalizes volatile data to prevent false failures:
- **GEDCOM**: Removes timestamps (DATE/TIME fields)
- **HTML**: Removes random IDs (`?i=123` → `?i=RANDOM`), query times (`q_time = 0.007` → `q_time = TIME`), dice icons (`fa-dice-one` → `fa-dice-RANDOM`)
- **Whitespace**: Trims trailing spaces and collapses multiple spaces

Notes
- If behavior is intentionally changed, re-run in create mode and commit the updated goldens with a short note in your PR.
- CI automatically runs validate mode on every push/PR.
- Linux users: download GeneWeb Linux binaries and run similarly; or configure the CI Linux job to validate on Ubuntu.

