# Literature review and contribution matrix

## Review question

What prevents a published data-center cooling LCA from being independently
updated, transferred across energy systems, coupled to measured thermal
performance, and converted into an efficient evidence-acquisition program?

| Literature stream | What is established | Remaining bottleneck | OpenDC-LCA contribution |
|---|---|---|---|
| Cooling technology reviews and experiments | Air, cold plate, single-phase, and two-phase systems have different heat-transfer, parasitic-power, control, and maturity envelopes [3-8]. | Results are design-, load-, coolant-, and weather-specific; useful computation is rarely linked to lifecycle inventory. | Bounded load-weather surface contract and explicit useful-computation equivalence requirement. |
| Data-center energy and environmental metrics | PUE and operational electricity are important, but can shift burdens outside the facility metric [9]. | PUE is not a lifecycle functional unit and cannot represent server production, fluid, replacement, or reliability. | Separate practitioner IT-MWh screening from service-based lifecycle comparison. |
| National energy-water footprint | Spatial electricity and water conditions change data-center burdens [10,11]. | Architecture foregrounds and useful-computation performance are not resolved at the same spatial scale. | Location scenarios remain screening transformations with preserved evidence class. |
| Cooling-device and facility LCA | Product and facility studies quantify manufacturing and operation across multiple categories [12,13,16]. | Product, rack, facility, and compute-service functional units are not interchangeable. | Claim gate rejects silent functional-unit conversion and missing equivalence. |
| Hyperscale cooling LCA | Alissa et al. provide a detailed Vcore-year comparison, normalized contributions, and pedigree assessment [14,15]. | Licensed backgrounds, complete BOMs, transferable performance mapping, and lifecycle electricity substitution are not fully public. | Arithmetic reconstruction plus conditional crossover, scope, and stress diagnostics without claiming proprietary reproduction. |
| Electricity accounting | Lifecycle, location-, market-, and marginal electricity answer different questions; inconsistent accounting can double count attributes [19-21]. | Common kg CO2e/kWh units conceal system-boundary and climate-metric differences. | Common-basis eGRID history, explicit intensity index, extrapolation count, and boundary-mismatch stress. |
| Dynamic/time-explicit LCA | Temporalis and bw_timex propagate temporal inventory and background change [22-26]. | Time resolution alone does not enforce cooling-domain functional equivalence or measured performance coverage. | Domain schema connects hourly cooling engineering to external LCA engines while preserving boundary and claim status. |
| Uncertainty and variability | Monte Carlo and sensitivity methods can separate input, scenario, and model effects [27,28]. | Unsupported ranges are often presented as confidence; correlations, convergence, and model form are underreported. | Declared stress envelopes, assumption-block and dependence diagnostics, and nested numerical-convergence checks, all separated from empirical probability. |
| Pedigree and data quality | Pedigree matrices document reliability and representativeness [28,29]. | A weak datum may have little decision consequence; converting scores to uncertainty is model dependent. | Rank sensitivity of a transparent contribution/weakness index and explicit limit relative to value of information. |
| Value of information | VoI can prioritize data according to expected decision benefit [30]. | Requires decision loss, empirical uncertainty, acquisition cost, and posterior updating. | Records the inputs needed to upgrade the current heuristic to formal VoI. |
| General LCA software | openLCA and Brightway calculate process networks and exchange inventories [31,32]. | They do not encode cooling performance, useful-computation equivalence, or a domain claim gate. | An interoperable cooling foreground/evidence layer, not a replacement LCA engine. |
| Comparative-claim review | ISO 14040/14044 define the LCA framework and requirements; ISO 14071 specifies review processes and reviewer competencies [42,43]. | Automated tests and coauthor review do not constitute independent critical review. | Machine-readable claim blockers plus an explicit external-review gate; no ISO-conformity claim. |

## Testable paper claims

1. The released Microsoft/WSP normalized totals are arithmetically reusable.
2. eGRID's changing GWP convention does not explain the 2012-2023 national
   generation-rate decline.
3. A nontrivial part of the state-year screen extrapolates beyond released
   electricity anchors.
4. The low-carbon cold-plate/single-phase reversal is sensitive to the
   electricity-boundary mismatch.
5. Deterministic first rank across grid factors is weaker than rank under joint
   foreground and functional-unit stress.
6. Useful-computation equivalence is a measurable first-order data need.

## Claims deliberately not made

- independent reproduction of licensed background inventories;
- a universal cooling-technology winner;
- state-specific lifecycle electricity results;
- probability of technology superiority from triangular stress envelopes;
- facility material reductions without bills of quantities;
- watershed scarcity from boundary geometry;
- empirical technology results from TMY/synthetic performance fixtures; or
- ISO critical review from automated tests or coauthor review.
