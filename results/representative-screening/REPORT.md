# Representative OpenDC-LCA screening results

> **Illustrative, not decision-grade.** The bundled scenarios use synthetic
> factors to demonstrate calculation, provenance, audit, sensitivity, and
> reporting behavior. They must not be used to select a cooling technology.

## Model

Annual IT electricity:

$$E_{IT} = P_{IT}\,CF\,(8,760\ \mathrm{h\,yr^{-1}})$$

Annual facility electricity:

$$E_{facility} = E_{IT}\,PUE$$

Discrete annualized component inventory:

$$q_{annual} =
\frac{q\,\lceil L_{facility}/L_{component}\rceil}{L_{facility}}$$

Annual coolant production includes the initial charge amortized over the
facility life plus annual replacement of losses:

$$m_{fluid,annual} =
\frac{m_{initial}}{L_{facility}} + m_{initial}f_{loss}$$

## Results

| Scenario | Architecture | kg CO₂e/IT MWh | MJ/IT MWh | L blue water/IT MWh |
|---|---|---:|---:|---:|
| Illustrative air-cooled 1 MW | air-cooled | 456.705 | 7824.759 | 1294.323 |
| Illustrative direct-to-chip 1 MW | direct-to-chip | 394.161 | 6750.340 | 441.256 |
| Illustrative single-phase immersion 1 MW | single-phase-immersion | 381.197 | 6526.482 | 381.340 |

![Normalized impact comparison](impact-comparison.svg)

![Annual GHG contribution analysis](ghg-contributions.svg)

## Leading local GHG sensitivities

| Scenario | Highest-ranked parameter | Elasticity |
|---|---|---:|
| Illustrative air-cooled 1 MW | `pue` | 0.996 |
| Illustrative direct-to-chip 1 MW | `grid.ghg_kgco2e_per_kwh` | 0.995 |
| Illustrative single-phase immersion 1 MW | `grid.ghg_kgco2e_per_kwh` | 0.992 |

Elasticity is a local one-at-a-time screening measure, not a substitute for
Monte Carlo or global sensitivity analysis.

## Reproducibility

- Model version: `0.2.0`
- Scenario SHA-256 digests and complete contribution results:
  [`results.json`](results.json)
- Inputs: bundled files from `examples/`
- Functional unit: one MWh delivered to IT equipment
- Comparative assertion: false

## Interpretation boundary

The numerical ordering shown here is an artifact of synthetic assumptions.
Publication-quality results require reviewed inventories, canonical impact
methods, quantified uncertainty, consistent system models, and critical review
as specified in `docs/BENCHMARK_PROTOCOL.md`.
