## GeneWeb Legacy — OCaml Architecture and Data Flow

### High-level Architecture
GeneWeb is a monolithic OCaml suite exposing a built-in HTTP server. It renders pages from templates, performs genealogical computations, and reads/writes binary genealogy bases. The suite is composed of:

- `gwd` — OCaml web daemon. Responsibilities:
  - Serve HTTP on a configurable port (historically 2317).
  - Render HTML via `gw/etc/*.txt` and `gw/etc/templm/*` templates.
  - Execute domain algorithms (ancestors, descendants, Sosa numbering, relations, consanguinity).
  - Read/write GeneWeb base format (`.gwb` directory structure under `bases/`).
- `gwsetup` — OCaml admin/setup UI. Responsibilities:
  - Create/open GeneWeb bases.
  - Import GEDCOM (via `ged2gwb`) and export GEDCOM (via `gwb2ged`).
  - Manage configuration (`*.gwf`) and basic users/rights.
- Utilities
  - `ged2gwb` — Import GEDCOM 5.5.x into `.gwb` base.
  - `gwb2ged` — Export `.gwb` base to GEDCOM.
  - `gwu` — Text export/inspection.
  - Maintenance tools: `gwfixbase`, `gwdiff`, `gwrepl`, `update_nldb`.

### Runtime Layout (as in this repo)
- `gw/` — OCaml binaries and runtime assets
  - `etc/` — templates, JS, CSS, modules, and textual configuration
  - `images/` — UI images and module assets
  - `lang/` — lexicons and localization
  - `plugins/` — legacy plugin binaries (`*.cmxs`) and docs
  - Core binaries: `gwd`, `gwsetup`, `ged2gwb`, `gwb2ged`, `gwu`, etc.
- `bases/` — working data
  - Example bases: `base.gwb/`, `test.gwb/`, `smith.gwb/`
  - Lock/flag files: `*.lck`, `*.gwf` configurations
  - Logs: `comm.log`, `gwsetup.log`, `gw/gwd.log`
- Helper scripts
  - `geneweb.sh` — orchestrates local start of `gwsetup` then `gwd`
  - `gwd.sh` — direct launcher for `gwd`
  - `gwsetup.sh` — launcher for `gwsetup`

### Data Model and Storage
- Storage format: `.gwb` directory containing indexed, binary structures with companion indexes (`*.inx`, `*.acc`, `*.dat`). The base stores persons, families, names, strings, and relations.
- Configuration: `*.gwf` files define base-level configuration, language, and display settings.
- Templates/UI: files under `gw/etc/` define menus, pages, and components, often in text-based template language consumed by `gwd`.

### Typical Request Flow
1. Browser requests a page (e.g., individual, family, or tree).
2. `gwd` parses query parameters and loads the target base in `bases/<name>.gwb/`.
3. `gwd` computes the requested domain view (e.g., ancestors tree) using internal OCaml algorithms.
4. `gwd` selects and renders the appropriate template from `gw/etc/`, injecting computed data.
5. Response HTML, CSS, and JS are returned to the browser.

### Admin and Import/Export Flow
1. Operator accesses `gwsetup` to create/open a base.
2. For imports, `ged2gwb` is called to transform GEDCOM into `.gwb` structures.
3. For exports, `gwb2ged` reads `.gwb` and writes GEDCOM for interoperability.
4. `gwu` can dump textual representations for verification/diagnostics.

### Security and Access Considerations (legacy)
- Authentication and session management are legacy-style; deployments should be isolated or fronted by a modern reverse proxy.
- Languages and templates are file-based; changes affect rendering immediately.
- Logs are written under `bases/` and `gw/` as plain text.

### Ports and Launching
While ports can be configured, historically:
- `gwsetup` listens on a setup/admin port (commonly 2316).
- `gwd` listens on the main HTTP port (commonly 2317).

The provided script demonstrates startup ordering and logging locations:

```1:81:GeneWeb/geneweb.sh
#!/bin/sh
...
"$DIR/gw/gwsetup" -gd "$DIR/gw" -lang $LANG > gwsetup.log 2>&1 &
...
"$DIR/gw/gwd" -hd "$DIR/gw" > "$DIR/gw/gwd.log" 2>&1 &
```

### Key Takeaways for Restoration
- Preserve `.gwb` format and utilities; do not rewrite core OCaml logic.
- Operate `gwsetup` and `gwd` as-is, augmenting with modern wrappers (reverse proxy, TLS) if needed.
- Document base structure, ports, and operational procedures to ensure safe, compliant deployments without altering core behavior.


