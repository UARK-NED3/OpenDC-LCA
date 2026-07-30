# Data sources and local organization

Raw third-party files are organized below `private-data/incoming/<provider>/`
and are intentionally excluded from Git. Small derived summaries in
`data/derived/` retain source identifiers and can be regenerated with
`python scripts/refresh_public_data.py`. The generated SHA-256 manifest allows
the exact local exports to be audited without redistributing them.

| Source | Local folder | Current use | Citation / access | Redistribution note |
|---|---|---|---|---|
| Microsoft/Nature supplementary information | `microsoft-nature/` | Method and result validation | Alissa et al., *Nature* 641, 331–338 (2025), [doi:10.1038/s41586-025-08832-3](https://doi.org/10.1038/s41586-025-08832-3) | Article and supplement retain publisher terms |
| Microsoft LCA model archive | `microsoft-zenodo/` | Equation and workbook cross-checks | Alissa et al., [Zenodo record 14268168](https://doi.org/10.5281/zenodo.14268168) | Retain record license and attribution |
| EPA eGRID 2023 | `egrid2023/` | Arkansas annual operational GHG factor | U.S. EPA, [eGRID detailed data](https://www.epa.gov/egrid/detailed-data) | US government data; preserve version and field |
| NOAA NCEI TMY | `noaa-tmy/` | Fayetteville climate context | NOAA NCEI, [Typical Meteorological Year](https://www.ncei.noaa.gov/access/typical-meteorological-year/) | Preserve station, period, and weighting |
| ÖKOBAUDAT 2024-II | `oekobaudat/` | Selected A1–A3 construction screening factors | BBSR, [ÖKOBAUDAT database](https://www.oekobaudat.de/en/database/database-browser.html) and [download](https://www.oekobaudat.de/en/database/downloads.html) | Derived values retain UUID, module, unit, URL; verify database terms before redistribution |
| GLAD / NREL hydrogen | `glad/nrel-hydrogen-jsonld/` | Future hydrogen and backup-power scenarios | UNEP, [Global LCA Data Access](https://www.globallcadataaccess.org/) and [Federal LCA Commons](https://www.lcacommons.gov/) | Seven downloaded JSON-LD packages are catalogued, not redistributed |
| USLCI v1.2026-06.0 | `uslci/` | Future US background inventory adapter | NREL, [USLCI Database](https://www.lcacommons.gov/lca-collaboration/National_Renewable_Energy_Laboratory/USLCI_Database_Public/datasets) | `.zolca` remains local; do not commit |
| Boavizta | `boavizta/` | ICT embodied-impact comparison and validation | Boavizta, [boaviztapi data repository](https://github.com/Boavizta/boaviztapi/tree/main/boaviztapi/data) | Follow upstream file-level source notes and license |
| USGS WBD HU12 | `usgs-wbd-hu12/` | Future watershed and water-context mapping | USGS, [Watershed Boundary Dataset](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset) | US government geospatial data |

## Interpretation rules

1. A downloaded dataset is not automatically compatible with another dataset.
   Preserve geography, year, system boundary, reference product, unit, and LCI
   modeling approach.
2. Do not mix EN 15804+A1 and EN 15804+A2 indicator values in one comparison.
3. eGRID `STC2ERTA` is an annual total-output CO2e rate. It is not marginal,
   hourly, or market-based electricity accounting.
4. GLAD is a discovery/access layer. Cite the original data provider and
   dataset record, not GLAD alone.
5. Provider-native raw files stay local unless their redistribution permission
   has been reviewed explicitly.
