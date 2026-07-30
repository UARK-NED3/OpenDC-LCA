# Practitioner guide

OpenDC-LCA helps data-center operators, designers, cooling vendors and
sustainability teams turn facility and cooling assumptions into a traceable
life-cycle screening. It is most useful for identifying hotspots, testing
scenarios and discovering which missing data could change a decision.

It does **not** automatically certify a technology, reproduce a commercial LCA
database, or authorize a public comparative claim.

## Fastest workflow

### Guided local interface

```bash
opendc-lca gui
```

The **Guided study** tab asks for facility, electricity and source information.
It constructs the governed scenario, displays normalized indicators, classifies
the evidence, lists missing data and lets the user download the complete
scenario JSON.

### Compact input files

```bash
opendc-lca new-study my-input.json
# Edit the values in my-input.json.
opendc-lca prepare-study my-input.json my-scenario.json
opendc-lca practitioner-report my-scenario.json --output-dir my-results
```

The output directory contains:

- `PRACTITIONER_REPORT.md`: decision status, main results, audit findings and
  data needed next;
- `practitioner-results.json`: machine-readable results, contributions,
  evidence classification, scenario digest and model version.

## What the package calculates

For a static annual scenario, OpenDC-LCA calculates:

- annual IT electricity from IT capacity and average utilization;
- annual facility electricity using PUE;
- electricity-related GHG, primary energy and blue water;
- on-site cooling-water consumption;
- annualized equipment production and end-of-life burdens;
- coolant production, replacement losses and direct emissions when supplied;
- maintenance and reliability-driven replacements in the advanced schema;
- totals and contribution breakdowns annually and per delivered IT MWh.

Advanced workflows add performance-map reduction, hourly integration,
uncertainty, sensitivity, reliability and openLCA/Brightway exchange.

## Minimum inputs

| Group | Required input | Unit or choice | Typical source |
|---|---|---|---|
| Facility | IT capacity | kW | design or metering |
| Facility | Capacity factor | fraction, 0–1 | utilization records |
| Facility | PUE | dimensionless, ≥1 | metering or engineering model |
| Facility | Study life | years | project assumption |
| Water | On-site consumption | L/kWh IT | make-up and discharge balance |
| Electricity | GHG factor | kg CO2e/kWh | eGRID or supplier factor |
| Electricity | Primary energy | MJ/kWh | compatible LCA inventory |
| Electricity | Blue water | L/kWh | compatible LCA inventory |
| Evidence | Citation, geography, year and source ID | text | dataset or record |

An operational screening can run without equipment data, but the audit labels
that omission. A lifecycle comparison should also supply equipment quantities,
production impacts, service lives and end-of-life treatment. Immersion studies
should supply fluid charge, loss, production, direct GWP and end of life.

## How to interpret outputs

The normalized functional unit is **one MWh delivered to IT equipment**.

- `annual_*` describes the modeled facility for one year.
- `*_per_it_mwh` supports scale-normalized interpretation.
- `contributions` shows whether electricity, equipment, water, maintenance or
  fluid controls the result.
- `audit_findings` identifies omitted or weak evidence.
- `evidence_level` distinguishes demonstration, screening, blocked comparative
  claim and decision-grade candidate.
- `next_data_required` is the handoff to the operator, laboratory or LCA
  practitioner.

Passing validation means that inputs are structurally usable. It does not prove
functional equivalence or constitute an ISO critical review.

## Screening versus decision-grade use

| Evidence | Appropriate use |
|---|---|
| Synthetic or illustrative | software demonstration and training |
| Practitioner-supplied, unreviewed | internal screening and data-gap analysis |
| Reviewed, quantified, boundary-compatible | engineering decision support |
| Independently reviewed product systems and uncertainty | candidate for a public comparative study |

Before procurement or a public claim, confirm functional equivalence, common
boundaries, compatible impact methods, uncertainty, geography, time,
replacement, fluid, water-scarcity and critical-review requirements.

## Current boundaries

The static workflow does not independently model hourly or marginal
electricity, water scarcity, useful computation, redundancy, repair queues,
heat reuse or a complete background LCA database. Those effects require the
advanced interfaces or linked calculations from openLCA/Brightway.
