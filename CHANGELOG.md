# Changelog

All notable changes are documented here. The project follows semantic
versioning after the first stable release.

## 0.3.0 — 2026-07-28

### Added

- Provider-native adapters for EPA eGRID XLSX, NOAA TMY CSV, ÖKOBAUDAT CSV, and
  GLAD/openLCA JSON-LD archives.
- A source registry, checksummed local-file manifest, and redistribution-safe
  derived data layer.
- A public-data screening report with Arkansas operational-GHG/PUE sensitivity,
  Fayetteville climate context, construction factors, equations, and SVG plots.
- Validated common laboratory performance-map CSV format.
- Duration-weighted derivation of measured PUE, on-site water intensity, and
  cooling COP.
- Seeded Monte Carlo propagation for uniform, triangular, normal, and
  lognormal input distributions.
- An uncertainty JSON Schema and installable example specification.
- Experimental Markdown/JSON reporting with performance and uncertainty SVG
  figures.

### Changed

- Model and package version advanced to 0.3.0.
- Scientific conventions now state the limits of independent-parameter
  uncertainty propagation.

## 0.2.0 — 2026-07-28

### Added

- Normative terminology, boundary, energy, water, allocation, and functional
  unit conventions.
- Required study declarations and data-source provenance.
- Required uncertainty declarations, including explicit `not_quantified`.
- SHA-256 scenario digests and model version in JSON output.
- One-at-a-time GHG sensitivity command.
- Architectural decision record for data-layer separation.
- Scientific audit with blockers for unsupported comparative assertions.
- Benchmark protocol, dataset-package schema, and inventory/performance templates.
- Source-backed responses to 15 LCA method questions, prepared for Dr. Darin
  Nutter to review for reasonableness.
- Discrete equipment-replacement schedules with explicit linearized screening.
- Impact-method, electricity-accounting, critical-review, source-review, and
  confidentiality declarations.
- Comparative-claim blockers for missing uncertainty, independent panel review,
  canonical methods, or confidential-data review.
- Installable example scenarios and deterministic Markdown, JSON, and SVG
  report generation.
- Representative synthetic screening results and release automation.

### Changed

- Example scenarios now identify synthetic inputs and prohibit comparative
  interpretation.
- CI validates sensitivity, reporting, source distributions, and installed
  wheels.

## 0.1.0 — 2026-07-28

- Initial screening model and illustrative cooling scenarios.
