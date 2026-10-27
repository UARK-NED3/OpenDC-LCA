# OCP foreground-disclosure intake

This blank template records product and facility information that is commonly
needed to make a future foreground LCA inventory auditable. It is informed by
the Open Compute Project (OCP) LCA guideline, the OCP and iMasons Climate
Accord embodied-carbon disclosure specification, and the OCP energy, carbon,
and water guideline.

Use `data/templates/ocp-foreground-disclosure-template.csv` for one record per
procured or installed item. Preserve the supplier document with its checksum.
Do not infer a missing value from a similar product.

For liquid cooling, use `cooling_loop_domain` to identify `FWS`, `TCS`, or
`direct_facility_connection`. Use `interface_role` for a CDU heat exchanger,
manifold, pipe, valve, hose, cold plate, pump, or other role. Record the actual
fluid identity only when it is documented. A generic glycol label is not a
substitute for concentration, inhibitor package, or material safety data.

The template supports evidence intake only. It does not make product-carbon
footprints comparable. Before aggregation, check the declared functional unit,
lifecycle modules, calculation method, background database, geography,
reference year, verification status, service life, and replacement rule.

For operational water, preserve a separate site water balance and electricity
consumption record. A water-use-effectiveness value is not a substitute for
inventory-level on-site or supply-chain water characterization.

## Source documents

1. Open Compute Project Foundation, *Guidelines: Life Cycle Assessment, LCA
   Guidelines for Cloud Providers*. https://www.opencompute.org/documents/lca-sop-in-ocp-document-submission-template-docx-pdf
2. Open Compute Project Foundation and iMasons Climate Accord, *Embodied Carbon
   Disclosure Base Specification*, version 1 (July 2025). https://www.opencompute.org/documents/carbon-disclosure-ocp-base-specification-20250730-pdf
3. Open Compute Project Foundation, *Guidelines: Impact of Strategies on Data
   Center Energy Consumption, Carbon Footprint, and Water Consumption* (March
   2026). https://www.opencompute.org/documents/dcf-water-heat-energy-2026march-pdf
4. Sharp et al., *Third Party Integration, Telemetry & APIs*, version 1.0
   (October 2025). https://www.opencompute.org/documents/third-party-integration-telemetry-apis-final-pdf
5. Mitchell et al., *Guidelines for Connection of Liquid Cooled Information
   Technology Equipment to Data Center Facility Systems*, revision 1, version
   1.0 (April 2022). https://www.opencompute.org/documents/ocp-acs-connection-guidance-acf-wp-05032022-pdf
6. Mitchell et al., *Data Center Liquid Distribution Guidance & Reference
   Designs*, revision 1.0 (January 2024). https://www.opencompute.org/documents/ocp-acf-reference-design-guidance-white-paper-r1-pdf
7. Yaroch et al., *Guidelines for Using Propylene Glycol-Based Heat Transfer
   Fluids in Single-Phase Cold Plate-Based Liquid Cooled Racks*. https://www.opencompute.org/documents/guidelines-for-using-propylene-glycol-based-heat-transfer-fluids-in-single-phase-cold-plate-based-liquid-cooled-racks-final-pdf
