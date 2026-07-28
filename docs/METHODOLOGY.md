# Phase 1 methodology

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

Excluded in Phase 1:

- servers and building elements common to all alternatives;
- temporal operation and grid marginal effects;
- water scarcity characterization;
- transport and maintenance unless embedded in supplied factors;
- reliability and replacement effects;
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
of losses. Direct fluid emissions are reported separately:

`m_production = initial_charge / facility_life + annual_loss`

`GHG_direct = annual_loss × direct_GWP`

## Interpretation

Always report:

- absolute annual results and normalized results;
- the full contribution breakdown;
- sensitivity to PUE, utilization, lifetime, fluid loss, and grid factors;
- data quality and uncertainty; and
- limitations that could reverse the ranking.

