# Pre-submission actions

These items require author approval or an external action and are intentionally
kept outside the manuscript text.

1. Obtain all authors' approval of the author order, Han Hu's corresponding-
   author role and email, and a CRediT contribution statement.
2. Confirm funding and acknowledgments. Approve the manuscript's HFA-employment
   and generative-AI disclosures, identify any additional competing interests,
   and document HFA's funding, technical, data, intellectual-property, and
   publication roles, if any.
3. Arrange an independent LCA critical review appropriate to the intended
   public comparative claim under ISO 14040, ISO 14044, and ISO 14071. The
   present Technology Assessment intentionally makes no superiority claim.
4. Reproduce the national, low, and high Federal electricity systems in
   openLCA or Brightway. Use the same JSON-LD product systems and IPCC method,
   then compare target amount, total, process count, link count, and cutoff
   count with the custom solver. Record software version and numerical
   tolerance, and trace any difference to units, providers, characterization,
   or cutoff treatment.
5. Deposit the accepted code commit, derived tables, figures, configuration,
   and reproducibility metadata in an immutable DOI-bearing archive.
6. Confirm redistribution rights for every provider-native file; otherwise
   retain checksum-only provenance and provider download instructions.
7. Refresh online references and software/database version statements on the
   submission date.
8. Retain the AI-use record required by Elsevier and confirm whether more
   specific tool/model version information is available for the final methods
   and disclosure statements.
9. Rebuild and inspect the Word, PDF, Overleaf, supplementary, and workbook
   artifacts from the final commit, then run the complete local and clone-only
   test workflows.
10. Before upgrading the paper from a Technology Assessment to a comparative
    cooling result, obtain authorized synchronized data for the declared
    boundary. The minimum record contains UPS input/output, IT or PDU energy,
    dedicated cooling and pump energy, shared-support energy or allocation,
    loop temperatures and flow, glycol concentration, environmental conditions,
    workload output, hardware configuration, availability, and meter-calibration
    metadata. Follow `docs/SHARED_INFRASTRUCTURE_MEASUREMENT_PROTOCOL.md` and
    obtain facility approval before releasing site-derived records.
