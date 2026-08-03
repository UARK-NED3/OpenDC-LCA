"""Validated laboratory performance maps and scenario parameter derivation."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, replace
import hashlib
import io
import json
import math
from pathlib import Path

from .models import Scenario, ValidationError

REQUIRED_COLUMNS = {
    "test_id",
    "architecture",
    "it_load_kw",
    "heat_removed_kw",
    "coolant_supply_c",
    "coolant_return_c",
    "flow_kg_s",
    "pressure_drop_kpa",
    "pump_power_kw",
    "fan_power_kw",
    "cdu_power_kw",
    "heat_rejection_power_kw",
    "onsite_water_l_h",
    "ambient_dry_bulb_c",
    "ambient_wet_bulb_c",
    "duration_hours",
    "measurement_uncertainty_percent",
    "source_id",
}


def _value(
    row: dict[str, str],
    name: str,
    *,
    positive: bool = False,
    allow_negative: bool = False,
) -> float:
    try:
        value = float(row[name])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError(f"{name} must be numeric") from exc
    if not math.isfinite(value):
        raise ValidationError(f"{name} must be finite")
    if (value < 0 and not allow_negative) or (positive and value <= 0):
        qualifier = "greater than zero" if positive else "non-negative"
        raise ValidationError(f"{name} must be {qualifier}")
    return value


@dataclass(frozen=True)
class PerformancePoint:
    test_id: str
    architecture: str
    it_load_kw: float
    heat_removed_kw: float
    coolant_supply_c: float
    coolant_return_c: float
    flow_kg_s: float
    pressure_drop_kpa: float
    pump_power_kw: float
    fan_power_kw: float
    cdu_power_kw: float
    heat_rejection_power_kw: float
    onsite_water_l_h: float
    ambient_dry_bulb_c: float
    ambient_wet_bulb_c: float
    duration_hours: float
    measurement_uncertainty_percent: float
    source_id: str

    @property
    def cooling_power_kw(self) -> float:
        return (
            self.pump_power_kw
            + self.fan_power_kw
            + self.cdu_power_kw
            + self.heat_rejection_power_kw
        )

    @property
    def partial_pue(self) -> float:
        return 1 + self.cooling_power_kw / self.it_load_kw


@dataclass(frozen=True)
class PerformanceSummary:
    architecture: str
    point_count: int
    total_duration_hours: float
    it_energy_kwh: float
    cooling_energy_kwh: float
    heat_removed_kwh: float
    onsite_water_l: float
    measured_pue: float
    onsite_water_l_per_kwh_it: float
    cooling_cop: float | None
    source_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class InterpolatedPerformance:
    architecture: str
    it_load_kw: float
    ambient_dry_bulb_c: float
    cooling_power_kw: float
    onsite_water_l_h: float
    measurement_uncertainty_percent: float

    @property
    def partial_pue(self) -> float:
        return 1 + self.cooling_power_kw / self.it_load_kw


@dataclass(frozen=True)
class HourlyPerformanceResult:
    architecture: str
    hours: int
    it_energy_kwh: float
    cooling_energy_kwh: float
    onsite_water_l: float
    mean_pue: float
    pue_lower: float
    pue_upper: float
    operational_kgco2e_per_it_mwh: float
    source_ids: tuple[str, ...]
    evidence_status: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _load_performance_reader(
    reader: csv.DictReader,
) -> list[PerformancePoint]:
    missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
    if missing:
        raise ValidationError(
            "Performance map is missing columns: " + ", ".join(sorted(missing))
        )
    points: list[PerformancePoint] = []
    seen: set[str] = set()
    for line_number, row in enumerate(reader, start=2):
        test_id = str(row.get("test_id", "")).strip()
        architecture = str(row.get("architecture", "")).strip()
        source_id = str(row.get("source_id", "")).strip()
        if not test_id or not architecture or not source_id:
            raise ValidationError(
                f"Line {line_number}: test_id, architecture, and source_id "
                "are required"
            )
        if test_id in seen:
            raise ValidationError(f"Duplicate test_id: {test_id}")
        seen.add(test_id)
        uncertainty = _value(row, "measurement_uncertainty_percent")
        if uncertainty > 100:
            raise ValidationError(
                "measurement_uncertainty_percent cannot exceed 100"
            )
        points.append(PerformancePoint(
            test_id=test_id,
            architecture=architecture,
            it_load_kw=_value(row, "it_load_kw", positive=True),
            heat_removed_kw=_value(row, "heat_removed_kw"),
            coolant_supply_c=_value(
                row, "coolant_supply_c", allow_negative=True
            ),
            coolant_return_c=_value(
                row, "coolant_return_c", allow_negative=True
            ),
            flow_kg_s=_value(row, "flow_kg_s"),
            pressure_drop_kpa=_value(row, "pressure_drop_kpa"),
            pump_power_kw=_value(row, "pump_power_kw"),
            fan_power_kw=_value(row, "fan_power_kw"),
            cdu_power_kw=_value(row, "cdu_power_kw"),
            heat_rejection_power_kw=_value(row, "heat_rejection_power_kw"),
            onsite_water_l_h=_value(row, "onsite_water_l_h"),
            ambient_dry_bulb_c=_value(
                row, "ambient_dry_bulb_c", allow_negative=True
            ),
            ambient_wet_bulb_c=_value(
                row, "ambient_wet_bulb_c", allow_negative=True
            ),
            duration_hours=_value(row, "duration_hours", positive=True),
            measurement_uncertainty_percent=uncertainty,
            source_id=source_id,
        ))
        point = points[-1]
        if point.ambient_wet_bulb_c > point.ambient_dry_bulb_c:
            raise ValidationError(
                f"Line {line_number}: ambient wet-bulb temperature cannot "
                "exceed dry-bulb temperature"
            )
        if point.coolant_return_c < point.coolant_supply_c:
            raise ValidationError(
                f"Line {line_number}: coolant return temperature cannot "
                "be below supply temperature for heat-removal tests"
            )
    return points


def _validate_performance_points(
    points: list[PerformancePoint],
) -> list[PerformancePoint]:
    if not points:
        raise ValidationError("Performance map must contain at least one row")
    architectures = {point.architecture for point in points}
    if len(architectures) != 1:
        raise ValidationError(
            "A performance map must contain exactly one cooling architecture"
        )
    return points


def load_performance_map(path: str | Path) -> list[PerformancePoint]:
    """Load and validate the common laboratory CSV format."""
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return _validate_performance_points(
            _load_performance_reader(csv.DictReader(handle))
        )


def load_performance_map_text(text: str) -> list[PerformancePoint]:
    """Load a performance map from UTF-8 CSV text (for APIs and the GUI)."""
    return _validate_performance_points(
        _load_performance_reader(csv.DictReader(io.StringIO(text)))
    )


def summarize_performance(points: list[PerformancePoint]) -> PerformanceSummary:
    """Aggregate measured points using their observation durations."""
    if not points:
        raise ValueError("At least one performance point is required")
    architectures = {point.architecture for point in points}
    if len(architectures) != 1:
        raise ValueError("Performance points must share one architecture")
    duration = sum(point.duration_hours for point in points)
    it_energy = sum(point.it_load_kw * point.duration_hours for point in points)
    cooling_energy = sum(
        point.cooling_power_kw * point.duration_hours for point in points
    )
    heat_removed = sum(
        point.heat_removed_kw * point.duration_hours for point in points
    )
    water = sum(point.onsite_water_l_h * point.duration_hours for point in points)
    return PerformanceSummary(
        architecture=points[0].architecture,
        point_count=len(points),
        total_duration_hours=duration,
        it_energy_kwh=it_energy,
        cooling_energy_kwh=cooling_energy,
        heat_removed_kwh=heat_removed,
        onsite_water_l=water,
        measured_pue=1 + cooling_energy / it_energy,
        onsite_water_l_per_kwh_it=water / it_energy,
        cooling_cop=(
            heat_removed / cooling_energy if cooling_energy > 0 else None
        ),
        source_ids=tuple(sorted({point.source_id for point in points})),
    )


def apply_performance(
    scenario: Scenario, summary: PerformanceSummary
) -> Scenario:
    """Return a scenario using measured cooling-only partial PUE and water."""
    if scenario.cooling_architecture != summary.architecture:
        raise ValueError(
            "Scenario and performance-map cooling architectures do not match"
        )
    declared_sources = {source.id for source in scenario.data_sources}
    missing_sources = set(summary.source_ids) - declared_sources
    if missing_sources:
        raise ValueError(
            "Performance-map source IDs are absent from the scenario: "
            + ", ".join(sorted(missing_sources))
        )
    derived_digest = hashlib.sha256(json.dumps(
        {
            "scenario_digest_sha256": scenario.source_digest_sha256,
            "performance_summary": summary.as_dict(),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()).hexdigest()
    return replace(
        scenario,
        pue=summary.measured_pue,
        onsite_water_l_per_kwh_it=summary.onsite_water_l_per_kwh_it,
        source_digest_sha256=derived_digest,
    )


def _bracket(values: list[float], target: float, name: str) -> tuple[float, float]:
    if target < values[0] or target > values[-1]:
        raise ValidationError(
            f"{name} {target} is outside measured range "
            f"[{values[0]}, {values[-1]}]; extrapolation is disabled"
        )
    lower = max(value for value in values if value <= target)
    upper = min(value for value in values if value >= target)
    return lower, upper


def _linear(value0: float, value1: float, fraction: float) -> float:
    return value0 + fraction * (value1 - value0)


def interpolate_performance(
    points: list[PerformancePoint],
    *,
    it_load_kw: float,
    ambient_dry_bulb_c: float,
) -> InterpolatedPerformance:
    """Bilinearly interpolate a complete load-by-temperature measurement grid."""
    if not points:
        raise ValidationError("At least one measured performance point is required")
    architectures = {point.architecture for point in points}
    if len(architectures) != 1:
        raise ValidationError("Interpolation points must share one architecture")
    loads = sorted({point.it_load_kw for point in points})
    temperatures = sorted({point.ambient_dry_bulb_c for point in points})
    grid = {
        (point.it_load_kw, point.ambient_dry_bulb_c): point for point in points
    }
    if len(grid) != len(points):
        raise ValidationError(
            "Performance surface contains duplicate load-temperature combinations"
        )
    if len(grid) != len(loads) * len(temperatures):
        raise ValidationError(
            "Performance surface must contain every load-temperature combination"
        )
    load0, load1 = _bracket(loads, it_load_kw, "IT load")
    temp0, temp1 = _bracket(
        temperatures, ambient_dry_bulb_c, "Ambient dry-bulb temperature"
    )
    load_fraction = 0.0 if load1 == load0 else (it_load_kw - load0) / (load1 - load0)
    temp_fraction = (
        0.0
        if temp1 == temp0
        else (ambient_dry_bulb_c - temp0) / (temp1 - temp0)
    )

    def bilinear(attribute: str) -> float:
        at_temp0 = _linear(
            getattr(grid[(load0, temp0)], attribute),
            getattr(grid[(load1, temp0)], attribute),
            load_fraction,
        )
        at_temp1 = _linear(
            getattr(grid[(load0, temp1)], attribute),
            getattr(grid[(load1, temp1)], attribute),
            load_fraction,
        )
        return _linear(at_temp0, at_temp1, temp_fraction)

    return InterpolatedPerformance(
        architecture=points[0].architecture,
        it_load_kw=it_load_kw,
        ambient_dry_bulb_c=ambient_dry_bulb_c,
        cooling_power_kw=bilinear("cooling_power_kw"),
        onsite_water_l_h=bilinear("onsite_water_l_h"),
        measurement_uncertainty_percent=bilinear(
            "measurement_uncertainty_percent"
        ),
    )


def integrate_hourly_performance(
    points: list[PerformancePoint],
    hourly_dry_bulb_c: list[float],
    hourly_load_fraction: list[float],
    *,
    rated_it_load_kw: float,
    grid_kgco2e_per_mwh: float,
    evidence_status: str,
) -> HourlyPerformanceResult:
    """Integrate a measured surface against aligned weather and workload."""
    if len(hourly_dry_bulb_c) != len(hourly_load_fraction):
        raise ValidationError("Weather and workload series must have equal length")
    if not hourly_dry_bulb_c:
        raise ValidationError("Hourly series cannot be empty")
    if rated_it_load_kw <= 0 or grid_kgco2e_per_mwh < 0:
        raise ValidationError("Rated IT load must be positive and grid factor non-negative")
    if evidence_status not in {"synthetic", "measured", "reviewed"}:
        raise ValidationError(
            "evidence_status must be synthetic, measured, or reviewed"
        )
    it_energy = 0.0
    cooling_energy = 0.0
    cooling_lower = 0.0
    cooling_upper = 0.0
    water = 0.0
    for temperature, fraction in zip(
        hourly_dry_bulb_c, hourly_load_fraction
    ):
        if fraction <= 0 or fraction > 1:
            raise ValidationError("Hourly load fractions must be in (0, 1]")
        point = interpolate_performance(
            points,
            it_load_kw=rated_it_load_kw * fraction,
            ambient_dry_bulb_c=temperature,
        )
        uncertainty = point.measurement_uncertainty_percent / 100.0
        it_energy += point.it_load_kw
        cooling_energy += point.cooling_power_kw
        cooling_lower += point.cooling_power_kw * (1 - uncertainty)
        cooling_upper += point.cooling_power_kw * (1 + uncertainty)
        water += point.onsite_water_l_h
    mean_pue = 1 + cooling_energy / it_energy
    return HourlyPerformanceResult(
        architecture=points[0].architecture,
        hours=len(hourly_dry_bulb_c),
        it_energy_kwh=it_energy,
        cooling_energy_kwh=cooling_energy,
        onsite_water_l=water,
        mean_pue=mean_pue,
        pue_lower=1 + cooling_lower / it_energy,
        pue_upper=1 + cooling_upper / it_energy,
        operational_kgco2e_per_it_mwh=mean_pue * grid_kgco2e_per_mwh,
        source_ids=tuple(sorted({point.source_id for point in points})),
        evidence_status=evidence_status,
    )


def measurement_declared_metadata_gate_passed(
    results: list[HourlyPerformanceResult],
) -> bool:
    """Check only the declared review label for two or more maps."""
    return len(results) >= 2 and all(
        result.evidence_status == "reviewed" for result in results
    )


def measurement_comparative_claim_allowed(
    results: list[HourlyPerformanceResult],
) -> bool:
    """Legacy alias for the declared metadata gate; not claim authorization."""
    return measurement_declared_metadata_gate_passed(results)
