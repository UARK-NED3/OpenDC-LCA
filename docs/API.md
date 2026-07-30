# OpenDC-LCA 1.x API

The functions below are the stable JSON-compatible interface for applications,
notebooks, services, and the local GUI.

```python
from opendc_lca import (
    analyze_scenario,
    audit_scenario,
    summarize_performance_csv,
    validate_scenario,
)
```

## Scenario functions

- `validate_scenario(data)` validates a decoded JSON object and returns its
  canonical SHA-256 digest.
- `analyze_scenario(data)` returns the complete result, automated scientific
  audit, and `comparative_claim_blocked` status.
- `audit_scenario(data)` returns audit findings without running the impact
  calculation.

## Performance maps

`summarize_performance_csv(text)` validates a performance-map CSV supplied as
text and returns its duration-weighted engineering summary.

## Inventory interoperability

- `read_openlca_jsonld(source, process_ids=None)` reads complete openLCA
  process exchanges.
- `export_scenario_openlca_jsonld(scenario, destination)` writes a foreground
  JSON-LD archive.
- `to_brightway_data(processes, database_name=...)` returns data compatible
  with `bw2data.Database.write`.
- `write_brightway_json(...)` writes the same mapping without requiring
  Brightway.
- `install_brightway_database(...)` installs into the active Brightway project
  when `bw2data` is available.

## Benchmark release

- `validate_benchmark_manifest(...)` validates metadata and file checksums.
- `validate_review_record(...)` validates an independent-review record.
- `package_benchmark_release(...)` creates a DOI-ready evidence package and
  enforces the review gate for datasets labeled `reviewed`.

Reliability results are additive fields in `analyze_scenario` output when a
scenario selects `replacement_model: "reliability"`.

## Compatibility

OpenDC-LCA follows semantic versioning. Within 1.x:

- documented inputs and result fields will retain their meaning;
- fields may be added but not silently removed;
- invalid physical values will continue to fail closed; and
- comparative-claim safeguards will not be weakened in a minor release.

The dataclass-level engineering API remains available for advanced users, but
the JSON-compatible functions are the preferred integration boundary.
