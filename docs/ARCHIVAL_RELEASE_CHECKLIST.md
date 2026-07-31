# DOI-bearing archival release checklist

Use this checklist for the exact commit submitted with the manuscript. A
GitHub tag is useful for software distribution but does not replace an
immutable research archive with a DOI.

## 1. Freeze the scientific state

- [ ] Confirm all provider-native raw files used by the analysis appear in
  `data/derived/source-file-manifest.json` with SHA-256 checksums.
- [ ] Confirm raw files with restricted or unclear redistribution rights are
  excluded from Git and listed with provider access URLs.
- [ ] Run both analysis scripts and verify that generated tables and figures
  match the manuscript.
- [ ] Run the full test suite in a clean environment.
- [ ] Build and visually inspect the DOCX, PDF, and Overleaf PDF.
- [ ] Confirm author, contribution, funding, competing-interest, and
  acknowledgment statements.
- [ ] Record the exact Git commit SHA in the manuscript metadata.

## 2. Build the archive payload

Include:

1. source code and packaging metadata;
2. public examples and schemas;
3. analysis scripts;
4. derived CSV tables and SVG/PDF figures;
5. manuscript and Supplementary Information source;
6. `analysis-metadata.json` files;
7. source-file manifest and checksums;
8. an environment/lock file or exact dependency list;
9. a machine-readable CITATION file;
10. licenses for code, documentation, and redistributable data; and
11. a README explaining which raw files are not redistributed and how to
    obtain them.

Do not include provider-native data unless the license permits redistribution.

## 3. Create the GitHub release

- [ ] Create a signed or annotated version tag from the submitted commit.
- [ ] Attach the source archive, wheel, manuscript artifacts, and archive
  payload checksum.
- [ ] Make release notes identify the scientific model version and any
  difference from the package version.

## 4. Mint the DOI

Recommended path:

1. connect the GitHub repository to Zenodo;
2. enable archiving for `UARK-NED3/OpenDC-LCA`;
3. publish the frozen GitHub release;
4. verify the deposited files, authors, affiliations, ORCIDs, title, abstract,
   keywords, license, related identifiers, and funding;
5. reserve or mint the DOI;
6. add the version DOI to `CITATION.cff`, the manuscript data/code statement,
   README, and release notes; and
7. use the concept DOI for the evolving software record and the version DOI
   for the exact manuscript release.

Alternative institutional repositories are acceptable if they provide an
immutable version DOI, public metadata, file checksums, and long-term access.

## 5. Verify reproducibility from the archive

- [ ] Download the deposited archive into a clean temporary directory.
- [ ] Verify payload checksums.
- [ ] Install the package without using the working repository.
- [ ] Re-run analyses with locally obtained provider files.
- [ ] Re-run tests.
- [ ] Compare derived file hashes with the deposited manifest.
- [ ] Confirm every DOI and access URL resolves.

## 6. Update manuscript claims

Only after the archive is public:

- replace “will be minted before submission” with the version DOI;
- cite the archival record as a dataset/software reference;
- identify the exact Git commit and package version;
- state which data are included, excluded, or available from providers; and
- confirm that the manuscript, code, archive metadata, and release notes use
  the same title and author list.
