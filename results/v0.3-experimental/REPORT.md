# OpenDC-LCA v0.3 experimental workflow

> **Synthetic demonstration—not decision-grade.** This report shows how
> laboratory performance points and input distributions enter the LCA workflow.

## Performance-map reduction

For observation $i$ with duration $t_i$, the measured aggregate PUE is:

$$PUE = 1 + \frac{\sum_i P_{cooling,i}t_i}
{\sum_i P_{IT,i}t_i}$$

The 4 points represent 24.0 h
and produce:

- measured PUE: **1.0795**
- on-site water: **0.0840 L/kWh IT**
- cooling COP: **12.579**

![Performance map](performance-map.svg)

## Uncertainty propagation

The seeded Monte Carlo analysis used 5,000 samples. GHG
screening results are **352.4 kg CO₂e/IT MWh** at p50, with a
p05–p95 interval of **293.8–410.5**.

![Uncertainty intervals](uncertainty-intervals.svg)

Inputs are sampled independently. Correlation, model-form uncertainty, and
experimental systematic error require additional analysis before comparative
interpretation. Complete machine-readable results are in
[`results.json`](results.json).
