# Data registry

No restricted or licensed unit-process datasets belong in this repository.

Every contributed dataset must include a registry record based on
`provenance-template.json`, with:

- creator and contact;
- source or DOI;
- measurement or modeling method;
- geography and reference year;
- functional unit and system boundary;
- uncertainty and data-quality assessment;
- license and redistribution permission; and
- version and change history.

Recommended open sources include EPD program operators, EPA eGRID, the Federal
LCA Commons, NREL datasets, public manufacturer documentation, and original
measurements released under an explicit data license.

New benchmark packages should validate against
`schemas/data-package.schema.json`. CSV starting points are available in
`data/templates/`. A data package must include SHA-256 checksums for every file;
metadata alone is not a substitute for preserving raw and processed data.

## Acquired data organization

The [`SOURCES.md`](SOURCES.md) registry describes every acquired provider
family, its role, citation, and redistribution constraint. Provider-native raw
files belong under `private-data/incoming/` and are excluded from version
control.

`data/derived/` contains only compact, reviewable outputs used by the public
screening example. Regenerate them and their complete local-file checksum
manifest with:

```bash
python scripts/refresh_public_data.py
```

Derived records do not erase the original dataset boundary. Always follow the
UUID or field code back to the cited provider record before using a factor in a
publication.
