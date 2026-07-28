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
