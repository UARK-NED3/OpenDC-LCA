# Reader questions and responses

This companion document separates direct manuscript support from derived screening calculations, partial linked-system results, and remaining evidence needs. It does not extend the claim boundary of the manuscript.

## Scope and contribution

### Q1. What engineering decision does this paper help inform?

**Response.** The paper helps a practitioner or researcher decide whether published data-center cooling LCA comparisons are transferable to a new grid, time period, or facility context. It identifies the evidence needed before a published numerical comparison can support a local design decision.

**Evidence status.** Directly supported by the stated research gap, framework, and conclusions.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 1.5, 2.1, and 5.

### Q2. Is this paper a new comparative life-cycle assessment of data-center cooling architectures?

**Response.** No. The paper is a transferability assessment of published cooling comparisons. It reconstructs and interrogates a released Microsoft and WSP workbook, tests selected electricity-accounting changes, and defines the measurements required for a new comparative assessment. It does not claim that one cooling architecture is environmentally superior across facilities.

**Evidence status.** Directly supported claim boundary.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.2, 3.1, 4.1, and 5.

### Q3. What is the paper's principal contribution beyond a review of prior data-center LCAs?

**Response.** The contribution is an evidence-to-decision framework that links a released comparative model to i) reconstruction checks, ii) electricity-boundary and time sensitivity screens, iii) rank-robustness diagnostics, and iv) a measurement plan for converting a published comparison into a facility-relevant assessment. The framework makes the difference between a numerical screen and an independently supported comparative result explicit.

**Evidence status.** Directly supported by the methods and released practitioner outputs.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 1.5, 2.1, and 3.7. [Repository README](../README.md).

### Q4. Why does the analysis focus on the released Microsoft and WSP workbook?

**Response.** It is a published comparison with a released workbook that can be examined programmatically. That availability permits reconstruction of the reported totals and documentation of the model's input and endpoint identities. The workbook is a case study, not a representative sample of all data-center cooling LCAs.

**Evidence status.** Directly supported for model availability and study scope. The limitation is explicit.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.3, 2.5, and 3.1.

### Q5. Does the paper present any new facility measurements or a new foreground cooling inventory?

**Response.** No. The paper does not report new metered facility operations, a foreground bill of cooling equipment and materials, or a complete measured inventory for a common workload. The AHPCC material is a preliminary shared-infrastructure context and measurement protocol rather than an operational result.

**Evidence status.** Directly supported limitation.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.7 and 4.8. [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q6. Which conclusions are independently supported by the authors' calculations, and which remain numerical screens based on the released workbook?

**Response.** The source-workbook reconstruction, historical national eGRID direct-generation comparison, and deterministic threshold calculations are derived from documented inputs and code. The cooling totals, rank order, and component values inherited from the workbook remain released-workbook numerical screens because the authors do not have a full foreground inventory or an independent LCA-software reproduction. The partial Federal LCA Commons result tests selected linked electricity systems only.

**Evidence status.** Mixed. The distinction is explicitly maintained in the manuscript.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 3.1 to 3.4 and 4.1 to 4.2. [Submission actions](SUBMISSION_ACTIONS.md).

## Model reconstruction

### Q7. How were the 24 published total results reconstructed, and how closely do the reconstructed values match the source workbook?

**Response.** The repository extracts the released workbook values and checks the 24 reported totals against the workbook's published structure. The paper reports reconstruction as a method-identity check. It does not convert the workbook inputs into a new independently verified foreground inventory.

**Evidence status.** Derived from the released workbook and repository code.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.5 and 3.1. [Execution manifest](../results/submission-execution-manifest.json).

### Q8. Why do the published workbook's GTP100 and GWP100 endpoint labels require special attention?

**Response.** The released Excel endpoint labeled GTP100/GWP100 does not numerically match the released GWP100 endpoint. Therefore, the paper preserves source-sheet identities, reports the discrepancy, and avoids treating the workbook endpoint label as a resolved indicator mapping. A reader should not combine values from those endpoints without confirming the original impact-method definition.

**Evidence status.** Directly checked against the released workbook.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.5 and 3.1.

### Q9. What does the eGRID harmonization represent, and what does it not represent?

**Response.** The eGRID calculation compares national direct generation-emission intensities over 2012 through 2023. The reported change from 517.73 to 349.67 kg CO2e/MWh is a historical generation-side sensitivity. It is not a full life-cycle electricity factor and does not establish a regional marginal emission factor, a facility power mix, or a cooling-system result.

**Evidence status.** Derived from public eGRID data under the stated national direct-generation boundary.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.6, 3.2, and 4.2.

### Q10. What does the Federal LCA Commons electricity calculation add beyond the eGRID comparison?

**Response.** It provides a separate, named-dataset screen using linked product systems from the Federal LCA Commons. It tests how the workbook comparison behaves under those available life-cycle inventory links, rather than only under historical direct-generation intensities.

**Evidence status.** Partial linked-system screen.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.7 and 3.3.

### Q11. Why is the Federal LCA Commons result described as a partial linked-system screen rather than a full life-cycle electricity factor?

**Response.** The calculation uses 71 ordinary non-residual 2023 product systems but finds 287 unlinked exchanges across 47 processes. Those unresolved links prevent the result from representing a complete life-cycle electricity system. The manuscript therefore reports the partial linked factor without calling it a complete benchmark or an independent reproduction.

**Evidence status.** Directly supported by the linked-system audit.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.7, 3.3, and 4.2.

### Q12. Why were 71 ordinary non-residual product systems used, and do they represent 71 independent data-center scenarios?

**Response.** The 71 systems are the ordinary non-residual 2023 electricity product systems available under the documented selection rule. They are inventory-system inputs for a partial electricity-accounting screen. They are not 71 independent data-center facilities, workload traces, or comparative cooling experiments.

**Evidence status.** Directly supported selection rule and interpretation boundary.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.7 and 4.2.

## Interpretation

### Q13. Why does the manuscript avoid declaring a universally preferable cooling architecture?

**Response.** A comparative architecture claim needs a common service definition, matched workload behavior, equipment quantities, operating conditions, and complete inventory boundaries. The released workbook does not provide all of those elements for independent confirmation. Changing only electricity factors does not establish functional equivalence or resolve foreground inventory differences.

**Evidence status.** Directly supported limitation.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.1, 4.4, and 4.8.

### Q14. What does the 1.32 percent all-block rank-robustness threshold mean?

**Response.** Under the paper's equal-width deterministic perturbation construction, a simultaneous change of 1.32 percent across all blocks is sufficient to remove the reported rank separation for at least one compared result. It is a diagnostic of fragility under the stated construction. It is not an uncertainty interval for a physical system.

**Evidence status.** Derived deterministic diagnostic.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.9, 3.4, and 4.3.

### Q15. Are the rank-robustness thresholds probabilities that one architecture will outperform another?

**Response.** No. The analysis does not assign probability distributions, correlations, or measurement-error models to the perturbations. The threshold indicates the size of an equal-width deterministic change needed to remove a rank separation, not the likelihood of reversal.

**Evidence status.** Directly supported method limitation.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.9 and 4.3.

### Q16. Why can service life, use-phase energy, and embodied impacts have different threshold values?

**Response.** Each block enters the total result with a different magnitude and allocation. A fixed percentage change in a dominant use-phase contribution can change a result more than the same percentage change in a smaller embodied contribution. The reported thresholds of 2.64 percent for service life, 2.99 percent for use phase, and 22.15 percent for embodied impacts describe the released-workbook comparison under the stated deterministic construction.

**Evidence status.** Derived deterministic diagnostic.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 3.4 and 4.3.

### Q17. What does the analysis indicate about server hardware and construction impacts?

**Response.** The analysis identifies these components as potentially decision-relevant evidence categories. It does not establish a universal contribution or ranking because the needed foreground quantities and functionally equivalent service data are not fully available for independent reproduction.

**Evidence status.** Evidence-priority assessment, not a generalized comparative result.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.10, 3.5, 3.6, and 4.8.

### Q18. How do grid decarbonization and the selected electricity accounting boundary affect the conclusions?

**Response.** National direct-generation intensity declined by 32.46 percent between 2012 and 2023 under the selected eGRID boundary. A different electricity boundary can alter absolute operating impacts and may affect the interpretation of a published comparison. Neither the historical trend nor the partial linked-system screen resolves missing functional-equivalence or foreground-inventory evidence.

**Evidence status.** Derived historical comparison with a stated boundary.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 3.2, 3.3, and 4.2.

## Functional equivalence

### Q19. What is the functional unit, and why is a Vcore-year used?

**Response.** The manuscript uses the published Vcore-year functional unit to preserve the source comparison's reported basis. A Vcore-year offers a normalizing service proxy, but it does not by itself ensure equivalent computational throughput, accelerator service, storage service, availability, or workload quality across systems.

**Evidence status.** Directly supported definition and limitation.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.2 and 4.4.

### Q20. Why is functional equivalence the central unresolved issue in comparative data-center LCAs?

**Response.** Environmental results can only be compared fairly when the alternatives deliver an equivalent defined service. Cooling equipment, server generations, accelerators, workloads, availability targets, storage, and network demand can all change the delivered service. Without a common measured workload and service definition, an apparent architecture difference can instead reflect a service difference.

**Evidence status.** Directly supported methodological requirement.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.1 and 4.4.

### Q21. Which measured quantities are needed before a cooling-architecture superiority claim can be made?

**Response.** A defensible comparison needs a common workload or service definition, IT and cooling energy time series, delivered computational and storage service, equipment bills of materials, service life and replacement records, refrigerant and water information where applicable, and an explicit electricity and construction boundary. Measurement uncertainty and allocation rules for shared systems must also be documented.

**Evidence status.** Proposed measurement requirement based on the paper's identified gaps.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.4, 4.7, and 4.8. [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q22. Can the framework use a common workload when servers, racks, or service levels differ?

**Response.** Yes, if the study defines an equivalent delivered service and measures it consistently. The basis may include completed jobs, computational throughput, accelerator use, storage, network service, availability, or another documented service metric. The selected metric must be matched to the decision and reported with the allocation rules and time basis.

**Evidence status.** Proposed analytical design requirement.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Section 4.4.

## Facility application

### Q23. Can this framework be applied to the Arkansas High Performance Computing Center?

**Response.** Yes, as a measurement and boundary-setting framework. The current facility context identifies shared building infrastructure, liquid-cooled HPC racks, a UPS, and a chiller, but it does not yet support a facility carbon, water, PUE, or comparative cooling result. The next action is to obtain metered time-series data and an agreed allocation boundary.

**Evidence status.** Proposed facility application. The described context is reported operational information rather than an analyzed performance dataset.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Section 4.7. [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q24. Does the manuscript report an AHPCC energy, carbon, water, or PUE result?

**Response.** No. The manuscript deliberately avoids reporting these performance results because dedicated facility meter data and a validated shared-infrastructure allocation have not been supplied. Any future result must identify its time window, meter locations, allocation method, units, and uncertainty.

**Evidence status.** Directly supported limitation.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Section 4.7.

### Q25. What boundary should a facility use when its data-center load shares building infrastructure with other occupants?

**Response.** The study should separately report i) directly metered IT and dedicated support loads, ii) shared infrastructure such as central cooling or electrical distribution, and iii) the allocation rule for shared loads. The chosen boundary must state whether the comparison is IT-only, dedicated-support, or a facility allocation. A single undifferentiated building electricity value is insufficient for a data-center-specific operational result.

**Evidence status.** Proposed boundary requirement.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md). [Manuscript](MANUSCRIPT.md), Section 4.7.

### Q26. How do PUE and a dedicated-support electricity ratio differ?

**Response.** PUE requires total facility energy divided by IT equipment energy within a defined facility boundary. A dedicated-support electricity ratio instead compares metered dedicated cooling and electrical-support energy with metered IT energy. The latter can be appropriate when the full facility boundary is shared and cannot be allocated credibly, but it must not be labeled PUE.

**Evidence status.** Proposed measurement-definition requirement.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md). [Manuscript](MANUSCRIPT.md), Section 4.7.

### Q27. What minimum meter data would provide the greatest value for an operational assessment?

**Response.** The highest-value initial records are synchronized interval measurements of UPS output or IT energy and of dedicated cooling-support energy, together with the interval duration, meter location, phases or circuits included, calibration status, and downtime or maintenance annotations. Supply and return water temperatures, flow rates, and workload or utilization indicators improve interpretation when available.

**Evidence status.** Proposed measurement plan.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

## Reproducibility and use

### Q28. What code, data, and execution records are available for audit or reuse?

**Response.** The repository contains the analysis code, documented source-data roles, practitioner outputs, tests, and a submission execution manifest. The manuscript's data and code statement identifies the repository and distinguishes released materials from external datasets and facility data that require their own access conditions.

**Evidence status.** Directly supported repository and manuscript availability statement.

**Where to verify.** [Repository README](../README.md). [Execution manifest](../results/submission-execution-manifest.json). [Manuscript](MANUSCRIPT.md), Data and code availability.

### Q29. Can a reader reproduce the full foreground cooling comparison in openLCA or Brightway today?

**Response.** Not fully. The repository includes reproducible calculations and a documented assessment workflow, but the authors do not claim a complete independent foreground reconstruction in openLCA or Brightway. Such a reconstruction requires process quantities, inventory links, impact-method identities, cutoffs, and data-access rights that fully specify the original comparison.

**Evidence status.** Directly supported reproducibility limitation.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.1, 4.8, and Data and code availability. [Submission actions](SUBMISSION_ACTIONS.md).

### Q30. What datasets or permissions are needed to extend the analysis without violating source or facility-data restrictions?

**Response.** An extension needs rights to use and redistribute each foreground inventory, background database, workbook, and facility dataset. For facility work, the data owner should approve the scope, aggregation, retention, access controls, and publication treatment. Public metadata can support discovery, but it does not establish redistribution rights or approval to publish operational records.

**Evidence status.** Research-governance requirement.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.3, 4.7, 4.8, and Data and code availability.

### Q31. Is there an immutable archived release with a DOI for the exact analyzed version?

**Response.** The current repository is version controlled and includes an execution manifest. The manuscript does not yet claim an immutable DOI archive for the exact submission state. Creating a tagged, archived release after final author and rights checks remains a submission action.

**Evidence status.** Current reproducibility gap.

**Where to verify.** [Submission actions](SUBMISSION_ACTIONS.md). [Execution manifest](../results/submission-execution-manifest.json).

### Q32. What are the most important next steps for research, software development, and facility engagement?

**Response.** The next steps are i) collect common-workload operational measurements and a complete foreground inventory, ii) establish a documented shared-infrastructure allocation, iii) reproduce the specified comparison in an LCA platform when data rights permit, iv) quantify cutoffs and uncertainty, and v) archive the final code and inputs at a stable release. These steps would turn the present transferability assessment into a stronger facility-specific comparative study.

**Evidence status.** Proposed next research and release plan.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.4, 4.7, 4.8, and 5. [Submission actions](SUBMISSION_ACTIONS.md).

## Applied assessment

### Q33. For a shared building that contains a data center and non-data-center occupants, how would you draw the electrical and thermal boundaries for an operational assessment?

**Response.** Begin with a one-line electrical diagram and a one-line thermal diagram. The electrical diagram should distinguish utility service, shared distribution, the data-center UPS, IT loads, dedicated cooling equipment, and non-data-center loads. The thermal diagram should distinguish the IT heat source, rack cooling interface, cooling loop, chiller or heat-rejection equipment, and any shared air-handling or plant components. Each meter and sensor should be assigned to one boundary category. The assessment must state the allocation method for every shared component.

**Evidence status.** Proposed facility-assessment method.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md). [Manuscript](MANUSCRIPT.md), Section 4.7.

### Q34. Which meter locations would allow you to separate IT energy, UPS losses, dedicated cooling-support energy, and shared building energy?

**Response.** The preferred hierarchy is i) UPS output or downstream IT distribution for IT energy, ii) UPS input for IT energy plus UPS losses, iii) dedicated chiller, pump, in-row, chilled-door, or other cooling-support circuits for dedicated cooling energy, and iv) whole-building or shared-plant meters for context only unless a documented allocation is defensible. Meter metadata must identify the voltage level, phases, circuits, interval duration, and whether a meter measures real energy or only apparent power.

**Evidence status.** Proposed measurement-design requirement.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q35. If UPS input energy and UPS output energy are available, how would you calculate UPS losses and avoid counting the same energy twice?

**Response.** Over the same synchronized interval, UPS loss energy is input energy minus output energy. The UPS loss fraction is \(1-E_{out}/E_{in}\) when input energy is nonzero. If the assessment reports IT energy from UPS output and support energy separately, add UPS losses once as support energy. Do not add UPS input, UPS output, and UPS losses together because input already includes output and losses.

**Evidence status.** Derived energy-balance relation. It requires synchronized energy measurements over the same boundary and time window.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q36. Under what conditions could you report PUE, and when should you report a dedicated-support electricity ratio instead?

**Response.** PUE may be reported only when total data-center facility energy and IT equipment energy are measured or credibly allocated over the same stated boundary and time window. The ratio is \(E_{facility}/E_{IT}\). When shared building loads cannot be allocated credibly, report a dedicated-support electricity ratio, such as dedicated cooling plus UPS losses divided by IT energy, and identify the omitted shared loads. It is an operational indicator and must not be called PUE.

**Evidence status.** Proposed measurement-definition requirement.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md). [Manuscript](MANUSCRIPT.md), Section 4.7.

### Q37. How would you establish whether a chilled-door retrofit changes the cooling energy required for a common HPC workload?

**Response.** Compare matched pre-retrofit and post-retrofit periods or matched racks operating the same documented workload. Hold or record the workload, IT configuration, uptime, thermal setpoints, outdoor conditions, water-supply conditions, and control mode. Measure IT energy, dedicated cooling-support energy, and delivered service. The primary comparison should be energy per equivalent delivered service, with repeated periods and an uncertainty analysis. A change in room temperature alone is not evidence of a cooling-energy reduction.

**Evidence status.** Proposed quasi-experimental design.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.4 and 4.7. [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q38. What operating measurements are needed to relate chilled-water or glycol-loop conditions to cooling energy and IT heat rejection?

**Response.** Measure supply and return fluid temperatures, flow rate, fluid composition or properties, pump and cooling-equipment electricity, and synchronized IT energy. The loop heat rate can then be estimated from \(\dot{Q}=\dot{m} c_p (T_{return}-T_{supply})\) using the documented property state. Interpret the result only after checking sensor locations, time synchronization, steady or transient window, heat losses, bypasses, and whether all rack heat passes through the measured loop.

**Evidence status.** Proposed measurement model.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md). [Manuscript](MANUSCRIPT.md), Section 4.7.

### Q39. How could supply-air, return-air, rack-inlet, and water temperatures be used to identify a potential airflow or control problem without claiming causation prematurely?

**Response.** Plot synchronized temperature differences by rack location, operating load, and cooling-equipment state. A persistent high rack-inlet temperature despite low supply-air temperature may indicate bypass, recirculation, uneven distribution, or inadequate local heat removal. A reduced water temperature difference at constant load may indicate a flow or heat-transfer change. These patterns are diagnostic hypotheses. Confirmation requires physical inspection, airflow or flow measurements, control-sequence records, and repeated observations.

**Evidence status.** Proposed diagnostic interpretation.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q40. What time resolution, operating period, and maintenance annotations would make an initial meter campaign useful for LCA and energy analysis?

**Response.** Use synchronized interval energy data that resolve material load and control changes. Fifteen-minute data are a practical initial target, while one-minute data are preferable when instrumentation and storage permit. Cover representative workload and weather conditions, including normal operation and identified high-load periods. Record meter outages, calibration changes, maintenance, failures, setpoint changes, outages, and configuration changes. The campaign duration should be stated rather than assumed representative.

**Evidence status.** Proposed measurement plan. The suitable duration depends on workload seasonality, cooling configuration, and the decision being evaluated.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md). [Manuscript](MANUSCRIPT.md), Section 4.7.

### Q41. How would you define a functionally equivalent service for comparing a largely CPU-based rack with a GPU-intensive rack?

**Response.** Define the service in terms of the actual user demand rather than installed core count. For a specified workload suite, report completed jobs, workload-specific throughput, job quality, accelerator utilization, memory and storage requirements, availability, and time basis as relevant. A CPU core-year and a GPU-hour should not be declared equivalent without a workload-specific translation supported by measured performance and service constraints.

**Evidence status.** Proposed functional-equivalence requirement.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Section 4.4.

### Q42. Which foreground inventory items would you request for an architecture-specific cooling LCA, and which omissions could materially change the result?

**Response.** Request quantities, materials, manufacturing or supplier information where available, transport, installation, maintenance, replacements, service life, refrigerant type and charge, fluid composition, water treatment, end-of-life treatment, and electricity or water use for cooling equipment. Also record rack interfaces, pumps, manifolds, heat exchangers, chillers, air-moving equipment, controls, and distribution infrastructure. Omitting a large or frequently replaced component, refrigerant leakage, shared-plant allocation, or the use-phase energy boundary can materially change a comparison.

**Evidence status.** Proposed foreground-inventory requirement.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.2, 4.1, and 4.8.

### Q43. How would you distinguish a sensitivity range from a statistical uncertainty interval when presenting an operational scenario analysis?

**Response.** A sensitivity range is created by deliberately varying assumptions or inputs over stated values. It does not have a probability interpretation unless distributions, dependence, and sampling or measurement models are defined and justified. A statistical uncertainty interval requires an uncertainty model, parameter estimation or calibration evidence, propagation method, and a stated coverage interpretation. Scenario ranges and confidence intervals should be labeled separately.

**Evidence status.** General uncertainty-reporting requirement.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 2.9 and 4.3. [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q44. A facility manager asks whether this framework can provide a free energy audit. What can be offered now, and what evidence is needed before reporting an audit result or investment recommendation?

**Response.** The team can offer a no-cost research assessment that defines boundaries, reviews available records, identifies missing meter data, computes transparent indicators from authorized data, and shares the resulting analysis. It should not promise the scope, certification, independence, liability coverage, or investment-grade conclusions of a contracted energy audit. A facility-specific result or recommendation needs approved meter data, equipment and control information, agreed boundaries and allocation rules, data-quality checks, and a review of the resulting analysis with the facility.

**Evidence status.** Proposed engagement boundary. It is not a claim that the present manuscript has audited a facility.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Section 4.7. [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q45. What quality-control checks would you perform before accepting a month of interval meter data for analysis?

**Response.** Check i) the meter identity and electrical boundary, ii) units and whether values are interval energy or power, iii) timestamps, time zone, daylight-saving treatment, and interval completeness, iv) synchronization among meters and sensors, v) negative, repeated, missing, or implausible values, vi) agreement with independent utility, UPS, or equipment totals when available, and vii) configuration, calibration, maintenance, and outage records. Retain the raw file and create a documented cleaned derivative rather than overwriting source data.

**Evidence status.** Proposed data-provenance and quality-control requirement.

**Where to verify.** [Shared-infrastructure measurement protocol](../docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md).

### Q46. After completing the measurement campaign, what evidence would be needed to convert this transferability assessment into a defensible comparative cooling LCA?

**Response.** The study would need a common measured service, matched or controlled workload periods, architecture-specific foreground bills of materials and use-phase records, explicit electricity, water, refrigerant, construction, and end-of-life boundaries, documented allocation for shared infrastructure, data-quality and uncertainty analysis, and an independently reproducible LCA model using identified methods and databases. A comparative assertion with external consequence may also require independent critical review under the applicable LCA standards and journal requirements.

**Evidence status.** Proposed evidence-completion gate.

**Where to verify.** [Manuscript](MANUSCRIPT.md), Sections 4.1, 4.4, 4.7, and 4.8. [Submission actions](SUBMISSION_ACTIONS.md).
