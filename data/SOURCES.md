# Data sources and local organization

Provider-native files are organized under `private-data/incoming/<provider>/`
and excluded from Git. Compact derived summaries in `data/derived/` retain
source identifiers. `scripts/build_source_manifest.py` records exact local
filenames, byte counts, and SHA-256 checksums without redistributing the data.

| Source | Local folder | Current use | Citation / access | Redistribution note |
|---|---|---|---|---|
| Microsoft/Nature supplementary information | `microsoft-nature/` | Arithmetic reconstruction of 24 normalized totals and released component contributions | Alissa et al., *Nature* 641, 331-338 (2025), [doi:10.1038/s41586-025-08832-3](https://doi.org/10.1038/s41586-025-08832-3) | Article and supplement retain publisher terms |
| Microsoft LCA model archive | `microsoft-zenodo/` | Equation and endpoint audit; no licensed background inventory redistribution | Alissa et al., [Zenodo record 14268168](https://doi.org/10.5281/zenodo.14268168) | Retain record license and attribution |
| EPA eGRID 2023 | `egrid2023/` | 51-state/DC numerical GHG transfer and observed generation-rate range | U.S. EPA, [eGRID detailed data](https://www.epa.gov/egrid/detailed-data) | Preserve version, field, unit, and direct-generation boundary |
| EPA historical eGRID | `egrid-historical/` | Nine releases and 459 state-year generation-rate records | U.S. EPA, [historical eGRID data](https://www.epa.gov/egrid/historical-egrid-data) | Provider workbooks remain local; derived tables retain field and conversion provenance |
| Federal LCA Commons U.S. Electricity Baseline 2023 | `us-electricity-baseline/` | Partial linked-system AR5-GWP100 factors for 60 balancing authorities, 10 FERC regions, and the United States; residual systems kept separate | NETL, [U.S. Electricity Baseline](https://www.lcacommons.gov/lca-collaboration/Federal_LCA_Commons/US_electricity_baseline), version 03.00.000 | JSON-LD archives remain local; outputs report unlinked inputs and provider-scope omissions |
| NOAA NCEI TMY | `noaa-tmy/` | Fayetteville climate fixture | NOAA NCEI, [Typical Meteorological Year](https://www.ncei.noaa.gov/access/typical-meteorological-year/) | Preserve station, period, and weighting |
| ÖKOBAUDAT 2024-II | `oekobaudat/` | Matched A1-A3 steel and cement route screens; not scaled without bills of quantities | BBSR, [database](https://www.oekobaudat.de/en/database/database-browser.html) and [download](https://www.oekobaudat.de/en/database/downloads.html) | Derived values retain UUID, module, unit, and URL; verify terms before redistribution |
| GLAD / NREL hydrogen | `glad/nrel-hydrogen-jsonld/` | Seven JSON-LD inventories parsed and exchange-tested; not used for cooling LCIA | UNEP, [GLAD](https://www.globallcadataaccess.org/) and [Federal LCA Commons](https://www.lcacommons.gov/) | Catalogued, not redistributed |
| USLCI v1.2026-06.0 | `uslci/` | Registered background source; requires portable export and product-system/LCIA harmonization | NREL, [USLCI Database](https://www.lcacommons.gov/lca-collaboration/National_Renewable_Energy_Laboratory/USLCI_Database_Public/datasets) | `.zolca` remains local |
| Boavizta | `boavizta/` | 55 server candidates, 48 included; explicit exclusion flow and manufacturing dispersion | Boavizta, [data repository](https://github.com/Boavizta/boaviztapi/tree/main/boaviztapi/data), accessed 29 July 2026 | Mutable snapshot pinned by SHA-256 `eaeb19cc36308c8759deeea496d270d9d6ed0e46c3f113099844c3f9bf6cca9c` |
| USGS WBD HU12 | `usgs-wbd-hu12/` | Geometry registered; not used as consumption or scarcity data | USGS, [Watershed Boundary Dataset](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset) | U.S. government geospatial data |

## Interpretation rules

1. A downloaded dataset is not automatically compatible with another.
   Preserve geography, year, system boundary, reference product, unit, and LCI
   modeling approach.
2. Do not mix EN 15804+A1 and EN 15804+A2 indicators.
3. eGRID annual total-output rates are not marginal, hourly, consumption-based,
   market-based, or complete lifecycle electricity factors.
4. Federal electricity results are partial provider-linked systems. Do not
   interpret absent provider links or out-of-scope infrastructure as zero
   lifecycle burden.
5. GLAD is a discovery/access layer; cite the original provider and record.
6. Provider-native files stay local until redistribution permission is
   reviewed explicitly.
