# Measured benchmark, critical review, and DOI release pathway

OpenDC-LCA can validate and package evidence, but it cannot create measurements,
declare an independent review complete, or register a DOI without the responsible
people and repository.

## 1. Prepare the benchmark

Copy `templates/benchmark-manifest.json` beside the measured files. Each file
record requires a relative path, role, and SHA-256 checksum.

Evidence status must be one of:

- `synthetic`;
- `experimental_unreviewed`; or
- `reviewed`.

Validate before sharing:

```bash
opendc-lca benchmark-validate benchmark-manifest.json
```

## 2. Record independent review

Copy `templates/critical-review-record.json`. The record identifies reviewers,
scope, findings, responses, disposition, and completion date. The software does
not infer approval from a name or an incomplete record.

A manifest marked `reviewed` cannot be packaged unless the review disposition
is `approved` or `approved_with_conditions`.

```bash
opendc-lca benchmark-validate benchmark-manifest.json \
  --review critical-review.json
```

## 3. Create the release artifact

```bash
opendc-lca benchmark-package benchmark-manifest.json \
  opendc-lca-benchmark-v1.zip --review critical-review.json
```

The ZIP contains the validated evidence, manifest, optional review record, and
`datapackage.json`. Provider-native files may be included only when their
licenses permit redistribution.

## 4. Register a DOI

Upload the ZIP to the University of Arkansas data repository, Zenodo, or another
approved repository. Reserve or register the DOI there, then insert the DOI into
the manifest and create the final immutable package. DOI registration remains a
human-controlled external action.

## Minimum measured benchmark

The first public benchmark should contain:

- a shared heat-load or IT-load boundary for air cooling and at least one
  liquid-cooling architecture;
- complete load-temperature points without extrapolation;
- pump, fan, CDU, and heat-rejection power;
- coolant temperatures, flow, and pressure drop;
- on-site water, duration, calibration, repeatability, and uncertainty;
- raw and processed data with processing code;
- source, license, authorship, and funding records; and
- Dr. Nutter's method-level review of functional unit, boundary, allocation,
  uncertainty, and comparative language.
