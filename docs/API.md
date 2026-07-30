# OpenDC-LCA 1.0 API

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

## Compatibility

OpenDC-LCA follows semantic versioning. Within 1.x:

- documented inputs and result fields will retain their meaning;
- fields may be added but not silently removed;
- invalid physical values will continue to fail closed; and
- comparative-claim safeguards will not be weakened in a minor release.

The dataclass-level engineering API remains available for advanced users, but
the JSON-compatible functions are the preferred integration boundary.
