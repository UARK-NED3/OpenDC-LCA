"""Seeded Monte Carlo propagation for screening uncertainty."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
import random
from typing import Any

from .engine import MODEL_VERSION, analyze
from .models import Scenario, ValidationError

SUPPORTED_PARAMETERS = {
    "it_capacity_kw",
    "capacity_factor",
    "pue",
    "facility_lifetime_years",
    "onsite_water_l_per_kwh_it",
    "grid.ghg_kgco2e_per_kwh",
    "grid.primary_energy_mj_per_kwh",
    "grid.blue_water_l_per_kwh",
    "fluid.annual_loss_fraction",
}
SUPPORTED_DISTRIBUTIONS = {"uniform", "triangular", "normal", "lognormal"}


@dataclass(frozen=True)
class ParameterDistribution:
    parameter: str
    distribution: str
    parameters: dict[str, float]
    minimum: float | None = None
    maximum: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParameterDistribution":
        parameter = str(data.get("parameter", ""))
        distribution = str(data.get("distribution", ""))
        if parameter not in SUPPORTED_PARAMETERS:
            raise ValidationError(f"Unsupported uncertain parameter: {parameter}")
        if distribution not in SUPPORTED_DISTRIBUTIONS:
            raise ValidationError(
                f"Unsupported uncertainty distribution: {distribution}"
            )
        raw = data.get("parameters")
        if not isinstance(raw, dict):
            raise ValidationError("Distribution parameters must be an object")
        try:
            parameters = {str(key): float(value) for key, value in raw.items()}
            minimum = (
                float(data["minimum"]) if data.get("minimum") is not None else None
            )
            maximum = (
                float(data["maximum"]) if data.get("maximum") is not None else None
            )
        except (TypeError, ValueError) as exc:
            raise ValidationError("Distribution values must be numeric") from exc
        required = {
            "uniform": {"low", "high"},
            "triangular": {"low", "mode", "high"},
            "normal": {"mean", "sd"},
            "lognormal": {"median", "geometric_sd"},
        }[distribution]
        missing = required - parameters.keys()
        if missing:
            raise ValidationError(
                f"{distribution} distribution is missing: "
                + ", ".join(sorted(missing))
            )
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValidationError("minimum cannot exceed maximum")
        if distribution in {"normal", "lognormal"}:
            scale = parameters["sd" if distribution == "normal" else "geometric_sd"]
            if scale <= 0:
                raise ValidationError("Distribution spread must be positive")
        if distribution == "lognormal" and parameters["median"] <= 0:
            raise ValidationError("Lognormal median must be positive")
        if distribution == "uniform" and parameters["low"] > parameters["high"]:
            raise ValidationError("Uniform low cannot exceed high")
        if distribution == "triangular" and not (
            parameters["low"] <= parameters["mode"] <= parameters["high"]
        ):
            raise ValidationError(
                "Triangular parameters must satisfy low <= mode <= high"
            )
        return cls(parameter, distribution, parameters, minimum, maximum)

    def sample(self, rng: random.Random) -> float:
        p = self.parameters
        if self.distribution == "uniform":
            value = rng.uniform(p["low"], p["high"])
        elif self.distribution == "triangular":
            value = rng.triangular(p["low"], p["high"], p["mode"])
        elif self.distribution == "normal":
            value = rng.gauss(p["mean"], p["sd"])
        else:
            value = rng.lognormvariate(
                math.log(p["median"]), math.log(p["geometric_sd"])
            )
        if self.minimum is not None:
            value = max(self.minimum, value)
        if self.maximum is not None:
            value = min(self.maximum, value)
        return value

    def as_dict(self) -> dict[str, object]:
        output: dict[str, object] = {
            "parameter": self.parameter,
            "distribution": self.distribution,
            "parameters": dict(self.parameters),
        }
        if self.minimum is not None:
            output["minimum"] = self.minimum
        if self.maximum is not None:
            output["maximum"] = self.maximum
        return output


@dataclass(frozen=True)
class MonteCarloResult:
    model_version: str
    scenario: str
    scenario_digest_sha256: str
    samples: int
    seed: int
    parameter_distributions: tuple[dict[str, object], ...]
    ghg_kgco2e_per_it_mwh: dict[str, float]
    primary_energy_mj_per_it_mwh: dict[str, float]
    blue_water_l_per_it_mwh: dict[str, float]

    def as_dict(self) -> dict[str, object]:
        return {
            "model_version": self.model_version,
            "scenario": self.scenario,
            "scenario_digest_sha256": self.scenario_digest_sha256,
            "samples": self.samples,
            "seed": self.seed,
            "parameter_distributions": list(self.parameter_distributions),
            "percentiles": {
                "ghg_kgco2e_per_it_mwh": self.ghg_kgco2e_per_it_mwh,
                "primary_energy_mj_per_it_mwh": (
                    self.primary_energy_mj_per_it_mwh
                ),
                "blue_water_l_per_it_mwh": self.blue_water_l_per_it_mwh,
            },
            "independence_assumption": (
                "Parameters are sampled independently; correlations are not modeled."
            ),
        }


def _with_parameter(scenario: Scenario, path: str, value: float) -> Scenario:
    if not math.isfinite(value):
        raise ValidationError(f"Sampled {path} must be finite")
    if path in {"it_capacity_kw", "facility_lifetime_years"} and value <= 0:
        raise ValidationError(f"Sampled {path} must be greater than zero")
    if path == "pue" and value < 1:
        raise ValidationError("Sampled pue must be at least 1")
    if path == "capacity_factor" and not 0 < value <= 1:
        raise ValidationError("Sampled capacity_factor must be in (0, 1]")
    if path == "fluid.annual_loss_fraction" and not 0 <= value <= 1:
        raise ValidationError(
            "Sampled fluid.annual_loss_fraction must be in [0, 1]"
        )
    if (
        path.startswith("grid.")
        or path == "onsite_water_l_per_kwh_it"
    ) and value < 0:
        raise ValidationError(f"Sampled {path} cannot be negative")
    if path.startswith("grid."):
        return replace(
            scenario,
            grid=replace(scenario.grid, **{path.split(".", 1)[1]: value}),
        )
    if path == "fluid.annual_loss_fraction":
        if scenario.fluid is None:
            raise ValidationError(
                "fluid.annual_loss_fraction requires a scenario fluid"
            )
        return replace(
            scenario,
            fluid=replace(scenario.fluid, annual_loss_fraction=value),
        )
    return replace(scenario, **{path: value})


def _percentiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)

    def quantile(probability: float) -> float:
        index = probability * (len(ordered) - 1)
        low = math.floor(index)
        high = math.ceil(index)
        if low == high:
            return ordered[low]
        return ordered[low] + (ordered[high] - ordered[low]) * (index - low)

    return {
        "p05": quantile(0.05),
        "p50": quantile(0.50),
        "p95": quantile(0.95),
        "mean": sum(ordered) / len(ordered),
    }


def monte_carlo(
    scenario: Scenario,
    distributions: list[ParameterDistribution],
    *,
    samples: int = 1000,
    seed: int = 42,
) -> MonteCarloResult:
    """Propagate independent parameter distributions through the LCA model."""
    if samples < 2:
        raise ValueError("Monte Carlo analysis requires at least two samples")
    if not distributions:
        raise ValueError("At least one parameter distribution is required")
    names = [item.parameter for item in distributions]
    if len(names) != len(set(names)):
        raise ValueError("Uncertain parameter names must be unique")
    rng = random.Random(seed)
    ghg: list[float] = []
    energy: list[float] = []
    water: list[float] = []
    for _ in range(samples):
        sampled = scenario
        for distribution in distributions:
            sampled = _with_parameter(
                sampled, distribution.parameter, distribution.sample(rng)
            )
        result = analyze(sampled).per_it_mwh
        ghg.append(result.ghg_kgco2e)
        energy.append(result.primary_energy_mj)
        water.append(result.blue_water_l)
    return MonteCarloResult(
        model_version=MODEL_VERSION,
        scenario=scenario.name,
        scenario_digest_sha256=scenario.source_digest_sha256,
        samples=samples,
        seed=seed,
        parameter_distributions=tuple(item.as_dict() for item in distributions),
        ghg_kgco2e_per_it_mwh=_percentiles(ghg),
        primary_energy_mj_per_it_mwh=_percentiles(energy),
        blue_water_l_per_it_mwh=_percentiles(water),
    )
