# ADR 0001: Separate foreground, background, and scenario data

- Status: accepted
- Date: 2026-07-28

## Context

Cooling performance measurements, generic LCA inventories, and deployment
assumptions have different owners, licenses, quality, and update frequencies.
Combining them in opaque aggregate factors prevents review and reuse.

## Decision

OpenDC-LCA will treat three layers separately:

1. Foreground engineering data describe the technology under study.
2. Background data translate materials, energy, and processes into impacts.
3. Scenario data describe location, workload, climate, lifetime, and operation.

Every input package must carry provenance. Licensed unit-process data remain on
the user's system; public adapters may map them to the open model.

## Consequences

Scenarios require more metadata, but calculations become auditable and users can
replace one layer without reconstructing the model. Results must identify the
exact scenario and data versions used.
