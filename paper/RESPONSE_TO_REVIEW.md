# Author response to internal major-review comments

This document records the changes made after the internal reviewer assessment
of the Applied Energy manuscript. It distinguishes completed revisions from
evidence that still must be acquired before submission.

## Major comments

### 1. Reference electricity mapping

**Response:** Addressed. The earlier transformation incorrectly treated the
2023 generation-weighted eGRID factor as the Microsoft grid endpoint. Direct
inspection of `LCA Tool with Detailed Equations.xlsx` identified the released
GaBi results as 524.893 kg CO2e/MWh for U.S. average electricity and 6.133
kg CO2e/MWh for U.S. average wind (IPCC AR5 GTP100, excluding biogenic
carbon). Equation 7, both analysis scripts, all affected tables and Figures 3-5
now use these two anchors. The cold-plate/one-phase crossover changes from
60.8 to 96.7 kg CO2e/MWh. Regression tests verify that both released endpoints
are reproduced and lock the corrected crossover.

### 2. Interpretation of 459 state-year records

**Response:** Addressed. The manuscript now calls these 459 controlled
electricity-factor scenarios evaluated with one fixed foreground model. It
explicitly states that they are neither independent LCAs nor statistical
replicates. The scenario count is used only to describe factor-space coverage.

### 3. Functional-unit consistency

**Response:** Addressed. Section 2.2 separates the package's default
practitioner unit (IT MWh) from the Microsoft research case (Vcore-year).
Results are not combined or converted because the public files do not provide
an architecture-independent mapping from electricity to useful computation.

### 4. Depth of energy analysis

**Response:** Partly addressed. The paper now describes the released primary
energy results more carefully and makes the energy-engineering meaning of the
break-even thresholds explicit. Synthetic hourly and performance-map examples
remain demonstrations, not findings. A submission-grade multi-climate energy
analysis still requires measured architecture-specific fan, pump, CDU and
heat-rejection power surfaces. This limitation and the required measurement
fields are stated in Sections 4.8 and 5.5.

### 5. Break-even versus uncertainty

**Response:** Addressed. The manuscript no longer claims that the 1-2% threshold
is an uncertainty bound. It identifies the 1.38% median cold-plate change and
6.46% median two-phase tolerance as deterministic performance-discrimination
thresholds. It states that ranking confidence requires joint propagation of
measurement, foreground, electricity, lifetime, correlation and model-form
uncertainty.

### 6. Boavizta stress-test interpretation

**Response:** Addressed in claims; further analysis remains possible. The text
now explains that common scaling of compute, storage and networking is a
structural stress test and does not represent architecture-specific server
substitution, separate product classes, server count, throughput, configuration
or lifetime. It remains secondary evidence rather than a probability model.

### 7. State production versus consumption factors

**Response:** Addressed. Methods, captions and limitations now identify eGRID
state total-output rates as generation-based. The manuscript explicitly
excludes imports, exports, contractual procurement, hourly dispatch,
transmission and consumption-based attribution.

### 8. Historical comparability

**Response:** Partly addressed. File, worksheet, field and unit-conversion
lineage is preserved for every record, and the manuscript warns that EPA data
and accounting revisions can affect cross-year comparisons. Before external
submission, the reconstructed national series should be checked against each
release's official national summary and any methodological discontinuities
should be tabulated.

### 9. Software material in the main paper

**Response:** Addressed. The two long capability and practitioner tables were
removed from the main manuscript. Section 4.9 now gives only the scientific
implementation and verification boundary, with detailed interface and release
material left in the repository and Supplementary Information.

### 10. Reconstruction versus validation

**Response:** Addressed. “Validation” and “reconstruction” claims were narrowed
to “arithmetic-consistency audit” or “reconciliation.” Captions, methods,
discussion and conclusions state that this does not validate proprietary
background inventories, confidential bills of materials, measured performance
or field operation.

### 11. Scope and title

**Response:** Addressed. The title now specifies “lifecycle greenhouse-gas
value.” Broader primary-energy, water and material findings remain supporting
context and are not presented as a complete multi-impact historical analysis.

### 12. Comparison against conventional methods

**Response:** Partly addressed. The literature review distinguishes PUE-only,
operational-only, static LCA and process-network tools from the present
foreground/evidence layer. A compact quantitative comparison table showing
which method detects crossover, embodied-share transition, evidence priority
and temporal effects remains a useful pre-submission addition.

## Presentation and reference corrections

- The abstract was reduced to approximately 260 words and now foregrounds the
  corrected anchors, functional-unit boundary and epistemic status.
- Main-text figure cross-references were corrected.
- References 24, 25, 30 and 31 were completed or corrected, including the
  journal for DOI `10.1016/j.cles.2025.100223`.
- The Overleaf, PDF and Word artifacts were regenerated.
- The final Word artifact passed visual rendering and an accessibility audit
  with no reported findings.

## Evidence still needed before an Applied Energy submission

1. Reviewed performance surfaces for air cooling and at least one liquid
   architecture, ideally all four, over load, coolant temperature and ambient
   conditions.
2. Component-resolved fan, pump, CDU and heat-rejection power; onsite water;
   replicate measurements; calibration records; and an uncertainty budget.
3. Hourly consumption-based or clearly specified location-based grid factors
   and multiple climate locations.
4. Architecture-specific bills of quantities and service lives.
5. A defensible useful-computation mapping for server count, throughput and
   cooling-enabled performance.
6. Independent LCA methodological review and confirmation of author,
   contribution, funding, competing-interest and acknowledgment statements.
