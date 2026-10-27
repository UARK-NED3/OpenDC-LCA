# Paper package

This directory is the stable handoff for manuscript development.

- `MANUSCRIPT.md`: editable, source-controlled manuscript draft.
- `SUPPLEMENTARY_INFORMATION.md`: detailed secondary analyses, illustrative
  software cases, data roles, and reproduction notes.
- `OpenDC-LCA_manuscript.docx`: formatted coauthor-review manuscript.
- `OpenDC-LCA_manuscript.pdf`: rendered review copy.
- `OpenDC-LCA_supplementary_information.pdf`: rendered supplementary review
  copy.
- `FIGURE_TABLE_PLAN.md`: prioritized main-text and supplementary figure/table
  portfolio with evidence labels.
- `RESULTS_PACKAGE.md`: consolidated interpretation, equations, limitations,
  and paper-use guidance.
- `RESPONSE_TO_REVIEW.md`: point-by-point record of completed revisions and
  evidence still required before submission.
- `SUBMISSION_READINESS_CYCLE_2026-08-02.md`: outcomes of the Step 0--5
  scientific assessment, reviewer-author revisions, and final verification.
- `SUBMISSION_ACTIONS.md`: author approvals and external actions intentionally
  kept outside the manuscript.
- `AUTHOR_REVISION_2026-08-23.md`: evidence-bearing response to the latest
  internal pre-submission review.
- `tables/`: machine-readable CSV tables.
- `figures/`: editable, publication-ready SVG figures.
- `OpenDC-LCA_integrated_evidence.xlsx`: auditable workbook for the earlier
  Tables 1--27 analysis. The machine-readable CSV files in `tables/` are the
  authoritative source for the new Federal electricity, endpoint-method,
  equal-width robustness, residual-mix, and server-inclusion Tables 28--34.
- `results-workbook.xlsx`: compact formula-driven example workbook retained
  for the practitioner workflow.
- `overleaf/`: compiling Elsevier `elsarticle` project for Applied Energy,
  including vector figures, highlights and a cover-letter draft.
- `OpenDC-LCA_Applied_Energy_Overleaf.zip`: reproducible Overleaf working
  archive. Known author affiliations, corresponding-author contact, HFA
  employment, and AI use are stated; CRediT roles, funding, any additional
  interests, a DOI deposit, and external critical review remain pre-submission
  actions.

Regenerate the Applied Energy analysis and submission files with:

```bash
python scripts/run_submission_pipeline.py --skip-refresh
```

The Applied Energy extension reconstructs all eGRID years to a common AR5
GWP100 basis and adds a partial Federal LCA Commons linked-system calculation,
explicit cutoff reporting, ordinary/residual accounting sensitivity, endpoint
method audit, exact equal-width rank bounds, and transparent server-record
inclusion flow. These are transferability tests of the released foreground
model, not substitutes for a common-method cooling LCA, measured performance
surfaces, or architecture-specific bills of quantities.

The manuscript is a scientific draft, not a submitted paper. All authors must
approve authorship, CRediT roles, funding, acknowledgments, competing interests,
AI disclosures, and the LCA critical-review pathway before submission.
The generic shared-site metering and functional-equivalence protocol is in
`docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md`. It contains no facility
telemetry or identifying site records.
