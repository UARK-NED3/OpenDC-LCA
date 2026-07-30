# Core figure and table plan

This plan separates validated findings from hypothesis-generating and synthetic
demonstrations. A manuscript must preserve those evidence labels in captions
and surrounding text.

## Core figures

1. **OpenDC-LCA concept and software workflow** (`figure0_opendc_lca_workflow.svg`)
   - Panel (a): evidence acquisition, source registration, harmonization, and
     scenario assembly.
   - Panel (b): calculation engines, scientific audit and claim gate, and
     reproducible outputs through the CLI, Python API, local GUI, openLCA
     JSON-LD, and Brightway-ready mappings.
   - Contribution emphasized: a traceable interface between heterogeneous
     public/experimental evidence and reproducible data-center cooling LCA.

2. **Independent reconstruction of the Microsoft/Nature results**
   (`figure1_microsoft_grid_reductions.svg`)
   - Validated arithmetic reproduction of all released Figure 4 component
     totals.
   - Contribution emphasized: exact, auditable reconstruction from released
     source data rather than a visual approximation.

3. **Climate context and monthly cooling-performance hypotheses**
   (`figure2_monthly_climate_pue.svg`)
   - Fayetteville TMY temperature and monthly PUE produced by explicit
     technology curves.
   - Contribution emphasized: temporal coupling between climate and cooling
     operation.
   - Status: hypothesis-generating; the curves are not measurements.

4. **Hourly operational greenhouse-gas screening**
   (`figure3_hourly_operational_ghg.svg`)
   - Operational GHG intensity under the assumed curves and Arkansas eGRID
     factor.
   - Contribution emphasized: transparent propagation of weather-sensitive PUE
     into normalized operational impact.
   - Status: hypothesis-generating.

5. **Measurement-to-annual-impact demonstration**
   (`figure4_measurement_surface_demo.svg`)
   - Hourly integration of load, weather, interpolated cooling power, PUE, and
     operational GHG.
   - Contribution emphasized: the direct interface for NED3 laboratory or
     simulation performance surfaces.
   - Status: synthetic software verification.

6. **Validated load-temperature surface contract**
   (`figure5_synthetic_performance_surface.svg`)
   - Complete rectangular performance surface, interpolation domain, and
     no-extrapolation boundary.
   - Contribution emphasized: physical input validation and explicit limits of
     applicability.
   - Status: synthetic software verification.

7. **Lifecycle contribution analysis**
   (`../results/representative-screening/ghg-contributions.svg`)
   - Operational, equipment, fluid-production, and direct-fluid contributions.
   - Contribution emphasized: interpretable hotspot decomposition.
   - Status: representative screening; not a technology benchmark.

8. **Uncertainty and sensitivity envelope**
   (`../results/v0.3-experimental/uncertainty-intervals.svg`, paired with a
   sensitivity ranking generated from the same scenario)
   - Contribution emphasized: exposing parameters that can reverse a ranking.
   - Status: screening uncertainty; independent parameter distributions.

9. **Reliability-driven replacement and maintenance sensitivity**
   - Expected Weibull renewal counts, Arrhenius-adjusted characteristic life,
     maintenance impacts, and downtime exposure across declared thermal
     conditions.
   - Contribution emphasized: connecting cooling-dependent component
     temperature assumptions to lifecycle replacement burdens.
   - Status: model demonstration until lifetime and maintenance parameters are
     supported by reviewed field or accelerated-life evidence.

Figures 1-6 form the recommended main-text set. Figures 7-8 are recommended
for the Supplementary Information unless journal length permits.

## Core tables

1. **OpenDC-LCA capability and evidence matrix**
   - Rows: source registration, scenario validation, static LCA, temporal
     operation, measurement surfaces, uncertainty, audit/claim gate, interfaces.
   - Columns: input, method, output, evidence requirement, current status.

2. **Microsoft/Nature reconstruction audit**
   (`table1_microsoft_reproduction_audit.csv`)
   - All architecture, electricity-scenario, and impact-metric combinations;
     released total, reconstructed total, and numerical difference.

3. **Grid-scenario reductions relative to air cooling**
   (`table2_grid_reductions_vs_air.csv`)
   - Compact validated result for cold plate, one-phase immersion, and
     two-phase immersion.

4. **Public-data and experimental evidence register**
   - Provider, dataset/version, geography, temporal coverage, role, license or
     redistribution constraint, and manuscript use.

5. **Hourly preview summary**
   (`table3_hourly_preview_summary.csv`)
   - Annual PUE, operational GHG intensity, and relative change.
   - Must be labeled hypothesis-generating.

6. **Monthly climate-performance summary**
   (`table4_monthly_temperature_pue.csv`)
   - Monthly temperature and architecture-specific mean PUE values.

7. **Measurement-surface annual integration**
   (`table5_measurement_surface_demo.csv`)
   - IT energy, cooling energy, water, mean PUE, uncertainty interval, and
     operational GHG.
   - Must be labeled synthetic.

8. **Scientific claim-gate criteria**
   - Evidence status, source completeness, functional-unit consistency,
     boundary compatibility, interpolation coverage, uncertainty disclosure,
   and independent review.

9. **Interoperability and reliability verification matrix**
   - openLCA exchange preservation, Brightway mapping, reference-flow handling,
     reliability equation checks, maintenance accounting, and unsupported
     availability features.

Tables 1-5 are recommended for the main text. Tables 6-8 can be supplementary.
