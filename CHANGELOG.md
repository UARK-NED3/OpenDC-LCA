# Changelog

All notable changes are documented here. The project follows semantic
versioning after the first stable release.

## 1.1.0 — 2026-07-30

### Added

- Complete openLCA JSON-LD process and exchange reader, with selected-process
  filtering and explicit `.zolca` export guidance.
- OpenDC-LCA foreground export to openLCA JSON-LD and mapping to Brightway
  `Database.write` structures, plus dependency-free Brightway JSON export.
- Weibull renewal and Arrhenius-Weibull reliability models with expected
  replacements, scheduled maintenance, downtime, unserved-service exposure,
  and separate maintenance impacts.
- Reliability-aware scenario example and deterministic interoperability,
  renewal, temperature-acceleration, maintenance, and benchmark tests.
- Validated benchmark manifest, independent-review record, citable release ZIP,
  and DOI handoff workflow.

### Changed

- Package and calculation model versions advanced to 1.1.0.
- Replacement models now support `discrete`, `linearized`, and `reliability`.
- Interoperability and reliability are documented as model interfaces, not
  evidence that imported inventories or synthetic failure parameters are
  automatically suitable for comparative claims.

## 1.0.0 — 2026-07-29

### Added

- Stable JSON-compatible Python API for scenario validation, analysis, audit,
  and performance-map summaries.
- Zero-dependency local web GUI with scenario and performance-map workflows,
  scientific audit display, KPI summaries, and JSON export.
- Localhost-only default binding, explicit remote-binding opt-in, a 2 MB
  request limit, no-store responses, and browser security headers.
- v1.0 API, GUI, migration, support, and reproducibility documentation.

### Changed

- Package and calculation model versions advanced to 1.0.0.
- The GUI and API use the same validation, calculation, provenance, and
  comparative-claim safeguards as the command line.
- Public API compatibility is governed by semantic versioning.

### Stability contract

- Existing v0.6 scenario and performance-map files remain valid.
- Additive result fields may appear in 1.x; existing documented fields will not
  be removed or redefined before 2.0.

## 0.6.0 — 2026-07-29

### Added

- Complete load-by-temperature performance-surface validation.
- Bilinear interpolation with an explicit prohibition on extrapolation.
- Hourly alignment of measured performance, NOAA weather, and workload.
- Screening PUE uncertainty bounds derived from declared measurement
  uncertainty.
- Evidence statuses and a comparative-claim gate requiring at least two
  reviewed performance datasets.
- Laboratory and workload templates, a synthetic two-architecture
  demonstration, two figures, and a paper table.

### Changed

- Package version advanced to 0.6.0.
- The next evidence gate is now replacement of synthetic surfaces with NED³
  measurements rather than additional assumed PUE curves.

## 0.5.0 — 2026-07-29

### Added

- Independent reconstruction of all 24 released Microsoft/Nature Figure 4
  totals from component contributions.
- A dependency-free XLSX cached-value reader for auditable source-data imports.
- An hourly Fayetteville climate research preview with explicit, replaceable
  temperature-PUE hypotheses and Arkansas eGRID operational GHG.
- A paper-ready package containing CSV tables, SVG/PDF figures, equations,
  provenance, and interpretation boundaries.

### Changed

- Package version advanced to 0.5.0.
- Reproduction results and hypothesis-generating preview results are kept in
  separate result namespaces to prevent unsupported comparative claims.

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
