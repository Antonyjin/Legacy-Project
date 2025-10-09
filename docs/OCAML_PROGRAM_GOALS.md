## GeneWeb Legacy — OCaml Program Goals and Capabilities

### Core Goal
Provide a complete, self-hostable genealogy web application able to compute and display family origins and relationships of individuals from structured datasets. The OCaml programs must remain intact; our work documents, secures, and operationalizes them without altering core behavior.

### Capabilities Delivered by the OCaml Suite
- Data storage and access
  - Read/write GeneWeb `.gwb` bases with indexes for high performance on large datasets.
  - Manage persons, families, names, events, and notes.
- Web presentation
  - Serve localized HTML pages with templates and static assets from `gw/etc/` and `gw/images/`.
  - Provide multi-language UI via `gw/lang/`.
- Genealogical computations
  - Ancestors/descendants trees, kinship paths, Sosa/Ahnentafel numbering.
  - Consanguinity and relationship analysis.
  - Statistics and summaries across a base.
- Interoperability
  - Import from GEDCOM using `ged2gwb`.
  - Export to GEDCOM using `gwb2ged`.
  - Text export for audits using `gwu`.
- Administration
  - Base creation and maintenance via `gwsetup`.
  - Configuration through `*.gwf` files and setup UI.

### Non-Goals (to avoid altering the legacy core)
- No rewrite of OCaml binaries (`gwd`, `gwsetup`, utilities).
- No change to `.gwb` on-disk format or index structures.
- No replacement of templating engine embedded in `gwd`.

### Operational Objectives for Compliance and Security (around the legacy core)
- Provide runbooks and deployment guidance to host the legacy suite safely (reverse proxy, TLS, backups).
- Define quality and testing policies to verify behavior without modifying core code (e.g., Golden Master comparisons via exports with `gwu`/`gwb2ged`).
- Document data protection and access controls to align with modern standards (GDPR awareness, logs hygiene, network isolation).

### Evidence in Repository
Launchers and assets confirm the presence and invocation of OCaml components:

```1:4:GeneWeb/gwd.sh
#!/bin/sh
cd `dirname "$0"`
exec gw/gwd -blang -log gw/gwd.log "$@" > gw/gwd.log
```

```1:4:GeneWeb/gwsetup.sh
#!/bin/sh
cd `dirname "$0"`
cd bases
exec ../gw/gwsetup -gd ../gw "$@"
```

These call into `gw/gwd` and `gw/gwsetup` respectively, aligning with the goals above.


