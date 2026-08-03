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
- `SUBMISSION_ACTIONS.md`: author approvals and external actions intentionally
  kept outside the manuscript.
- `tables/`: machine-readable CSV tables.
- `figures/`: editable, publication-ready SVG figures.
- `OpenDC-LCA_integrated_evidence.xlsx`: auditable workbook containing the
  harmonized eGRID series, boundary and anchor diagnostics, joint stress and
  numerical-convergence results, functional-unit sensitivity, public server records, material
  levers, and evidence-priority tables.
- `results-workbook.xlsx`: compact formula-driven example workbook retained
  for the practitioner workflow.
- `overleaf/`: compiling Elsevier `elsarticle` project for Applied Energy,
  including vector figures, highlights and a cover-letter draft.
- `OpenDC-LCA_Applied_Energy_Overleaf.zip`: reproducible Overleaf working
  archive; author metadata, declarations, DOI deposit, and external critical
  review remain pre-submission actions.

Regenerate the Applied Energy analysis and submission files with:

```bash
python scripts/run_applied_energy_analysis.py
python scripts/build_source_manifest.py --check
python -m unittest discover -s tests -v
python paper/build_overleaf.py
cd paper/overleaf && tectonic main.tex
```

The Applied Energy extension now reconstructs all eGRID years to a common AR5
GWP100 basis and adds anchor-extrapolation, electricity-boundary,
functional-unit, joint assumption-stress, and evidence-priority diagnostics.
These are transparent tests of the released foreground model, not substitutes
for lifecycle-consistent electricity processes, measured cooling-performance
surfaces, or architecture-specific bills of quantities.

The manuscript is a scientific draft, not a submitted paper. Authorship,
contributions, funding, competing interests, target-journal formatting, and the
LCA critical-review pathway must be confirmed by the authors before submission.
