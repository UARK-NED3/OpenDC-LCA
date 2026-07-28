# OpenDC-LCA

Open, physics-informed life-cycle analysis for data-center cooling.

OpenDC-LCA connects measured or simulated cooling performance with transparent
life-cycle inventories. The first release is a small, dependency-free reference
model for comparing air cooling, direct-to-chip liquid cooling, and immersion
cooling on a common annual basis.

> [!IMPORTANT]
> The example impact factors are illustrative—not decision-grade inventory
> data. Replace them with reviewed public data, licensed databases, EPDs, or
> partner-provided data before publishing conclusions.

## Why this project exists

Cooling comparisons are often reduced to PUE. That misses equipment production,
coolant manufacture and loss, water consumption, hardware replacement, and the
effect of location and utilization. OpenDC-LCA makes those assumptions explicit
and machine-readable.

The long-term goal is an open benchmark and model interface that can combine:

- laboratory measurements and uncertainty;
- CFD and reduced-order performance maps;
- hourly weather, grid, workload, and water-stress data;
- equipment bills of materials and EPDs;
- reliability, replacement, heat reuse, and end-of-life scenarios; and
- optional adapters for licensed LCA databases without redistributing them.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m pip install -e .
opendc-lca validate examples/air-cooled.json
opendc-lca run examples/air-cooled.json
opendc-lca compare examples/air-cooled.json \
  examples/direct-to-chip.json examples/single-phase-immersion.json
opendc-lca sensitivity examples/single-phase-immersion.json
opendc-lca audit examples/single-phase-immersion.json
python -m unittest discover -s tests -v
```

Outputs are annual totals and values normalized per delivered IT MWh. JSON output
is available with `--json`.

## Model boundary

The Phase 1 model includes:

- IT and facility electricity derived from IT capacity, capacity factor, and PUE;
- electricity-related GHG, primary-energy, and blue-water impacts;
- on-site cooling water;
- annualized production and end-of-life impacts of equipment;
- coolant manufacture, replenishment, and direct emissions from loss; and
- an auditable contribution breakdown.
- required provenance and explicit study-boundary declarations;
- scenario SHA-256 digests and model version in JSON results; and
- one-at-a-time GHG sensitivity screening.
- automated scientific-quality findings and comparative-claim blockers.

It does not yet model hourly operation, uncertainty propagation, water scarcity,
heat reuse, workload output, or temperature-dependent reliability. These are
tracked in the [research roadmap](docs/ROADMAP.md).

## Repository map

- `src/opendc_lca/`: model, validation, and command-line interface
- `schemas/`: canonical scenario JSON Schema
- `examples/`: runnable illustrative scenarios
- `data/`: data registry and provenance template
- `docs/`: methodology, data plan, roadmap, and governance
- `tests/`: deterministic reference tests
- `CHANGELOG.md`: release-level scientific and software changes

## Scientific principles

1. State the functional unit and system boundary.
2. Separate foreground engineering measurements from background LCA factors.
3. Preserve source, geography, year, license, uncertainty, and data quality.
4. Report contribution analysis and sensitivity—not only a technology ranking.
5. Never represent illustrative example factors as measured or authoritative.

See [CONVENTIONS.md](docs/CONVENTIONS.md),
[METHODOLOGY.md](docs/METHODOLOGY.md), and [DATA_PLAN.md](docs/DATA_PLAN.md).
The first open dataset must follow the
[benchmark protocol](docs/BENCHMARK_PROTOCOL.md).
The 15 methodology questions and provisional, source-backed responses are
maintained in [LCA method decision notes](docs/LCA_METHOD_DECISION_NOTES.md).

## Contributing

Research groups, operators, manufacturers, and students are welcome. Start with
[CONTRIBUTING.md](CONTRIBUTING.md). Contributions of measured data must include
units, boundary, test conditions, uncertainty, and a redistribution license.

## License and citation

Code and original documentation are available under the MIT License. Third-party
datasets retain their own terms and must not be committed unless redistribution
is permitted. Citation metadata are in [CITATION.cff](CITATION.cff).
