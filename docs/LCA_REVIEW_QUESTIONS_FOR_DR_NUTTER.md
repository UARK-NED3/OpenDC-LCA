# Questions for Dr. Darin Nutter

These questions identify decisions where LCA expertise is needed before the
methodology is promoted from draft to a reviewed benchmark. Short directional
answers are sufficient for the first review.

## Priority questions before merging the v0.2 methodology

1. Is `one MWh delivered to IT equipment` a defensible initial functional unit
   when compute hardware, utilization, reliability, and service are held
   constant? What additional functional unit should be mandatory for AI/HPC?

2. Should the default comparison use attributional, cut-off LCA, or should the
   package avoid selecting a default system model?

3. How should metal recycling be handled in the public benchmark: cut-off,
   recycled-content, avoided burden/substitution, or parallel scenarios?

4. Is annualizing equipment impacts by `quantity × impact / service life`
   acceptable for screening, or should replacements be modeled discretely over
   the facility study period?

5. Which impact-assessment methods and versions should be canonical for:
   - GHG emissions;
   - primary energy; and
   - water consumption or water scarcity?

6. Should direct dielectric-fluid loss be characterized only by climate GWP, or
   should persistence, toxicity, and other indicators be required when data
   exist?

7. How should renewable procurement be treated so location-based and
   market-based claims remain separate and consistent with LCA practice?

8. Should upstream electricity-related water and on-site cooling water be
   combined in the headline result, or always reported separately?

## Data quality and uncertainty

9. Would an EPA-style pedigree matrix with reliability, completeness, temporal,
   geographical, and technological scores from 1–5 be appropriate? Should the
   scores determine quantitative uncertainty distributions or remain
   qualitative?

10. What minimum uncertainty treatment should be required before a public
    comparative assertion: parameter ranges, Monte Carlo confidence intervals,
    global sensitivity analysis, or all three?

11. What is the minimum acceptable evidence for manufacturer foreground data
    that cannot be publicly disclosed? Would independent review of normalized
    values be sufficient?

12. When public and licensed databases produce different rankings, what
    reporting and interpretation protocol should we use?

## Review and publication

13. What should qualify as an independent critical review for an open academic
    benchmark that may make public comparative assertions?

14. Which ISO 14040/14044 requirements should be implemented directly in the
    software and which should remain responsibilities of the study author?

15. Are there supermarket or refrigeration LCA practices—particularly
    refrigerant leakage, equipment replacement, water, and end-of-life
    allocation—that we should adapt for data-center cooling?

## Requested review artifacts

The most useful first review would be comments on:

- `docs/CONVENTIONS.md`;
- `docs/BENCHMARK_PROTOCOL.md`;
- `schemas/scenario.schema.json`;
- `schemas/data-package.schema.json`; and
- the audit rules in `src/opendc_lca/audit.py`.
