# Current screening methodology

## Goal

Provide a transparent screening calculation that exposes the assumptions needed
to compare cooling architectures. It is not a substitute for a reviewed ISO
14040/14044 study.

## Functional unit

The current reporting unit is one MWh of delivered IT electricity during one
operating year. It is appropriate for comparing facility cooling alternatives
when IT service is equivalent. It is not adequate when cooling changes compute
performance, throttling, hardware lifetime, or utilization. Future releases will
support GPU-hour and workload-based functional units.

## Boundary

Included:

- facility electricity;
- electricity supply-chain impacts represented by user-provided factors;
- on-site cooling water;
- production and end of life for cooling equipment;
- coolant initial charge, annual replenishment, end of life, and direct loss.

Excluded unless supplied explicitly:

- servers and building elements common to all alternatives;
- temporal operation and grid marginal effects;
- water scarcity characterization;
- transport and maintenance unless embedded in supplied factors;
- dependent failures, redundancy, repair queues, and maintenance logistics;
- heat-reuse credits.

Researchers should include common systems when cooling changes their mass,
configuration, lifetime, or utilization.

## Equations

Annual IT electricity:

`E_IT = IT_capacity × capacity_factor × 8,760`

Annual facility electricity:

`E_facility = E_IT × PUE`

Equipment impacts are annualized independently:

`I_equipment = Σ quantity × (I_production + I_EOL) / service_life`

Annual coolant production includes the amortized initial charge and replacement
of losses. Losses are treated as direct releases and replaced to hold the
operating charge constant. The full remaining charge is treated at facility
end of life; lost mass is not counted again as end-of-life-treated mass:

`m_production = initial_charge / facility_life + annual_loss`

`I_fluid = m_production I_production + (initial_charge / facility_life) I_EOL`

`GHG_direct = annual_loss × direct_GWP`

## Interpretation

Always report:

- absolute annual results and normalized results;
- the full contribution breakdown;
- sensitivity to PUE, utilization, lifetime, fluid loss, and grid factors;
- data quality and uncertainty; and
- limitations that could reverse the ranking.

## Public-data operational screening

For one delivered IT MWh, annual location-based operational greenhouse-gas
emissions are calculated as

```text
GHG_operational [kg CO2e / IT MWh]
  = EF_grid [kg CO2e / facility MWh] × PUE
```

The public-data example uses EPA eGRID 2023 state field `STC2ERTA`.
This is a total-output annual factor. It must not be interpreted as an hourly,
marginal, or market-based factor. NOAA TMY weather is reported separately as
climate context until an hourly cooling-performance model is connected.

Construction-product factors retain the ÖKOBAUDAT dataset UUID, declared unit,
module, geography, reference year, and source URL. The current selected values
are EN 15804+A2 A1–A3 screening proxies; they are not combined with A1 indicators
or treated as a US data-center bill of materials.
