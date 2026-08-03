# Consolidated scientific results package

## Central result

The paper no longer treats deterministic rank across grid factors as proof of
technology robustness. It separates four questions:

1. Can the released totals be reconstructed?
2. Is the historical electricity trend comparable?
3. Does the transformation remain inside the released evidence?
4. Does the rank survive joint foreground and functional-unit stress?

## Results suitable for the main paper

### Released arithmetic

- 24 of 24 normalized Microsoft/WSP totals reconcile at workbook precision.
- The result validates reuse of the public contribution table, not licensed
  background inventories, bills of quantities, or field performance.

### Common-basis eGRID history

- Harmonized U.S. factor: 517.731 kg CO2e/MWh in 2012 and
  349.667 kg CO2e/MWh in 2023.
- Decline: 32.462%.
- Largest provider-versus-harmonized national difference:
  0.248 kg CO2e/MWh (2012).
- Interpretation: the long-run generation decarbonization result is robust to
  eGRID's SAR/AR4/AR5 GWP changes.

### Anchor coverage and electricity-boundary sensitivity

- 322/459 state-years lie between the two released GaBi electricity anchors.
- 1/459 lies below the renewable anchor.
- 136/459 lie above the grid anchor.
- Total extrapolation: 137/459, or 29.85%.
- In 2023, 9/51 rates exceed the grid anchor.
- Cold plate/single-phase crossover: 96.704 kg CO2e/MWh.
- Vermont is the only unadjusted 2023 state below the crossover.
- Exact additive clearance for the Vermont crossover: 73.009 kg CO2e/MWh.
- The 75 kg CO2e/MWh grid point is the first declared 25-unit stress step above
  that threshold; it is not an upstream estimate.
- Two-phase remains deterministic first rank in all 51 states across the
  0-100 kg CO2e/MWh boundary-allowance cases.

### Joint assumption stress

At 2023 U.S. generation:

| Envelope | Two-phase first-rank frequency |
|---|---:|
| Narrow | 99.19% |
| Screening | 76.17% |
| Wide | 55.05% |

At the lowest-carbon 2023 state:

| Envelope | Two-phase first-rank frequency |
|---|---:|
| Narrow | 63.03% |
| Screening | 42.72% |
| Wide | 32.43% |

These are seeded triangular stress frequencies, not probabilities or
confidence.

### Assumption-block and dependence sensitivity

At 2023 U.S. generation under the wide envelope, two-phase first-rank
frequency was 100% for grid-only variation, 79.52% for use-only variation,
63.36% for embodied-only variation, 73.90% for service-only variation, and
55.05% with all four blocks active when technology-specific errors were
independent. In the all-block case, the frequency increased to 64.50% at a
declared latent correlation of 0.5 and 100% under fully common-mode errors.

The result identifies embodied foreground data and error dependence as the
largest unresolved levers within the declared design. The copula correlations
are not fitted and the frequencies are not probabilities.

### Numerical convergence

Nested 5,000-, 20,000-, and 80,000-draw runs show that the three U.S.
20,000-draw frequencies differ from the 80,000-draw results by no more than
0.110 percentage points. Across both locations, the maximum difference is
0.709 percentage points. This verifies numerical integration precision within
the declared stress designs; it does not validate the stress marginals or
dependence assumptions.

### Functional-unit sensitivity

- Median adverse correction to two-phase impact per equivalent useful
  computation required to erase first rank across 2023 states: 5.503%.
- Range: 5.236-6.042%.
- Interpretation: useful throughput, server count, throttling, availability,
  and lifetime need approximately this order of resolution for the released
  ranking.

### Decarbonization and absolute benefit

- Air-cooled screen: 36.230 to 25.613 kg CO2e/Vcore-year from the 2012 to 2023
  national generation conditions.
- Two-phase screen: 28.746 to 20.333 kg CO2e/Vcore-year.
- Absolute two-phase-versus-air difference: 7.484 to 5.280 kg
  CO2e/Vcore-year, a 29.45% contraction.
- Air-cooled embodied share: 9.69% to 13.71%.

## Secondary evidence

- Boavizta server manufacturing spans 465-2,503 kg CO2e/server; annualized
  values span 116-626 kg CO2e/server-year.
- The 0.38-2.06-fold common server-contribution stress does not alter the
  deterministic two-phase first rank, but it is not an architecture-specific
  server substitution.
- Selected ÖKOBAUDAT high-scrap EAF steel has 59.9% lower A1-A3 GHG than the
  matched BF route; selected CEM III has 49.8% lower GHG than CEM II/A.
- Neither material lever can be propagated without an architecture bill of
  quantities.

## Data-priority robustness

Across nine alternative contribution/weakness weighting specifications:

- use phase ranks first in 8 and top-three in 8;
- networking ranks first once and top-three in 6;
- storage is top-three in all 9;
- compute is top-three in 4.

The index defines a transparent acquisition heuristic. It is not formal value
of information.

## Evidence that remains illustrative

The Fayetteville TMY and synthetic load-temperature performance surfaces
verify the hourly calculation and data contract. They do not support
technology comparisons. The GLAD hydrogen, USLCI, and USGS files verify source
registration and interoperability only.

## Regeneration

```bash
python scripts/run_integrated_evidence_analysis.py
python scripts/run_applied_energy_analysis.py
python -m unittest discover -s tests -v
```

The complete machine-readable outputs are in `paper/tables/` and
`results/applied-energy/`.
