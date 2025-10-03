## GeneWeb Legacy — Goals, Architecture, and OCaml Program Scope

### 1) Goal of the GeneWeb Project
GeneWeb is a historical, production-grade genealogy suite written in OCaml (initial phase 1995–2008, then maintained). It enables users and organizations to:
- Manage family trees (persons, families, events, notes)
- Compute ancestry/descendancy, kinship, Sosa/Ahnentafel numbering, and consanguinity
- Publish and browse genealogical data on the web with multi-language support
- Interoperate via the GEDCOM standard (import/export)

Where it lives in this repository:
- Binaries and runtime assets: `GeneWeb/gw/`
- Templates, JS, CSS, modules: `GeneWeb/gw/etc/`
- Languages and lexicons: `GeneWeb/gw/lang/`
- Images: `GeneWeb/gw/images/`
- Example/working bases: `GeneWeb/bases/` (`*.gwb/` folders, logs, configs)

### 2) GeneWeb Architecture (OCaml)
Monolithic OCaml suite with a built-in HTTP server and an admin tool:
- `gwd` — web daemon
  - Serves HTTP, renders templates from `gw/etc/`, performs genealogy computations
  - Reads/writes `.gwb` base format under `bases/`
- `gwsetup` — setup/admin UI
  - Creates/opens bases; drives import/export; manages base configuration (`*.gwf`)
- Utilities
  - `ged2gwb` (GEDCOM → GWB import), `gwb2ged` (GWB → GEDCOM export), `gwu` (text export)
  - Maintenance tools: `gwfixbase`, `gwdiff`, `gwrepl`, `update_nldb`

Runtime layout (excerpt):
- `GeneWeb/gw/` → core binaries and runtime assets
- `GeneWeb/bases/` → data (example bases, logs, lock files)
- `GeneWeb/geneweb.sh` → starts `gwsetup` then `gwd`
- `GeneWeb/gwd.sh` → direct launcher for `gwd`

Startup references (as-is in this repository):

```1:3:GeneWeb/gwd.sh
#!/bin/sh
cd `dirname "$0"`
exec gw/gwd -blang -log gw/gwd.log "$@" > gw/gwd.log
```

```42:43:GeneWeb/geneweb.sh
"$DIR/gw/gwsetup" -gd "$DIR/gw" -lang $LANG > gwsetup.log 2>&1 &
sleep 1
```

```57:58:GeneWeb/geneweb.sh
"$DIR/gw/gwd" -hd "$DIR/gw" > "$DIR/gw/gwd.log" 2>&1 &
sleep 1
```

Typical request flow:
1. Browser → `gwd` (HTTP) with base and page parameters
2. `gwd` loads `bases/<name>.gwb/`, computes view (ancestors, profile, etc.)
3. `gwd` renders `gw/etc/` templates and returns HTML/JS/CSS

Admin/import/export flow:
1. Operator uses `gwsetup` to create/open a base
2. `ged2gwb` imports GEDCOM into `.gwb`; `gwb2ged` exports `.gwb` back to GEDCOM
3. `gwu` dumps textual output for verification

Notes for safe operation (legacy):
- Authentication/session are legacy; prefer running behind a reverse proxy with TLS
- `.gwb` is a binary, indexed format with companion files (`*.inx`, `*.acc`, `*.dat`)
- Logs are plain text under `bases/` and `gw/`

### 3) Goal and Scope of the OCaml Program
What the OCaml core must continue to provide (do not rewrite):
- Data storage and retrieval in `.gwb` bases
- Web rendering using GeneWeb templates and assets
- Genealogical computations (ancestors/descendants, kinship, Sosa, consanguinity)
- Interoperability via GEDCOM import/export
- Admin operations through `gwsetup` and `*.gwf` configuration

Non-goals (to keep the core intact):
- No rewrite of `gwd`, `gwsetup`, or utilities
- No changes to `.gwb` on-disk format or indexing
- No replacement of the embedded templating engine

Operational objectives around the legacy (documentation/compliance):
- Provide clear run instructions and deployment notes (reverse proxy, TLS, backups)
- Define testing policy without altering behavior (e.g., compare outputs via `gwu`/`gwb2ged`)
- Align with data protection expectations (visibility of logs, network isolation)

Status
- This document consolidates the legacy overview, architecture, and OCaml program goals into a single reference under `docs/`.


