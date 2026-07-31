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
import random
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
    2023: ("egrid2023_data_rev2.xlsx", "ST23"),
}
GWP_BASIS = {
    2012: ("IPCC SAR GWP100", 21.0, 310.0),
    2014: ("IPCC SAR GWP100", 21.0, 310.0),
    2016: ("IPCC SAR GWP100", 21.0, 310.0),
    2018: ("IPCC AR4 GWP100", 25.0, 298.0),
    2019: ("IPCC AR4 GWP100", 25.0, 298.0),
    2020: ("IPCC AR4 GWP100", 25.0, 298.0),
    2021: ("IPCC AR4 GWP100", 25.0, 298.0),
    2022: ("IPCC AR4 GWP100", 25.0, 298.0),
    2023: ("IPCC AR5 GWP100", 28.0, 265.0),
}
AR5_GWP100_CH4 = 28.0
AR5_GWP100_N2O = 265.0
JOINT_STRESS_SEED = 20250730


def egrid_source(year: int) -> Path:
    if year == 2023:
        return (
            ROOT
            / "private-data"
            / "incoming"
            / "egrid2023"
            / FILES[year][0]
        )
    return HISTORICAL / FILES[year][0]


def _harmonized_rate(
    *,
    generation_mwh: float,
    co2_short_tons: float,
    ch4_lb: float,
    n2o_lb: float,
) -> tuple[float, float]:
    """Return AR5-GWP100 CO2e and CO2-only rates in kg/MWh."""
    co2_lb = 2000.0 * co2_short_tons
    co2e_lb = (
        co2_lb
        + AR5_GWP100_CH4 * ch4_lb
        + AR5_GWP100_N2O * n2o_lb
    )
    return (
        co2e_lb / generation_mwh * LB_TO_KG,
        co2_lb / generation_mwh * LB_TO_KG,
    )


def official_national_egrid() -> list[dict[str, object]]:
    """Read and harmonize provider-published U.S. aggregate eGRID data."""
    output = []
    for year in sorted(FILES):
        path = egrid_source(year)
        sheet = f"US{str(year)[-2:]}"
        rows = read_xlsx_rows(path, sheet)
        code_row = next(
            index for index, row in enumerate(rows[:6]) if "USC2ERTA" in row
        )
        codes = {
            str(value): index for index, value in enumerate(rows[code_row]) if value
        }
        values = rows[code_row + 1]
        generation = float(values[codes["USNGENAN"]])
        reported = float(values[codes["USC2ERTA"]]) * LB_TO_KG
        harmonized, co2_only = _harmonized_rate(
            generation_mwh=generation,
            co2_short_tons=float(values[codes["USCO2AN"]]),
            ch4_lb=float(values[codes["USCH4AN"]]),
            n2o_lb=float(values[codes["USN2OAN"]]),
        )
        output.append(
            {
                "year": year,
                "official_us_net_generation_mwh": generation,
                "reported_us_co2e_kg_per_mwh": reported,
                "harmonized_ar5_us_co2e_kg_per_mwh": harmonized,
                "co2_only_us_kg_per_mwh": co2_only,
                "provider_gwp_basis": GWP_BASIS[year][0],
                "harmonized_gwp_basis": (
                    "IPCC AR5 GWP100; CH4=28 and N2O=265"
                ),
                "official_source_file": path.name,
                "official_source_sheet_field": (
                    f"{sheet}!USCO2AN, USCH4AN, USN2OAN, USNGENAN; "
                    "reported comparison from USC2ERTA"
                ),
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
        if "PSTATABB" in row
        and "STNGENAN" in row
        and "STC2ERTA" in row
    )
    codes = {
        str(value): index for index, value in enumerate(rows[code_row]) if value
    }
    required = {
        "PSTATABB",
        "STNGENAN",
        "STCO2AN",
        "STCH4AN",
        "STN2OAN",
        "STC2ERTA",
    }
    if not required.issubset(codes):
        raise ValueError(f"Missing eGRID fields in {path.name}: {required-codes.keys()}")
    output = []
    for row in rows[code_row + 1 :]:
        try:
            generation = float(row[codes["STNGENAN"]])
            reported = float(row[codes["STC2ERTA"]]) * LB_TO_KG
            harmonized, co2_only = _harmonized_rate(
                generation_mwh=generation,
                co2_short_tons=float(row[codes["STCO2AN"]]),
                ch4_lb=float(row[codes["STCH4AN"]]),
                n2o_lb=float(row[codes["STN2OAN"]]),
            )
        except (TypeError, ValueError, IndexError):
            continue
        state = str(row[codes["PSTATABB"]])
        if (
            state in {"US", "PR"}
            or generation <= 0
            or reported < 0
            or harmonized < 0
        ):
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
                "co2e_kg_per_mwh": harmonized,
                "reported_co2e_kg_per_mwh": reported,
                "co2_kg_per_mwh": co2_only,
                "provider_gwp_basis": GWP_BASIS[expected_year][0],
                "harmonized_gwp_basis": (
                    "IPCC AR5 GWP100; CH4=28 and N2O=265"
                ),
                "source_file": path.name,
                "source_field": (
                    f"{sheet}!STCO2AN, STCH4AN, STN2OAN, STNGENAN; "
                    "reported comparison from STC2ERTA"
                ),
            }
        )
    return output


def historical_egrid() -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for year, (filename, sheet) in FILES.items():
        output.extend(egrid_year(egrid_source(year), sheet, year))
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
        official_factor = float(
            provider["harmonized_ar5_us_co2e_kg_per_mwh"]
        )
        reported_factor = float(provider["reported_us_co2e_kg_per_mwh"])
        official_generation = float(provider["official_us_net_generation_mwh"])
        output.append(
            {
                "year": year,
                "states_included": len(group),
                "net_generation_mwh": generation,
                "generation_weighted_co2e_kg_per_mwh": official_factor,
                "reported_generation_weighted_co2e_kg_per_mwh": reported_factor,
                "reported_minus_harmonized_kgco2e_per_mwh": (
                    reported_factor - official_factor
                ),
                "co2_only_generation_weighted_kg_per_mwh": provider[
                    "co2_only_us_kg_per_mwh"
                ],
                "provider_gwp_basis": provider["provider_gwp_basis"],
                "harmonized_gwp_basis": provider["harmonized_gwp_basis"],
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


def anchor_extrapolation_diagnostics(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Count interpolation and extrapolation relative to released anchors."""
    output = []
    cohorts = {
        "all state-years": rows,
        "2023 states/DC": [row for row in rows if int(row["year"]) == 2023],
    }
    for cohort, group in cohorts.items():
        below = sum(
            float(row["co2e_kg_per_mwh"])
            < MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
            for row in group
        )
        above = sum(
            float(row["co2e_kg_per_mwh"])
            > MICROSOFT_GRID_GHG_KG_PER_MWH
            for row in group
        )
        within = len(group) - below - above
        output.append(
            {
                "cohort": cohort,
                "n": len(group),
                "within_released_anchors": within,
                "below_renewable_anchor": below,
                "above_grid_anchor": above,
                "extrapolated_total": below + above,
                "extrapolated_pct": 100 * (below + above) / len(group),
                "renewable_anchor_kgco2e_per_mwh": (
                    MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
                ),
                "grid_anchor_kgco2e_per_mwh": MICROSOFT_GRID_GHG_KG_PER_MWH,
                "interpretation": (
                    "Counts positions of harmonized eGRID screening rates "
                    "relative to the released GaBi electricity endpoints; "
                    "the rates do not share a complete system boundary."
                ),
            }
        )
    return output


def boundary_adder_stress(
    states_2023: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    reference_factor: float,
) -> list[dict[str, object]]:
    """Stress an unrepresented lifecycle electricity-boundary allowance.

    The additive terms are deliberately not estimates. They show whether the
    qualitative ranking depends on treating direct eGRID output rates as if
    they had the same upstream boundary as the released GaBi anchors.
    """
    output = []
    for adder in (0.0, 25.0, 50.0, 75.0, 100.0):
        winners = {technology: 0 for technology in TECHNOLOGIES}
        cp_below_one = 0
        margins = []
        for state in states_2023:
            factor = float(state["co2e_kg_per_mwh"]) + adder
            totals = {
                technology: total_at_factor(
                    components, technology, factor, reference_factor
                )[0]
                for technology in TECHNOLOGIES
            }
            order = sorted(totals, key=totals.get)
            winners[order[0]] += 1
            cp_below_one += totals["Cold plate"] < totals["One-phase"]
            margins.append(100 * (totals[order[1]] / totals[order[0]] - 1))
        output.append(
            {
                "boundary_adder_kgco2e_per_mwh": adder,
                "states_dc_tested": len(states_2023),
                "cold_plate_below_one_phase_count": cp_below_one,
                "one_phase_below_cold_plate_count": (
                    len(states_2023) - cp_below_one
                ),
                "two_phase_first_rank_count": winners["Two-phase"],
                "air_first_rank_count": winners["Air-cooled"],
                "cold_plate_first_rank_count": winners["Cold plate"],
                "one_phase_first_rank_count": winners["One-phase"],
                "median_first_to_second_margin_pct": statistics.median(margins),
                "interpretation": (
                    "Boundary-mismatch stress only; additive allowance is not "
                    "an upstream inventory estimate or uncertainty distribution."
                ),
            }
        )
    return output


def functional_unit_sensitivity(
    rows: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    reference_factor: float,
) -> list[dict[str, object]]:
    """Quantify the useful-computation correction that erases first rank."""
    output = []
    cohorts = {
        "all state-years": rows,
        "2023 states/DC": [row for row in rows if int(row["year"]) == 2023],
    }
    for cohort, group in cohorts.items():
        penalties = []
        for row in group:
            factor = float(row["co2e_kg_per_mwh"])
            totals = {
                technology: total_at_factor(
                    components, technology, factor, reference_factor
                )[0]
                for technology in TECHNOLOGIES
            }
            two_phase = totals["Two-phase"]
            runner_up = min(
                value
                for technology, value in totals.items()
                if technology != "Two-phase"
            )
            penalties.append(100 * (runner_up / two_phase - 1))
        output.append(
            {
                "cohort": cohort,
                "n": len(penalties),
                "minimum_adverse_two_phase_service_correction_pct": min(penalties),
                "p25_adverse_two_phase_service_correction_pct": integrated.percentile(
                    penalties, 0.25
                ),
                "median_adverse_two_phase_service_correction_pct": (
                    statistics.median(penalties)
                ),
                "p75_adverse_two_phase_service_correction_pct": integrated.percentile(
                    penalties, 0.75
                ),
                "maximum_adverse_two_phase_service_correction_pct": max(penalties),
                "interpretation": (
                    "Multiplicative increase in two-phase impact per equivalent "
                    "useful computation required to equal the runner-up; not a "
                    "measured performance penalty."
                ),
            }
        )
    return output


def joint_assumption_stress(
    states_2023: list[dict[str, object]],
    national_factors: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    reference_factor: float,
    *,
    iterations: int = 20000,
) -> list[dict[str, object]]:
    """Run seeded joint assumption-stress ensembles.

    The triangular draws are deliberately declared envelopes, not fitted
    parameter distributions. Frequencies therefore measure sensitivity to a
    specified perturbation design and must not be read as confidence levels.
    """
    national_2023 = next(
        float(row["generation_weighted_co2e_kg_per_mwh"])
        for row in national_factors
        if int(row["year"]) == 2023
    )
    low_state = min(
        states_2023, key=lambda row: float(row["co2e_kg_per_mwh"])
    )
    contexts = {
        "2023 U.S. generation": national_2023,
        f"2023 low-carbon state ({low_state['state_abbreviation']})": float(
            low_state["co2e_kg_per_mwh"]
        ),
    }
    envelopes = {
        "narrow": {
            "grid": 0.02,
            "use": 0.02,
            "embodied": 0.20,
            "service": 0.02,
        },
        "screening": {
            "grid": 0.05,
            "use": 0.05,
            "embodied": 0.50,
            "service": 0.05,
        },
        "wide": {
            "grid": 0.10,
            "use": 0.10,
            "embodied": 1.00,
            "service": 0.10,
        },
    }
    rng = random.Random(JOINT_STRESS_SEED)
    output = []
    for context, base_factor in contexts.items():
        for envelope, widths in envelopes.items():
            first = {technology: 0 for technology in TECHNOLOGIES}
            cp_below_one = 0
            margins = []
            for _ in range(iterations):
                grid_multiplier = rng.triangular(
                    1 - widths["grid"], 1 + widths["grid"], 1
                )
                factor = max(0.0, base_factor * grid_multiplier)
                totals = {}
                for technology in TECHNOLOGIES:
                    base_total, base_use, base_embodied = total_at_factor(
                        components, technology, factor, reference_factor
                    )
                    del base_total
                    use_multiplier = rng.triangular(
                        1 - widths["use"], 1 + widths["use"], 1
                    )
                    embodied_multiplier = rng.triangular(
                        max(0.0, 1 - widths["embodied"]),
                        1 + widths["embodied"],
                        1,
                    )
                    service_multiplier = rng.triangular(
                        1 - widths["service"], 1 + widths["service"], 1
                    )
                    totals[technology] = (
                        base_use * use_multiplier
                        + base_embodied * embodied_multiplier
                    ) * service_multiplier
                order = sorted(totals, key=totals.get)
                first[order[0]] += 1
                cp_below_one += totals["Cold plate"] < totals["One-phase"]
                margins.append(100 * (totals[order[1]] / totals[order[0]] - 1))
            for technology in TECHNOLOGIES:
                output.append(
                    {
                        "context": context,
                        "base_factor_kgco2e_per_mwh": base_factor,
                        "stress_envelope": envelope,
                        "iterations": iterations,
                        "grid_half_width_pct": 100 * widths["grid"],
                        "use_phase_half_width_pct": 100 * widths["use"],
                        "embodied_half_width_pct": 100 * widths["embodied"],
                        "service_equivalence_half_width_pct": (
                            100 * widths["service"]
                        ),
                        "technology": technology,
                        "first_rank_frequency_pct": 100
                        * first[technology]
                        / iterations,
                        "cold_plate_below_one_phase_frequency_pct": (
                            100 * cp_below_one / iterations
                        ),
                        "median_first_to_second_margin_pct": statistics.median(
                            margins
                        ),
                        "seed": JOINT_STRESS_SEED,
                        "interpretation": (
                            "Seeded triangular assumption-stress frequency; "
                            "not a probability, confidence interval or fitted "
                            "parameter uncertainty."
                        ),
                    }
                )
    return output


def priority_index_sensitivity(
    priority: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Test whether data-priority ranks survive alternative index weights."""
    rank_lists = {str(row["component"]): [] for row in priority}
    for share_exponent in (0.5, 1.0, 2.0):
        for weakness_exponent in (0.5, 1.0, 2.0):
            scored = []
            for row in priority:
                share = float(row["mean_grid_ghg_contribution_pct"]) / 100
                weakness = float(row["normalized_data_weakness"])
                scored.append(
                    (
                        share**share_exponent
                        * weakness**weakness_exponent,
                        str(row["component"]),
                    )
                )
            for rank, (_, component) in enumerate(
                sorted(scored, reverse=True), start=1
            ):
                rank_lists[component].append(rank)
    output = []
    for component, ranks in rank_lists.items():
        output.append(
            {
                "component": component,
                "weighting_specifications": len(ranks),
                "ranked_first_count": sum(rank == 1 for rank in ranks),
                "top_three_count": sum(rank <= 3 for rank in ranks),
                "minimum_rank": min(ranks),
                "median_rank": statistics.median(ranks),
                "maximum_rank": max(ranks),
                "interpretation": (
                    "Ranks across P = contribution^a × weakness^b for "
                    "a,b in {0.5,1,2}; diagnostic robustness, not value of information."
                ),
            }
        )
    return sorted(
        output,
        key=lambda row: (
            -int(row["ranked_first_count"]),
            float(row["median_rank"]),
            int(row["minimum_rank"]),
        ),
    )


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


def figure_scope_and_uncertainty(
    extrapolation: list[dict[str, object]],
    boundary: list[dict[str, object]],
    joint: list[dict[str, object]],
    functional_unit: list[dict[str, object]],
) -> None:
    """Create a compact four-panel robustness diagnostic."""
    body = svg_header(
        "Three diagnostics separate a conditional result from a robust claim",
        width=1200,
        height=760,
    )
    body += [
        '<text class="label" x="65" y="76" style="font-weight:700">A  Anchor coverage</text>',
        '<text class="label" x="625" y="76" style="font-weight:700">B  Boundary-mismatch stress</text>',
        '<text class="label" x="65" y="405" style="font-weight:700">C  Joint assumption-stress ensemble</text>',
        '<text class="label" x="625" y="405" style="font-weight:700">D  Functional-unit sensitivity</text>',
    ]

    # Panel A: interpolation versus extrapolation.
    for index, row in enumerate(extrapolation):
        y = 115 + index * 100
        n = int(row["n"])
        within = int(row["within_released_anchors"])
        below = int(row["below_renewable_anchor"])
        above = int(row["above_grid_anchor"])
        scale = 470 / n
        body += [
            f'<text class="axis" x="65" y="{y-10}">{row["cohort"]} (n={n})</text>',
            f'<rect x="65" y="{y}" width="{within*scale:.1f}" height="32" fill="#009E73"/>',
            f'<rect x="{65+within*scale:.1f}" y="{y}" width="{below*scale:.1f}" height="32" fill="#0072B2"/>',
            f'<rect x="{65+(within+below)*scale:.1f}" y="{y}" width="{above*scale:.1f}" height="32" fill="#D55E00"/>',
            f'<text class="note" x="65" y="{y+54}">{within} interpolated · {below} below · {above} above</text>',
        ]
    body += [
        '<rect x="65" y="305" width="16" height="12" fill="#009E73"/><text class="note" x="88" y="315">within anchors</text>',
        '<rect x="190" y="305" width="16" height="12" fill="#0072B2"/><text class="note" x="213" y="315">below</text>',
        '<rect x="270" y="305" width="16" height="12" fill="#D55E00"/><text class="note" x="293" y="315">above</text>',
    ]

    # Panel B: CP/1P count under a transparent boundary allowance.
    bx, by, bw, bh = 660, 105, 465, 205
    for tick in (0, 10, 20, 30, 40, 50):
        y = by + bh - tick / 51 * bh
        body += [
            f'<line x1="{bx}" y1="{y:.1f}" x2="{bx+bw}" y2="{y:.1f}" stroke="#E5E7EB"/>',
            f'<text class="note" x="{bx-10}" y="{y+4:.1f}" text-anchor="end">{tick}</text>',
        ]
    cp_points = []
    one_points = []
    for row in boundary:
        x = bx + float(row["boundary_adder_kgco2e_per_mwh"]) / 100 * bw
        cp_y = by + bh - int(row["cold_plate_below_one_phase_count"]) / 51 * bh
        one_y = by + bh - int(row["one_phase_below_cold_plate_count"]) / 51 * bh
        cp_points.append(f"{x:.1f},{cp_y:.1f}")
        one_points.append(f"{x:.1f},{one_y:.1f}")
    body += [
        f'<polyline points="{" ".join(cp_points)}" fill="none" stroke="#0072B2" stroke-width="4"/>',
        f'<polyline points="{" ".join(one_points)}" fill="none" stroke="#009E73" stroke-width="4"/>',
        f'<text class="axis" x="{bx+bw/2:.1f}" y="345" text-anchor="middle">Added screening allowance (kg CO₂e/MWh)</text>',
        '<text class="note" x="660" y="370">Blue: CP lower than 1P · Green: 1P lower than CP · two-phase remains first in 51/51.</text>',
    ]

    # Panel C: U.S. 2023 first-rank frequencies by declared envelope.
    us_rows = [
        row
        for row in joint
        if str(row["context"]) == "2023 U.S. generation"
    ]
    envelopes = ("narrow", "screening", "wide")
    technologies = ("Air-cooled", "Cold plate", "One-phase", "Two-phase")
    for row_index, technology in enumerate(technologies):
        y = 455 + row_index * 55
        body.append(
            f'<text class="axis" x="160" y="{y+24}" text-anchor="end">{technology}</text>'
        )
        for column, envelope in enumerate(envelopes):
            value = next(
                float(row["first_rank_frequency_pct"])
                for row in us_rows
                if row["stress_envelope"] == envelope
                and row["technology"] == technology
            )
            x = 185 + column * 120
            opacity = 0.12 + 0.88 * value / 100
            body += [
                f'<rect x="{x}" y="{y}" width="95" height="38" rx="4" fill="#D55E00" opacity="{opacity:.3f}"/>',
                f'<text class="label" x="{x+47.5}" y="{y+25}" text-anchor="middle">{value:.1f}%</text>',
            ]
    for column, envelope in enumerate(envelopes):
        body.append(
            f'<text class="note" x="{232.5+column*120}" y="690" text-anchor="middle">{envelope}</text>'
        )
    body.append(
        '<text class="note" x="65" y="720">Frequencies describe seeded triangular stress designs, not confidence.</text>'
    )

    # Panel D: scalar useful-computation correction thresholds.
    fu_2023 = next(
        row for row in functional_unit if row["cohort"] == "2023 states/DC"
    )
    median = float(
        fu_2023["median_adverse_two_phase_service_correction_pct"]
    )
    minimum = float(
        fu_2023["minimum_adverse_two_phase_service_correction_pct"]
    )
    maximum = float(
        fu_2023["maximum_adverse_two_phase_service_correction_pct"]
    )
    fx, fy, fw = 680, 500, 420
    body += [
        f'<line x1="{fx}" y1="{fy}" x2="{fx+fw}" y2="{fy}" stroke="#CBD5E1" stroke-width="10"/>',
        f'<circle cx="{fx+minimum/maximum*fw:.1f}" cy="{fy}" r="9" fill="#0072B2"/>',
        f'<circle cx="{fx+median/maximum*fw:.1f}" cy="{fy}" r="11" fill="#D55E00"/>',
        f'<circle cx="{fx+fw:.1f}" cy="{fy}" r="9" fill="#0072B2"/>',
        f'<text class="note" x="{fx}" y="{fy+34}">min {minimum:.1f}%</text>',
        f'<text class="label" x="{fx+median/maximum*fw:.1f}" y="{fy-22}" text-anchor="middle">median {median:.1f}%</text>',
        f'<text class="note" x="{fx+fw}" y="{fy+34}" text-anchor="end">max {maximum:.1f}%</text>',
        '<text class="axis" x="890" y="600" text-anchor="middle">Adverse correction to two-phase impact</text>',
        '<text class="axis" x="890" y="622" text-anchor="middle">per equivalent useful computation</text>',
        '<text class="note" x="625" y="666">A correction this small can erase first rank; measured</text>',
        '<text class="note" x="625" y="684">throughput, server count and lifetime are therefore decision data.</text>',
    ]
    write_svg(FIGURES / "figure8_scope_uncertainty.svg", body)


def main() -> None:
    for path in (TABLES, FIGURES, RESULTS):
        path.mkdir(parents=True, exist_ok=True)
    components = integrated.microsoft_ghg_components()
    historical = historical_egrid()
    current_states = [row for row in historical if int(row["year"]) == 2023]
    reference_factor = sum(
        float(row["co2e_kg_per_mwh"]) * float(row["net_generation_mwh"])
        for row in current_states
    ) / sum(float(row["net_generation_mwh"]) for row in current_states)
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
    extrapolation = anchor_extrapolation_diagnostics(historical)
    boundary = boundary_adder_stress(
        current_states, components, reference_factor
    )
    functional_unit = functional_unit_sensitivity(
        historical, components, reference_factor
    )
    joint = joint_assumption_stress(
        current_states, factors, components, reference_factor
    )
    pedigree = integrated.pedigree_scores()
    priority = integrated.data_priority(pedigree, components)
    priority_sensitivity = priority_index_sensitivity(priority)
    outputs = {
        "table14_egrid_historical_state_factors.csv": historical,
        "table15_egrid_historical_national_factors.csv": factors,
        "table16_historical_cooling_results.csv": detailed,
        "table17_historical_ranking_robustness.csv": summary,
        "table18_national_decarbonization_results.csv": national,
        "table19_server_inventory_stress_test.csv": stress,
        "table20_method_comparison.csv": comparison,
        "table21_anchor_extrapolation_diagnostic.csv": extrapolation,
        "table22_boundary_mismatch_stress.csv": boundary,
        "table23_joint_assumption_stress.csv": joint,
        "table24_functional_unit_sensitivity.csv": functional_unit,
        "table25_priority_index_sensitivity.csv": priority_sensitivity,
    }
    for name, rows in outputs.items():
        write_csv(TABLES / name, rows)
        write_csv(RESULTS / name, rows)
    figure_historical(historical, factors, crossover)
    figure_performance_robustness(summary)
    figure_scope_and_uncertainty(
        extrapolation, boundary, joint, functional_unit
    )
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
            "historical_transition": (
                "AR5-harmonized direct eGRID generation rates used as a "
                "numerical intensity index for the released foreground"
            ),
            "performance_robustness": "deterministic break-even stress test",
            "server_inventory": "empirical multiplicative stress test; not probabilistic uncertainty",
            "joint_assumption_stress": (
                "seeded triangular perturbation envelopes; frequencies are "
                "not probabilities or confidence levels"
            ),
            "boundary_mismatch": (
                "transparent additive stress; not an upstream inventory estimate"
            ),
        },
    }
    (RESULTS / "analysis-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
