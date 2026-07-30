"""Reproduction and climate-aware research-preview analyses."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean

from .public_data import EgridStateFactor, read_xlsx_rows


TECHNOLOGIES = ("Air-cooled", "Cold plate", "One-phase", "Two-phase")
METRICS = ("Primary energy", "GHG", "Blue water")


@dataclass(frozen=True)
class ReproductionResult:
    metric: str
    electricity: str
    technology: str
    published_normalized: float
    reproduced_component_sum: float
    absolute_difference: float
    reduction_vs_air_pct: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class HourlyTechnologyResult:
    technology: str
    mean_pue: float
    minimum_pue: float
    maximum_pue: float
    facility_mwh_per_it_mwh: float
    operational_kgco2e_per_it_mwh: float
    reduction_vs_air_pct: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def reproduce_microsoft_figure4(
    source_data_xlsx: str | Path,
) -> list[ReproductionResult]:
    """Reproduce Microsoft Figure 4 totals by summing reported components."""
    rows = read_xlsx_rows(source_data_xlsx, "Figure4")
    sections = {
        "Primary energy": 1,
        "GHG": 11,
        "Blue water": 21,
    }
    outputs: list[ReproductionResult] = []
    for metric, start in sections.items():
        header = rows[start + 1]
        component_rows = rows[start + 2:start + 9]
        total_row = rows[start + 9]
        for offset, electricity in ((1, "Grid"), (6, "100% renewable")):
            air_total = float(total_row[offset])
            for technology_index, technology in enumerate(TECHNOLOGIES):
                column = offset + technology_index
                component_sum = sum(float(row[column]) for row in component_rows)
                published = float(total_row[column])
                reduction = 100.0 * (1.0 - published / air_total)
                outputs.append(
                    ReproductionResult(
                        metric=metric,
                        electricity=electricity,
                        technology=technology,
                        published_normalized=published,
                        reproduced_component_sum=component_sum,
                        absolute_difference=abs(published - component_sum),
                        reduction_vs_air_pct=reduction,
                    )
                )
    return outputs


def illustrative_pue(technology: str, dry_bulb_c: float) -> float:
    """Transparent hypothesis-generating PUE curve, not a measured model."""
    parameters = {
        "Air-cooled": (1.080, 15.0, 0.0025, 5.0, 0.0005),
        "Cold plate": (1.050, 20.0, 0.0015, 2.0, 0.0002),
        "One-phase": (1.040, 25.0, 0.0010, 0.0, 0.0001),
        "Two-phase": (1.035, 28.0, 0.0008, 0.0, 0.0001),
    }
    base, hot_threshold, hot_slope, cold_threshold, cold_slope = parameters[technology]
    return (
        base
        + hot_slope * max(dry_bulb_c - hot_threshold, 0.0)
        + cold_slope * max(cold_threshold - dry_bulb_c, 0.0)
    )


def hourly_climate_screening(
    tmy_csv: str | Path,
    egrid_factor: EgridStateFactor,
) -> tuple[list[HourlyTechnologyResult], list[dict[str, object]]]:
    """Apply illustrative temperature-response curves to an hourly TMY."""
    with Path(tmy_csv).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        next(reader)
        next(reader)
        fields = next(reader)
        raw_rows = [dict(zip(fields, row)) for row in reader]
    temperatures = [float(row["Temperature"]) for row in raw_rows]
    monthly: list[dict[str, object]] = []
    for month in range(1, 13):
        month_temperatures = [
            float(row["Temperature"]) for row in raw_rows
            if int(row["Month"]) == month
        ]
        record: dict[str, object] = {
            "month": month,
            "mean_temperature_c": fmean(month_temperatures),
        }
        for technology in TECHNOLOGIES:
            record[f"{technology}_mean_pue"] = fmean(
                illustrative_pue(technology, value)
                for value in month_temperatures
            )
        monthly.append(record)

    results: list[HourlyTechnologyResult] = []
    air_mean = fmean(illustrative_pue("Air-cooled", value) for value in temperatures)
    for technology in TECHNOLOGIES:
        pues = [illustrative_pue(technology, value) for value in temperatures]
        mean_pue = fmean(pues)
        results.append(
            HourlyTechnologyResult(
                technology=technology,
                mean_pue=mean_pue,
                minimum_pue=min(pues),
                maximum_pue=max(pues),
                facility_mwh_per_it_mwh=mean_pue,
                operational_kgco2e_per_it_mwh=(
                    mean_pue * egrid_factor.co2e_kg_per_mwh
                ),
                reduction_vs_air_pct=100.0 * (1.0 - mean_pue / air_mean),
            )
        )
    return results, monthly
