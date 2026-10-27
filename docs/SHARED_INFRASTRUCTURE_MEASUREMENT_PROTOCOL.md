# Shared-infrastructure measurement protocol

## Purpose

This protocol defines the minimum evidence needed to convert a preliminary
shared-data-center boundary record into an operational validation dataset for
OpenDC-LCA. It is intended for facilities in which a research-computing load
shares electrical or mechanical infrastructure with other occupants. It does
not authorize a facility PUE, a comparative cooling claim, or publication of
site data by itself.

## Decision boundary

Define the study boundary before collecting data. List every energy item as
`metered`, `allocated`, or `excluded`, together with its meter identifier,
allocation method, or exclusion rationale. Maintain an energy-flow diagram
that identifies whether each meter is upstream or downstream of the UPS and
whether cooling electricity is dedicated or shared.

## Liquid-loop boundary

Record the physical loop before assigning a thermal measurement or a coolant
inventory. The facility water system (FWS) delivers facility-side heat removal.
The technology cooling system (TCS) carries liquid between a CDU and the
liquid-cooled rack, including manifolds, hoses, cold plates, and the TCS fluid.
When a CDU heat exchanger separates the fluids, record the FWS and TCS as
separate loops. For a direct facility connection, record the connection and
heat-exchange location instead of assigning a CDU boundary by assumption.

This terminology follows OCP liquid-ITE connection, liquid-distribution, and
glycol-fluid guidance. It specifies the collection schema only. It does not
show that a particular site uses a CDU, a glycol concentration, or a given
cooling topology.

The following interval quantities use non-overlapping electrical boundaries:

\[
E_{\mathrm{IT}}=E_{\mathrm{UPS,out}}, \qquad
E_{\mathrm{UPS,loss}}=E_{\mathrm{UPS,in}}-E_{\mathrm{UPS,out}}.
\]

The first identity applies only when the UPS output feeds the selected IT load
and no non-IT load. A dedicated-support ratio may then be reported as

\[
R_{\mathrm{dedicated}}=\frac{E_{\mathrm{IT}}+E_{\mathrm{UPS,loss}}+
E_{\mathrm{dedicated\ cooling}}+E_{\mathrm{dedicated\ pumps}}}
{E_{\mathrm{IT}}}.
\]

This ratio is not PUE. Report facility PUE only when the denominator is a
metered IT boundary and the numerator includes all support energy inside the
declared facility boundary. Shared CRAC, lighting, building, and other loads
must be metered or allocated with an auditable method. Any excluded shared
support load blocks the facility-PUE label.

## Required data

Record interval energy in kWh or interval-average real power in kW. Use a
single timezone, state whether timestamps mark interval start or end, and
retain the native sampling interval. Five- or fifteen-minute intervals are
usually suitable when available. The same interval must be used for all power,
thermal, and workload records after synchronization.

| Evidence group | Minimum fields | Purpose and boundary rule |
|---|---|---|
| IT and UPS | timestamp; UPS input and output kWh; meter IDs; voltage, current, frequency, phase, PDU or busway location | Quantifies IT energy and UPS loss without double counting. |
| Dedicated cooling | timestamp; chiller, CDU, rear-door, and dedicated-pump kWh where applicable; equipment ID and operating status | Quantifies cooling support that is demonstrably inside the IT boundary. |
| Shared support | timestamp; CRAC, central plant, and building energy where available; allocation driver and uncertainty | Required before a facility-PUE statement. Keep unavailable shared loads excluded rather than estimated silently. |
| FWS and TCS thermal loops | loop identifier; supply and return temperature in degrees C; volumetric or mass flow; differential pressure; pump speed; valve position; sensor locations | Supports \(\dot Q=\dot m c_p(T_{\mathrm{return}}-T_{\mathrm{supply}})\) within a declared loop. Do not subtract heat rates across loops without synchronized data and stated uncertainty. |
| Coolant condition | loop identifier; fluid manufacturer and product; glycol volume or mass fraction; initial fill mass; makeup, flushing, and disposal mass; inhibitor or treatment record; liquid-quality and leak records | Defines the fluid foreground inventory. Evaluate \(c_p\) at the recorded fluid composition and representative loop temperature. |
| Environment | timestamp; outdoor dry-bulb and humidity or wet-bulb; room inlet temperature and humidity | Establishes the weather and condensation-control domain of the measurements. |
| Computing service | timestamp; hardware configuration; scheduler/job records or a fixed benchmark; completed work; availability | Defines the service denominator. Rack count, cores, or nameplate capacity alone do not establish functional equivalence. |
| Provenance and quality | meter model; calibration date; accuracy class; data export method; missing-data flags; maintenance/outage log | Supports uncertainty analysis and interpretation of discontinuities. |

Use `data/templates/operational-telemetry-template.csv` for normalized
interval records. The template is intentionally blank and does not imply that
any listed measurement point is available at a particular facility.

## Functional-equivalence experiment

Compare architectures only under a common, declared workload. For each test,
record hardware configuration, firmware and power-management settings,
accelerator and memory use, network and storage constraints, completed work,
wall time, and rejected or failed jobs. Report the service metric, such as
completed benchmark work, simulation steps, or validated application output,
together with IT and cooling energy. The workload must cover the operating
range used in annual integration. A result measured at one load state should
not be extrapolated to a different workload or weather regime without a
separately validated model.

## Data reduction and quality controls

First, verify that all interval energy values are non-negative and that UPS
input is not lower than UPS output beyond meter accuracy. Second, reconcile
each electrical subtotal against its upstream meter over the same interval.
Third, identify missing, repeated, clock-shifted, and maintenance intervals
before aggregation. Fourth, retain raw exports separately from derived tables.
Fifth, propagate documented meter, temperature, flow, and glycol-property
uncertainty to reported ratios and heat rates. Do not treat a missing shared
meter as zero support energy.

## Release and publication controls

Store the raw telemetry and site identifiers in the facility-controlled
location unless the owner authorizes release. A public package may contain the
schema, de-identified aggregate intervals, transformation code, and a manifest
of source files and hashes when that release is authorized. Before making a
comparative environmental claim, combine the measured service and energy data
with common-method foreground inventories, a complete or bounded electricity
system, characterized water impacts where relevant, and an independent LCA
critical review appropriate to the claim.
