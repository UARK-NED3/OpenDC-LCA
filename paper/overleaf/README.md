# OpenDC-LCA Applied Energy submission package

Upload this directory as a ZIP to Overleaf and select `main.tex` as the main
document. The project uses Overleaf's standard `elsarticle` class.

Included:

- `main.tex`: complete manuscript;
- `supplement.tex`: standalone Supplementary Information;
- `figures/`: publication figures converted to vector PDF;
- `highlights.tex`: Applied Energy highlights;
- `cover_letter_draft.tex`: editable cover letter;
- eight key CSV result tables for reviewer traceability.

Before submission, confirm author order, corresponding-author email, funding,
acknowledgments, competing interests, CRediT roles, and whether the manuscript
should be linked to the Applied Energy data-center special issue or submitted
as a regular article.

Regenerate after editing `paper/MANUSCRIPT.md`:

```bash
python paper/build_overleaf.py
cd paper/overleaf
tectonic main.tex
tectonic supplement.tex
```
