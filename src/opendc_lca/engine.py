"""Transparent annualized calculations for data-center cooling scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import math

from .models import Impacts, Scenario

HOURS_PER_YEAR = 8760.0
MODEL_VERSION = "1.0.0"


@dataclass(frozen=True)
class Result:
    model_version: str
    scenario_digest_sha256: str
    scenario: str
    cooling_architecture: str
    annual_it_energy_kwh: float
    annual_facility_energy_kwh: float
    annual_impacts: Impacts
    per_it_mwh: Impacts
    contributions: dict[str, Impacts]
    study_manifest: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "model_version": self.model_version,
            "scenario_digest_sha256": self.scenario_digest_sha256,
            "scenario": self.scenario,
            "cooling_architecture": self.cooling_architecture,
            "annual_it_energy_kwh": self.annual_it_energy_kwh,
            "annual_facility_energy_kwh": self.annual_facility_energy_kwh,
            "annual_impacts": self.annual_impacts.as_dict(),
            "per_it_mwh": self.per_it_mwh.as_dict(),
            "contributions": {
                key: value.as_dict() for key, value in self.contributions.items()
            },
            "study": self.study_manifest,
            "normalization": {
                "basis": "one MWh of delivered IT electricity",
                "result_field": "per_it_mwh",
            },
        }


def analyze(scenario: Scenario) -> Result:
    """Calculate annualized impacts and contribution analysis."""
    it_kwh = (
        scenario.it_capacity_kw * scenario.capacity_factor * HOURS_PER_YEAR
    )
    facility_kwh = it_kwh * scenario.pue

    electricity = Impacts(
        ghg_kgco2e=facility_kwh * scenario.grid.ghg_kgco2e_per_kwh,
        primary_energy_mj=(
            facility_kwh * scenario.grid.primary_energy_mj_per_kwh
        ),
        blue_water_l=facility_kwh * scenario.grid.blue_water_l_per_kwh,
    )
    onsite_water = Impacts(
        blue_water_l=it_kwh * scenario.onsite_water_l_per_kwh_it
    )

    equipment = Impacts()
    for component in scenario.components:
        lifecycle = component.production + component.end_of_life
        if scenario.study.replacement_model == "discrete":
            installations = math.ceil(
                scenario.facility_lifetime_years
                / component.service_life_years
            )
            annual_quantity = (
                component.quantity
                * installations
                / scenario.facility_lifetime_years
            )
        else:
            annual_quantity = (
                component.quantity / component.service_life_years
            )
        equipment += lifecycle.scaled(annual_quantity)

    fluid = Impacts()
    direct_fluid_emissions = Impacts()
    if scenario.fluid:
        annual_loss_kg = (
            scenario.fluid.initial_charge_kg
            * scenario.fluid.annual_loss_fraction
        )
        annual_production_kg = (
            scenario.fluid.initial_charge_kg
            / scenario.facility_lifetime_years
            + annual_loss_kg
        )
        annual_eol_kg = (
            scenario.fluid.initial_charge_kg
            * (1 - scenario.fluid.annual_loss_fraction)
            / scenario.facility_lifetime_years
        )
        fluid = (
            scenario.fluid.production_per_kg.scaled(annual_production_kg)
            + scenario.fluid.end_of_life_per_kg.scaled(annual_eol_kg)
        )
        direct_fluid_emissions = Impacts(
            ghg_kgco2e=(
                annual_loss_kg * scenario.fluid.direct_gwp_kgco2e_per_kg
            )
        )

    contributions = {
        "electricity": electricity,
        "onsite_water": onsite_water,
        "equipment": equipment,
        "fluid_lifecycle": fluid,
        "direct_fluid_emissions": direct_fluid_emissions,
    }
    total = Impacts()
    for value in contributions.values():
        total += value

    normalization = 1000.0 / it_kwh
    return Result(
        model_version=MODEL_VERSION,
        scenario_digest_sha256=scenario.source_digest_sha256,
        scenario=scenario.name,
        cooling_architecture=scenario.cooling_architecture,
        annual_it_energy_kwh=it_kwh,
        annual_facility_energy_kwh=facility_kwh,
        annual_impacts=total,
        per_it_mwh=total.scaled(normalization),
        contributions=contributions,
        study_manifest={
            "functional_unit": scenario.study.functional_unit,
            "system_boundary": scenario.study.system_boundary,
            "electricity_accounting": scenario.study.electricity_accounting,
            "water_metric": scenario.study.water_metric,
            "allocation_method": scenario.study.allocation_method,
            "intended_use": scenario.study.intended_use,
            "comparative_assertion": scenario.study.comparative_assertion,
            "ghg_method": scenario.study.ghg_method,
            "primary_energy_method": scenario.study.primary_energy_method,
            "water_method": scenario.study.water_method,
            "replacement_model": scenario.study.replacement_model,
            "critical_review_status": scenario.study.critical_review_status,
            "data_source_ids": [source.id for source in scenario.data_sources],
        },
    )


def compare(scenarios: list[Scenario]) -> list[Result]:
    """Analyze scenarios in input order."""
    if len(scenarios) < 2:
        raise ValueError("Comparison requires at least two scenarios")
    return [analyze(scenario) for scenario in scenarios]


@dataclass(frozen=True)
class Sensitivity:
    parameter: str
    low_value: float
    high_value: float
    low_ghg_kgco2e_per_it_mwh: float
    high_ghg_kgco2e_per_it_mwh: float
    elasticity: float

    def as_dict(self) -> dict[str, float | str]:
        return {
            "parameter": self.parameter,
            "low_value": self.low_value,
            "high_value": self.high_value,
            "low_ghg_kgco2e_per_it_mwh": self.low_ghg_kgco2e_per_it_mwh,
            "high_ghg_kgco2e_per_it_mwh": self.high_ghg_kgco2e_per_it_mwh,
            "elasticity": self.elasticity,
        }


def sensitivity(scenario: Scenario, fraction: float = 0.1) -> list[Sensitivity]:
    """One-at-a-time sensitivity around selected continuous assumptions."""
    if not 0 < fraction < 1:
        raise ValueError("fraction must be between 0 and 1")
    baseline = analyze(scenario).per_it_mwh.ghg_kgco2e
    parameters = {
        "pue": scenario.pue,
        "capacity_factor": scenario.capacity_factor,
        "grid.ghg_kgco2e_per_kwh": scenario.grid.ghg_kgco2e_per_kwh,
        "onsite_water_l_per_kwh_it": scenario.onsite_water_l_per_kwh_it,
    }
    if scenario.fluid:
        parameters["fluid.annual_loss_fraction"] = (
            scenario.fluid.annual_loss_fraction
        )

    output: list[Sensitivity] = []
    for name, value in parameters.items():
        if value == 0:
            continue
        low_value = value * (1 - fraction)
        high_value = value * (1 + fraction)
        if name == "pue":
            low_value = max(1.0, low_value)
            low = replace(scenario, pue=low_value)
            high = replace(scenario, pue=high_value)
        elif name == "capacity_factor":
            high_value = min(1.0, high_value)
            low = replace(scenario, capacity_factor=low_value)
            high = replace(scenario, capacity_factor=high_value)
        elif name == "grid.ghg_kgco2e_per_kwh":
            low = replace(
                scenario,
                grid=replace(scenario.grid, ghg_kgco2e_per_kwh=low_value),
            )
            high = replace(
                scenario,
                grid=replace(scenario.grid, ghg_kgco2e_per_kwh=high_value),
            )
        elif name == "onsite_water_l_per_kwh_it":
            low = replace(
                scenario, onsite_water_l_per_kwh_it=low_value
            )
            high = replace(
                scenario, onsite_water_l_per_kwh_it=high_value
            )
        else:
            high_value = min(1.0, high_value)
            low = replace(
                scenario,
                fluid=replace(
                    scenario.fluid, annual_loss_fraction=low_value
                ),
            )
            high = replace(
                scenario,
                fluid=replace(
                    scenario.fluid, annual_loss_fraction=high_value
                ),
            )
        low_result = analyze(low).per_it_mwh.ghg_kgco2e
        high_result = analyze(high).per_it_mwh.ghg_kgco2e
        input_span = (high_value - low_value) / value
        elasticity = (
            ((high_result - low_result) / baseline) / input_span
            if baseline and input_span
            else 0.0
        )
        output.append(Sensitivity(
            parameter=name,
            low_value=low_value,
            high_value=high_value,
            low_ghg_kgco2e_per_it_mwh=low_result,
            high_ghg_kgco2e_per_it_mwh=high_result,
            elasticity=elasticity,
        ))
    return sorted(output, key=lambda item: abs(item.elasticity), reverse=True)
