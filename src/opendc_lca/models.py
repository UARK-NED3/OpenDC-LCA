"""Validated domain models for the Phase 1 screening model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ValidationError(ValueError):
    """Raised when a scenario is incomplete or physically invalid."""


def _number(
    data: dict[str, Any],
    key: str,
    *,
    positive: bool = False,
    allow_negative: bool = False,
) -> float:
    if key not in data or isinstance(data[key], bool):
        raise ValidationError(f"Missing numeric field: {key}")
    try:
        value = float(data[key])
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{key} must be numeric") from exc
    if positive and value <= 0:
        raise ValidationError(f"{key} must be greater than zero")
    if not positive and not allow_negative and value < 0:
        raise ValidationError(f"{key} cannot be negative")
    return value


@dataclass(frozen=True)
class Impacts:
    ghg_kgco2e: float = 0.0
    primary_energy_mj: float = 0.0
    blue_water_l: float = 0.0

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], *, allow_negative: bool = False
    ) -> "Impacts":
        return cls(
            _number(data, "ghg_kgco2e", allow_negative=allow_negative),
            _number(data, "primary_energy_mj", allow_negative=allow_negative),
            _number(data, "blue_water_l", allow_negative=allow_negative),
        )

    def __add__(self, other: "Impacts") -> "Impacts":
        return Impacts(
            self.ghg_kgco2e + other.ghg_kgco2e,
            self.primary_energy_mj + other.primary_energy_mj,
            self.blue_water_l + other.blue_water_l,
        )

    def scaled(self, multiplier: float) -> "Impacts":
        return Impacts(
            self.ghg_kgco2e * multiplier,
            self.primary_energy_mj * multiplier,
            self.blue_water_l * multiplier,
        )

    def as_dict(self) -> dict[str, float]:
        return {
            "ghg_kgco2e": self.ghg_kgco2e,
            "primary_energy_mj": self.primary_energy_mj,
            "blue_water_l": self.blue_water_l,
        }


@dataclass(frozen=True)
class GridFactors:
    ghg_kgco2e_per_kwh: float
    primary_energy_mj_per_kwh: float
    blue_water_l_per_kwh: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GridFactors":
        return cls(
            _number(data, "ghg_kgco2e_per_kwh"),
            _number(data, "primary_energy_mj_per_kwh"),
            _number(data, "blue_water_l_per_kwh"),
        )


@dataclass(frozen=True)
class Component:
    name: str
    quantity: float
    service_life_years: float
    production: Impacts
    end_of_life: Impacts = field(default_factory=Impacts)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Component":
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValidationError("Each component requires a name")
        return cls(
            name=name,
            quantity=_number(data, "quantity", positive=True),
            service_life_years=_number(data, "service_life_years", positive=True),
            production=Impacts.from_dict(data.get("production", {})),
            end_of_life=Impacts.from_dict(
                data.get("end_of_life", {
                    "ghg_kgco2e": 0,
                    "primary_energy_mj": 0,
                    "blue_water_l": 0,
                }),
                allow_negative=True,
            ),
        )


@dataclass(frozen=True)
class Fluid:
    name: str
    initial_charge_kg: float
    annual_loss_fraction: float
    production_per_kg: Impacts
    end_of_life_per_kg: Impacts
    direct_gwp_kgco2e_per_kg: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Fluid":
        loss = _number(data, "annual_loss_fraction")
        if loss > 1:
            raise ValidationError("annual_loss_fraction must be between 0 and 1")
        return cls(
            name=str(data.get("name", "unspecified fluid")),
            initial_charge_kg=_number(data, "initial_charge_kg"),
            annual_loss_fraction=loss,
            production_per_kg=Impacts.from_dict(data["production_per_kg"]),
            end_of_life_per_kg=Impacts.from_dict(
                data["end_of_life_per_kg"], allow_negative=True
            ),
            direct_gwp_kgco2e_per_kg=_number(
                data, "direct_gwp_kgco2e_per_kg"
            ),
        )


@dataclass(frozen=True)
class Scenario:
    name: str
    cooling_architecture: str
    it_capacity_kw: float
    capacity_factor: float
    pue: float
    facility_lifetime_years: float
    onsite_water_l_per_kwh_it: float
    grid: GridFactors
    components: tuple[Component, ...]
    fluid: Fluid | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scenario":
        name = str(data.get("name", "")).strip()
        architecture = str(data.get("cooling_architecture", "")).strip()
        if not name or not architecture:
            raise ValidationError("name and cooling_architecture are required")
        capacity_factor = _number(data, "capacity_factor", positive=True)
        if capacity_factor > 1:
            raise ValidationError("capacity_factor must be no greater than 1")
        pue = _number(data, "pue", positive=True)
        if pue < 1:
            raise ValidationError("pue must be at least 1")
        components = tuple(
            Component.from_dict(item) for item in data.get("components", [])
        )
        fluid_data = data.get("fluid")
        return cls(
            name=name,
            cooling_architecture=architecture,
            it_capacity_kw=_number(data, "it_capacity_kw", positive=True),
            capacity_factor=capacity_factor,
            pue=pue,
            facility_lifetime_years=_number(
                data, "facility_lifetime_years", positive=True
            ),
            onsite_water_l_per_kwh_it=_number(
                data, "onsite_water_l_per_kwh_it"
            ),
            grid=GridFactors.from_dict(data["grid"]),
            components=components,
            fluid=Fluid.from_dict(fluid_data) if fluid_data else None,
            metadata=dict(data.get("metadata", {})),
        )
