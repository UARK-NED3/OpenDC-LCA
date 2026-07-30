# openLCA and Brightway interoperability

OpenDC-LCA exchanges **foreground inventories**, not proprietary databases or
LCIA methods. Geography, allocation, system model, flow mapping, and impact
method compatibility remain explicit study decisions.

## Read openLCA JSON-LD

```bash
opendc-lca openlca-inspect database-jsonld.zip
opendc-lca openlca-inspect database-jsonld.zip \
  --process-id 982230dc-87c0-4ea0-8511-8e36064f66be --json
```

The reader preserves every process exchange:

- flow and provider identifiers;
- flow type, amount, and unit;
- input/output and quantitative-reference flags; and
- process identity, category, location, type, version, and description.

An openLCA `.zolca` file is a database backup tied to openLCA's embedded
database implementation. OpenDC-LCA deliberately does not reverse-engineer it.
Open the file in openLCA and export the selected database or processes as
JSON-LD, which is the portable exchange format.

## Export an OpenDC-LCA foreground process

```bash
opendc-lca openlca-export examples/direct-to-chip.json foreground.zip
```

The export contains a quantitative reference for annual delivered IT MWh and
physical foreground inputs for facility electricity, on-site water, and
equipment. It does **not** encode the OpenDC-LCA impact factors as elementary
flows. In openLCA, link those inputs to compatible background providers and
calculate with the selected LCIA methods.

## Export to Brightway

```bash
opendc-lca brightway-export database-jsonld.zip brightway.json \
  --database uslci-selection
```

`brightway.json` is a dependency-free representation of the mapping passed to
`bw2data.Database.write`. Python users can call:

```python
from opendc_lca import (
    install_brightway_database,
    read_openlca_jsonld,
    to_brightway_data,
)

processes = read_openlca_jsonld("database-jsonld.zip")
data = to_brightway_data(processes, database_name="uslci-selection")

# Optional: requires bw2data in the active Brightway project.
install_brightway_database(
    processes,
    database_name="uslci-selection",
    overwrite=False,
)
```

Biosphere exchanges are mapped to `biosphere3` by openLCA flow UUID. Users must
run a flow-mapping audit if the active Brightway biosphere uses different
identifiers. Unlinked technosphere flows retain their source UUID so missing
providers remain visible.

## Compatibility checklist

Before using exchanged data in a comparative study, verify:

1. attributional or consequential system model;
2. reference product, amount, and unit;
3. provider links and cutoff flows;
4. elementary-flow mapping;
5. geography and reference period;
6. allocation and end-of-life treatment;
7. LCIA method and characterization-factor compatibility; and
8. license and redistribution conditions.
