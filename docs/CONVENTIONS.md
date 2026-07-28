# OpenDC-LCA conventions

This document is normative for model version 0.2. Terms such as **must** and
**should** indicate requirements and recommendations for publishable studies.

## Functional unit

Version 0.2 supports `it_mwh`: one MWh of electricity delivered to IT equipment.
It may be used only when alternatives deliver equivalent computational service,
utilization, reliability, and hardware life. If cooling changes any of these,
authors must also report absolute results and explain why IT MWh remains a fair
denominator. GPU-hour and workload-based units are planned but not yet supported.

## Energy boundary

- **IT electricity** powers compute, storage, networking, and integral IT fans.
- **Facility electricity** is IT electricity multiplied by PUE.
- PUE must refer to the same temporal and physical boundary as the IT load.
- Location-based and market-based electricity results must not be combined.
- Renewable procurement must not be represented by setting operational impacts
  to zero unless the chosen accounting method supports that treatment.

## Water

`blue_water_l` means consumptive use of surface water or groundwater, expressed
in litres. Withdrawal, discharge, and consumption are not interchangeable.
On-site cooling consumption and electricity supply-chain consumption are
reported as separate contributions. Water-scarcity weighting is not yet
implemented and must be calculated externally if claimed.

## Greenhouse gases

Results use kilograms of carbon-dioxide equivalent. Every study must identify
the characterization method and time horizon in its data-source records or
study documentation. Direct emissions from coolant loss are separated from
coolant production and end-of-life impacts.

## Primary energy

Primary energy is reported in MJ. Authors must state whether factors use higher
or lower heating values and whether renewable and non-renewable energy are
combined. Example scenarios are illustrative and do not establish a convention
for a specific background database.

## Equipment and lifetime

For benchmark studies, production and end-of-life impacts use discrete
installations across the study period:

`quantity × ceil(study period / service life) × impact / study period`

The `linearized` screening option instead uses:

`quantity × impact / service life`

Component service life may differ from facility life. Studies must declare the
replacement model and test lifetime sensitivity when it affects conclusions.

## End-of-life credits

Negative end-of-life values are allowed only when the allocation method grants a
recovery or substitution credit. Production values cannot be negative. Authors
must report the allocation method and test a no-credit sensitivity case when
the credit materially affects the ranking.

## System boundaries

- `cooling_system_cradle_to_grave`: cooling and heat-rejection equipment,
  fluids, operation, maintenance represented by inputs, and end of life.
- `facility_cradle_to_grave`: cooling system plus included facility, power,
  building, and IT assets.
- `custom`: permitted only with a complete boundary description in the study
  documentation.

Common systems may be excluded from a comparison only if their quantities,
performance, lifetime, and end of life are demonstrably unchanged.

## Comparative claims

Illustrative or synthetic data must set `comparative_assertion` to `false`.
Public comparative claims require quantified uncertainty, consistent boundaries,
decision-grade provenance, and an independent critical-review panel. The
automated audit is a quality gate, not an ISO conformity assessment.

## Significant figures

Machine-readable output retains calculation precision. Human-facing results
should reflect input uncertainty and normally use no more than three significant
figures. Numerical precision does not imply scientific certainty.
