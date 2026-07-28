# Open benchmark protocol

This protocol defines the minimum package for the first reviewed OpenDC-LCA
cooling benchmark. It is intended for air, direct-to-chip, and single-phase
immersion systems at a common IT service level.

## Benchmark objective

Determine the conditions under which cooling architectures differ materially in
life-cycle GHG emissions, primary energy, and blue-water consumption. The
benchmark must identify break-even conditions rather than publish an
unqualified technology ranking.

## Reference system

The first benchmark should use:

- 1 MW nominal IT capacity;
- 25%, 50%, 75%, and 100% load points;
- one shared workload and hardware-performance assumption;
- a 15-year facility study period;
- component-specific service lives;
- at least three US climate/grid regions; and
- air, direct-to-chip, and single-phase immersion alternatives.

Values above are starting hypotheses, not locked methodological decisions.
Departures must be documented.

## Required foreground inventory

For every architecture:

- cooling and heat-rejection equipment quantities and capacities;
- mass by steel, stainless steel, aluminum, copper, polymer, electronics, and
  other material;
- coolant or refrigerant identity, charge, replenishment, loss, and disposal;
- service life, replacement, maintenance, and recovery assumptions;
- IT fan or other server hardware added or removed by the architecture; and
- sources and uncertainty for each quantity.

Use `data/templates/foreground-inventory-template.csv`.

## Required performance data

At each load and boundary condition:

- IT load and heat removed;
- supply and return temperatures;
- mass flow and pressure drop;
- pump, fan, CDU, and heat-rejection electricity;
- on-site water consumption;
- ambient dry- and wet-bulb temperature; and
- measurement or model uncertainty.

Use `data/templates/performance-map-template.csv`. Raw laboratory data should be
preserved separately with calibration and processing records.

## Background data

Every material, energy, transport, and waste factor must identify:

- database and version;
- process or dataset identifier;
- geography and reference year;
- allocation/system model;
- impact method and version;
- license and redistribution status; and
- proxy rationale when no exact process exists.

The public benchmark must run using redistributable factors. Licensed-database
results may be reported as a sensitivity layer without distributing the data.

## Quality gates

A benchmark may be marked `independently_reviewed` only after:

1. Schema and automated audit pass.
2. Units and mass/energy balances are checked.
3. Foreground models are validated against measurements or manufacturer curves.
4. Uncertainty and sensitivity results are reported.
5. No confidential or non-redistributable values are exposed.
6. An independent LCA reviewer approves method, allocation, and interpretation.
7. An independent thermal reviewer approves the performance boundary.
8. A public comparative assertion receives an independent critical-review panel
   consistent with ISO 14044 and ISO 14071.

## Required outputs

- Versioned data package with checksums
- Scenario files and exact software commit
- Absolute and functional-unit results
- Contribution analysis
- Uncertainty intervals
- Sensitivity and break-even analysis
- Boundary diagram and inclusion/exclusion table
- Limitations and rank-reversal conditions
