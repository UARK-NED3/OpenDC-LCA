# EnergyPlus Archetype Extension

## Purpose

This extension provides a controlled starting point for a future climate and
IT-load study. It is not an AHPCC model, an EnergyPlus simulation result, or a
comparative cooling LCA. The design preserves that distinction because AHPCC
uses liquid-cooled racks on shared building infrastructure, whereas the
reference archetypes are air-cooled building models.

## Reference Models

Sun, Luo, Luo, and Hong implemented two data-center prototypes in OpenStudio
and EnergyPlus [Sun et al., *Energy and Buildings* 231, 110603 (2021),
https://doi.org/10.1016/j.enbuild.2020.110603]. The small prototype represents
a computer room served by CRAC units at IT-equipment load densities of 40 and
100 W/ft2. The large prototype represents a stand-alone data center served by
CRAH units and a central chiller plant at 100 and 500 W/ft2. The authors used
supply and return approach temperatures to account for nonuniform air
distribution. The machine-readable contract is
`data/derived/energyplus_archetype_contract.json`.

The source is a useful archetype because it covers multiple U.S. climates and
two IT-load levels. It does not provide a liquid-loop representation for the
AHPCC racks, a calibrated description of the ADSB shared infrastructure, or a
common workload comparison among cooling technologies.

## Reproduction Controls

Before execution, the analyst must i) pin the OpenStudio-standards or source
model revision and SHA-256 checksum, ii) select compatible OpenStudio and
EnergyPlus versions, iii) retain weather-file provenance and checksum, iv)
declare the HVAC configuration and controls for each scenario, and v) review
the model for physical validity. The workflow records runtime availability in
`results/transferability-extension/status.json`. A missing executable is a
blocked model execution, not a zero-energy result.

The recommended scenario matrix uses the small and large reference prototypes,
their two reported IT-equipment load densities, and selected climates. A
liquid-cooling scenario must be introduced only with a separately documented
plant and rack-loop model. An analyst must not substitute an air-side CRAC or
CRAH result for liquid cooling.

## LCA Coupling

Annual EnergyPlus outputs can inform a lifecycle calculation only after i) the
compared alternatives deliver a defined common useful-computation service,
ii) cooling performance is measured or independently validated, iii) the
foreground inventories and replacement rules are reviewed, and iv) electricity
inventories use a compatible method and system boundary. The current manuscript
reports the archetype contract and its blocked execution status. It does not
report simulated energy, PUE, water, or climate-specific lifecycle results.
