# Submission-readiness and reviewer-author cycle

Date: 2026-08-02

Scope examined: manuscript and supplementary information; released Microsoft/
WSP workbook and component data; historical eGRID workbooks; Federal LCA
Commons 2023 U.S. Electricity Baseline JSON-LD; IPCC AR5 characterization
factors; Boavizta, OKOBAUDAT, NOAA, USLCI, GLAD, and USGS source material;
package code, schemas, tests, generated tables and figures; current primary
literature and journal requirements; DOCX, PDF, and Overleaf deliverables.

Epistemic status: numerical values below were reproduced or derived by the
repository workflow. Statements about publication fit are reviewer judgments,
not editorial decisions. The original cooling architectures have not been
recalculated from foreground inventories under one LCIA method, and no new
experimental measurements were supplied.

## Step 0 - Mechanical-engineering research assessment and improvement

### Entry assessment

The earlier draft did not support a defensible claim that one cooling
architecture has the lowest lifecycle impact. Its released endpoints combine
incompatible electricity boundaries and an unresolved LCIA-method identity;
server service equivalence and architecture-specific quantities were also not
demonstrated. A paper framed mainly as a new comparative LCA would therefore
have insufficient evidentiary support.

The work does contain a publishable methodological contribution when framed as
a Technology Assessment and transferability audit. Its distinctive contribution
is the integrated test of four failure modes that are usually treated
separately: endpoint-method identity, lifecycle-electricity scope, functional
equivalence, and exact rank robustness. The software turns these checks into
explicit claim gates and traceable evidence classes.

### Analysis added

1. Parsed the released workbook at worksheet-XML level. The two detailed
   endpoint cells use AR5 GTP100, while the comparative formulas reference
   blank GWP100 cells. The two published numerical endpoints are retained only
   as numerical transfer anchors, not as a common-method LCA comparison.
2. Reconstructed all nine eGRID releases on one AR5 GWP100 basis. The national
   direct-generation rate fell from 517.731 kg CO2e/MWh in 2012 to 349.667 kg
   CO2e/MWh in 2023, a 32.462% decrease.
3. Implemented a linked-product-system calculation for 71 ordinary and 71
   residual Federal LCA Commons consumption systems. The national ordinary
   partial linked-system result is 422.931 kg CO2e/MWh: 369.848 from named
   generation processes and 53.084 from other linked processes. The residual
   result is 455.350 kg CO2e/MWh. These values retain documented cutoffs and
   are not described as full reproduced openLCA LCIA results.
4. Replaced unequal stress ranges with exact equal-relative-half-width rank
   certificates. At the national factor, the first reversal occurs at 2.994%
   for use-phase variation, 2.637% for service equivalence, 22.154% for
   embodied burden, and 1.318% when all four blocks move adversely together.
5. Added a useful-computation break-even diagnostic. The required one-sided
   correction is 5.24--6.04% across the 2023 state cases (median 5.50%); this is
   a measurement target, not an observed performance difference.
6. Audited all 55 Boavizta Datacenter/Server candidates. Forty-eight meet the
   declared inclusion rule and seven Lenovo records are excluded because the
   manufacturing share is blank. The included values are retained as
   heterogeneous evidence, not an architecture-specific product-substitution
   model.
7. Corrected fluid replacement and end-of-life mass accounting, added
   finite-value rejection, field-level lineage, boundary definitions,
   comparison incompatibility gates, deterministic manifests, and regression
   tests for the new calculations.

### Step 0 outcome

The revised contribution is potentially publishable as a transferability
Technology Assessment. It is not a verified public assertion that two-phase
immersion or any other architecture is environmentally superior. Stronger
acceptance evidence would be one measured architecture-resolved case or a
multi-case external validation showing that the audit finds known boundary and
method failures without excessive false blocks.

## Step 1 - Reviewer assessment

Recommendation at the start of this cycle: **major revision**.

Critical comments:

1. The released cooling endpoints do not establish a common LCIA method.
2. Direct-generation eGRID rates were being transferred into lifecycle cooling
   totals without a provider-linked consumption-system check.
3. A deterministic first rank over grid factors was presented too close to a
   comparative environmental conclusion despite unmeasured service
   equivalence and foreground quantities.
4. The earlier stress ranges assigned a much wider range to embodied burden,
   making its apparent dominance partly a design artifact.
5. The software's claim fields could be read as authorization for a public
   comparative assertion even though they checked declared metadata only.
6. Server records were not accompanied by a complete inclusion/exclusion flow.
7. Refrigerant/fluid replacement and end-of-life equations did not conserve
   the declared initial charge correctly.
8. The provenance path did not connect every final claim to exact inputs, code,
   runtime, tests, and outputs in one reproducible directed workflow.
9. The manuscript overclaimed transferability, mixed evidence classes, and did
   not place unresolved empirical requirements at the center of the argument.
10. The figures, supplement, generated TeX, and release notes were stale with
    respect to the newer analysis.

Constructive recommendation: recast the manuscript around a bounded decision
problem, retain incompatible results as auditable diagnostics, add exact
robustness and lifecycle-electricity scope checks, and state the measurements
needed to close the claim boundary.

## Step 2 - First author revision

The author response changed the calculations, data model, software controls,
and paper structure rather than only weakening the language.

1. Retitled and reframed the paper as a transferability audit and Technology
   Assessment; removed the cooling-winner claim.
2. Added the endpoint-method audit, Federal linked-system calculation, residual
   accounting sensitivity, exact equal-width certificates, and server-record
   inclusion table.
3. Kept generation-only and partial linked-system electricity factors separate
   in both data products and prose.
4. Replaced “claim allowed” user-facing text with “declared metadata gate
   passed” and an explicit notice that scientific or public authorization is
   not implied.
5. Added structured boundary and source maps and made mismatched functional
   units, electricity accounting, water treatment, allocation, LCIA method,
   and replacement rules block comparison.
6. Corrected the fluid mass balance and synchronized the methodology,
   equations, report generator, and tests.
7. Added an analytic toy JSON-LD solver test covering provider scaling, units,
   signs, and cutoffs, plus exact checks for all released totals and new tables.
8. Added a single submission workflow joining source-manifest creation,
   analyses, tests, and document generation with an execution manifest.
9. Rewrote the abstract, introduction, methods, results, discussion,
   conclusions, supplement, highlights, cover-letter draft, and data/code
   availability statement to preserve evidence classes and remaining blockers.

## Step 3 - Second reviewer assessment

Recommendation after the first author revision: **potentially acceptable as a
Technology Assessment after focused revision; not acceptable as a comparative
superiority LCA**.

Verified improvements:

- The endpoint-method conflict is now explicit and machine-tested.
- The 71 ordinary and 71 residual Federal systems remain separate, with
  process/link counts and cutoff disclosures.
- Equal-width certificates remove the earlier range-allocation artifact.
- The functional-unit shortfall is converted into a measurable break-even
  requirement.
- Source identity, file hashes, source-to-result lineage, and numerical
  regression tests are materially stronger.

Remaining reviewer findings:

1. The Federal calculation is a custom partial linked-system solver and has not
   been independently reproduced in openLCA or Brightway.
2. Claim gates validate metadata consistency and source presence, not physical
   truth, representativeness, or ISO-conformant critical review.
3. The hourly performance examples validate software pathways only; they do
   not include a closed facility energy balance or aligned time-varying grid
   impacts.
4. The work has one detailed transfer case. Journal significance would be
   stronger with a second published LCA or one measured cooling case.
5. The development revision is not yet an immutable public release with a DOI,
   tag, and independently runnable archive.

## Step 4 - Second author revision

1. Renamed the Federal output and Figure 4 as a **partial linked-system** or
   **screening** factor everywhere; documented the 287 unlinked technosphere
   inputs across 47 processes and infrastructure exclusions.
2. Changed practitioner, performance, CLI, and GUI fields so a passing gate is
   described as declared-metadata consistency, not permission to publish a
   comparative claim. Legacy field names remain only as compatibility aliases.
3. Narrowed every performance statement to cooling-only partial PUE software
   testing under declared weather/load inputs and a constant grid factor.
4. Added the second-review limitations and concrete next-data requirements to
   the Discussion, Conclusions, Supplement, and submission actions.
5. Rebuilt the DOCX, Elsevier TeX, figures, main PDF, supplement PDF, and
   Overleaf package from the revised sources.

Items not “resolved” by prose, because new evidence is required:

- original/common-method foreground inventories for all cooling alternatives;
- measured useful computation, IT and cooling electricity, server count and
  configuration, architecture-specific bills of quantities, fluid inventory,
  lifetime, maintenance, and replacement;
- empirical uncertainty distributions and correlations;
- water consumption with location-specific scarcity characterization;
- independent openLCA or Brightway reproduction and ISO-aligned external
  critical review;
- a tagged, archived public release and data DOI where redistribution rights
  permit.

## Step 5 - Language, consistency, and artifact audit

The final pass checked the Markdown sources, generated TeX, extracted PDF text,
captions, tables, references, data availability, and repository-facing prose.
Awkward and overgeneralized statements were narrowed; lifecycle, generation,
consumption, partial-linked, screening, measured, derived, and illustrative
results are now distinguished consistently. No hidden prompts, model
instructions, TODO/FIXME markers, authoring placeholders, or AI-attribution
language remain in the manuscript or supplement. Formulaic transition terms
were reviewed in context rather than replaced mechanically; no occurrence of
“consequently” remains, and technical uses of “establish” do not assert more
than the evidence supports.

Verification:

- 65 tests and 6 parameterized subtests passed under Python 3.12.
- The main Elsevier PDF compiled to 48 pages and the supplement to 14 pages.
- All 62 pages were rendered and visually inspected; figures are readable and
  no clipping, broken tables, or missing glyphs were found in the main and
  supplementary PDFs.
- The DOCX was regenerated and checked structurally. Its canonical visual
  render could not be completed because LibreOffice is absent; two bounded,
  read-only Microsoft Word export attempts also timed out. The DOCX is not
  included in the 62-page visual-pass claim.
- No undefined citations, references, or overfull boxes remain in the final
  LaTeX logs. Benign underfull-line and PDF-bookmark warnings remain.
- The earlier integrated-evidence workbook covers Tables 1--27; Tables 28--34
  are authoritative CSV outputs and are not silently represented as workbook
  sheets.

## Final outcome

The local manuscript package is ready for coauthor and external scientific
review as a Technology Assessment. Its central defensible result is that the
released numerical rank is not transferable as a public comparative LCA claim
until common-method, functionally equivalent, provider-linked evidence is
available. The paper now quantifies where rank sensitivity begins and specifies
the data required to make the next claim.

Before journal submission, the authors still need to approve authorship,
contributions, funding, conflicts, and declarations; decide whether the
single-case validation is sufficient for the target journal; obtain independent
technical/critical review; and tag and archive the exact public release. A
cooling-architecture superiority statement should not be added unless the
unresolved empirical and common-method evidence is supplied.
