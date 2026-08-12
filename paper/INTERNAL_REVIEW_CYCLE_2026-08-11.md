# Internal reviewer-author-verifier cycle, 11 August 2026

## Scope

This pass re-examined the current manuscript, generated Overleaf source,
submission files, repository state, prior review records, and current Applied
Energy and Elsevier author requirements. It did not reinterpret unavailable
licensed inventories or convert conditional cooling screens into comparative
LCA results.

## Reviewer assessment before revision

**Editorial decision: major revision for submission compliance; scientific
claim boundary retained.** The paper's transferability-audit contribution was
substantive and appropriately limited, but six correctable problems remained:

1. The abstract had regrown to 299 words after coauthor revision, exceeding the
   journal's 250-word limit.
2. References 44, 45, and 48 appeared before reference 16, violating numerical
   order of first appearance.
3. The title page omitted the corresponding author's email, and the manuscript
   omitted known HFA employment and the substantive use of OpenAI Codex.
4. “Blocks comparisons” overstated what a metadata validator can enforce.
5. “FERC systems” was inconsistent with the defined term “FERC regions.”
6. Several web references lacked access dates, and earlier source encodings
   made names and non-ASCII text vulnerable during regeneration.

The reviewer panel did not identify a defensible new cooling-architecture
winner or a missing secondary calculation that would close the primary-data
gap. Adding another arbitrary sensitivity design would not strengthen the
paper.

## Author revisions

- Rewrote the abstract to 242 words while retaining the purpose, audit design,
  endpoint-method conflict, direct-generation trend, partial linked-system
  result, exact rank thresholds, and claim ceiling.
- Renumbered all 48 references and in-text citations in order of first
  appearance; no citation or reference is orphaned.
- Added the verified corresponding-author email and a disclosure of the two
  HFA employees.
- Added a methods description and manuscript declaration for OpenAI Codex use,
  plus a Figure 1 caption disclosure for the AI-assisted explanatory layout.
- Recast the validator claim as rejection of configured scenarios with
  incompatible declared metadata and retained the explicit limit that it does
  not verify underlying science.
- Corrected the FERC-region terminology, restored Unicode author and database
  names, and added access dates to mutable web references.
- Updated the author action list so funding, CRediT roles, any additional
  interests, HFA's organizational role, AI records, immutable archiving, and
  external critical review cannot be mistaken for completed work.

## Verifier and second-review gates

The following checks must pass on the regenerated package:

- abstract no longer than 250 words;
- one to seven keywords and three to five highlights, each no longer than 85
  characters;
- references 1--48 cited exactly once or more and first introduced in numerical
  order;
- complete automated test suite;
- two-pass LaTeX compilation without undefined references or overfull boxes;
- text extraction free of hidden prompts and authoring placeholders; and
- visual inspection of every manuscript page.

## Residual author and external actions

The revised paper remains a Technology Assessment, not a public comparative
assertion of cooling superiority. Before submission, the authors must approve
CRediT roles, funding, acknowledgments, all competing-interest and AI
statements, and HFA's role; archive the exact analyzed revision with a durable
identifier; independently reproduce the linked-system electricity calculation
in an established LCA engine; and determine the appropriate ISO critical-review
path. These items require author decisions or external evidence and were not
filled with assumptions in this cycle.

## Completed verification

- The abstract is 242 words; the manuscript has seven keywords. The separate
  highlights file contains five items of 67--71 characters.
- All 48 references are cited, no citation is missing, and first appearances
  follow the sequence 1--48.
- All 65 automated tests passed under Python 3.12.
- The Elsevier manuscript compiled twice to 52 pages and the supplement twice
  to 15 pages. The final logs contain no undefined citations or references,
  fatal errors, or overfull boxes. Benign underfull-line, bookmark, and MiKTeX
  update-notice messages remain.
- All 52 manuscript pages and all 15 supplementary pages were rasterized and
  visually inspected. No clipping, overlap, broken figures or tables, missing
  glyphs, or footer collision was found. Hyperlink borders were hidden to
  improve readability.
- Extracted PDF and DOCX text contain no TODO/TBD markers, hidden prompts,
  authoring instructions, or AI self-reference outside the required disclosure.
- The regenerated DOCX passed ZIP/package and structural checks (one section,
  313 paragraphs, two tables, and five figures). The canonical DOCX renderer
  could not run because LibreOffice is not installed, so the DOCX does not have
  an independent visual-render pass; the submission-facing PDF does.

**Second-review decision: minor author/external action.** The correctable
manuscript defects found in this cycle are resolved. The residual items above
cannot be closed without author confirmation, a public archival action, or
independent LCA evidence.

## Section-heading style revision

At the author's request, the main-text and supplementary headings were audited
for grammatical form and rhetorical function. Sentence-like headings and
headings that disclosed a finding or conclusion were replaced with short noun
phrases that identify the subject of each section. This editorial revision did
not change the section order, technical content, numerical results, equations,
figures, tables, citations, or claim boundaries.

## Colon and semicolon revision

At the author's request, colons and semicolons were removed from the manuscript
narrative and supplementary prose wherever they were not part of a source
title, URL, identifier, or required syntax. Short lists were recast with i),
ii), and subsequent markers. Longer lists were rewritten as complete sentences
with First, Second, and related transitions. The revision preserved the
technical relationships, numerical values, equations, evidence classes,
citations, and claim limits.

## Figure and table integration revision

Generic visual signposting was replaced with figure-led technical orientation.
The main-text introductions now identify the plotted cooling architectures,
impact indicators, electricity cases, source populations, lifecycle boundaries,
thresholds, and panel roles. Supplementary figure introductions now state the
independent and dependent variables, operating ranges, sample sizes, percentile
markers, and screening limits that are visible in each plot. Table references
now describe the fields and methodological decisions conveyed by the table
rather than merely announcing its presence. Weak short transitions were also
merged with the technical statements they introduced. Numerical values and
evidence classifications were checked against the current plotted artifacts.
