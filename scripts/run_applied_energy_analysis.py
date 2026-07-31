#!/usr/bin/env python3
"""Generate energy-system extensions for the Applied Energy manuscript.

The analysis combines released Microsoft/WSP component results with nine EPA
eGRID data years. It preserves the original foreground model and varies only
the electricity-dependent term. A separate server-inventory stress test uses
the empirical dispersion of public Boavizta records as multiplicative
scenarios; it is not interpreted as a probability distribution.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendc_lca.public_data import read_xlsx_rows  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    "integrated", ROOT / "scripts" / "run_integrated_evidence_analysis.py"
)
assert SPEC and SPEC.loader
integrated = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integrated)

HISTORICAL = ROOT / "private-data" / "incoming" / "egrid-historical"
TABLES = ROOT / "paper" / "tables"
FIGURES = ROOT / "paper" / "figures"
RESULTS = ROOT / "results" / "applied-energy"
TECHNOLOGIES = integrated.TECHNOLOGIES
COLORS = integrated.COLORS
LB_TO_KG = 0.45359237
MICROSOFT_GRID_GHG_KG_PER_MWH = integrated.MICROSOFT_GRID_GHG_KG_PER_MWH
MICROSOFT_RENEWABLE_GHG_KG_PER_MWH = (
    integrated.MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
)

FILES = {
    2012: ("eGRID2012_Data.xlsx", "ST12"),
    2014: ("eGRID2014_Data_v2.xlsx", "ST14"),
    2016: ("egrid2016_data.xlsx", "ST16"),
    2018: ("egrid2018_data.xlsx", "ST18"),
    2019: ("egrid2019_data.xlsx", "ST19"),
    2020: ("egrid2020_data.xlsx", "ST20"),
    2021: ("egrid2021_data.xlsx", "ST21"),
    2022: ("egrid2022_data.xlsx", "ST22"),
}


def official_national_egrid() -> list[dict[str, object]]:
    """Read provider-published U.S. aggregate factors from each eGRID release."""
    output = []
    for year in sorted((*FILES, 2023)):
        if year == 2023:
            path = (
                ROOT
                / "private-data"
                / "incoming"
                / "egrid2023"
                / "egrid2023_data_metric_rev2.xlsx"
            )
        else:
            path = HISTORICAL / FILES[year][0]
        sheet = f"US{str(year)[-2:]}"
        rows = read_xlsx_rows(path, sheet)
        code_row = next(
            index for index, row in enumerate(rows[:6]) if "USC2ERTA" in row
        )
        codes = {
            str(value): index for index, value in enumerate(rows[code_row]) if value
        }
        values = rows[code_row + 1]
        factor = float(values[codes["USC2ERTA"]])
        if year < 2023:
            factor *= LB_TO_KG
        output.append(
            {
                "year": year,
                "official_us_net_generation_mwh": float(
                    values[codes["USNGENAN"]]
                ),
                "official_us_co2e_kg_per_mwh": factor,
                "official_source_file": path.name,
                "official_source_sheet_field": f"{sheet}!USC2ERTA",
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def egrid_year(path: Path, sheet: str, expected_year: int) -> list[dict[str, object]]:
    rows = read_xlsx_rows(path, sheet)
    code_row = next(
        index
        for index, row in enumerate(rows[:10])
        if "PSTATABB" in row and "STNGENAN" in row and "STC2ERTA" in row
    )
    codes = {
        str(value): index for index, value in enumerate(rows[code_row]) if value
    }
    required = {"PSTATABB", "STNGENAN", "STC2ERTA"}
    if not required.issubset(codes):
        raise ValueError(f"Missing eGRID fields in {path.name}: {required-codes.keys()}")
    output = []
    for row in rows[code_row + 1 :]:
        try:
            factor = float(row[codes["STC2ERTA"]]) * LB_TO_KG
            generation = float(row[codes["STNGENAN"]])
        except (TypeError, ValueError, IndexError):
            continue
        state = str(row[codes["PSTATABB"]])
        if state in {"US", "PR"} or generation <= 0 or factor < 0:
            continue
        output.append(
            {
                "year": (
                    int(float(row[codes["YEAR"]]))
                    if "YEAR" in codes and row[codes["YEAR"]] is not None
                    else expected_year
                ),
                "state_abbreviation": state,
                "net_generation_mwh": generation,
                "co2e_kg_per_mwh": factor,
                "source_file": path.name,
                "source_field": f"{sheet}!STC2ERTA converted from lb/MWh",
            }
        )
    return output


def historical_egrid() -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for year, (filename, sheet) in FILES.items():
        output.extend(egrid_year(HISTORICAL / filename, sheet, year))
    current, _ = integrated.egrid_states()
    output.extend(
        {
            "year": row["year"],
            "state_abbreviation": row["state_abbreviation"],
            "net_generation_mwh": row["net_generation_mwh"],
            "co2e_kg_per_mwh": row["co2e_kg_per_mwh"],
            "source_file": "egrid2023_data_metric_rev2.xlsx",
            "source_field": row["source_field"],
        }
        for row in current
    )
    return sorted(
        output,
        key=lambda row: (int(row["year"]), str(row["state_abbreviation"])),
    )


def generation_weighted_factors(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_year: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        by_year.setdefault(int(row["year"]), []).append(row)
    official = {row["year"]: row for row in official_national_egrid()}
    output = []
    for year, group in sorted(by_year.items()):
        generation = sum(float(row["net_generation_mwh"]) for row in group)
        reconstructed_factor = sum(
            float(row["co2e_kg_per_mwh"]) * float(row["net_generation_mwh"])
            for row in group
        ) / generation
        provider = official[year]
        official_factor = float(provider["official_us_co2e_kg_per_mwh"])
        official_generation = float(provider["official_us_net_generation_mwh"])
        output.append(
            {
                "year": year,
                "states_included": len(group),
                "net_generation_mwh": generation,
                "generation_weighted_co2e_kg_per_mwh": official_factor,
                "reconstructed_state_weighted_co2e_kg_per_mwh": (
                    reconstructed_factor
                ),
                "reconstruction_minus_official_kgco2e_per_mwh": (
                    reconstructed_factor - official_factor
                ),
                "reconstruction_minus_official_pct": 100
                * (reconstructed_factor / official_factor - 1),
                "state_generation_coverage_of_official_pct": 100
                * generation
                / official_generation,
                "official_source_file": provider["official_source_file"],
                "official_source_sheet_field": provider[
                    "official_source_sheet_field"
                ],
                "minimum_state_kgco2e_per_mwh": min(
                    float(row["co2e_kg_per_mwh"]) for row in group
                ),
                "median_state_kgco2e_per_mwh": statistics.median(
                    float(row["co2e_kg_per_mwh"]) for row in group
                ),
                "maximum_state_kgco2e_per_mwh": max(
                    float(row["co2e_kg_per_mwh"]) for row in group
                ),
            }
        )
    return output


def method_comparison(
    components: dict[str, dict[str, dict[str, float]]],
    crossover: float,
) -> list[dict[str, object]]:
    grid_totals = {
        technology: components["grid"][technology]["Total"]
        for technology in TECHNOLOGIES
    }
    operational_totals = {
        technology: components["grid"][technology]["Use Phase Impacts"]
        for technology in TECHNOLOGIES
    }
    grid_order = sorted(grid_totals, key=grid_totals.get)
    operational_order = sorted(operational_totals, key=operational_totals.get)
    grid_gap = (
        grid_totals["Cold plate"] - grid_totals["One-phase"]
    )
    return [
        {
            "approach": "PUE-only",
            "case_result": "Not recoverable from normalized LCA totals alone",
            "detects_cp_1p_crossover": "No",
            "detects_embodied_share_transition": "No",
            "detects_evidence_priority": "No",
            "interpretation": (
                "Requires architecture PUE at equivalent useful computation; "
                "omits hardware, fluid, replacement and electricity impacts."
            ),
        },
        {
            "approach": "Operational-GHG-only",
            "case_result": (
                f"{operational_order[0]} lowest at the Microsoft grid endpoint"
            ),
            "detects_cp_1p_crossover": "No embodied crossover",
            "detects_embodied_share_transition": "No",
            "detects_evidence_priority": "No",
            "interpretation": (
                "Uses released use-phase terms but cannot expose a crossover "
                "created by unequal non-use-phase contributions."
            ),
        },
        {
            "approach": "Static cradle-to-grave LCA at one grid",
            "case_result": (
                f"{grid_order[0]} lowest; cold plate minus one-phase = "
                f"{grid_gap:.3f} kg CO2e/Vcore-year"
            ),
            "detects_cp_1p_crossover": "No; one electricity point",
            "detects_embodied_share_transition": "No; one electricity point",
            "detects_evidence_priority": "Contribution only",
            "interpretation": (
                "Includes released lifecycle terms but cannot establish "
                "geographic or temporal transferability from one scenario."
            ),
        },
        {
            "approach": "OpenDC-LCA factor-swept evidence analysis",
            "case_result": (
                f"Cold-plate/one-phase crossover = {crossover:.1f} kg "
                "CO2e/MWh; two-phase lowest in tested scenarios"
            ),
            "detects_cp_1p_crossover": "Yes",
            "detects_embodied_share_transition": "Yes",
            "detects_evidence_priority": "Yes; contribution x pedigree weakness",
            "interpretation": (
                "Adds bounded transformation, functional-unit separation, "
                "provenance and claim limitations to the released foreground."
            ),
        },
    ]


def total_at_factor(
    components: dict[str, dict[str, dict[str, float]]],
    technology: str,
    factor: float,
    reference_factor: float,
    *,
    server_scale: float = 1.0,
    use_scale: float = 1.0,
) -> tuple[float, float, float]:
    grid = components["grid"][technology]
    renewable = components["renewable"][technology]
    endpoint_fraction = (
        factor - MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
    ) / (
        MICROSOFT_GRID_GHG_KG_PER_MWH
        - MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
    )
    use = (
        renewable["Use Phase Impacts"]
        + (grid["Use Phase Impacts"] - renewable["Use Phase Impacts"])
        * endpoint_fraction
    ) * use_scale
    server_labels = {
        "Compute Server Impacts",
        "Storage Server Impacts",
        "Networking Server Impacts",
    }
    embodied = sum(
        value * (server_scale if label in server_labels else 1.0)
        for label, value in renewable.items()
        if label not in {"Use Phase Impacts", "Total"}
    )
    return use + embodied, use, embodied


def historical_technology_results(
    egrid: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    reference_factor: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    detailed = []
    summary = []
    for state_year in egrid:
        factor = float(state_year["co2e_kg_per_mwh"])
        totals = {}
        details = {}
        for technology in TECHNOLOGIES:
            total, use, embodied = total_at_factor(
                components, technology, factor, reference_factor
            )
            totals[technology] = total
            details[technology] = (use, embodied)
        best = min(totals, key=totals.get)
        second = sorted(totals, key=totals.get)[1]
        for technology in TECHNOLOGIES:
            use, embodied = details[technology]
            detailed.append(
                {
                    **state_year,
                    "technology": technology,
                    "use_phase_kgco2e_per_vcore_year": use,
                    "embodied_kgco2e_per_vcore_year": embodied,
                    "total_kgco2e_per_vcore_year": totals[technology],
                    "embodied_share_pct": 100 * embodied / totals[technology],
                    "regret_vs_lowest_pct": 100
                    * (totals[technology] / totals[best] - 1),
                }
            )
        cp_use = details["Cold plate"][0]
        one_use = details["One-phase"][0]
        two_use = details["Two-phase"][0]
        cp_break_even = (totals["One-phase"] - details["Cold plate"][1]) / cp_use
        two_tolerance = (
            (totals[second] - details["Two-phase"][1]) / two_use
            if second != "Two-phase"
            else 1.0
        )
        summary.append(
            {
                **state_year,
                "lowest_ghg_technology": best,
                "second_lowest_technology": second,
                "margin_to_second_pct": 100
                * (totals[second] / totals[best] - 1),
                "cold_plate_use_multiplier_to_equal_one_phase": cp_break_even,
                "cold_plate_use_change_to_equal_one_phase_pct": 100
                * (cp_break_even - 1),
                "one_phase_use_multiplier_to_equal_cold_plate": (
                    totals["Cold plate"] - details["One-phase"][1]
                )
                / one_use,
                "two_phase_use_increase_tolerated_before_losing_pct": 100
                * (two_tolerance - 1),
                "two_phase_vs_air_reduction_pct": 100
                * (1 - totals["Two-phase"] / totals["Air-cooled"]),
            }
        )
    return detailed, summary


def annual_national_results(
    factors: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    reference_factor: float,
) -> list[dict[str, object]]:
    output = []
    for row in factors:
        factor = float(row["generation_weighted_co2e_kg_per_mwh"])
        totals = {
            technology: total_at_factor(
                components, technology, factor, reference_factor
            )
            for technology in TECHNOLOGIES
        }
        best = min(totals, key=lambda technology: totals[technology][0])
        for technology, (total, use, embodied) in totals.items():
            output.append(
                {
                    **row,
                    "technology": technology,
                    "total_kgco2e_per_vcore_year": total,
                    "use_phase_kgco2e_per_vcore_year": use,
                    "embodied_kgco2e_per_vcore_year": embodied,
                    "embodied_share_pct": 100 * embodied / total,
                    "reduction_vs_air_pct": 100
                    * (1 - total / totals["Air-cooled"][0]),
                    "lowest_ghg_technology": best,
                }
            )
    return output


def server_stress_test(
    state_rows_2023: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    reference_factor: float,
    server_records: list[dict[str, object]],
) -> list[dict[str, object]]:
    values = [
        float(row["annualized_manufacturing_kgco2e_per_year"])
        for row in server_records
    ]
    median = statistics.median(values)
    scales = {
        "minimum": min(values) / median,
        "p25": integrated.percentile(values, 0.25) / median,
        "median": 1.0,
        "p75": integrated.percentile(values, 0.75) / median,
        "maximum": max(values) / median,
    }
    output = []
    for label, scale in scales.items():
        winners = {technology: 0 for technology in TECHNOLOGIES}
        margins = []
        for state in state_rows_2023:
            factor = float(state["co2e_kg_per_mwh"])
            totals = {
                technology: total_at_factor(
                    components,
                    technology,
                    factor,
                    reference_factor,
                    server_scale=scale,
                )[0]
                for technology in TECHNOLOGIES
            }
            ordered = sorted(totals, key=totals.get)
            winners[ordered[0]] += 1
            margins.append(100 * (totals[ordered[1]] / totals[ordered[0]] - 1))
        for technology in TECHNOLOGIES:
            output.append(
                {
                    "server_scenario": label,
                    "server_inventory_scale_vs_boavizta_median": scale,
                    "technology": technology,
                    "states_where_lowest_ghg": winners[technology],
                    "median_winner_margin_pct": statistics.median(margins),
                    "interpretation": (
                        "Multiplicative stress test using empirical Boavizta "
                        "annualized server-footprint dispersion; not a probability model."
                    ),
                }
            )
    return output


def svg_header(title: str, width: int = 1100, height: int = 620) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        "<style>text{font-family:Arial,sans-serif;fill:#17212b}"
        ".title{font-size:23px;font-weight:700}.axis{font-size:13px}"
        ".label{font-size:12px}.note{font-size:11px;fill:#52606d}</style>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text class="title" x="68" y="40">{title}</text>',
    ]


def write_svg(path: Path, body: list[str]) -> None:
    path.write_text("\n".join(body + ["</svg>", ""]), encoding="utf-8")


def figure_historical(
    factors: list[dict[str, object]],
    national: list[dict[str, object]],
    crossover: float,
) -> None:
    body = svg_header(
        "Grid decarbonization moves more states into a ranking-sensitive regime"
    )
    left, top, width, height = 90, 90, 920, 380
    years = [int(row["year"]) for row in factors]
    ymin, ymax = min(years), max(years)
    max_factor = 1100.0
    for tick in range(0, 1001, 200):
        x = left + tick / max_factor * width
        body += [
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+height}" stroke="#E5E7EB"/>',
            f'<text class="axis" x="{x:.1f}" y="{top+height+24}" text-anchor="middle">{tick}</text>',
        ]
    for year in sorted(set(years)):
        y = top + (year - ymin) / (ymax - ymin) * height
        body += [
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+width}" y2="{y:.1f}" stroke="#F3F4F6"/>',
            f'<text class="axis" x="{left-12}" y="{y+4:.1f}" text-anchor="end">{year}</text>',
        ]
    for row in factors:
        x = left + min(float(row["co2e_kg_per_mwh"]), max_factor) / max_factor * width
        y = top + (int(row["year"]) - ymin) / (ymax - ymin) * height
        color = "#0072B2" if float(row["co2e_kg_per_mwh"]) < crossover else "#9CA3AF"
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" opacity="0.72"/>')
    points = []
    for row in national:
        x = left + float(row["generation_weighted_co2e_kg_per_mwh"]) / max_factor * width
        y = top + (int(row["year"]) - ymin) / (ymax - ymin) * height
        points.append(f"{x:.1f},{y:.1f}")
    body.append(
        f'<polyline points="{" ".join(points)}" fill="none" stroke="#D55E00" stroke-width="4"/>'
    )
    cx = left + crossover / max_factor * width
    body += [
        f'<line x1="{cx:.1f}" y1="{top}" x2="{cx:.1f}" y2="{top+height}" stroke="#7C3AED" stroke-width="2" stroke-dasharray="6 5"/>',
        f'<text class="label" x="{cx+7:.1f}" y="{top+18}">cold-plate/one-phase crossover: {crossover:.1f}</text>',
        '<text class="axis" x="550" y="535" text-anchor="middle">State total-output electricity intensity (kg CO₂e/MWh)</text>',
        '<text class="note" x="90" y="578">Dots: state-year scenarios; orange line: provider U.S. aggregate; blue dots fall below the released-model crossover.</text>',
    ]
    write_svg(FIGURES / "figure6_historical_grid_transition.svg", body)


def figure_performance_robustness(summary: list[dict[str, object]]) -> None:
    rows = [row for row in summary if int(row["year"]) == 2023]
    rows.sort(key=lambda row: float(row["co2e_kg_per_mwh"]))
    body = svg_header("Small performance deviations can reverse close cooling rankings")
    left, top, width, height = 90, 90, 900, 350
    max_factor = max(float(row["co2e_kg_per_mwh"]) for row in rows)
    for tick in range(0, 1001, 200):
        x = left + tick / max_factor * width
        body += [
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+height}" stroke="#E5E7EB"/>',
            f'<text class="axis" x="{x:.1f}" y="{top+height+23}" text-anchor="middle">{tick}</text>',
        ]
    for tick in range(-4, 13, 4):
        y = top + height - (tick + 4) / 16 * height
        body += [
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+width}" y2="{y:.1f}" stroke="#E5E7EB"/>',
            f'<text class="axis" x="{left-10}" y="{y+4:.1f}" text-anchor="end">{tick}%</text>',
        ]
    cp_points = []
    two_points = []
    for row in rows:
        x = left + float(row["co2e_kg_per_mwh"]) / max_factor * width
        cp = float(row["cold_plate_use_change_to_equal_one_phase_pct"])
        two = float(row["two_phase_use_increase_tolerated_before_losing_pct"])
        cp_y = top + height - (cp + 4) / 16 * height
        two_y = top + height - (two + 4) / 16 * height
        cp_points.append(f"{x:.1f},{cp_y:.1f}")
        two_points.append(f"{x:.1f},{two_y:.1f}")
    body += [
        f'<polyline points="{" ".join(cp_points)}" fill="none" stroke="#0072B2" stroke-width="3"/>',
        f'<polyline points="{" ".join(two_points)}" fill="none" stroke="#D55E00" stroke-width="3"/>',
        f'<line x1="{left}" y1="{top+height-height/4:.1f}" x2="{left+width}" y2="{top+height-height/4:.1f}" stroke="#111827" stroke-dasharray="3 4"/>',
        '<text class="axis" x="540" y="500" text-anchor="middle">2023 state electricity intensity (kg CO₂e/MWh)</text>',
        '<text class="axis" transform="translate(25 370) rotate(-90)">Required use-phase change at break-even</text>',
        '<line x1="170" y1="555" x2="200" y2="555" stroke="#0072B2" stroke-width="4"/>',
        '<text class="axis" x="210" y="560">Cold-plate change to equal one-phase</text>',
        '<line x1="570" y1="555" x2="600" y2="555" stroke="#D55E00" stroke-width="4"/>',
        '<text class="axis" x="610" y="560">Two-phase degradation tolerated before losing</text>',
        '<text class="note" x="90" y="598">The calculation holds embodied terms fixed and scales the released use-phase contribution; it defines measurement precision needs, not expected field performance.</text>',
    ]
    write_svg(FIGURES / "figure7_performance_robustness.svg", body)


def main() -> None:
    for path in (TABLES, FIGURES, RESULTS):
        path.mkdir(parents=True, exist_ok=True)
    components = integrated.microsoft_ghg_components()
    current_states, reference_factor = integrated.egrid_states()
    historical = historical_egrid()
    factors = generation_weighted_factors(historical)
    detailed, summary = historical_technology_results(
        historical, components, reference_factor
    )
    national = annual_national_results(factors, components, reference_factor)
    server_records, _ = integrated.boavizta_server_summary()
    stress = server_stress_test(
        current_states, components, reference_factor, server_records
    )
    crossover = float(
        next(
            row["crossover_kgco2e_per_mwh"]
            for row in integrated.crossover_rows(components, reference_factor)
            if row["technology_a"] == "Cold plate"
            and row["technology_b"] == "One-phase"
        )
    )
    comparison = method_comparison(components, crossover)
    outputs = {
        "table14_egrid_historical_state_factors.csv": historical,
        "table15_egrid_historical_national_factors.csv": factors,
        "table16_historical_cooling_results.csv": detailed,
        "table17_historical_ranking_robustness.csv": summary,
        "table18_national_decarbonization_results.csv": national,
        "table19_server_inventory_stress_test.csv": stress,
        "table20_method_comparison.csv": comparison,
    }
    for name, rows in outputs.items():
        write_csv(TABLES / name, rows)
        write_csv(RESULTS / name, rows)
    figure_historical(historical, factors, crossover)
    figure_performance_robustness(summary)
    metadata = {
        "egrid_years": [row["year"] for row in factors],
        "state_year_observations": len(historical),
        "egrid_2023_state_weighted_excluding_pr_kgco2e_per_mwh": (
            reference_factor
        ),
        "egrid_2023_official_us_kgco2e_per_mwh": next(
            row["generation_weighted_co2e_kg_per_mwh"]
            for row in factors
            if row["year"] == 2023
        ),
        "microsoft_grid_endpoint_kgco2e_per_mwh": MICROSOFT_GRID_GHG_KG_PER_MWH,
        "microsoft_renewable_endpoint_kgco2e_per_mwh": (
            MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
        ),
        "cold_plate_one_phase_crossover_kgco2e_per_mwh": crossover,
        "evidence_status": {
            "historical_transition": "EPA eGRID observations plus affine released-model re-basing",
            "performance_robustness": "deterministic break-even stress test",
            "server_inventory": "empirical multiplicative stress test; not probabilistic uncertainty",
        },
    }
    (RESULTS / "analysis-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
