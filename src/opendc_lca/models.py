"""Validated domain models for the Phase 1 screening model."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

SUPPORTED_FUNCTIONAL_UNITS = {"it_mwh"}
SUPPORTED_BOUNDARIES = {
    "cooling_system_cradle_to_grave",
    "facility_cradle_to_grave",
    "custom",
}
SUPPORTED_ELECTRICITY_ACCOUNTING = {
    "location_based",
    "market_based",
    "consequential",
}
SUPPORTED_REPLACEMENT_MODELS = {"discrete", "linearized", "reliability"}
SUPPORTED_RELIABILITY_MODELS = {"weibull", "arrhenius_weibull"}
SUPPORTED_REVIEW_STATUSES = {
    "not_required",
    "planned",
    "internal",
    "independent",
    "independent_panel",
}
SUPPORTED_SOURCE_REVIEW_STATUSES = {
    "unreviewed",
    "internally_reviewed",
    "independently_reviewed",
}
SUPPORTED_CONFIDENTIALITY = {"public", "aggregated_confidential", "confidential"}


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
    if not math.isfinite(value):
        raise ValidationError(f"{key} must be finite")
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
class DataSource:
    """Provenance for a foreground or background input."""

    id: str
    title: str
    source_type: str
    citation: str
    license: str
    geography: str
    reference_year: int
    quality: str
    uncertainty: dict[str, Any]
    review_status: str
    confidentiality: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DataSource":
        required = (
            "id", "title", "source_type", "citation", "license",
            "geography", "reference_year", "quality", "uncertainty",
            "review_status", "confidentiality",
        )
        missing = [key for key in required if data.get(key) in (None, "")]
        if missing:
            raise ValidationError(
                f"Data source is missing required fields: {', '.join(missing)}"
            )
        year = data["reference_year"]
        if isinstance(year, bool) or not isinstance(year, int):
            raise ValidationError("Data source reference_year must be an integer")
        uncertainty = data["uncertainty"]
        if not isinstance(uncertainty, dict) or not uncertainty.get("distribution"):
            raise ValidationError(
                "Data source uncertainty requires a distribution declaration"
            )
        review_status = str(data["review_status"])
        if review_status not in SUPPORTED_SOURCE_REVIEW_STATUSES:
            raise ValidationError(
                "Data source review_status must be one of: "
                + ", ".join(sorted(SUPPORTED_SOURCE_REVIEW_STATUSES))
            )
        confidentiality = str(data["confidentiality"])
        if confidentiality not in SUPPORTED_CONFIDENTIALITY:
            raise ValidationError(
                "Data source confidentiality must be one of: "
                + ", ".join(sorted(SUPPORTED_CONFIDENTIALITY))
            )
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            source_type=str(data["source_type"]),
            citation=str(data["citation"]),
            license=str(data["license"]),
            geography=str(data["geography"]),
            reference_year=year,
            quality=str(data["quality"]),
            uncertainty=dict(uncertainty),
            review_status=review_status,
            confidentiality=confidentiality,
        )


@dataclass(frozen=True)
class StudyDefinition:
    """Method choices required to interpret and reproduce a result."""

    functional_unit: str
    system_boundary: str
    electricity_accounting: str
    water_metric: str
    allocation_method: str
    intended_use: str
    comparative_assertion: bool
    ghg_method: str
    primary_energy_method: str
    water_method: str
    replacement_model: str
    critical_review_status: str
    boundary_definition: dict[str, Any] | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StudyDefinition":
        functional_unit = str(data.get("functional_unit", ""))
        if functional_unit not in SUPPORTED_FUNCTIONAL_UNITS:
            raise ValidationError(
                "functional_unit must be one of: "
                + ", ".join(sorted(SUPPORTED_FUNCTIONAL_UNITS))
            )
        boundary = str(data.get("system_boundary", ""))
        if boundary not in SUPPORTED_BOUNDARIES:
            raise ValidationError(
                "system_boundary must be one of: "
                + ", ".join(sorted(SUPPORTED_BOUNDARIES))
            )
        electricity = str(data.get("electricity_accounting", ""))
        if electricity not in SUPPORTED_ELECTRICITY_ACCOUNTING:
            raise ValidationError(
                "electricity_accounting must be one of: "
                + ", ".join(sorted(SUPPORTED_ELECTRICITY_ACCOUNTING))
            )
        required_text = (
            "water_metric", "allocation_method", "intended_use",
            "ghg_method", "primary_energy_method", "water_method",
        )
        missing = [key for key in required_text if not str(data.get(key, "")).strip()]
        if missing:
            raise ValidationError(
                f"Study definition is missing: {', '.join(missing)}"
            )
        comparative = data.get("comparative_assertion")
        if not isinstance(comparative, bool):
            raise ValidationError("comparative_assertion must be true or false")
        replacement_model = str(data.get("replacement_model", ""))
        if replacement_model not in SUPPORTED_REPLACEMENT_MODELS:
            raise ValidationError(
                "replacement_model must be one of: "
                + ", ".join(sorted(SUPPORTED_REPLACEMENT_MODELS))
            )
        review_status = str(data.get("critical_review_status", ""))
        if review_status not in SUPPORTED_REVIEW_STATUSES:
            raise ValidationError(
                "critical_review_status must be one of: "
                + ", ".join(sorted(SUPPORTED_REVIEW_STATUSES))
            )
        boundary_definition_raw = data.get("boundary_definition")
        boundary_definition: dict[str, Any] | None = None
        if boundary_definition_raw is not None:
            if not isinstance(boundary_definition_raw, dict):
                raise ValidationError("boundary_definition must be an object")
            included = boundary_definition_raw.get("included_processes")
            excluded = boundary_definition_raw.get("excluded_processes")
            rationale = str(boundary_definition_raw.get("rationale", "")).strip()
            if (
                not isinstance(included, list)
                or not all(str(item).strip() for item in included)
                or not isinstance(excluded, list)
                or not all(str(item).strip() for item in excluded)
                or not rationale
            ):
                raise ValidationError(
                    "boundary_definition requires included_processes and "
                    "excluded_processes lists plus a rationale"
                )
            boundary_definition = {
                "included_processes": sorted(str(item).strip() for item in included),
                "excluded_processes": sorted(str(item).strip() for item in excluded),
                "rationale": rationale,
            }
        if boundary == "custom" and comparative and boundary_definition is None:
            raise ValidationError(
                "A comparative custom boundary requires boundary_definition"
            )
        return cls(
            functional_unit=functional_unit,
            system_boundary=boundary,
            electricity_accounting=electricity,
            water_metric=str(data["water_metric"]),
            allocation_method=str(data["allocation_method"]),
            intended_use=str(data["intended_use"]),
            comparative_assertion=comparative,
            ghg_method=str(data["ghg_method"]),
            primary_energy_method=str(data["primary_energy_method"]),
            water_method=str(data["water_method"]),
            replacement_model=replacement_model,
            critical_review_status=review_status,
            boundary_definition=boundary_definition,
        )


@dataclass(frozen=True)
class Component:
    name: str
    quantity: float
    service_life_years: float
    production: Impacts
    end_of_life: Impacts = field(default_factory=Impacts)
    reliability: "ReliabilityModel | None" = None

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
            reliability=(
                ReliabilityModel.from_dict(data["reliability"])
                if data.get("reliability")
                else None
            ),
        )


@dataclass(frozen=True)
class ReliabilityModel:
    """Failure, maintenance, and downtime assumptions for one component."""

    model: str
    characteristic_life_years: float
    shape: float
    reference_temperature_c: float | None
    operating_temperature_c: float | None
    activation_energy_ev: float | None
    repair_downtime_hours: float
    affected_capacity_fraction: float
    maintenance_interval_years: float | None
    maintenance_downtime_hours: float
    maintenance_impacts: Impacts

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReliabilityModel":
        model = str(data.get("model", ""))
        if model not in SUPPORTED_RELIABILITY_MODELS:
            raise ValidationError(
                "reliability.model must be one of: "
                + ", ".join(sorted(SUPPORTED_RELIABILITY_MODELS))
            )
        affected = _number(data, "affected_capacity_fraction")
        if affected > 1:
            raise ValidationError(
                "affected_capacity_fraction must be between 0 and 1"
            )
        reference = operating = activation = None
        if model == "arrhenius_weibull":
            reference = _number(
                data, "reference_temperature_c", allow_negative=True
            )
            operating = _number(
                data, "operating_temperature_c", allow_negative=True
            )
            activation = _number(data, "activation_energy_ev", positive=True)
            if reference <= -273.15 or operating <= -273.15:
                raise ValidationError(
                    "Reliability temperatures must exceed absolute zero"
                )
        interval_raw = data.get("maintenance_interval_years")
        interval = (
            _number(data, "maintenance_interval_years", positive=True)
            if interval_raw is not None
            else None
        )
        maintenance_impacts = data.get("maintenance_impacts", {
            "ghg_kgco2e": 0,
            "primary_energy_mj": 0,
            "blue_water_l": 0,
        })
        return cls(
            model=model,
            characteristic_life_years=_number(
                data, "characteristic_life_years", positive=True
            ),
            shape=_number(data, "shape", positive=True),
            reference_temperature_c=reference,
            operating_temperature_c=operating,
            activation_energy_ev=activation,
            repair_downtime_hours=_number(data, "repair_downtime_hours"),
            affected_capacity_fraction=affected,
            maintenance_interval_years=interval,
            maintenance_downtime_hours=_number(
                data, "maintenance_downtime_hours"
            ),
            maintenance_impacts=Impacts.from_dict(maintenance_impacts),
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
    study: StudyDefinition
    data_sources: tuple[DataSource, ...]
    input_source_map: dict[str, str] = field(default_factory=dict)
    fluid: Fluid | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    source_digest_sha256: str = ""

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
        sources = tuple(
            DataSource.from_dict(item) for item in data.get("data_sources", [])
        )
        if not sources:
            raise ValidationError("At least one data_sources entry is required")
        source_ids = [source.id for source in sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValidationError("data_sources IDs must be unique")
        input_source_map = data.get("input_source_map", {})
        if not isinstance(input_source_map, dict):
            raise ValidationError("input_source_map must be an object")
        unknown_source_ids = sorted(
            {
                str(source_id)
                for source_id in input_source_map.values()
                if str(source_id) not in source_ids
            }
        )
        if unknown_source_ids:
            raise ValidationError(
                "input_source_map references unknown data source IDs: "
                + ", ".join(unknown_source_ids)
            )
        fluid_data = data.get("fluid")
        study = StudyDefinition.from_dict(data.get("study", {}))
        if (
            study.replacement_model == "reliability"
            and any(component.reliability is None for component in components)
        ):
            raise ValidationError(
                "Every component requires reliability data when "
                "replacement_model is 'reliability'"
            )
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
            study=study,
            data_sources=sources,
            input_source_map={
                str(field_name): str(source_id)
                for field_name, source_id in input_source_map.items()
            },
            fluid=Fluid.from_dict(fluid_data) if fluid_data else None,
            metadata=dict(data.get("metadata", {})),
        )
