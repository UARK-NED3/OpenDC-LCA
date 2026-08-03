# Figure and table plan for Applied Energy

The revised portfolio gives the main paper one argument: what is reproducible,
what is conditional, and which evidence would resolve the condition. Peripheral
software demonstrations and proxy-data distributions are moved to
Supplementary Information.

## Main-text figures

1. **Evidence-to-decision architecture**
   (`figure0_opendc_lca_workflow.svg`). Shows the numerical role of each
   evidence class, harmonization spine, claim gate, and decision outputs.
2. **Released-model arithmetic**
   (`figure1_microsoft_grid_reductions.svg`). Shows the reconstructed
   Microsoft/WSP reduction results while limiting the claim to released
   arithmetic.
3. **Historical electricity transition**
   (`figure6_historical_grid_transition.svg`). Uses the harmonized AR5-GWP100
   eGRID series and distinguishes state-generation scenarios from the provider
   U.S. aggregate.
4. **Scope and robustness diagnostic**
   (`figure8_scope_uncertainty.svg`). Combines anchor extrapolation,
   boundary-mismatch stress, joint assumption-stress frequency, and
   functional-unit sensitivity.
5. **Assumption-block and dependence diagnostic**
   (`figure9_stress_structure.svg`). Separates grid, use-phase, embodied, and
   service-equivalence stress and tests zero, intermediate, and common-mode
   latent dependence without interpreting the frequencies as probabilities.

## Main-text tables

1. **Dataset role and exclusion logic.** Makes clear how Microsoft/WSP,
   eGRID, Boavizta, ÖKOBAUDAT, NOAA, USLCI, GLAD, and USGS enter the study.
2. **Joint stress envelopes.** Declares all triangular half-widths and prevents
   stress frequencies from being interpreted as fitted probabilities.

Machine-readable supporting tables:

- `table15_egrid_historical_national_factors.csv`
- `table21_anchor_extrapolation_diagnostic.csv`
- `table22_boundary_mismatch_stress.csv`
- `table23_joint_assumption_stress.csv`
- `table24_functional_unit_sensitivity.csv`
- `table25_priority_index_sensitivity.csv`
- `table26_stress_structure_sensitivity.csv`
- `table27_stress_convergence.csv`

## Supplementary figures

1. Detailed 2023 crossover: `figure2_grid_crossover.svg`.
2. Deterministic performance discrimination:
   `figure7_performance_robustness.svg`.
3. Boavizta server distribution: `figure4_server_epd_distribution.svg`.
4. ÖKOBAUDAT material levers: `figure5_material_levers.svg`.
5. Fayetteville TMY illustrative PUE:
   `figure2_monthly_climate_pue.svg`.
6. Synthetic performance-map contract:
   `figure5_synthetic_performance_surface.svg`.
7. Evidence-priority heuristic: `figure3_data_priority.svg`; its alternative
   weighting ranks are reported in `table25_priority_index_sensitivity.csv`.

The supplement labels the weather/performance cases as software fixtures and
the Boavizta/ÖKOBAUDAT cases as secondary evidence that lacks
architecture-specific quantities or functional equivalence.
