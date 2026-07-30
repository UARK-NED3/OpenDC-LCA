#!/usr/bin/env python3
"""Create reviewable, redistributable summaries from locally held source data."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendc_lca.public_data import (  # noqa: E402
    inspect_glad_jsonld,
    load_egrid_state_factor,
    load_oekobaudat_factors,
    operational_ghg_per_it_mwh,
    summarize_noaa_tmy,
)

RAW = ROOT / "private-data" / "incoming"
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results" / "public-data-v0.3"

OEKO_UUIDS = [
    "42de525f-7c48-4722-b503-6f423b39b4f4",  # steel, EAF/high scrap
    "755a481d-a74b-4ba0-b417-cc26767b2d50",  # steel, BF/low scrap
    "d6f982e3-beda-49f0-a298-694fcbf3ba38",  # concrete C30/37
    "a71e60a5-b64b-4715-ae8a-c8c8819149d2",  # concrete C25/30
    "aaaedf41-a759-4756-bd55-cd2af3af17f4",  # cement CEM II/A
    "8f4e4fdb-fa6c-46b3-8680-57120c4bee5e",  # cement CEM III
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def svg_bar_chart(path: Path, title: str, labels: list[str], values: list[float],
                  unit: str, note: str) -> None:
    width, height, left, top = 900, 460, 275, 75
    plot_width = 560
    maximum = max(values) * 1.12
    rows = []
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + index * 65
        bar_width = value / maximum * plot_width
        rows.append(
            f'<text x="{left - 12}" y="{y + 22}" text-anchor="end">{label}</text>'
            f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="30" '
            f'rx="3" fill="#2b6f8e"/>'
            f'<text x="{left + bar_width + 8:.1f}" y="{y + 21}">{value:.3f}</text>'
        )
    content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
<style>text{{font-family:Arial,sans-serif;fill:#17212b;font-size:15px}}
.title{{font-size:24px;font-weight:bold}}.note{{font-size:13px;fill:#52606d}}</style>
<rect width="100%" height="100%" fill="white"/>
<text class="title" x="35" y="38">{title}</text>
{''.join(rows)}
<text x="{left}" y="{height - 55}">{unit}</text>
<text class="note" x="35" y="{height - 22}">{note}</text>
</svg>
"""
    path.write_text(content)


def main() -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)

    egrid_path = RAW / "egrid2023" / "egrid2023_data_metric_rev2.xlsx"
    egrid = load_egrid_state_factor(egrid_path, "AR")
    write_json(DERIVED / "egrid2023-arkansas.json", egrid.as_dict())

    tmy_dir = RAW / "noaa-tmy" / "fayetteville-ar-usw00093993"
    tmy_csv = next(tmy_dir.glob("*equal.csv"))
    tmy_metadata = next(tmy_dir.glob("*metadata.csv"))
    climate = summarize_noaa_tmy(tmy_csv, tmy_metadata)
    write_json(DERIVED / "noaa-tmy-fayetteville-summary.json", climate.as_dict())

    oeko_path = next((RAW / "oekobaudat").glob("OBD_*.csv"))
    factors = load_oekobaudat_factors(oeko_path, OEKO_UUIDS)
    factor_path = DERIVED / "oekobaudat-selected-a1-a3.csv"
    with factor_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(factors[0].as_dict()))
        writer.writeheader()
        writer.writerows(factor.as_dict() for factor in factors)

    glad_paths = sorted((RAW / "glad" / "nrel-hydrogen-jsonld").glob("*.zip"))
    glad = [inspect_glad_jsonld(path).as_dict() for path in glad_paths]
    write_json(DERIVED / "glad-nrel-hydrogen-processes.json", glad)

    pue_values = [1.10, 1.20, 1.30, 1.40]
    operating = [operational_ghg_per_it_mwh(egrid, pue) for pue in pue_values]
    analysis = {
        "status": "screening analysis; not a comparative cooling-technology LCA",
        "equation": "operational GHG [kg CO2e/IT MWh] = eGRID STC2ERTA [kg CO2e/MWh] × PUE",
        "electricity_factor": egrid.as_dict(),
        "pue_sensitivity": [
            {"pue": pue, "kg_co2e_per_it_mwh": value}
            for pue, value in zip(pue_values, operating)
        ],
        "climate_context": climate.as_dict(),
        "construction_screening_factors": [factor.as_dict() for factor in factors],
        "limitations": [
            "The eGRID calculation is annual, location-based, and operational only.",
            "The TMY summary provides climate context; it is not yet coupled to cooling performance.",
            "ÖKOBAUDAT factors are German EN 15804+A2 construction proxies, not a US bill of materials.",
            "GLAD hydrogen records are catalogued but not used in the numerical results.",
            "No cooling-technology ranking or comparative environmental claim is supported.",
        ],
    }
    write_json(RESULTS / "results.json", analysis)
    svg_bar_chart(
        RESULTS / "arkansas-operational-ghg-vs-pue.svg",
        "Arkansas operational GHG sensitivity to PUE",
        [f"PUE {value:.2f}" for value in pue_values],
        operating,
        "kg CO₂e per delivered IT MWh",
        "EPA eGRID 2023 ST23 total-output CO₂e rate; annual location-based screening.",
    )
    selected = [factor for factor in factors if factor.reference_unit == "kg"]
    svg_bar_chart(
        RESULTS / "selected-material-gwp.svg",
        "Selected ÖKOBAUDAT A1–A3 material factors",
        [factor.name[:28] for factor in selected],
        [factor.gwp_total_kgco2e for factor in selected],
        "kg CO₂e per kg of material",
        "German EN 15804+A2 datasets; screening proxies only. Concrete omitted because its unit is m³.",
    )
    report = f"""# Public-data screening results

This run demonstrates that OpenDC-LCA can ingest provider-native public data
without committing the large raw databases. It is **not** a comparative
cooling-technology LCA.

## Equations and results

The location-based operational calculation is

`GHG_operational = EF_grid × PUE`,

where `EF_grid` is EPA eGRID field `STC2ERTA`. For Arkansas, the 2023 factor is
**{egrid.co2e_kg_per_mwh:.3f} kg CO2e/MWh**. The evaluated PUE range produces
**{min(operating):.1f}–{max(operating):.1f} kg CO2e per delivered IT MWh**.

![Operational GHG sensitivity](arkansas-operational-ghg-vs-pue.svg)

The Fayetteville TMY contains **{climate.hours:,} hours** with mean dry-bulb
temperature **{climate.mean_dry_bulb_c:.2f} °C**, a range of
**{climate.minimum_dry_bulb_c:.1f} to {climate.maximum_dry_bulb_c:.1f} °C**,
and **{climate.hours_above_30c:,} hours above 30 °C. These values establish
local climate context; a later release will couple hourly weather to measured
cooling performance.

![Selected construction factors](selected-material-gwp.svg)

## Interpretation limits

- ÖKOBAUDAT values are A1–A3 German construction-product proxies and are not a
  replacement for a US data-center bill of materials.
- The seven GLAD/NREL hydrogen packages are preserved in the catalog for future
  hydrogen/backup-power scenarios; they do not affect this result.
- USLCI, Microsoft/Nature, Boavizta, USGS, and other acquired files are
  catalogued inputs for later adapters and validation.
- See [`data/SOURCES.md`](../../data/SOURCES.md) for citations, rights, hashes,
  and exact source roles.
"""
    (RESULTS / "REPORT.md").write_text(report)

    source_files = sorted(path for path in RAW.rglob("*") if path.is_file())
    manifest = [
        {
            "source_group": path.relative_to(RAW).parts[0],
            "local_path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        }
        for path in source_files
    ]
    write_json(DERIVED / "source-file-manifest.json", manifest)
    print(f"Wrote derived data to {DERIVED}")
    print(f"Wrote analysis to {RESULTS}")


if __name__ == "__main__":
    main()
