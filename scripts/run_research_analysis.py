#!/usr/bin/env python3
"""Generate the v0.4 reproduction and v0.5 research-preview paper package."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendc_lca.public_data import load_egrid_state_factor  # noqa: E402
from opendc_lca.research import (  # noqa: E402
    TECHNOLOGIES,
    hourly_climate_screening,
    reproduce_microsoft_figure4,
)

RAW = ROOT / "private-data" / "incoming"
PAPER = ROOT / "paper"
TABLES = PAPER / "tables"
FIGURES = PAPER / "figures"
V04 = ROOT / "results" / "v0.4-microsoft-reproduction"
V05 = ROOT / "results" / "v0.5-hourly-preview"

COLORS = {
    "Air-cooled": "#4B5563",
    "Cold plate": "#0072B2",
    "One-phase": "#009E73",
    "Two-phase": "#D55E00",
}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def svg_start(title: str, width: int = 900, height: int = 520) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        "<style>text{font-family:Arial,sans-serif;fill:#17212b}"
        ".title{font-size:22px;font-weight:bold}.axis{font-size:14px}"
        ".small{font-size:12px;fill:#52606d}</style>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text class="title" x="55" y="36">{title}</text>',
    ]


def write_svg(path: Path, elements: list[str]) -> None:
    path.write_text("\n".join(elements + ["</svg>", ""]))


def main() -> None:
    for directory in (PAPER, TABLES, FIGURES, V04, V05):
        directory.mkdir(parents=True, exist_ok=True)

    microsoft_xlsx = (
        RAW / "microsoft-nature" / "41586_2025_8832_MOESM2_ESM.xlsx"
    )
    reproduction = reproduce_microsoft_figure4(microsoft_xlsx)
    reproduction_rows = [item.as_dict() for item in reproduction]
    write_csv(TABLES / "table1_microsoft_reproduction_audit.csv", reproduction_rows)
    (V04 / "results.json").write_text(
        json.dumps(reproduction_rows, indent=2) + "\n"
    )

    grid_reductions = [
        item.as_dict()
        for item in reproduction
        if item.electricity == "Grid" and item.technology != "Air-cooled"
    ]
    write_csv(TABLES / "table2_grid_reductions_vs_air.csv", grid_reductions)

    metrics = ["GHG", "Primary energy", "Blue water"]
    technologies = ["Cold plate", "One-phase", "Two-phase"]
    svg = svg_start("Released Microsoft component data reproduce Figure 4 totals")
    left, top, plot_width, plot_height = 85, 80, 750, 340
    for tick in range(0, 56, 10):
        y = top + plot_height - tick / 55 * plot_height
        svg += [
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_width}" y2="{y:.1f}" '
            'stroke="#D1D5DB" stroke-width="1"/>',
            f'<text class="axis" x="{left-12}" y="{y+5:.1f}" text-anchor="end">{tick}</text>',
        ]
    bar_width, group_width = 48, plot_width / len(metrics)
    for index, technology in enumerate(technologies):
        values = [
            next(
                item.reduction_vs_air_pct
                for item in reproduction
                if item.metric == metric
                and item.electricity == "Grid"
                and item.technology == technology
            )
            for metric in metrics
        ]
        for group_index, value in enumerate(values):
            x = left + group_index * group_width + 35 + index * (bar_width + 8)
            height = value / 55 * plot_height
            y = top + plot_height - height
            svg.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{height:.1f}" '
                f'fill="{COLORS[technology]}"/>'
            )
    for index, metric in enumerate(metrics):
        x = left + index * group_width + group_width / 2
        svg.append(
            f'<text class="axis" x="{x:.1f}" y="{top+plot_height+27}" '
            f'text-anchor="middle">{metric}</text>'
        )
    for index, technology in enumerate(technologies):
        x = 145 + index * 225
        svg += [
            f'<rect x="{x}" y="458" width="18" height="18" fill="{COLORS[technology]}"/>',
            f'<text class="axis" x="{x+27}" y="473">{technology}</text>',
        ]
    svg.append(
        '<text class="axis" transform="translate(20 330) rotate(-90)">'
        "Reduction relative to air-cooled (%)</text>"
    )
    write_svg(FIGURES / "figure1_microsoft_grid_reductions.svg", svg)

    egrid = load_egrid_state_factor(
        RAW / "egrid2023" / "egrid2023_data_metric_rev2.xlsx", "AR"
    )
    tmy = next(
        (
            RAW
            / "noaa-tmy"
            / "fayetteville-ar-usw00093993"
        ).glob("*equal.csv")
    )
    hourly, monthly = hourly_climate_screening(tmy, egrid)
    hourly_rows = [item.as_dict() for item in hourly]
    write_csv(TABLES / "table3_hourly_preview_summary.csv", hourly_rows)
    write_csv(TABLES / "table4_monthly_temperature_pue.csv", monthly)
    (V05 / "results.json").write_text(
        json.dumps(
            {
                "status": (
                    "hypothesis-generating research preview; PUE curves are "
                    "transparent assumptions pending NED3 measurements"
                ),
                "egrid": egrid.as_dict(),
                "annual": hourly_rows,
                "monthly": monthly,
            },
            indent=2,
        )
        + "\n"
    )

    months = [item["month"] for item in monthly]
    svg = svg_start("Fayetteville climate applied to transparent PUE hypotheses")
    left, top, plot_width, plot_height = 85, 80, 750, 340
    for month in months:
        x = left + (month - 1) / 11 * plot_width
        svg.append(f'<text class="axis" x="{x:.1f}" y="445" text-anchor="middle">{month}</text>')
    for technology in TECHNOLOGIES:
        points = " ".join(
            f"{left+(month-1)/11*plot_width:.1f},"
            f"{top+plot_height-(float(item[f'{technology}_mean_pue'])-1.03)/0.08*plot_height:.1f}"
            for month, item in zip(months, monthly)
        )
        svg.append(
            f'<polyline points="{points}" fill="none" stroke="{COLORS[technology]}" '
            'stroke-width="3"/>'
        )
    for tick in (1.03, 1.05, 1.07, 1.09, 1.11):
        y = top + plot_height - (tick - 1.03) / 0.08 * plot_height
        svg += [
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_width}" y2="{y:.1f}" '
            'stroke="#E5E7EB"/>',
            f'<text class="axis" x="{left-10}" y="{y+5:.1f}" text-anchor="end">{tick:.2f}</text>',
        ]
    for index, technology in enumerate(TECHNOLOGIES):
        x = 60 + index * 200
        svg += [
            f'<line x1="{x}" y1="480" x2="{x+25}" y2="480" '
            f'stroke="{COLORS[technology]}" stroke-width="4"/>',
            f'<text class="axis" x="{x+32}" y="485">{technology}</text>',
        ]
    svg.append(
        '<text class="axis" transform="translate(23 330) rotate(-90)">'
        "Illustrative monthly mean PUE</text>"
    )
    write_svg(FIGURES / "figure2_monthly_climate_pue.svg", svg)

    values = [item.operational_kgco2e_per_it_mwh for item in hourly]
    svg = svg_start("Illustrative hourly operational GHG screening in Arkansas")
    left, top, plot_width, plot_height = 90, 80, 740, 330
    maximum = 550
    for tick in range(0, 551, 100):
        y = top + plot_height - tick / maximum * plot_height
        svg += [
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_width}" y2="{y:.1f}" '
            'stroke="#D1D5DB"/>',
            f'<text class="axis" x="{left-12}" y="{y+5:.1f}" text-anchor="end">{tick}</text>',
        ]
    for index, item in enumerate(hourly):
        x = left + 40 + index * 185
        height = item.operational_kgco2e_per_it_mwh / maximum * plot_height
        y = top + plot_height - height
        svg += [
            f'<rect x="{x}" y="{y:.1f}" width="105" height="{height:.1f}" '
            f'fill="{COLORS[item.technology]}"/>',
            f'<text class="axis" x="{x+52.5}" y="{y-8:.1f}" '
            f'text-anchor="middle">{item.operational_kgco2e_per_it_mwh:.1f}</text>',
            f'<text class="axis" x="{x+52.5}" y="440" text-anchor="middle">'
            f'{item.technology}</text>',
        ]
    svg.append(
        '<text class="axis" transform="translate(22 345) rotate(-90)">'
        "kg CO2e per delivered IT MWh</text>"
    )
    write_svg(FIGURES / "figure3_hourly_operational_ghg.svg", svg)

    max_error = max(item.absolute_difference for item in reproduction)
    grid_ghg = {
        item.technology: item.reduction_vs_air_pct
        for item in reproduction
        if item.metric == "GHG" and item.electricity == "Grid"
    }
    preview_reductions = {
        item.technology: item.reduction_vs_air_pct for item in hourly
    }
    report = f"""# Consolidated v0.4-v0.5 results package

## Scope and evidentiary status

This package contains two deliberately separated contributions:

1. **v0.4 reproduction audit (validated):** an independent calculation from
   the released Microsoft/Nature Figure 4 source data.
2. **v0.5 hourly research preview (hypothesis-generating):** NOAA TMY weather,
   EPA eGRID 2023, and transparent temperature-PUE curves. The curves are not
   measurements and cannot support comparative environmental claims.

## Reproduction result

All 24 Figure 4 totals (three impact metrics, two electricity scenarios, and
four cooling architectures) were reconstructed by summing the seven released
component contributions. The maximum absolute disagreement was
**{max_error:.2e} percentage points**, attributable to floating-point rounding.

For the grid scenario, the reproduced GHG reductions relative to air cooling
are **{grid_ghg['Cold plate']:.2f}%** for cold plate,
**{grid_ghg['One-phase']:.2f}%** for one-phase immersion, and
**{grid_ghg['Two-phase']:.2f}%** for two-phase immersion.

![Reproduced Microsoft reductions](figures/figure1_microsoft_grid_reductions.svg)

This audits arithmetic consistency of the public component table. It does
not independently reproduce proprietary LCA for Experts or ecoinvent
background processes, confidential manufacturer data, or the Microsoft
foreground bill of materials.

## Hourly research preview

The Fayetteville TMY was evaluated hour by hour using explicit piecewise-linear
PUE hypotheses. With the EPA eGRID 2023 Arkansas factor of
**{egrid.co2e_kg_per_mwh:.3f} kg CO2e/MWh**, the assumed curves produce
operational-only reductions of **{preview_reductions['Cold plate']:.2f}%**,
**{preview_reductions['One-phase']:.2f}%**, and
**{preview_reductions['Two-phase']:.2f}%** relative to the air-cooled curve.

![Monthly climate and PUE](figures/figure2_monthly_climate_pue.svg)

![Operational GHG preview](figures/figure3_hourly_operational_ghg.svg)

These percentages are **not findings about the technologies**. They quantify
the implications of stated PUE hypotheses and define the exact laboratory
measurements needed to replace them.

## Equations

For hour h, technology j, and dry-bulb temperature T_h:

`PUE[j,h] = PUE_base[j] + a_hot[j] max(T_h-T_hot[j],0)
                         + a_cold[j] max(T_cold[j]-T_h,0)`

`GHG_operational[j] = sum_h(E_IT,h × PUE[j,h] × EF_grid) / sum_h(E_IT,h)`

The current preview assumes constant hourly IT energy, an annual location-based
grid factor, and no humidity, load, water, reliability, or embodied-impact
coupling.

## Paper-use guidance

- Figure 1 and Tables 1-2 are reproducibility results.
- Figures 2-3 and Tables 3-4 are a research protocol demonstration only.
- Replace the assumed PUE parameters with measured performance maps before
  submitting comparative conclusions.
- Retain the source and limitation statements in any derivative manuscript.

## Sources

- Alissa et al., “Using life cycle assessment to drive innovation for
  sustainable cool clouds,” *Nature* 641, 331-338 (2025),
  https://doi.org/10.1038/s41586-025-08832-3
- Released model archive: https://doi.org/10.5281/zenodo.14268168
- EPA eGRID detailed data: https://www.epa.gov/egrid/detailed-data
- NOAA Typical Meteorological Year:
  https://www.ncei.noaa.gov/access/typical-meteorological-year/
"""
    (PAPER / "RESULTS_PACKAGE.md").write_text(report)
    (V04 / "REPORT.md").write_text(
        "# v0.4 Microsoft/Nature reproduction\n\n"
        "See [`paper/RESULTS_PACKAGE.md`](../../paper/RESULTS_PACKAGE.md). "
        f"All 24 totals reconcile; maximum error: {max_error:.2e}.\n"
    )
    (V05 / "REPORT.md").write_text(
        "# v0.5 hourly research preview\n\n"
        "See [`paper/RESULTS_PACKAGE.md`](../../paper/RESULTS_PACKAGE.md). "
        "This is a hypothesis-generating protocol demonstration pending "
        "measured NED3 performance maps.\n"
    )
    print(f"Wrote paper package to {PAPER}")


if __name__ == "__main__":
    main()
