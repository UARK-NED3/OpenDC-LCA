# Data acquisition plan

## Foreground data: measure or obtain from partners

Highest-priority laboratory measurements:

- heat removed, coolant flow, temperatures, and pressure drop;
- pump, fan, CDU, and heat-rejection electricity;
- partial-load and transient performance;
- coolant inventory, loss, degradation, and replacement;
- thermal uniformity, throttling, and reliability indicators.

Highest-priority partner data:

- redacted bills of materials by principal material;
- equipment quantities, capacities, and service lives;
- time-series IT load, subsystem electricity, and water;
- coolant charge and replenishment history;
- failure, maintenance, and replacement records;
- EPDs and manufacturer performance curves.

## Simulation data

Use validated CFD or reduced-order models to interpolate laboratory performance,
test scale-up, and examine failures. Use annual energy simulation to map
performance across climates. Preserve code version, mesh or model convergence,
boundary conditions, validation error, and uncertainty.

## Background data

Start with redistributable sources. Add ecoinvent or Sphera adapters only as
optional user-side integrations. Never commit licensed unit-process inventories.

## Minimum experimental metadata

- apparatus and calibration;
- test article geometry and materials;
- coolant identity and properties;
- boundary and initial conditions;
- sampling rate and duration;
- raw and processed variables with units;
- uncertainty method;
- excluded or failed runs;
- license and persistent identifier.

## Initial benchmark matrix

Test air, direct-to-chip, and single-phase immersion at:

- 25%, 50%, 75%, and 100% load;
- at least three coolant or ambient boundary temperatures;
- steady and representative transient AI loads; and
- normal plus one degraded or failure condition.

