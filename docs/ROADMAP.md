# Research and software roadmap

## Stable software milestone: v1.0

- Stable JSON-compatible Python API.
- Command-line and local graphical workflows over one calculation engine.
- Semantic-versioning compatibility contract, migration notes, and support
  policy.
- Release-ready tests, examples, research artifacts, and scientific safeguards.

## Delivered in v0.4-v0.5

- Independent arithmetic reconstruction of all 24 released Microsoft/Nature
  Figure 4 totals.
- Hourly TMY ingestion and temperature-dependent PUE research-preview model.
- Paper-ready tables, figures, equations, workbook, citations, and review notes.

## Delivered in v0.6

- Complete load-temperature performance-surface contract.
- In-envelope bilinear interpolation and explicit extrapolation failure.
- Hourly workload-weather integration and measurement uncertainty bounds.
- Evidence-status controls that block comparisons of synthetic datasets.

## Next evidence gate

- Replace synthetic performance surfaces with NED³ measurements for an air-cooled
  reference and at least one liquid-cooling architecture.
- Add load, humidity or wet-bulb conditions, coolant-loop measurements, and
  uncertainty.
- Add a compute-service functional unit compatible with the Microsoft study.

## Phase 1 — transparent screening model

- [x] Versioned scenario schema
- [x] Air, direct-to-chip, and single-phase immersion examples
- [x] Electricity, equipment, water, and fluid calculations
- [x] Contribution analysis and normalized results
- [x] Automated validation tests
- [ ] Replace illustrative examples with reviewed open benchmark data
- [x] Publish a formal terminology and unit convention
- [x] Require scenario provenance and study-boundary metadata
- [x] Emit a versioned reproducibility digest
- [x] Add one-at-a-time sensitivity screening
- [x] Add automated scientific-quality and comparative-claim audit rules
- [x] Publish a benchmark intake protocol and data templates
- [x] Draft expert-review questions for the LCA methodology
- [x] Develop source-backed provisional responses to all 15 method questions
- [x] Encode discrete replacement schedules and comparative-review gates

## Phase 2 — experimental performance maps

- [x] Common laboratory data format
- [x] Pump, fan, CDU, and heat-rejection performance-map interface
- [x] Partial-load hourly workload support
- [x] Independent-parameter Monte Carlo uncertainty propagation
- [ ] Correlated measurement uncertainty and model-form uncertainty
- [ ] Reproducible reference experiments

## Phase 3 — dynamic and regionalized LCA

- [x] Hourly weather and workload engine with annual grid factors
- [ ] Dry, evaporative, and hybrid heat rejection
- [ ] Water-scarcity characterization
- [ ] Grid-decarbonization scenarios
- [x] Screening Monte Carlo analysis
- [ ] Correlated Monte Carlo and global sensitivity analysis

## Phase 4 — reliability and circularity

- [ ] Temperature-history-to-failure models
- [ ] Hardware replacement and second-life scenarios
- [ ] Fluid degradation, recovery, and loss distributions
- [ ] Embodied impacts of servers, buildings, and power systems

## Phase 5 — heat reuse and decision support

- [ ] Exergy-aware heat-reuse model
- [ ] Time-matched agricultural, industrial, and campus heat sinks
- [ ] Cost and reliability objectives
- [ ] Technology adoption maps by climate, grid, and rack density
- [ ] Validated public benchmark and API
