# LCA method decision notes

These notes preserve the original 15 questions, our provisional responses, the
evidence used, and the resulting package behavior. They are not presented as Dr.
Darin Nutter's conclusions. His requested task is to identify responses that are
unreasonable, incomplete, or too prescriptive.

## 1. Is IT MWh a defensible functional unit?

**Provisional response.** One MWh delivered to IT equipment is acceptable for
cooling-system screening only when alternatives provide the same computational
service, utilization, reliability, throttling behavior, and hardware life. If
those conditions differ, a public benchmark should add a workload-oriented unit
such as completed benchmark jobs, useful FLOP, or another auditable service
measure.

**Package response.** Version 0.2 supports `it_mwh`, requires its declaration,
and does not claim that it measures useful computation. Workload units remain a
roadmap item.

Sources: [ISO 14044](https://www.iso.org/standard/38498.html);
[ILCD Handbook](https://op.europa.eu/de/publication-detail/-/publication/325e9630-8447-4b96-b668-5291d913898e);
[Microsoft/WSP Nature study](https://www.nature.com/articles/s41586-025-08832-3);
[ASHRAE framework](https://www.ashrae.org/technical-resources/ai-data-center-framework/introduction-and-purpose).

## 2. Should the default be attributional, cut-off, or consequential?

**Provisional response.** Do not silently choose a universal system model. Every
study must declare its modeling and allocation approach. The first engineering
benchmark should be attributional because its purpose is transparent technology
comparison. Consequential scenarios should address decisions such as siting,
procurement, and large-scale adoption.

**Package response.** Allocation is required metadata. Electricity accounting is
explicitly `location_based`, `market_based`, or `consequential`.

Sources: [ILCD Handbook](https://eplca.jrc.ec.europa.eu/reportGuidelines.html);
[ecoinvent system models](https://support.ecoinvent.org/system-models).

## 3. How should metal recycling be handled?

**Provisional response.** Use one internally consistent allocation method for
every alternative. Report gross production and end-of-life contributions
separately. When recovery credits materially affect the ranking, run a no-credit
case and at least one alternative recycling allocation. Do not combine cut-off
background data with avoided-burden credits without testing the hybrid.

**Package response.** Negative end-of-life values are allowed. The audit warns
when allocation does not explain recycling, recovery, or substitution. A
parallel-allocation runner is still needed.

Sources: [ISO 14044](https://www.iso.org/standard/38498.html);
[Environmental Footprint method](https://environment.ec.europa.eu/document/download/cb899bd7-bb06-491d-9989-c856a401fcd0_en?filename=CommissionRecommendationontheuseoftheEnvironmentalFootprintmethods_0.pdf);
[ecoinvent system models](https://support.ecoinvent.org/system-models).

## 4. Should replacements be annualized or modeled discretely?

**Provisional response.** Discrete replacements over the facility study period
are preferred for benchmark studies. Linear annualization is acceptable for
screening when service lives and timing are uncertain, but it must be labeled.

**Package response.** `replacement_model` is required. `discrete` counts
installations across the study period; `linearized` preserves the earlier
screening approximation.

Sources: [ILCD Handbook](https://op.europa.eu/de/publication-detail/-/publication/325e9630-8447-4b96-b668-5291d913898e);
[Microsoft/WSP Methods](https://www.nature.com/articles/s41586-025-08832-3).

## 5. Which impact methods should be canonical?

**Provisional response.** Require a method and version for every result. The
proposed first benchmark should report IPCC AR6 GWP100 with an AR5 sensitivity;
renewable, non-renewable, and total primary energy with heating-value convention;
and inventory-level blue-water consumption plus regionalized AWARE scarcity.
Exact versions remain subject to expert review and database availability.

**Package response.** GHG, primary-energy, and water method identifiers are
required. Illustrative methods block public comparative assertions.

Sources: [IPCC AR6 WGI Chapter 7](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/);
[ISO 14046](https://www.iso.org/standard/43263.html);
[Environmental Footprint method](https://environment.ec.europa.eu/publications/recommendation-use-environmental-footprint-methods_en);
[Microsoft/WSP study](https://www.nature.com/articles/s41586-025-08832-3).

## 6. Should dielectric-fluid assessment extend beyond GWP?

**Provisional response.** Yes. Report fluid production, replenishment, direct
loss, recovery, and end of life. Add human-toxicity and freshwater-ecotoxicity
indicators when inventory and characterization factors are defensible.
Distinguish LCA toxicity screening from site-specific chemical risk assessment.

**Package response.** Fluid lifecycle impacts and direct emissions are separate.
Additional impact categories and persistence indicators are deferred.

Sources: [USEtox](https://usetox.org/model);
[USEtox manual](https://manual.usetox.org/);
[ASHRAE refrigerants chapter](https://handbook.ashrae.org/Handbooks/F25/SI/F25_Ch29/F25_Ch29_si.aspx);
[Microsoft/WSP PFAS discussion](https://www.nature.com/articles/s41586-025-08832-3).

## 7. How should renewable electricity procurement be treated?

**Provisional response.** Never substitute market-based procurement for the
physical grid result. Report location-based and market-based results separately,
using eligible contractual instruments and residual mix where applicable.
Consequential effects belong in a different scenario, not Scope 2 arithmetic.

**Package response.** Electricity accounting mode is mandatory. Dual reporting
within one scenario is not yet implemented.

Sources: [GHG Protocol Scope 2 Guidance](https://ghgprotocol.org/sites/default/files/2023-03/Scope%202%20Guidance.pdf);
[Scope 2 FAQs](https://ghgprotocol.org/scope-2-frequently-asked-questions);
[EPA eGRID](https://www.epa.gov/egrid).

## 8. Should upstream and on-site water be combined?

**Provisional response.** Preserve them as separate contributions. They may be
summed for inventory-level blue-water consumption only when definitions and
boundaries are compatible. Scarcity-weighted results must retain geography.

**Package response.** Electricity supply-chain water and on-site cooling water
are separate contributions. Regional AWARE characterization is deferred.

Sources: [ISO 14046](https://www.iso.org/standard/43263.html);
[Microsoft/WSP water definition](https://www.nature.com/articles/s41586-025-08832-3);
[ASHRAE framework](https://www.ashrae.org/technical-resources/ai-data-center-framework).

## 9. Should we use a pedigree matrix?

**Provisional response.** Yes. Use reliability, completeness, temporal,
geographical, and technological scores to document fitness for the goal. Do not
automatically convert scores to probability distributions; quantitative
uncertainty requires separate evidence.

**Package response.** The data-package schema contains the five dimensions and
review status. Scenario sources separately declare uncertainty.

Sources: [EPA LCI data-quality guidance](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P100R8JX.TXT);
[EPA data-quality paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC5919259/).

## 10. What uncertainty is required for a public comparison?

**Provisional response.** Require quantified parameter uncertainty, propagation
such as Monte Carlo, contribution analysis, and sensitivity/rank-reversal
analysis. Confidence intervals alone are insufficient; identify the inputs
controlling the conclusion. Ranges and one-at-a-time sensitivity support
screening, not a decision-grade claim.

**Package response.** The audit blocks comparisons with `not_quantified`
sources. Version 0.2 provides one-at-a-time screening; correlated Monte Carlo and
global sensitivity remain roadmap work.

Sources: [GHG Protocol uncertainty guidance](https://ghgprotocol.org/sites/default/files/2022-12/Quantitative%20Uncertainty%20Guidance.pdf);
[Brightway tutorial](https://learn.brightway.dev/en/latest/content/chapters/BW25/BW25_introduction.html);
[Brightway cautions](https://docs.brightway.dev/en/latest/content/faq/negative_results.html).

## 11. How should confidential manufacturer data be handled?

**Provisional response.** Confidential data may inform an analysis if a
competent independent reviewer can inspect the evidence. Public results should
disclose normalized or aggregated values, ranges, quality, and reviewer status.
If independent scrutiny is impossible, the data cannot support a public claim.

**Package response.** Sources declare `public`, `aggregated_confidential`, or
`confidential` and their review status. The audit blocks non-public data without
independent review from supporting a comparative assertion.

Sources: [ISO 14044](https://www.iso.org/standard/38498.html);
[Microsoft/WSP data sources](https://www.nature.com/articles/s41586-025-08832-3).

## 12. What if databases produce different rankings?

**Provisional response.** Harmonize unit, boundary, allocation, geography, time,
and impact method first. Then treat database/system model as a scenario
variable. Report contribution differences and rank reversals; never select the
database that produces the preferred result.

**Package response.** Dataset IDs, methods, and allocation are recorded.
Automated multi-database comparison is deferred.

Sources: [ILCD Handbook](https://op.europa.eu/de/publication-detail/-/publication/325e9630-8447-4b96-b668-5291d913898e);
[ecoinvent models](https://support.ecoinvent.org/system-models);
[Environmental Footprint method](https://environment.ec.europa.eu/document/download/cb899bd7-bb06-491d-9989-c856a401fcd0_en?filename=CommissionRecommendationontheuseoftheEnvironmentalFootprintmethods_0.pdf).

## 13. What should count as independent critical review?

**Provisional response.** Follow ISO 14044 and ISO 14071. Internal or
single-reviewer feedback is useful during development, but a public comparative
assertion should receive an independent panel review with suitable LCA and
technical competencies and a published review statement.

**Package response.** Critical-review status is required. The audit
conservatively requires `independent_panel` for a public comparative assertion.

Sources: [ISO 14044](https://www.iso.org/standard/38498.html);
[ISO 14071](https://www.iso.org/cms/%20render/live/en/sites/isoorg/contents/data/standard/08/62/86264.html);
[ISO review analysis](https://link.springer.com/article/10.1007/s11367-019-01706-7).

## 14. What belongs in software versus author responsibility?

**Provisional response.** Software should enforce structure, units, traceability,
declared methods, versioning, calculation consistency, and explicit gates. The
author remains responsible for goal and scope, functional equivalence, boundary
completeness, proxies, allocation, uncertainty evidence, interpretation, and
claims. Passing an audit is not ISO conformity or critical review.

**Package response.** Automated checks are called an audit, not certification.

Sources: [ISO 14044](https://www.iso.org/standard/38498.html);
[ILCD guidance](https://eplca.jrc.ec.europa.eu/reportGuidelines.html);
[EPA pedigree limitations](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P100R8JX.TXT).

## 15. Which supermarket and refrigeration practices should we adapt?

**Provisional response.** Adapt separation of direct fluid emissions and
indirect energy, explicit charge and leakage histories, climate-sensitive hourly
operation, replacement, end-of-life recovery, and refrigerant sensitivity. Also
adapt Dr. Nutter's regional treatment of electricity and water. Do not copy
historical supermarket leakage defaults into data centers; collect
technology-specific measurements or bounded scenarios.

**Package response.** Charge, loss, direct GWP, production, and end of life are
separate. The performance template captures load, climate, energy, and water.
Hourly simulation and measured loss distributions are next.

Sources: [Burek and Nutter, storage and retail](https://ideas.repec.org/a/eee/rensus/v133y2020ics1364032120303610.html);
[Burek and Nutter, regional distribution centers](https://hero.epa.gov/reference/5052553/);
[ORNL open LCCP framework](https://www.ornl.gov/publication/comparative-study-environmental-impact-supermarket-refrigerations-systems-using-low-gwp);
[IIR LCCP guideline](https://www.cold.org.gr/library/downloads/Docs/Guideline%20for%20life%20cycle%20climate%20performance.pdf).

## Consolidated request for Dr. Nutter

Please identify:

1. Any response that is methodologically unreasonable.
2. Any quality gate that is too strict or too weak.
3. Any important alternative method that should be represented.
4. Any statement that overinterprets ISO, ILCD, PEF, or accepted practice.
5. Decisions that should remain configurable rather than project defaults.
