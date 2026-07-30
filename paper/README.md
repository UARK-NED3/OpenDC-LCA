# Paper package

This directory is the stable handoff for manuscript development.

- `MANUSCRIPT.md`: editable, source-controlled manuscript draft.
- `OpenDC-LCA_manuscript.docx`: formatted coauthor-review manuscript.
- `OpenDC-LCA_manuscript.pdf`: rendered review copy.
- `FIGURE_TABLE_PLAN.md`: prioritized main-text and supplementary figure/table
  portfolio with evidence labels.
- `RESULTS_PACKAGE.md`: consolidated interpretation, equations, limitations,
  and paper-use guidance.
- `tables/`: machine-readable CSV tables.
- `figures/`: editable, publication-ready SVG figures.
- `results-workbook.xlsx`: formula-driven review workbook.
- `overleaf/`: compiling Elsevier `elsarticle` project for Applied Energy,
  including vector figures, highlights and a cover-letter draft.
- `OpenDC-LCA_Applied_Energy_Overleaf.zip`: upload-ready Overleaf archive.

Regenerate the Applied Energy analysis and submission files with:

```bash
python scripts/run_applied_energy_analysis.py
python paper/build_overleaf.py
cd paper/overleaf && tectonic main.tex
```

The v0.4 reproduction results are validated against released Microsoft/Nature
source data. The v0.5 hourly results remain a research preview. Version 0.6
provides the file contract and hourly engine for replacing its assumptions with
measured NED³ performance surfaces.

The Applied Energy extension adds nine EPA eGRID releases, 459 state-year
observations, historical absolute-benefit and embodied-share trajectories,
use-phase break-even requirements, and a Boavizta-informed server-inventory
stress test. These are transparent screening transformations of released
foreground results, not substitutes for measured cooling-performance surfaces
or a state-specific process LCA.

The manuscript is a scientific draft, not a submitted paper. Authorship,
contributions, funding, competing interests, target-journal formatting, and the
LCA critical-review pathway must be confirmed by the authors before submission.
