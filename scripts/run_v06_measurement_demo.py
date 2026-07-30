#!/usr/bin/env python3
"""Generate a synthetic v0.6 demonstration of the measurement-ready engine."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendc_lca.performance import (  # noqa: E402
    integrate_hourly_performance,
    load_performance_map,
    measurement_comparative_claim_allowed,
)
from opendc_lca.public_data import load_egrid_state_factor  # noqa: E402

RAW = ROOT / "private-data" / "incoming"
RESULTS = ROOT / "results" / "v0.6-measurement-demo"
TABLES = ROOT / "paper" / "tables"
FIGURES = ROOT / "paper" / "figures"
EXAMPLES = ROOT / "examples"
PACKAGE_EXAMPLES = ROOT / "src" / "opendc_lca" / "example_data"

FIELDS = [
    "test_id", "architecture", "it_load_kw", "heat_removed_kw",
    "coolant_supply_c", "coolant_return_c", "flow_kg_s",
    "pressure_drop_kpa", "pump_power_kw", "fan_power_kw", "cdu_power_kw",
    "heat_rejection_power_kw", "onsite_water_l_h", "ambient_dry_bulb_c",
    "ambient_wet_bulb_c", "duration_hours",
    "measurement_uncertainty_percent", "source_id",
]


def synthetic_rows(architecture: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for load in (40.0, 70.0, 100.0):
        fraction = load / 100.0
        for temperature in (-15.0, 0.0, 20.0, 35.0):
            if architecture == "air-cooled":
                ratio = (
                    0.055 + 0.025 * (1 - fraction)
                    + 0.0025 * max(temperature - 15, 0)
                    + 0.0005 * max(5 - temperature, 0)
                )
                split = (0.0, 0.65, 0.0, 0.35)
                water = 0.15 * max(temperature - 10, 0) * fraction
            else:
                ratio = (
                    0.035 + 0.018 * (1 - fraction)
                    + 0.0012 * max(temperature - 20, 0)
                    + 0.0002 * max(2 - temperature, 0)
                )
                split = (0.22, 0.08, 0.20, 0.50)
                water = 0.04 * max(temperature - 10, 0) * fraction
            cooling = ratio * load
            rows.append({
                "test_id": f"SYN-{architecture}-{int(load)}-{int(temperature)}",
                "architecture": architecture,
                "it_load_kw": load,
                "heat_removed_kw": load,
                "coolant_supply_c": 25.0 if architecture == "air-cooled" else 30.0,
                "coolant_return_c": 35.0 if architecture == "air-cooled" else 40.0,
                "flow_kg_s": 1.0 * fraction,
                "pressure_drop_kpa": 20.0 * fraction,
                "pump_power_kw": cooling * split[0],
                "fan_power_kw": cooling * split[1],
                "cdu_power_kw": cooling * split[2],
                "heat_rejection_power_kw": cooling * split[3],
                "onsite_water_l_h": water,
                "ambient_dry_bulb_c": temperature,
                "ambient_wet_bulb_c": min(temperature, temperature - 3),
                "duration_hours": 1.0,
                "measurement_uncertainty_percent": 5.0,
                "source_id": "synthetic-v0.6-demo",
            })
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_bar_svg(path: Path, results: list[dict[str, object]]) -> None:
    colors = {"air-cooled": "#4B5563", "direct-to-chip": "#0072B2"}
    maximum = max(float(row["operational_kgco2e_per_it_mwh"]) for row in results)
    bars = []
    for index, row in enumerate(results):
        value = float(row["operational_kgco2e_per_it_mwh"])
        x = 180 + index * 310
        height = value / (maximum * 1.15) * 300
        y = 390 - height
        bars += [
            f'<rect x="{x}" y="{y:.1f}" width="150" height="{height:.1f}" '
            f'fill="{colors[str(row["architecture"])]}"/>',
            f'<text x="{x+75}" y="{y-10:.1f}" text-anchor="middle">{value:.1f}</text>',
            f'<text x="{x+75}" y="420" text-anchor="middle">{row["architecture"]}</text>',
        ]
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500"
viewBox="0 0 900 500" role="img" aria-label="Synthetic measurement-map demonstration">
<style>text{font-family:Arial,sans-serif;fill:#17212b;font-size:16px}
.title{font-size:23px;font-weight:bold}.note{font-size:13px;fill:#7A3E00}</style>
<rect width="100%" height="100%" fill="white"/>
<text class="title" x="55" y="38">Hourly integration of synthetic performance surfaces</text>
<line x1="90" y1="390" x2="830" y2="390" stroke="#17212b"/>
"""
        + "\n".join(bars)
        + """
<text transform="translate(28 350) rotate(-90)">kg CO2e per delivered IT MWh</text>
<text class="note" x="55" y="470">Protocol demonstration only - replace synthetic surfaces with NED3 measurements.</text>
</svg>
"""
    )


def write_surface_svg(path: Path, rows: list[dict[str, object]]) -> None:
    colors = {40.0: "#56B4E9", 70.0: "#009E73", 100.0: "#D55E00"}
    elements = []
    for load in (40.0, 70.0, 100.0):
        selected = [row for row in rows if float(row["it_load_kw"]) == load]
        points = []
        for row in selected:
            temperature = float(row["ambient_dry_bulb_c"])
            cooling = sum(float(row[name]) for name in (
                "pump_power_kw", "fan_power_kw", "cdu_power_kw",
                "heat_rejection_power_kw",
            ))
            pue = 1 + cooling / load
            x = 100 + (temperature + 15) / 50 * 680
            y = 400 - (pue - 1.03) / 0.09 * 300
            points.append(f"{x:.1f},{y:.1f}")
        elements.append(
            f'<polyline points="{" ".join(points)}" fill="none" '
            f'stroke="{colors[load]}" stroke-width="4"/>'
        )
    for temperature in (-15.0, 0.0, 20.0, 35.0):
        x = 100 + (temperature + 15) / 50 * 680
        elements += [
            f'<line x1="{x:.1f}" y1="100" x2="{x:.1f}" y2="400" '
            'stroke="#E5E7EB"/>',
            f'<text x="{x:.1f}" y="423" text-anchor="middle">{temperature:.0f}</text>',
        ]
    for pue in (1.03, 1.06, 1.09, 1.12):
        y = 400 - (pue - 1.03) / 0.09 * 300
        elements += [
            f'<line x1="100" y1="{y:.1f}" x2="780" y2="{y:.1f}" '
            'stroke="#E5E7EB"/>',
            f'<text x="88" y="{y+5:.1f}" text-anchor="end">{pue:.2f}</text>',
        ]
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500"
viewBox="0 0 900 500" role="img" aria-label="Synthetic air-cooled performance surface">
<style>text{font-family:Arial,sans-serif;fill:#17212b;font-size:15px}
.title{font-size:23px;font-weight:bold}.note{font-size:13px;fill:#7A3E00}</style>
<rect width="100%" height="100%" fill="white"/>
<text class="title" x="55" y="38">Synthetic air-cooled load-temperature performance map</text>
<line x1="100" y1="400" x2="780" y2="400" stroke="#17212b"/>
<line x1="100" y1="100" x2="100" y2="400" stroke="#17212b"/>
"""
        + "\n".join(elements)
        + """
<text x="390" y="440">Ambient dry-bulb temperature (C)</text>
<text transform="translate(35 300) rotate(-90)">Partial PUE</text>
<text x="590" y="75" fill="#56B4E9">40 kW</text>
<text x="670" y="75" fill="#009E73">70 kW</text>
<text x="750" y="75" fill="#D55E00">100 kW</text>
<text class="note" x="55" y="475">Synthetic values define the file and interpolation contract; they are not experimental evidence.</text>
</svg>
"""
    )


def main() -> None:
    for directory in (RESULTS, TABLES, FIGURES, EXAMPLES, PACKAGE_EXAMPLES):
        directory.mkdir(parents=True, exist_ok=True)
    map_paths: dict[str, Path] = {}
    all_rows: dict[str, list[dict[str, object]]] = {}
    for architecture in ("air-cooled", "direct-to-chip"):
        rows = synthetic_rows(architecture)
        path = EXAMPLES / f"synthetic-surface-{architecture}.csv"
        write_csv(path, rows)
        write_csv(PACKAGE_EXAMPLES / path.name, rows)
        map_paths[architecture] = path
        all_rows[architecture] = rows

    workload_rows = [
        {
            "hour_of_day": hour,
            "it_load_fraction": (
                0.4 if hour <= 5 or hour == 23
                else 0.7 if hour <= 8 or hour >= 19
                else 1.0
            ),
        }
        for hour in range(24)
    ]
    write_csv(EXAMPLES / "synthetic-hourly-workload-profile.csv", workload_rows)
    write_csv(
        PACKAGE_EXAMPLES / "synthetic-hourly-workload-profile.csv",
        workload_rows,
    )

    tmy_path = next(
        (RAW / "noaa-tmy" / "fayetteville-ar-usw00093993").glob("*equal.csv")
    )
    with tmy_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        next(reader)
        next(reader)
        fields = next(reader)
        weather = [dict(zip(fields, row)) for row in reader]
    temperatures = [float(row["Temperature"]) for row in weather]
    fractions = [
        float(workload_rows[int(row["Hour"])]["it_load_fraction"])
        for row in weather
    ]
    egrid = load_egrid_state_factor(
        RAW / "egrid2023" / "egrid2023_data_metric_rev2.xlsx", "AR"
    )
    result_objects = []
    for architecture, path in map_paths.items():
        result = integrate_hourly_performance(
            load_performance_map(path),
            temperatures,
            fractions,
            rated_it_load_kw=100.0,
            grid_kgco2e_per_mwh=egrid.co2e_kg_per_mwh,
            evidence_status="synthetic",
        )
        result_objects.append(result)
    results = [result.as_dict() for result in result_objects]
    write_csv(TABLES / "table5_measurement_surface_demo.csv", results)
    (RESULTS / "results.json").write_text(
        json.dumps(
            {
                "status": "synthetic protocol demonstration",
                "comparative_claim_allowed": (
                    measurement_comparative_claim_allowed(result_objects)
                ),
                "egrid": egrid.as_dict(),
                "results": results,
            },
            indent=2,
        )
        + "\n"
    )
    write_bar_svg(FIGURES / "figure4_measurement_surface_demo.svg", results)
    write_surface_svg(
        FIGURES / "figure5_synthetic_performance_surface.svg",
        all_rows["air-cooled"],
    )
    (RESULTS / "REPORT.md").write_text(
        """# v0.6 measurement-ready demonstration

This result proves the data path from a complete load-temperature performance
surface through hourly NOAA weather and workload integration to operational
GHG. Both performance surfaces are synthetic and have
`evidence_status = synthetic`; comparative claims are therefore blocked.

The engine performs bilinear interpolation only inside the measured grid.
Extrapolation is rejected. The reported PUE interval applies the declared
measurement uncertainty to interpolated cooling power and is a screening
interval, not a full correlated uncertainty analysis.

See the paper package Figures 4-5 and Table 5.
"""
    )
    print(f"Wrote v0.6 demonstration to {RESULTS}")


if __name__ == "__main__":
    main()
