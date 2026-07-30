# OpenDC-LCA

Open, physics-informed life-cycle analysis for data-center cooling.

OpenDC-LCA connects measured or simulated cooling performance with transparent
life-cycle inventories. The first release is a small, dependency-free reference
model for comparing air cooling, direct-to-chip liquid cooling, and immersion
cooling on a common annual basis. Version 0.5 adds a Microsoft/Nature public
result reproduction audit and an hourly climate-aware research preview.

> [!IMPORTANT]
> The cooling-technology examples remain illustrative. A separate
> [public-data screening](results/public-data-v0.3/REPORT.md) now demonstrates
> traceable EPA eGRID, NOAA TMY, ÖKOBAUDAT, and GLAD adapters, but it does not
> support a cooling-technology ranking.

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
opendc-lca report examples/air-cooled.json \
  examples/direct-to-chip.json examples/single-phase-immersion.json \
  --output-dir results/my-screening
opendc-lca performance examples/performance-map-direct-to-chip.csv
opendc-lca monte-carlo examples/direct-to-chip.json \
  examples/uncertainty-direct-to-chip.json
opendc-lca experimental-report examples/direct-to-chip.json \
  examples/performance-map-direct-to-chip.csv \
  examples/uncertainty-direct-to-chip.json \
  --output-dir results/my-experiment
python -m unittest discover -s tests -v
```

Outputs are annual totals and values normalized per delivered IT MWh. JSON output
is available with `--json`. Installed wheels include the examples; copy them to
a working directory with:

```bash
opendc-lca examples --output-dir examples
```

## Representative output

The repository includes a reproducible
[screening report](results/representative-screening/REPORT.md), its
[machine-readable results](results/representative-screening/results.json), and
two dependency-free SVG figures:

![Illustrative normalized impact comparison](results/representative-screening/impact-comparison.svg)

![Illustrative GHG contribution analysis](results/representative-screening/ghg-contributions.svg)

These results use synthetic factors to demonstrate the workflow. The displayed
ranking is not evidence that one cooling architecture is environmentally
preferable.

The [v0.3 experimental report](results/v0.3-experimental/REPORT.md) demonstrates
the measurement-to-LCA path:

![Synthetic partial-load performance map](results/v0.3-experimental/performance-map.svg)

![Monte Carlo screening intervals](results/v0.3-experimental/uncertainty-intervals.svg)

The [public-data report](results/public-data-v0.3/REPORT.md) provides a
reproducible Arkansas operational-GHG/PUE sensitivity, Fayetteville climate
summary, and selected construction-material factors:

![Arkansas operational GHG sensitivity](results/public-data-v0.3/arkansas-operational-ghg-vs-pue.svg)

Its raw third-party inputs are not redistributed. See the
[data-source registry](data/SOURCES.md) and regenerate the committed derived
records with `python scripts/refresh_public_data.py`.

## v0.4-v0.5 research results

The [paper results package](paper/RESULTS_PACKAGE.md) consolidates equations,
machine-readable tables, editable figures, and a review workbook. Version 0.4
independently reconstructs all 24 totals in the released Microsoft/Nature
Figure 4 source data from their component contributions. Version 0.5 applies
transparent hourly PUE hypotheses to the Fayetteville TMY and Arkansas eGRID
factor.

The reproduction audit is validated. The hourly technology comparison remains
hypothesis-generating until the PUE curves are replaced by measured NED³
performance maps.

```bash
python scripts/run_research_analysis.py
```

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
- duration-weighted laboratory performance maps that derive measured PUE,
  on-site water intensity, and cooling COP; and
- reproducible independent-parameter Monte Carlo propagation with p05, p50,
  p95, and mean results.

It does not yet model hourly operation, correlated or model-form uncertainty,
water scarcity, heat reuse, workload output, or temperature-dependent
reliability. These are tracked in the [research roadmap](docs/ROADMAP.md).

## Repository map

- `src/opendc_lca/`: model, validation, and command-line interface
- `schemas/`: canonical scenario JSON Schema
- `examples/`: runnable illustrative scenarios
- `data/`: data registry and provenance template
- `data/derived/`: compact, auditable summaries generated from local public data
- `docs/`: methodology, data plan, roadmap, and governance
- `tests/`: deterministic reference tests
- `results/representative-screening/`: reproducible example report and figures
- `results/v0.3-experimental/`: performance and uncertainty demonstration
- `results/v0.4-microsoft-reproduction/`: released-result arithmetic audit
- `results/v0.5-hourly-preview/`: climate-aware hypothesis demonstration
- `paper/`: manuscript-ready tables, figures, workbook, and results narrative
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
Laboratory and uncertainty inputs follow
[PERFORMANCE_AND_UNCERTAINTY.md](docs/PERFORMANCE_AND_UNCERTAINTY.md).
The 15 methodology questions and provisional, source-backed responses are
maintained in [LCA method decision notes](docs/LCA_METHOD_DECISION_NOTES.md).

## Contributing

Research groups, operators, manufacturers, and students are welcome. Start with
[CONTRIBUTING.md](CONTRIBUTING.md). Contributions of measured data must include
units, boundary, test conditions, uncertainty, and a redistribution license.
Release maintainers should follow [RELEASING.md](RELEASING.md).

## License and citation

Code and original documentation are available under the MIT License. Third-party
datasets retain their own terms and must not be committed unless redistribution
is permitted. Citation metadata are in [CITATION.cff](CITATION.cff).
