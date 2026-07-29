# Releasing OpenDC-LCA

OpenDC-LCA releases must be reproducible as both software and scientific
artifacts. A maintainer should complete this checklist from a clean checkout.

## Release checklist

1. Confirm that `pyproject.toml`, `src/opendc_lca/__init__.py`,
   `CITATION.cff`, and `CHANGELOG.md` use the same version.
2. Regenerate the representative report:

   ```bash
   opendc-lca report examples/*.json \
     --output-dir results/representative-screening
   ```

   For version 0.3 and later, also regenerate the experimental report:

   ```bash
   opendc-lca experimental-report examples/direct-to-chip.json \
     examples/performance-map-direct-to-chip.csv \
     examples/uncertainty-direct-to-chip.json \
     --output-dir results/v0.3-experimental
   ```

3. Run unit tests and the complete command-line smoke test:

   ```bash
   python -m unittest discover -s tests -v
   opendc-lca validate examples/air-cooled.json
   opendc-lca audit examples/air-cooled.json
   ```

4. Build and inspect both distributions:

   ```bash
   python -m pip install build twine
   python -m build
   python -m twine check dist/*
   ```

5. Install the wheel in a new virtual environment. Copy its bundled examples
   and generate a report without referring to the source checkout.
6. Review the generated equations, tables, figures, warnings, scenario digests,
   and source licenses.
7. Obtain the scientific review appropriate to the intended claims. Synthetic
   examples never authorize comparative environmental claims.
8. Merge the reviewed release pull request and create an annotated `vX.Y.Z`
   tag. Pushing the tag runs the GitHub release workflow and attaches the wheel
   and source distribution.

The workflow creates a GitHub release. Publishing to PyPI is intentionally a
separate maintainer decision and requires configured trusted publishing.
