# Reference acquisition plan

This list prioritizes papers that can materially change the OpenDC-LCA
manuscript, model boundary, or interpretation. A link appearing here does not
mean that the paper has already been reviewed in full. Download the publisher
PDF and supplementary files when access permits; preserve the DOI in the file
name or an adjacent source record.

## Priority A: download first

1. **Siddik, Shehabi and Marston (2021), “The environmental footprint of data
   centers in the United States.”** Nationally resolved energy, carbon and
   water accounting; essential for positioning the eGRID and water-context
   analysis. [Article and data page](https://eta.lbl.gov/publications/environmental-footprint-data-centers),
   [DOI](https://doi.org/10.1088/1748-9326/abfba1).
2. **Whitehead et al. (2012), “The environmental burden of data centres - a
   screening LCA methodology.”** An early whole-facility LCA and a direct
   predecessor to the proposed screening workflow.
   [Full-text record](https://www.researchgate.net/publication/282848812_The_Environmental_Burden_of_Data_Centres_-_A_Screening_LCA_Methodology).
3. **Isler-Kaya and Karaosmanoglu (2023), “Life cycle assessment of a
   climate-friendly data center cooling device.”** Manufacturer inventory,
   multi-impact assessment, and manufacturing scenarios.
   [DOI](https://doi.org/10.1016/j.enbuild.2023.113006).
4. **Wenzel et al. (2023), “Extending effectiveness to efficiency: Comparing
   energy and environmental assessment methods for a wet cooling tower.”**
   Compares LCA with material-flow, inventory, exergy and life-cycle-exergy
   methods for data-center cooling.
   [DOI](https://doi.org/10.1111/jiec.13396).
5. **“Cleaner grid or smarter cooling? Environmental impact trade-offs of a
   data center using the life cycle assessment method” (2025).** Directly
   tests grid decarbonization versus PUE improvement across impact categories
   and is the closest comparator for the new crossover analysis.
   [DOI](https://doi.org/10.1016/j.cles.2025.100223).
6. **Ristic et al. (2015), “The water footprint of data centers.”** Separates
   direct and electricity-mediated water and documents water-factor
   uncertainty. [DOI](https://doi.org/10.3390/su70811260).
7. **Boulay et al. (2018), AWARE consensus water-scarcity method.** Required
   before converting water consumption into scarcity-weighted impacts.
   [DOI](https://doi.org/10.1007/s11367-017-1333-8).
8. **Boyd et al. (2012), “Comparing embodied greenhouse gas emissions of
   modern computing and electronics products.”** Foundational ICT inventory
   paper used to assess whether modern server and semiconductor factors remain
   representative. [DOI](https://doi.org/10.1021/es303012r).
9. **Masanet et al. (2020), “Recalibrating global data center energy-use
   estimates.”** Establishes the sector-scale efficiency and demand context.
   [DOI](https://doi.org/10.1126/science.aba3758).
10. **OCP, “LCA Guidelines for Cloud Providers.”** Industry guidance tied
    directly to the Microsoft/WSP study and necessary for the methods
    comparison. [OCP project page](https://www.opencompute.org/projects/sustainability).

## Priority B: thermal-performance and temporal coupling

11. Khalaj and Halgamuge (2017), review of air- and liquid-cooled data-center
    thermal management. [DOI](https://doi.org/10.1016/j.apenergy.2017.08.037).
12. Xu, Zhang and Wang (2023), review of thermal management and energy
    consumption in air, liquid and free cooling.
    [DOI](https://doi.org/10.3390/en16031279).
13. Kanbur et al. (2020), experimental and thermoeconomic assessment of
    two-phase immersion cooling.
    [DOI](https://doi.org/10.1016/j.ijrefrig.2020.08.012).
14. Ramakrishnan et al. (2021), air, cold-plate and two-phase immersion
    overclocking comparison.
    [DOI](https://doi.org/10.1109/TCPMT.2021.3109025).
15. Progressive-loading, multi-chiller life-cycle performance study (2024);
    useful for replacing annual-average PUE with part-load performance.
    [DOI](https://doi.org/10.1007/s12273-024-1167-9).
16. Hot-arid hourly energy and water dynamics study (2025); an important
    comparator for 8,760-hour cooling and water models.
    [DOI](https://doi.org/10.1016/j.applthermaleng.2025.126802).

## Priority C: uncertainty, water and prospective assessment

17. Boulay et al. (2021), uncertainty distributions for AWARE factors.
    [DOI](https://doi.org/10.1111/jiec.13173).
18. AWARE 2.0 method and supporting information; relevant for time- and
    watershed-resolved water impacts.
    [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13111518/).
19. Baustert et al. (2022), prospective electricity and water scarcity in
    LCA. [DOI](https://doi.org/10.1111/jiec.13272).
20. International Energy Agency, *Energy and AI* and current data-center
    electricity outlook. [IEA topic page](https://www.iea.org/topics/artificial-intelligence).

## Already available locally

- Alissa et al. (2025), Nature article, supplementary information, source data,
  and released Zenodo model.
- EPA eGRID 2023 detailed and summary workbooks and technical guide.
- NOAA Fayetteville TMY CSV, EPW and metadata.
- Boavizta U.S. and French product-footprint tables plus source register.
- ÖKOBAUDAT 2024-II export and documentation.
- Seven NREL hydrogen JSON-LD packages accessed through GLAD.
- USLCI v1.2026-06.0 openLCA database.
- USGS HU12 watershed boundary archive.

## Data still needed for decision-grade cooling comparisons

1. Measured load-temperature-humidity performance surfaces for air, cold
   plate, one-phase immersion and two-phase immersion under consistent IT and
   facility boundaries.
2. Architecture-specific bills of materials for tanks, racks, CDUs, cold
   plates, piping, heat rejection, fluids and modified servers.
3. Fluid production, loss, maintenance, toxicity and end-of-life data with
   chemical identity or independently reviewed aggregated inventories.
4. Failure, repair and service-life data stratified by cooling architecture
   and component temperature.
5. A compute-service functional unit connecting hardware count, utilization,
   performance and workload delivered.
6. Watershed-specific water-consumption inventories and AWARE characterization
   factors; watershed boundaries alone are insufficient.
