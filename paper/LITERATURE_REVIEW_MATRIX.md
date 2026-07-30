# Literature review and gap matrix

## Review question

What prevents published data-center cooling LCAs from being independently
updated, geographically transferred, coupled to measured thermal performance,
and used to prioritize the next measurements or inventories?

## Synthesis

| Literature stream | Established contribution | Persistent limitation | OpenDC-LCA response |
|---|---|---|---|
| Whole-data-center screening LCA | Whitehead et al. established that operational metrics alone can transfer burdens across life stages. | Models and background data are difficult to reconstruct; early studies predate current AI hardware. | Explicit system-boundary schemas, source registry, component contributions and claim gates. |
| Hyperscale cooling LCA | Alissa et al. compared air, cold plate, one-phase and two-phase immersion per Vcore-year across GHG, primary energy and blue water. | Released normalized results are rich, but foreground bills of materials and licensed background processes remain unavailable; spatial and hourly variation are limited. | Reconstruct all released totals, retain their functional unit, then add transparent eGRID re-basing and evidence-status labels without claiming independent reproduction of proprietary inventories. |
| Cooling-device product LCA | Isler-Kaya and Karaosmanoglu used manufacturer inventory and multi-impact manufacturing scenarios. | A device functional unit does not capture compute delivered, facility interaction or server-life effects. | Keep device, facility and compute-service units separate and require an explicit equivalence argument. |
| National energy-water footprint | Siddik et al. quantified regional trade-offs between data-center energy, carbon and water. | Cooling architectures, embodied inventories and workload performance are not resolved at the same level. | Join region-specific factors to architecture contributions while preserving the screening status of the join. |
| Water-footprint methods | Ristic et al. separated onsite and electricity-mediated water; AWARE adds scarcity characterization. | Water withdrawal, consumption and scarcity are frequently conflated; temporal and watershed resolution are often absent. | Separate onsite and supply-chain consumption, reject scarcity claims without characterization factors, and register watershed/time metadata. |
| Cooling performance and thermoeconomics | Reviews and experimental studies establish PUE, heat-transfer and overclocking advantages under particular designs and conditions. | Annual-average or vendor values are not portable across load, weather and heat-rejection configurations. | A measured rectangular performance-surface contract, bounded interpolation and 8,760-hour integration. |
| Electronics embodied impacts | Boyd et al. and manufacturer PCFs show that server manufacturing is material, especially on cleaner grids. | Semiconductor inventories are old, proprietary, product-specific and methodologically heterogeneous. | Preserve product-level EPD records, quantify cross-product dispersion and identify server inventories as a priority rather than treating one factor as universal. |
| LCA software and databases | openLCA, Brightway, ecoinvent, Sphera, USLCI and GLAD provide calculation engines, formats or inventories. | General tools do not supply a data-center cooling ontology, functional-unit equivalence tests, performance-map coupling or an evidence claim gate. | A domain layer that exchanges JSON-LD/Brightway data while retaining cooling-specific engineering and review rules. |
| Prospective and consequential assessment | Prospective electricity and water methods can represent future infrastructure conditions. | Scenario assumptions, technology learning and grid evolution can dominate results, and are rarely packaged with cooling models. | Versioned scenarios, declared temporal scope, sensitivity and reliability modules; prospective inventories remain a planned extension. |

## Gaps that motivate the paper

1. **Reproducibility gap.** A published total cannot be updated unless source
   identities, foreground quantities, background mappings, characterization
   methods and calculation equations are retained together.
2. **Transferability gap.** A U.S.-average result does not reveal whether
   cooling choices retain the same order across grids, climates or water
   contexts.
3. **Functional-unit gap.** IT MWh, server-year, rack, facility area and
   Vcore-year answer different questions and cannot be combined silently.
4. **Performance-coupling gap.** Cooling LCAs usually use static PUE values,
   whereas cooling energy and water vary with load, temperature, humidity,
   controls and heat-rejection design.
5. **Embodied-data gap.** Server, electronics, support-equipment and fluid
   inventories are incomplete, old or proprietary precisely when grid
   decarbonization makes them more influential.
6. **Uncertainty-to-measurement gap.** Pedigree matrices identify weak data,
   but published studies rarely combine weakness with contribution magnitude
   to prioritize experiments and inventory development.
7. **Water-context gap.** Consumption volumes without watershed- and
   time-specific scarcity factors cannot support water-impact claims.
8. **Interoperability gap.** General LCA engines calculate impacts, but do not
   enforce the engineering equivalence, evidence status and claim conditions
   specific to alternative cooling architectures.

## Paper thesis

OpenDC-LCA is not proposed as another general LCA engine. It is an
evidence-governed, data-center cooling research layer that makes heterogeneous
released results, public factors, experimental performance surfaces and
general-purpose LCA databases interoperable without erasing their incompatible
units or evidentiary limits. Its scientific contribution is demonstrated by
new deductions from released and public data: geographic re-ranking, the
operational-to-embodied transition, contribution-weighted evidence priorities,
server-footprint dispersion and construction-material leverage.
