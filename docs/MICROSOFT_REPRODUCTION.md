# Microsoft/Nature reproduction protocol

## Claim being tested

The v0.4 audit tests whether the normalized totals released as Figure 4 source
data equal the sum of the reported contributions for use phase, building,
server, rack or tank, cable, supporting equipment, and cooling fluid.

It covers three impact metrics, two electricity scenarios, and four cooling
architectures, producing 24 independently checked totals.

## Result

All totals reconcile. The maximum absolute difference is approximately
`1.42e-14` percentage points, consistent with floating-point rounding.

## What this does not reproduce

The audit does not independently recreate proprietary LCA for Experts
processes, licensed ecoinvent inventories, confidential manufacturer data,
Microsoft bills of materials or measured PUE values, or the complete
annualized virtual-core model. It is an arithmetic and public-data-lineage
reproduction, not an independent cradle-to-grave replication.

## v0.5 extension

The hourly preview replaces one annual-average PUE value with an explicit
temperature-response function evaluated against 8,760 NOAA TMY observations.
The present functions are hypotheses. The next scientific step is to estimate
their parameters from NED³ measurements across load, coolant conditions,
ambient conditions, and heat-rejection mode.

## Citations

- Alissa et al., “Using life cycle assessment to drive innovation for
  sustainable cool clouds,” *Nature* 641, 331-338 (2025),
  https://doi.org/10.1038/s41586-025-08832-3
- Released model files: https://doi.org/10.5281/zenodo.14268168
