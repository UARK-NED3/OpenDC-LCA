# Reliability-driven replacement and maintenance

`replacement_model: "reliability"` enables component-specific failure,
replacement, maintenance, downtime, and lifecycle calculations. This is a
probabilistic expectation model, not a fault-tree, redundancy, or site
availability simulator.

## Weibull renewal model

For characteristic life `eta` and shape `beta`, the time-to-first-failure CDF is

```text
F(t) = 1 - exp[-(t / eta)^beta]
```

OpenDC-LCA numerically solves the renewal equation

```text
M(t) = F(t) + integral[0,t] M(t-x) dF(x)
```

to estimate failures when a failed component is replaced as good as new.
Expected installations equal the initial installation plus expected failures.
For `beta = 1`, the model converges to the exponential renewal rate `t / eta`.

## Temperature acceleration

`arrhenius_weibull` adjusts the reference characteristic life:

```text
AF = exp[Ea / kB * (1 / Tref - 1 / Top)]
eta_operating = eta_reference / AF
```

Temperatures are converted to kelvin, `Ea` is in eV, and
`kB = 8.617333262145e-5 eV/K`. A hotter operating temperature therefore reduces
life for positive activation energy. Use this model only when the selected
failure mechanism is demonstrably Arrhenius-governed.

## Scenario fields

```json
{
  "study": {"replacement_model": "reliability"},
  "components": [{
    "name": "CDU",
    "quantity": 2,
    "service_life_years": 15,
    "production": {
      "ghg_kgco2e": 1000,
      "primary_energy_mj": 10000,
      "blue_water_l": 100
    },
    "reliability": {
      "model": "arrhenius_weibull",
      "characteristic_life_years": 15,
      "shape": 2.5,
      "reference_temperature_c": 25,
      "operating_temperature_c": 35,
      "activation_energy_ev": 0.35,
      "repair_downtime_hours": 12,
      "affected_capacity_fraction": 0.5,
      "maintenance_interval_years": 1,
      "maintenance_downtime_hours": 2,
      "maintenance_impacts": {
        "ghg_kgco2e": 50,
        "primary_energy_mj": 500,
        "blue_water_l": 10
      }
    }
  }]
}
```

Results include adjusted characteristic life, expected failures and
installations, maintenance events, annual downtime, and annual unserved IT
energy. Maintenance impacts are a separate contribution.

## Interpretation limits

- Expected values can be fractional; they describe a population or repeated
  lifecycle expectation, not a literal partial replacement.
- Component downtime is summed. Common-cause failures, repair queues,
  load-sharing, standby failure, and dependency are not represented.
- `annual_unserved_it_kwh` is an exposure indicator. It is not subtracted from
  the IT functional unit and does not include backup-system energy.
- Weibull and Arrhenius parameters require empirical justification and
  uncertainty analysis.
- Synthetic reliability inputs cannot support comparative claims.
