#!/usr/bin/env python3
"""Generate the multi-source evidence synthesis used by the manuscript."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendc_lca.public_data import read_xlsx_rows  # noqa: E402

RAW = ROOT / "private-data" / "incoming"
DERIVED = ROOT / "data" / "derived"
TABLES = ROOT / "paper" / "tables"
FIGURES = ROOT / "paper" / "figures"
RESULTS = ROOT / "results" / "integrated-evidence"

TECHNOLOGIES = ("Air-cooled", "Cold plate", "One-phase", "Two-phase")
MICROSOFT_GRID_GHG_KG_PER_MWH = 524.893385656191
MICROSOFT_RENEWABLE_GHG_KG_PER_MWH = 6.13302490385571
COLORS = {
    "Air-cooled": "#4B5563",
    "Cold plate": "#0072B2",
    "One-phase": "#009E73",
    "Two-phase": "#D55E00",
}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def microsoft_ghg_components() -> dict[str, dict[str, dict[str, float]]]:
    source = (
        RAW
        / "microsoft-zenodo"
        / "LCA_Tool_w_Raw_&_Normalized_PlusUncertainty&Details.xlsx"
    )
    rows = read_xlsx_rows(source, "Normalized GHG results")
    result = {"grid": {}, "renewable": {}}
    for row in rows:
        if len(row) < 11 or not isinstance(row[1], str):
            continue
        label = row[1].strip()
        if label not in {
            "Use Phase Impacts",
            "Building Impacts",
            "Compute Server Impacts",
            "Storage Server Impacts",
            "Networking Server Impacts",
            "Rack/Tank Impacts",
            "Cable Impacts",
            "Support Equipment Impacts",
            "Fluid Impacts",
            "Total",
        }:
            continue
        if not all(isinstance(row[column], (int, float)) for column in range(2, 6)):
            continue
        for index, technology in enumerate(TECHNOLOGIES):
            result["grid"].setdefault(technology, {})[label] = float(row[2 + index])
            result["renewable"].setdefault(technology, {})[label] = float(row[7 + index])
        if label == "Total":
            break
    for scenario in result.values():
        if len(scenario) != 4:
            raise ValueError("Microsoft normalized GHG table could not be parsed")
    return result


def egrid_states() -> tuple[list[dict[str, object]], float]:
    source = RAW / "egrid2023" / "egrid2023_data_metric_rev2.xlsx"
    rows = read_xlsx_rows(source, "ST23")
    codes = {str(value): index for index, value in enumerate(rows[1]) if value}
    required = {"YEAR", "PSTATABB", "STNAME", "STNGENAN", "STC2ERTA"}
    if not required.issubset(codes):
        # The state-name code is STNAME in the metric workbook but older
        # provider releases may omit it; fall back to abbreviation.
        required.remove("STNAME")
    output = []
    for row in rows[2:]:
        try:
            factor = float(row[codes["STC2ERTA"]])
            generation = float(row[codes["STNGENAN"]])
        except (TypeError, ValueError, IndexError):
            continue
        abbreviation = str(row[codes["PSTATABB"]])
        if abbreviation in {"US", "PR"} or factor < 0 or generation <= 0:
            continue
        output.append(
            {
                "year": int(float(row[codes["YEAR"]])),
                "state_abbreviation": abbreviation,
                "state": (
                    str(row[codes["STNAME"]])
                    if "STNAME" in codes and row[codes["STNAME"]]
                    else abbreviation
                ),
                "net_generation_mwh": generation,
                "co2e_kg_per_mwh": factor,
                "source_field": "eGRID2023 ST23!STC2ERTA",
            }
        )
    national = sum(
        float(row["co2e_kg_per_mwh"]) * float(row["net_generation_mwh"])
        for row in output
    ) / sum(float(row["net_generation_mwh"]) for row in output)
    return output, national


def state_rebased_results(
    components: dict[str, dict[str, dict[str, float]]],
    states: list[dict[str, object]],
    national_factor: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    summary = []
    for state in states:
        ratio = (
            float(state["co2e_kg_per_mwh"]) - MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
        ) / (
            MICROSOFT_GRID_GHG_KG_PER_MWH
            - MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
        )
        totals = {}
        for technology in TECHNOLOGIES:
            grid = components["grid"][technology]
            renewable = components["renewable"][technology]
            use = renewable["Use Phase Impacts"] + (
                grid["Use Phase Impacts"] - renewable["Use Phase Impacts"]
            ) * ratio
            embodied = sum(
                value
                for label, value in renewable.items()
                if label not in {"Use Phase Impacts", "Total"}
            )
            total = use + embodied
            totals[technology] = total
            rows.append(
                {
                    **state,
                    "technology": technology,
                    "egrid_to_national_ratio": ratio,
                    "use_phase_kgco2e_per_vcore_year": use,
                    "embodied_kgco2e_per_vcore_year": embodied,
                    "total_kgco2e_per_vcore_year": total,
                    "embodied_share_pct": 100 * embodied / total,
                    "method": (
                        "Affine re-basing between Microsoft 100% renewable and "
                        "grid endpoints using their released GaBi factors"
                    ),
                }
            )
        best = min(totals, key=totals.get)
        summary.append(
            {
                **state,
                "lowest_ghg_technology": best,
                "cold_plate_vs_air_reduction_pct": 100
                * (1 - totals["Cold plate"] / totals["Air-cooled"]),
                "one_phase_vs_air_reduction_pct": 100
                * (1 - totals["One-phase"] / totals["Air-cooled"]),
                "two_phase_vs_air_reduction_pct": 100
                * (1 - totals["Two-phase"] / totals["Air-cooled"]),
                "cold_plate_minus_one_phase_kgco2e": (
                    totals["Cold plate"] - totals["One-phase"]
                ),
            }
        )
    return rows, summary


def crossover_rows(
    components: dict[str, dict[str, dict[str, float]]],
    national_factor: float,
) -> list[dict[str, object]]:
    rows = []
    for left, right in (
        ("Cold plate", "One-phase"),
        ("Cold plate", "Two-phase"),
        ("One-phase", "Two-phase"),
    ):
        left_zero = components["renewable"][left]["Total"]
        right_zero = components["renewable"][right]["Total"]
        left_slope = components["grid"][left]["Total"] - left_zero
        right_slope = components["grid"][right]["Total"] - right_zero
        denominator = left_slope - right_slope
        ratio = (
            (right_zero - left_zero) / denominator
            if abs(denominator) > 1e-12
            else math.nan
        )
        rows.append(
            {
                "technology_a": left,
                "technology_b": right,
                "crossover_egrid_ratio": ratio,
                "crossover_kgco2e_per_mwh": (
                    MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
                    + ratio
                    * (
                        MICROSOFT_GRID_GHG_KG_PER_MWH
                        - MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
                    )
                ),
                "within_observed_state_range": False,
                "interpretation": (
                    f"{left} has lower modeled GHG below the crossover; "
                    f"{right} has lower modeled GHG above it."
                ),
            }
        )
    return rows


def boavizta_server_summary() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    source = RAW / "boavizta" / "boavizta-data-us.csv"
    records = []
    with source.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["category"] != "Datacenter" or row["subcategory"] != "Server":
                continue
            try:
                total = float(row["gwp_total"])
                manufacturing_ratio = float(row["gwp_manufacturing_ratio"])
                lifetime = float(row["lifetime"])
            except (TypeError, ValueError):
                continue
            manufacturing = total * manufacturing_ratio
            records.append(
                {
                    "manufacturer": row["manufacturer"],
                    "product": row["name"],
                    "report_date": row["report_date"],
                    "lifetime_years": lifetime,
                    "total_gwp_kgco2e": total,
                    "manufacturing_share_pct": 100 * manufacturing_ratio,
                    "manufacturing_gwp_kgco2e": manufacturing,
                    "annualized_manufacturing_kgco2e_per_year": manufacturing / lifetime,
                    "source_url": row["sources"],
                    "source_dataset": "Boavizta boavizta-data-us.csv",
                }
            )
    values = [float(row["manufacturing_gwp_kgco2e"]) for row in records]
    annualized = [
        float(row["annualized_manufacturing_kgco2e_per_year"]) for row in records
    ]
    summary = [
        {
            "metric": "server manufacturing GWP",
            "unit": "kg CO2e/server",
            "n": len(values),
            "minimum": min(values),
            "p25": percentile(values, 0.25),
            "median": statistics.median(values),
            "p75": percentile(values, 0.75),
            "maximum": max(values),
        },
        {
            "metric": "annualized server manufacturing GWP",
            "unit": "kg CO2e/server-year",
            "n": len(annualized),
            "minimum": min(annualized),
            "p25": percentile(annualized, 0.25),
            "median": statistics.median(annualized),
            "p75": percentile(annualized, 0.75),
            "maximum": max(annualized),
        },
    ]
    return records, summary


def material_levers() -> list[dict[str, object]]:
    source = DERIVED / "oekobaudat-selected-a1-a3.csv"
    with source.open(encoding="utf-8", newline="") as stream:
        records = {row["name"]: row for row in csv.DictReader(stream)}
    comparisons = [
        (
            "Steel route",
            "Galvanized steel profile (blast furnace route, low scrap content), Steel sections",
            "Galvanized steel profile (electric arc furnace route, high scrap content)",
        ),
        ("Cement chemistry", "Cement (CEM II/A)", "Cement (CEM III 42,5)"),
    ]
    output = []
    for lever, baseline_name, alternative_name in comparisons:
        baseline = records[baseline_name]
        alternative = records[alternative_name]
        for indicator, unit in (
            ("gwp_total_kgco2e", "kg CO2e per kg"),
            ("nonrenewable_primary_energy_mj", "MJ per kg"),
            ("freshwater_m3", "m3 per kg"),
        ):
            base = float(baseline[indicator])
            alt = float(alternative[indicator])
            output.append(
                {
                    "lever": lever,
                    "indicator": indicator,
                    "unit": unit,
                    "baseline": baseline_name,
                    "baseline_value": base,
                    "alternative": alternative_name,
                    "alternative_value": alt,
                    "reduction_pct": 100 * (1 - alt / base),
                    "baseline_uuid": baseline["uuid"],
                    "alternative_uuid": alternative["uuid"],
                    "source": "ÖKOBAUDAT 2024-II, modules A1-A3",
                    "propagation_limit": (
                        "Unit-process comparison only; a disclosed bill of "
                        "materials is required for facility-level propagation."
                    ),
                }
            )
    return output


def pedigree_scores() -> list[dict[str, object]]:
    source = (
        RAW
        / "microsoft-zenodo"
        / "LCA_Tool_w_Raw_&_Normalized_PlusUncertainty&Details.xlsx"
    )
    rows = read_xlsx_rows(source, "Pedigree matrix assessment")
    criterion = ""
    output = []
    for row in rows:
        if row and isinstance(row[0], str) and row[0].strip():
            criterion = row[0].strip()
        text = row[1] if len(row) > 1 and isinstance(row[1], str) else ""
        if not criterion or ":" not in text:
            continue
        component = text.split(":", 1)[0].strip()
        matches = re.findall(
            r"(?:scor(?:e|ed|ing)(?:\s+is|\s+at|\s+as|\s+of|\s+to)?|set at)"
            r"\s*(?:a\s*)?(?:conservative(?:ly)?\s*)?(\d)",
            text,
            flags=re.IGNORECASE,
        )
        if not matches:
            matches = re.findall(r"(\d)\s*(?:\.|$)", text[-80:])
        if not matches:
            continue
        score = int(matches[-1])
        if not 1 <= score <= 5:
            continue
        output.append(
            {
                "criterion": criterion,
                "component": component,
                "score_1_best_5_worst": score,
                "source": "Microsoft/WSP released pedigree matrix assessment",
                "rationale": text,
            }
        )
    return output


def data_priority(
    pedigree: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
) -> list[dict[str, object]]:
    aliases = {
        "Use Phase": "Use Phase Impacts",
        "Building": "Building Impacts",
        "Compute Server": "Compute Server Impacts",
        "Storage Server": "Storage Server Impacts",
        "Networking Equipment": "Networking Server Impacts",
        "Rack/Tank": "Rack/Tank Impacts",
        "Cable": "Cable Impacts",
        "Support Equipment": "Support Equipment Impacts",
        "Fluid": "Fluid Impacts",
    }
    score_groups: dict[str, list[float]] = {}
    for row in pedigree:
        score_groups.setdefault(str(row["component"]), []).append(
            float(row["score_1_best_5_worst"])
        )
    output = []
    for component, impact_label in aliases.items():
        scores = score_groups.get(component, [])
        if not scores:
            continue
        shares = []
        for technology in TECHNOLOGIES:
            value = components["grid"][technology][impact_label]
            total = components["grid"][technology]["Total"]
            shares.append(value / total)
        mean_score = statistics.fmean(scores)
        mean_share = statistics.fmean(shares)
        output.append(
            {
                "component": component,
                "pedigree_criteria_scored": len(scores),
                "mean_pedigree_score_1_best_5_worst": mean_score,
                "mean_grid_ghg_contribution_pct": 100 * mean_share,
                "normalized_data_weakness": (mean_score - 1) / 4,
                "contribution_weighted_priority_index": (
                    mean_share * (mean_score - 1) / 4
                ),
                "interpretation": (
                    "Higher values identify evidence whose improvement has "
                    "both greater modeled consequence and poorer data quality."
                ),
            }
        )
    return sorted(
        output,
        key=lambda row: float(row["contribution_weighted_priority_index"]),
        reverse=True,
    )


def svg_header(title: str, width: int = 980, height: int = 560) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        "<style>text{font-family:Arial,sans-serif;fill:#17212b}"
        ".title{font-size:22px;font-weight:700}.axis{font-size:13px}"
        ".label{font-size:12px}.note{font-size:11px;fill:#52606d}</style>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text class="title" x="64" y="38">{title}</text>',
    ]


def write_svg(path: Path, body: list[str]) -> None:
    path.write_text("\n".join(body + ["</svg>", ""]), encoding="utf-8")


def figure_grid_crossover(
    state_rows: list[dict[str, object]],
    national_factor: float,
    crossovers: list[dict[str, object]],
) -> None:
    body = svg_header(
        "Grid decarbonization changes impact magnitude and can reverse close rankings"
    )
    left, top, width, height = 85, 85, 820, 340
    by_tech = {technology: [] for technology in TECHNOLOGIES}
    for row in state_rows:
        by_tech[str(row["technology"])].append(row)
    xmax = max(float(row["co2e_kg_per_mwh"]) for row in state_rows)
    ymax = max(float(row["total_kgco2e_per_vcore_year"]) for row in state_rows) * 1.05
    for tick in range(0, 1001, 200):
        x = left + tick / xmax * width
        body += [
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+height}" '
            'stroke="#E5E7EB"/>',
            f'<text class="axis" x="{x:.1f}" y="{top+height+23}" '
            f'text-anchor="middle">{tick}</text>',
        ]
    for tick in range(0, 51, 10):
        y = top + height - tick / ymax * height
        body += [
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+width}" y2="{y:.1f}" '
            'stroke="#E5E7EB"/>',
            f'<text class="axis" x="{left-10}" y="{y+4:.1f}" '
            f'text-anchor="end">{tick}</text>',
        ]
    for technology in TECHNOLOGIES:
        ordered = sorted(
            by_tech[technology], key=lambda row: float(row["co2e_kg_per_mwh"])
        )
        points = " ".join(
            f"{left+float(row['co2e_kg_per_mwh'])/xmax*width:.1f},"
            f"{top+height-float(row['total_kgco2e_per_vcore_year'])/ymax*height:.1f}"
            for row in ordered
        )
        body.append(
            f'<polyline points="{points}" fill="none" stroke="{COLORS[technology]}" '
            'stroke-width="3"/>'
        )
    crossover = next(
        row
        for row in crossovers
        if row["technology_a"] == "Cold plate"
        and row["technology_b"] == "One-phase"
    )
    cx = left + float(crossover["crossover_kgco2e_per_mwh"]) / xmax * width
    body += [
        f'<line x1="{cx:.1f}" y1="{top}" x2="{cx:.1f}" y2="{top+height}" '
        'stroke="#7C3AED" stroke-width="2" stroke-dasharray="6 5"/>',
        f'<text class="label" x="{cx+7:.1f}" y="{top+18}">'
        f'CP/1P crossover ≈ {float(crossover["crossover_kgco2e_per_mwh"]):.0f} kg CO₂e/MWh'
        "</text>",
        f'<line x1="{left+national_factor/xmax*width:.1f}" y1="{top}" '
        f'x2="{left+national_factor/xmax*width:.1f}" y2="{top+height}" '
        'stroke="#111827" stroke-dasharray="2 4"/>',
        f'<text class="note" x="{left+national_factor/xmax*width+5:.1f}" '
        f'y="{top+height-8}">eGRID 2023 weighted 50-state + DC factor</text>',
        '<text class="axis" x="490" y="485" text-anchor="middle">'
        "State total-output electricity intensity (kg CO₂e/MWh)</text>",
        '<text class="axis" transform="translate(22 350) rotate(-90)">'
        "kg CO₂e per Vcore-year (screening re-base)</text>",
    ]
    for index, technology in enumerate(TECHNOLOGIES):
        x = 80 + index * 205
        body += [
            f'<line x1="{x}" y1="525" x2="{x+25}" y2="525" '
            f'stroke="{COLORS[technology]}" stroke-width="4"/>',
            f'<text class="axis" x="{x+33}" y="530">{technology}</text>',
        ]
    write_svg(FIGURES / "figure2_grid_crossover.svg", body)


def figure_priority(priority: list[dict[str, object]]) -> None:
    body = svg_header("Contribution-weighted data quality identifies the next evidence")
    rows = priority[:8]
    left, top, width, row_height = 290, 82, 590, 48
    maximum = max(float(row["contribution_weighted_priority_index"]) for row in rows)
    for index, row in enumerate(rows):
        y = top + index * row_height
        bar = float(row["contribution_weighted_priority_index"]) / maximum * width
        body += [
            f'<text class="axis" x="{left-14}" y="{y+20}" text-anchor="end">'
            f'{row["component"]}</text>',
            f'<rect x="{left}" y="{y+5}" width="{bar:.1f}" height="23" '
            'rx="4" fill="#2563EB"/>',
            f'<text class="label" x="{left+bar+8:.1f}" y="{y+21}">'
            f'{100*float(row["contribution_weighted_priority_index"]):.1f}</text>',
            f'<text class="note" x="{left}" y="{y+42}">'
            f'{float(row["mean_grid_ghg_contribution_pct"]):.1f}% mean contribution; '
            f'pedigree {float(row["mean_pedigree_score_1_best_5_worst"]):.1f}/5</text>',
        ]
    body += [
        '<text class="axis" x="590" y="505" text-anchor="middle">'
        "Priority index = mean GHG share × normalized pedigree weakness</text>",
        '<text class="note" x="64" y="542">'
        "Screening diagnostic from released Microsoft/WSP contribution and pedigree data; "
        "not a statistical value-of-information calculation.</text>",
    ]
    write_svg(FIGURES / "figure3_data_priority.svg", body)


def figure_server_distribution(
    server_rows: list[dict[str, object]], summary: list[dict[str, object]]
) -> None:
    values = sorted(float(row["manufacturing_gwp_kgco2e"]) for row in server_rows)
    stats = summary[0]
    body = svg_header("Public server manufacturing footprints span 5.4-fold")
    left, top, width, height = 90, 95, 800, 310
    bins = 12
    low, high = min(values), max(values)
    step = (high - low) / bins
    counts = [0] * bins
    for value in values:
        counts[min(int((value - low) / step), bins - 1)] += 1
    max_count = max(counts)
    for index, count in enumerate(counts):
        x = left + index / bins * width
        bar_width = width / bins - 3
        bar_height = count / max_count * height
        body.append(
            f'<rect x="{x:.1f}" y="{top+height-bar_height:.1f}" '
            f'width="{bar_width:.1f}" height="{bar_height:.1f}" fill="#009E73"/>'
        )
    for value, label, color, label_y in (
        (float(stats["p25"]), "P25", "#7C3AED", top + 18),
        (float(stats["median"]), "Median", "#D55E00", top + 42),
        (float(stats["p75"]), "P75", "#7C3AED", top + 66),
    ):
        x = left + (value - low) / (high - low) * width
        body += [
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+height}" '
            f'stroke="{color}" stroke-width="2" stroke-dasharray="6 4"/>',
            f'<text class="label" x="{x+5:.1f}" y="{label_y}">{label}: {value:.0f}</text>',
        ]
    body += [
        '<text class="axis" x="490" y="455" text-anchor="middle">'
        "Manufacturing GWP (kg CO₂e per server)</text>",
        '<text class="axis" transform="translate(28 330) rotate(-90)">Count</text>',
        f'<text class="note" x="90" y="500">n = {len(values)} Boavizta server records; '
        "values inherit heterogeneous manufacturer PCF methods and declared lifetimes.</text>",
    ]
    write_svg(FIGURES / "figure4_server_epd_distribution.svg", body)


def figure_material_levers(rows: list[dict[str, object]]) -> None:
    ghg = [row for row in rows if row["indicator"] == "gwp_total_kgco2e"]
    body = svg_header("Open construction datasets expose large procurement levers")
    left, top, width, height = 110, 110, 700, 270
    for index, row in enumerate(ghg):
        y = top + index * 130
        baseline = float(row["baseline_value"])
        alternative = float(row["alternative_value"])
        maximum = max(float(item["baseline_value"]) for item in ghg)
        body += [
            f'<text class="axis" x="{left}" y="{y-16}">{row["lever"]}</text>',
            f'<rect x="{left}" y="{y}" width="{baseline/maximum*width:.1f}" '
            'height="34" rx="4" fill="#6B7280"/>',
            f'<text class="label" x="{left+baseline/maximum*width+8:.1f}" y="{y+22}">'
            f'{baseline:.3f} baseline</text>',
            f'<rect x="{left}" y="{y+45}" width="{alternative/maximum*width:.1f}" '
            'height="34" rx="4" fill="#009E73"/>',
            f'<text class="label" x="{left+alternative/maximum*width+8:.1f}" '
            f'y="{y+67}">{alternative:.3f} alternative '
            f'(-{float(row["reduction_pct"]):.0f}%)</text>',
        ]
    body += [
        '<text class="axis" x="475" y="430" text-anchor="middle">'
        "A1-A3 GWP (kg CO₂e per kg product)</text>",
        '<text class="note" x="80" y="485">ÖKOBAUDAT 2024-II German generic datasets. '
        "Facility consequences require a disclosed bill of materials.</text>",
    ]
    write_svg(FIGURES / "figure5_material_levers.svg", body)


def main() -> None:
    for directory in (DERIVED, TABLES, FIGURES, RESULTS):
        directory.mkdir(parents=True, exist_ok=True)
    components = microsoft_ghg_components()
    states, national_factor = egrid_states()
    state_rows, state_summary = state_rebased_results(
        components, states, national_factor
    )
    crossovers = crossover_rows(components, national_factor)
    observed_min = min(float(row["co2e_kg_per_mwh"]) for row in states)
    observed_max = max(float(row["co2e_kg_per_mwh"]) for row in states)
    for row in crossovers:
        row["within_observed_state_range"] = (
            observed_min
            <= float(row["crossover_kgco2e_per_mwh"])
            <= observed_max
        )
    server_rows, server_summary = boavizta_server_summary()
    materials = material_levers()
    pedigree = pedigree_scores()
    priority = data_priority(pedigree, components)

    outputs = {
        "table6_state_rebased_ghg.csv": state_rows,
        "table7_state_rank_summary.csv": state_summary,
        "table8_crossover_thresholds.csv": crossovers,
        "table9_boavizta_server_records.csv": server_rows,
        "table10_boavizta_server_summary.csv": server_summary,
        "table11_material_decarbonization_levers.csv": materials,
        "table12_microsoft_pedigree_scores.csv": pedigree,
        "table13_data_improvement_priority.csv": priority,
    }
    for name, rows in outputs.items():
        write_csv(TABLES / name, rows)
        write_csv(RESULTS / name, rows)
    (RESULTS / "analysis-metadata.json").write_text(
        json.dumps(
            {
                "egrid_generation_weighted_national_kgco2e_per_mwh": national_factor,
                "microsoft_grid_endpoint_kgco2e_per_mwh": (
                    MICROSOFT_GRID_GHG_KG_PER_MWH
                ),
                "microsoft_renewable_endpoint_kgco2e_per_mwh": (
                    MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
                ),
                "state_factor_range_kgco2e_per_mwh": [observed_min, observed_max],
                "states_included": len(states),
                "boavizta_servers_included": len(server_rows),
                "microsoft_pedigree_records_parsed": len(pedigree),
                "evidence_status": {
                    "microsoft_reconstruction": "released arithmetic consistency audit",
                    "state_rebase": (
                        "controlled screening scenario; affine interpolation "
                        "between released GaBi electricity endpoints"
                    ),
                    "boavizta": "cross-product evidence synthesis",
                    "oekobaudat": "unit-process scenario; no facility BOM propagation",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    figure_grid_crossover(state_rows, national_factor, crossovers)
    figure_priority(priority)
    figure_server_distribution(server_rows, server_summary)
    figure_material_levers(materials)
    print(f"Wrote integrated evidence results to {RESULTS}")


if __name__ == "__main__":
    main()
