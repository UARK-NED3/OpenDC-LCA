# Practitioner input and output reference

## Compact input

`opendc-lca new-study` creates four input groups.

### Facility and cooling

| Field | Meaning | Validation |
|---|---|---|
| `study_name` | Human-readable case name | non-empty |
| `cooling_architecture` | Declared cooling design | non-empty |
| `geography` | Location represented by factors | text |
| `reference_year` | Year represented by source | integer |
| `it_capacity_kw` | Modeled IT capacity | >0 |
| `capacity_factor` | Mean fraction of IT capacity used | >0 and ≤1 |
| `pue` | Facility/IT electricity ratio | ≥1 |
| `facility_lifetime_years` | Study period | >0 |
| `onsite_water_l_per_kwh_it` | On-site consumption per IT electricity | ≥0 |

### Electricity

| Field | Unit |
|---|---|
| `grid_ghg_kgco2e_per_kwh` | kg CO2e/kWh |
| `grid_primary_energy_mj_per_kwh` | MJ/kWh |
| `grid_blue_water_l_per_kwh` | L/kWh |

All factors must have a declared, compatible accounting basis. A zero value
means zero burden in the calculation; it does not mean “unknown.”

### Equipment and evidence

Set `equipment.include` to `true` to annualize one aggregate equipment record.
The advanced schema accepts multiple components, fluids and reliability data.
The `source` object records ID, title, citation, license, geography, year,
quality, uncertainty, review status and confidentiality.

## Output

`practitioner-results.json` contains:

| Field | Meaning |
|---|---|
| `evidence_level` | Automated interpretation category |
| `comparative_claim_allowed` | Whether declared comparative intent passes blockers |
| `interpretation_scope` | Operational-only or operational-plus-equipment |
| `key_outputs` | Annual and normalized indicators |
| `contributions` | Electricity, water, equipment, maintenance and fluid |
| `audit_findings` | Scientific warnings and blockers |
| `next_data_required` | Evidence needed to strengthen the study |
| `model_version` | Calculation version |
| `scenario_digest_sha256` | Digest of the governed input |
| `capability_boundary` | Important effects not calculated |

## Core equations

```text
annual_it_kWh = it_capacity_kW × capacity_factor × 8760
annual_facility_kWh = annual_it_kWh × PUE
annual_operational_impact_k = annual_facility_kWh × EF_k
```

Normalized results divide annual totals by annual IT electricity in MWh.
Component production and end-of-life impacts are annualized over the declared
study and service lives according to the replacement model.
