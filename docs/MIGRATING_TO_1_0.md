# Migrating to OpenDC-LCA 1.0

Version 1.0 preserves the v0.6 scenario JSON, uncertainty JSON, laboratory CSV,
and workload CSV formats.

## Calculation result version

New calculations report `model_version: "1.0.0"`. Historical result files
retain their original model-version labels and should not be rewritten merely
to change a version string.

## Recommended application interface

Applications that previously wrote temporary JSON files can now pass decoded
objects directly to `validate_scenario`, `analyze_scenario`, and
`audit_scenario`. Performance CSV text can be passed to
`summarize_performance_csv`.

## GUI

The new GUI is optional and has no additional Python dependencies. Existing
CLI workflows remain supported.

## Scientific behavior

Validation and audit rules remain fail-closed. Version 1.0 does not convert the
synthetic examples or v0.5-v0.6 demonstrations into comparative evidence.
