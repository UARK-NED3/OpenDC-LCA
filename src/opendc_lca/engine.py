"""Transparent annualized calculations for data-center cooling scenarios."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Impacts, Scenario

HOURS_PER_YEAR = 8760.0


@dataclass(frozen=True)
class Result:
    scenario: str
    cooling_architecture: str
    annual_it_energy_kwh: float
    annual_facility_energy_kwh: float
    annual_impacts: Impacts
    per_it_mwh: Impacts
    contributions: dict[str, Impacts]

    def as_dict(self) -> dict[str, object]:
        return {
            "scenario": self.scenario,
            "cooling_architecture": self.cooling_architecture,
            "annual_it_energy_kwh": self.annual_it_energy_kwh,
            "annual_facility_energy_kwh": self.annual_facility_energy_kwh,
            "annual_impacts": self.annual_impacts.as_dict(),
            "per_it_mwh": self.per_it_mwh.as_dict(),
            "contributions": {
                key: value.as_dict() for key, value in self.contributions.items()
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
        equipment += lifecycle.scaled(
            component.quantity / component.service_life_years
        )

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
        scenario=scenario.name,
        cooling_architecture=scenario.cooling_architecture,
        annual_it_energy_kwh=it_kwh,
        annual_facility_energy_kwh=facility_kwh,
        annual_impacts=total,
        per_it_mwh=total.scaled(normalization),
        contributions=contributions,
    )


def compare(scenarios: list[Scenario]) -> list[Result]:
    """Analyze scenarios in input order."""
    if len(scenarios) < 2:
        raise ValueError("Comparison requires at least two scenarios")
    return [analyze(scenario) for scenario in scenarios]

