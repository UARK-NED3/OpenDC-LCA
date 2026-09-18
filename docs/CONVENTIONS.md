# OpenDC-LCA conventions

This document is normative for model version 1.x. Terms such as **must** and
**should** indicate requirements and recommendations for publishable studies.

## Functional unit

Version 1.x supports `it_mwh`: one MWh of electricity delivered to IT equipment.
It may be used only when alternatives deliver equivalent computational service,
utilization, reliability, and hardware life. If cooling changes any of these,
authors must also report absolute results and explain why IT MWh remains a fair
denominator. The current schema rejects GPU-hour and workload-based units.

### Pathway to compute-service units

A future `gpu_device_hour` unit will mean one installed GPU device operated for
one wall-clock hour. It is not, by itself, a measure of useful computation.
It may support a comparison only when the accelerator model, count, memory
configuration, clock or power limit, utilization definition, availability rule,
and workload or benchmark are the same across alternatives. A comparison across
different accelerator generations, CPU and GPU systems, or materially different
workloads must not use GPU-device hours as the sole service denominator.

A future workload-based unit will mean one declared unit of completed work that
meets a stated output-quality criterion. The workload identifier, software and
model version, input set or input class, completion rule, quality metric,
hardware configuration, and availability rule must be recorded. Examples such
as completed jobs, simulation time steps, model inferences, or validated
application output are not interchangeable unless a study supplies and
validates a conversion.

Before OpenDC-LCA accepts either unit, a release must provide i) a versioned
input schema with these metadata, ii) time-aligned IT energy and workload
records, iii) an explicit crosswalk to absolute energy and the existing
`it_mwh` result, iv) unit and integration tests for zero, missing, and mixed
hardware records, and v) independent review of the service-equivalence rule.
Until then, GPU-device-hour and workload-normalized values may be retained as
user-side evidence records but are not supported calculation outputs or public
comparative-claim denominators.

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

## Units and sign conventions

Machine-readable inputs use SI-derived units stated in their field names.
Electricity is recorded in kWh or MWh, power in kW, primary energy in MJ,
mass in kg, water volume in L, time in h or year, and greenhouse-gas results in
kg CO$_2$e. Temperatures must state the scale and are converted only at a
documented input boundary. Multipliers and fractions are dimensionless.

Positive inventory and impact values indicate a burden within the declared
system boundary. Negative values are permitted only for a documented recovery
or substitution credit. A zero is a numeric value and never means unknown,
missing, or excluded. Missing, allocated, and excluded flows must be identified
explicitly in the scenario or measurement record.

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

The `reliability` option uses an expected renewal count from a Weibull lifetime
distribution. An optional Arrhenius acceleration factor adjusts characteristic
life for a declared constant operating temperature. Scheduled maintenance
impacts and downtime are represented separately. These are expectation models,
not facility-availability simulations: redundancy, common-cause failures,
repair queues, workload migration, time-varying temperature damage, and
second-life pathways remain outside the current boundary.

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

## Laboratory performance maps

Performance-map rows represent observations with explicit duration. Aggregate
PUE and water intensity are energy-weighted, not arithmetic averages of row
ratios. Cooling-system power includes the recorded pump, fan, CDU, and
heat-rejection terms. Authors must define whether IT-integral fans are included
in IT power or cooling power and apply that boundary consistently.

## Monte Carlo screening

Version 1.0 supports uniform, triangular, normal, and lognormal distributions
for selected continuous inputs. A random seed and sample count are mandatory
for reproducibility. Inputs are sampled independently. This implementation does
not represent correlations, systematic measurement bias, or model-form
uncertainty, and therefore does not by itself satisfy the uncertainty
requirements for a public comparative assertion.
