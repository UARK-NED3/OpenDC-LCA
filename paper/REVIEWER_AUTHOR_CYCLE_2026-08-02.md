# Five-step reviewer-author revision record

Date: 2026-08-02

Scope: manuscript, supplementary information, analysis scripts, package code,
tests, downloaded-data provenance, generated CSV/SVG/XLSX/DOCX/PDF artifacts,
Overleaf project, repository documentation, primary-source web pages, and the
local Microsoft/WSP, eGRID, Boavizta, ÖKOBAUDAT, NOAA, USLCI, GLAD, and USGS
evidence archive.

## Step 1 - Reviewer assessment

Recommendation at entry: **major revision**. The paper had a useful
boundary-aware premise, but the evidence and software claims were not yet
fully aligned.

| Priority | Reviewer comment | Evidence examined |
|---|---|---|
| Major | The eGRID-to-Microsoft transfer combined direct generation GWP100 rates with lifecycle GTP100 anchors. The common unit did not make the boundaries or characterization methods equivalent. | Microsoft/Nature paper and Zenodo workbook; nine eGRID workbooks; Eqs. (7)-(9) |
| Major | State-level results were described too strongly despite extrapolation beyond both released electricity anchors. | 459 state/DC-year records; released wind and U.S.-grid endpoints |
| Major | Deterministic first rank across grid factors was not a joint uncertainty result. Foreground, embodied, service-equivalence, and dependence assumptions could change the ranking. | Microsoft normalized contributions; original break-even analysis |
| Major | The functional unit retained Vcore-year but did not quantify the useful-computation error required to overturn a rank. | Released normalized results and technology margins |
| Major | Downloaded datasets appeared in the repository but their numerical role, exclusion logic, and provenance were not sufficiently clear. | All local provider groups, source notes, derived tables, manuscript Table 1 |
| Major | The raw-file checksum manifest omitted the historical eGRID inputs used in the paper. | `source-file-manifest.json`; analysis file-loading code |
| Major | The stress calculation used one global random-number stream, making scenario results dependent on iteration order; it also lacked a dependence analysis. | `run_applied_energy_analysis.py`; generated stress tables |
| Major | The manuscript did not distinguish automated/coauthor checks from independent critical review under ISO 14071. | claim-gate text; ISO 14040, ISO 14044, and ISO 14071 source pages |
| Major | The package reproduction command used undeclared extras and `pytest`, although the project did not supply those extras and the clean environment did not include pytest. | `pyproject.toml`; supplement commands; clean-clone test |
| Major | The clean-install and test-count claims were not reproducible as written. | local test suite; clean clone without `private-data/` |
| Major | The main workflow figure was too wordy and the results portfolio did not make dependence and assumption blocks central. | manuscript-scale figure renders; figure plan |
| Major | The main PDF had poor float placement and a long evidence table that could not fit safely on one page. | page-by-page PDF render; TeX log |
| Moderate | A 75 kg CO2e/MWh boundary allowance was described qualitatively without reporting the exact crossover clearance. | crossover equation and 2023 Vermont rate |
| Moderate | Monte Carlo integration precision was not separated from epistemic uncertainty in the assumed stress ranges and correlations. | 20,000-draw output only |
| Moderate | The draft contained stale result values, incomplete author/declaration placeholders, an overlength abstract, and highlights that no longer matched the analysis. | Markdown, Overleaf, cover letter, journal guide |

## Step 2 - First author revision

The response changed the analysis rather than only reframing the claims.

1. Recast the electricity transfer as a **numerical intensity-position index**,
   not a lifecycle-process substitution. The manuscript now states the GWP/GTP,
   generation/consumption, and direct/lifecycle differences explicitly.
2. Reconstructed 2012-2023 eGRID releases from gas-specific emissions on one
   AR5 GWP100 basis. The U.S. rate declines from 517.731 to 349.667 kg
   CO2e/MWh; the largest provider-versus-harmonized difference is 0.248
   kg CO2e/MWh.
3. Counted released-anchor coverage: 322/459 rows interpolate, one falls below
   the low anchor, and 136 exceed the high anchor. Every extrapolation is now
   labeled.
4. Calculated the exact 2023 boundary clearance, 73.0086 kg CO2e/MWh, instead
   of treating the 75-unit grid point as an upstream estimate.
5. Added a useful-computation break-even diagnostic. The median adverse
   correction needed to erase the two-phase first rank is 5.503% across 2023
   states.
6. Added seeded triangular stress designs for grid, use phase, embodied
   contribution, and service equivalence; added block decomposition and latent
   Gaussian-copula dependence cases at 0, 0.5, and 1.
7. Added SHA-256-derived scenario seeds so results are independent of loop
   order and stored them as hexadecimal strings to avoid spreadsheet precision
   loss.
8. Added a file-level provenance module and manifest builder/checker. The
   ledger now covers 40 provider files in ten source groups; analysis metadata
   records the 11 numerical inputs and analysis-code hash.
9. Converted analysis tests to the Python standard library, added provenance,
   exact-boundary, order-invariance, and stress-structure regression checks,
   and corrected package reproduction commands.
10. Reorganized the literature review around cooling experiments, LCA
    boundaries, electricity accounting, time-explicit LCA, uncertainty,
    pedigree data, value of information, interoperability, and critical review.
11. Replaced the central evidence-priority graphic with an assumption-block and
    dependence heat map; retained the heuristic priority analysis in the
    supplement.
12. Rebuilt the manuscript, result tables, figures, workbook, and practitioner
    documentation from the revised code.

## Step 3 - Second reviewer assessment

Recommendation after the first revision: **minor-to-moderate revision**, with
five new issues found by attempting to reconcile every claim to code and every
artifact to the manuscript.

1. **Headline/decomposition mismatch.** The headline independent stress used
   direct triangular draws, whereas the zero-correlation decomposition used a
   Gaussian-copula transform. The U.S. wide values differed (55.25% versus
   55.05%) even though the text treated them as the same design.
2. **No numerical convergence result.** Twenty thousand draws were declared,
   but the paper did not show that Monte Carlo noise was small relative to the
   reported design effects.
3. **Manifest-to-analysis linkage lacked a regression gate.** Both records
   existed, but no test required every computational input checksum to equal
   the provider ledger.
4. **Publication layout defect.** The four-column evidence table extended below
   the PDF page boundary; its last rows and link annotations were outside the
   printable area.
5. **Submission hygiene.** The abstract exceeded Applied Energy's 250-word
   limit; highlights were stale; author/declaration prompts remained in the
   compiled draft; the archive statement promised a DOI that did not yet
   exist; and the workflow schematic still showed the old 99%-to-56% range.

The second reviewer also confirmed that the following first-round issues were
fully addressed: common-basis eGRID reconstruction, anchor counts, exact
boundary clearance, useful-computation break-even, dataset-role table,
source-file coverage, stable scenario seeds, ISO-review distinction, and
clone-only raw-data skips.

## Step 4 - Second author revision

1. Made the headline joint stress exactly the all-block, zero-correlation
   member of the dependence analysis, using the same copula transform and
   scenario seed. A regression test now requires exact table reconciliation.
2. Added nested 5,000-, 20,000-, and 80,000-draw convergence runs. For the U.S.
   cases, 20,000-draw frequencies differ from 80,000-draw results by at most
   0.110 percentage points; the maximum across both locations is 0.709 points.
   The reported Monte Carlo standard error is labeled as numerical integration
   precision, not empirical uncertainty.
3. Added a test that every analysis input path and SHA-256 matches the complete
   provider-file ledger.
4. Rebuilt the integrated workbook with separate `Joint Stress`, `Stress
   Structure`, and `Stress Convergence` sheets. Scenario seeds are text, not
   rounded spreadsheet numbers.
5. Converted manuscript Table 1 to a multi-page longtable with repeated headers
   and safe break points; gave Table 2 a separate balanced column layout.
6. Reduced the abstract to 247 words, refreshed all five highlights to remain
   below 85 characters, removed unapproved declarations from the manuscript,
   removed correspondence placeholders, and moved external actions to
   `SUBMISSION_ACTIONS.md`.
7. Changed the archive statement to say plainly that no DOI-bearing deposit has
   yet been minted.
8. Updated the workflow schematic from 99%-to-56% to 99%-to-55% and synchronized
   the manuscript, supplement, response, results summary, workbook, figures,
   and machine-readable tables.

## Step 5 - Final language and consistency audit

Checks performed:

- searched the manuscript and generated TeX for hidden prompts, chat-system
  instructions, model references, TODO/TBD markers, confirmation prompts, and
  unapproved placeholders;
- checked citation/reference reciprocity, contiguous reference numbering,
  DOI resolution, equation numbering, figure/table numbering, and result-value
  consistency;
- checked abstract and highlight limits against the current Applied Energy
  author guide;
- reviewed frequent formulaic words such as “consequently,” “enable,”
  “establish,” “comprehensive,” “notably,” “furthermore,” “demonstrates,” and
  “transformative”; removed avoidable instances while retaining technical uses
  of “robust” and “robustness” where they name the analysis question;
- tightened awkward phrases, removed unsupported superlatives, and separated
  verified results from sensitivity designs, recommendations, and future data
  needs;
- verified Eq. (1)-(13) for variable definition, unit consistency, and stated
  boundary; and
- rendered and inspected the manuscript, supplement, figures, and every
  workbook sheet/chunk for clipping, overlap, stale values, and unreadable seed
  fields.

Final internal recommendation: **the code and secondary-analysis manuscript are
coherent and reproducible, but a decision-grade public comparative assertion
still requires primary architecture-resolved performance/useful-computation
data, bills of quantities, lifecycle-consistent electricity inventories,
empirical joint uncertainty, water-scarcity characterization where claimed, an
external LCA critical review, author-approved declarations, and a DOI-bearing
archive.** These are scientific or external requirements and were not hidden by
proxy data or optimistic language.
