# Performance maps and uncertainty

Version 0.3 connects laboratory or simulated cooling measurements to the
screening LCA model while preserving an explicit boundary between observed
performance and background impact factors.

## Common performance-map format

The canonical CSV header is in
`data/templates/performance-map-template.csv`. Each row is one steady or
time-aggregated observation and must contain:

- a unique test ID, cooling architecture, source ID, and duration;
- IT load and heat removed;
- pump, fan, CDU, and heat-rejection power;
- on-site water consumption rate; and
- a declared measurement-uncertainty percentage.

Coolant and ambient conditions remain in the format for engineering
traceability even though version 0.3 does not yet interpolate them.

For row \(i\), cooling parasitic power is

\[
P_{\mathrm{cooling},i}=P_{\mathrm{pump},i}+P_{\mathrm{fan},i}
+P_{\mathrm{CDU},i}+P_{\mathrm{rejection},i}.
\]

Duration-weighted aggregate PUE and water intensity are:

\[
PUE=1+\frac{\sum_iP_{\mathrm{cooling},i}t_i}
{\sum_iP_{\mathrm{IT},i}t_i},
\qquad
WUE_{\mathrm{onsite}}=
\frac{\sum_i\dot V_{\mathrm{water},i}t_i}
{\sum_iP_{\mathrm{IT},i}t_i}.
\]

`opendc-lca performance FILE.csv` validates and summarizes a map. The Python
API can apply the derived PUE and water intensity to a matching scenario.

## Uncertainty specifications

The JSON format is defined by `schemas/uncertainty.schema.json`. Supported
distributions are:

- uniform: `low`, `high`;
- triangular: `low`, `mode`, `high`;
- normal: `mean`, `sd`; and
- lognormal: `median`, `geometric_sd`.

Optional minimum and maximum values truncate sampled values to physical bounds.
The command

```bash
opendc-lca monte-carlo SCENARIO.json UNCERTAINTY.json
```

reports p05, p50, p95, and mean GHG, primary-energy, and blue-water results.
The seed makes results exactly reproducible.

## Interpretation limits

The sampler treats parameters as independent. It does not yet model:

- shared background factors across technologies;
- correlation between load, PUE, weather, and water;
- systematic instrument uncertainty;
- discrete model choices or model-form uncertainty; or
- probability that one technology ranks better than another.

Consequently, v0.3 Monte Carlo results are screening evidence. A decision-grade
comparison still requires justified joint distributions, correlation treatment,
global sensitivity or rank-reversal analysis, and appropriate critical review.
