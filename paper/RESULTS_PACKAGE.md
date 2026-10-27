# Consolidated scientific results package

## Central result

The defensible contribution is a Technology Assessment of whether a released
cooling LCA can be transferred across electricity contexts. It is not a new
comparative LCA and does not establish an environmentally preferred cooling
architecture.

## Main-paper results

### Released arithmetic and method identity

- All 24 normalized Microsoft/WSP totals reconcile at workbook precision from
  seven released component rows.
- The article states AR5 GWP100, but the archived detailed workbook places the
  two numeric endpoints in GTP100-labelled cells while the corresponding
  GWP100 cells are blank.
- Direct worksheet-XML parsing verifies that comparative use-phase formulas in
  `Comparative results 0% RE!D118` and `Comparative results 100% RE!D122`
  reference those blank F29 cells.
- Arithmetic reproduction therefore does not establish a common LCIA method,
  functional equivalence, or foreground completeness.

### Electricity contexts

- The national eGRID rate declined from 517.731 kg CO2e/MWh in 2012 to 349.667
  kg CO2e/MWh in 2023 after harmonization to AR5 GWP100.
- Of 459 state-year rates, 137 (29.85%) lie outside the two released numerical
  anchors. eGRID remains a direct-generation inventory.
- The 71 ordinary Federal at-user systems span 0.921-987.844 kg CO2e/MWh.
- The national ordinary system is 422.931 kg CO2e/MWh: 369.848 from named
  generation processes and 53.084 from other linked processes.
- The national residual-consumption system is 455.350 kg CO2e/MWh, 7.67% above
  the ordinary system; the accounting products are kept separate.
- The national ordinary calculation has 582 processes, 1,174 links, and 287
  unlinked technosphere inputs across 47 processes.
- Provider-scope infrastructure omissions and cutoffs make these partial
  linked-system factors, not complete lifecycle electricity benchmarks.

### Exact equal-width robustness

| Active block | National critical half-width |
|---|---:|
| Shared grid factor only | No reversal through 99.999% |
| Technology-specific use phase | 2.994% |
| Embodied burden | 22.154% |
| Service equivalence | 2.637% |
| All four blocks | 1.318% |

Across all 71 electricity systems, the all-block threshold is 1.123-1.479%.
The earlier embodied-dominance result was an artifact of assigning that block
a stress width ten times larger than use and service. At equal widths, service
equivalence and use phase are the limiting one-block factors.

The one-sided correction to two-phase impact per equivalent useful computation
needed to erase its numerical first rank is 5.24-6.04% across 2023 states, with
a 5.50% median. This is a break-even measurement target, not an observed
performance difference.

## Secondary evidence

- All 55 Boavizta server candidates are retained in an inclusion-flow table;
  48 are included and seven lack manufacturing share.
- Included manufacturing values span 465-2,503 kg CO2e/server and 116-626 kg
  CO2e/server-year. This is not an architecture substitution model.
- Selected ÖKOBAUDAT reductions are per-kilogram procurement screens and
  cannot be propagated without architecture bills of quantities.
- Triangular and Gaussian-copula frequencies are diagnostics of declared
  ranges and dependence, not probabilities.

## Software changes relevant to interpretation

- Fluid production, loss, and end-of-life mass balance under an explicit
  top-up convention.
- Scenario and performance parsing reject NaN and infinity.
- Comparative execution blocks method, boundary, accounting, and lineage
  mismatches; custom boundaries require matching structured records.
- Result manifests retain field-to-source maps and source-record digests.
- These are metadata checks, not authentication, empirical validation,
  parameter-level uncertainty mapping, ISO conformity, or critical review.

## Evidence required for a public comparative assertion

1. Common-method cooling inventories with complete bills of quantities and
   resolved electricity endpoint identity.
2. Architecture-resolved useful computation, IT configuration, throttling,
   availability, lifetime, and workload equivalence.
3. Measured use-phase power across common load and environmental domains, with
   energy-balance residuals and uncertainty.
4. Fluid production, loss, release, recovery, and end-of-life data under a
   conserved mass balance.
5. Complete electricity product systems or quantitative cutoff bounds,
   independently reproduced in an established LCA tool.
6. Water-scarcity characterization, empirical joint uncertainty, and external
   critical review if a superiority claim is intended.

## Regeneration

```bash
python scripts/run_submission_pipeline.py --skip-refresh
```

Machine-readable outputs are in `paper/tables/` and
`results/applied-energy/`.
