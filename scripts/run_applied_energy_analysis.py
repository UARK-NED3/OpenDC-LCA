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
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
import random
import statistics
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from opendc_lca.public_data import read_xlsx_rows  # noqa: E402
from opendc_lca.provenance import sha256_file  # noqa: E402
from normalize_figure_typography import normalize as normalize_figure_typography  # noqa: E402

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
MICROSOFT_DETAILED_WORKBOOK = (
    ROOT
    / "private-data"
    / "incoming"
    / "microsoft-zenodo"
    / "LCA Tool with Detailed Equations.xlsx"
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
ELECTRICITY_BASELINE_ZIP = (
    ROOT
    / "private-data"
    / "incoming"
    / "us-electricity-baseline"
    / "US_electricity_baseline_2023_jsonld.zip"
)
IPCC_GWP_ZIP = (
    ROOT
    / "private-data"
    / "incoming"
    / "us-electricity-baseline"
    / "IPCC_GWP_jsonld.zip"
)
IPCC_AR5_100_CATEGORY_ID = "7d05b807-2caa-3cd9-b55c-399d3b820cbc"


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


def _zip_json_records(
    archive: zipfile.ZipFile, folder: str
) -> dict[str, dict[str, object]]:
    """Load an openLCA JSON-LD record folder by UUID."""
    records: dict[str, dict[str, object]] = {}
    prefix = f"{folder}/"
    for name in archive.namelist():
        if not name.startswith(prefix) or not name.endswith(".json"):
            continue
        record = json.loads(archive.read(name))
        records[str(record["@id"])] = record
    return records


def _unit_conversion_factors(
    archives: tuple[zipfile.ZipFile, ...],
) -> dict[str, float]:
    """Return openLCA unit conversion factors to each property reference unit."""
    factors: dict[str, float] = {}
    for archive in archives:
        for group in _zip_json_records(archive, "unit_groups").values():
            for unit in group.get("units", []):
                factors[str(unit["@id"])] = float(unit["conversionFactor"])
    return factors


def _process_reference_exchange(process: dict[str, object]) -> dict[str, object]:
    references = [
        exchange
        for exchange in process.get("exchanges", [])
        if exchange.get("isQuantitativeReference")
    ]
    if len(references) != 1:
        raise ValueError(
            f"Expected one quantitative reference in process {process.get('@id')}"
        )
    return references[0]


def _exchange_in_reference_units(
    exchange: dict[str, object], unit_factors: dict[str, float]
) -> float:
    unit = exchange.get("unit", {})
    unit_id = str(unit.get("@id", ""))
    if unit_id not in unit_factors:
        raise ValueError(f"Missing conversion factor for unit {unit_id!r}")
    return float(exchange.get("amount", 0.0)) * unit_factors[unit_id]


def _solve_openlca_product_system(
    product_system: dict[str, object],
    processes: dict[str, dict[str, object]],
    unit_factors: dict[str, float],
    impact_factors: dict[str, tuple[float, str]],
    *,
    tolerance: float = 1e-12,
    maximum_iterations: int = 10000,
) -> dict[str, object]:
    """Solve one linked openLCA product system without external LCA software.

    Activities are expressed as multiples of each process quantitative
    reference exchange. Product-system links define the technosphere matrix.
    Elementary exchanges are then characterized with the selected LCIA
    factors. Unlinked product or waste inputs remain cutoffs and are counted.
    """
    process_ids = [str(record["@id"]) for record in product_system["processes"]]
    subset = {process_id: processes[process_id] for process_id in process_ids}
    link_by_exchange = {
        (
            str(link["process"]["@id"]),
            int(link["exchange"]["internalId"]),
        ): str(link["provider"]["@id"])
        for link in product_system.get("processLinks", [])
    }
    reference_amounts = {
        process_id: _exchange_in_reference_units(
            _process_reference_exchange(process), unit_factors
        )
        for process_id, process in subset.items()
    }
    coefficients: list[tuple[str, str, float]] = []
    unlinked_inputs = 0
    unlinked_records: list[tuple[str, dict[str, object]]] = []
    for consumer_id, process in subset.items():
        for exchange in process.get("exchanges", []):
            if not exchange.get("isInput"):
                continue
            flow_type = str(exchange.get("flow", {}).get("flowType", ""))
            if flow_type not in {"PRODUCT_FLOW", "WASTE_FLOW"}:
                continue
            key = (consumer_id, int(exchange["internalId"]))
            provider_id = link_by_exchange.get(key)
            if provider_id is None:
                unlinked_inputs += 1
                unlinked_records.append((consumer_id, exchange))
                continue
            provider_reference = reference_amounts[provider_id]
            requirement = _exchange_in_reference_units(exchange, unit_factors)
            coefficients.append(
                (provider_id, consumer_id, requirement / provider_reference)
            )

    reference_process_id = str(product_system["refProcess"]["@id"])
    target_unit_id = str(product_system["targetUnit"]["@id"])
    demand = {
        process_id: 0.0 for process_id in process_ids
    }
    demand[reference_process_id] = (
        float(product_system["targetAmount"])
        * unit_factors[target_unit_id]
        / reference_amounts[reference_process_id]
    )
    activities = demand.copy()
    residual = math.inf
    iterations = 0
    for iterations in range(1, maximum_iterations + 1):
        updated = demand.copy()
        for provider_id, consumer_id, coefficient in coefficients:
            updated[provider_id] += coefficient * activities[consumer_id]
        residual = max(
            abs(updated[process_id] - activities[process_id])
            for process_id in process_ids
        )
        activities = updated
        if residual <= tolerance:
            break
    else:
        raise RuntimeError(
            f"Product-system solver did not converge for {product_system['name']}"
        )

    characterized_by_process: dict[str, float] = {}
    for process_id, process in subset.items():
        characterized = 0.0
        for exchange in process.get("exchanges", []):
            flow_id = str(exchange.get("flow", {}).get("@id", ""))
            factor_record = impact_factors.get(flow_id)
            if factor_record is None:
                continue
            factor, factor_unit_id = factor_record
            amount = _exchange_in_reference_units(exchange, unit_factors)
            amount_in_factor_units = amount / unit_factors[factor_unit_id]
            direction = -1.0 if exchange.get("isInput") else 1.0
            characterized += direction * amount_in_factor_units * factor
        characterized_by_process[process_id] = characterized * activities[process_id]

    total = sum(characterized_by_process.values())
    direct_generation = sum(
        value
        for process_id, value in characterized_by_process.items()
        if str(subset[process_id].get("name", "")).startswith("Electricity - ")
    )
    cutoff_totals: dict[tuple[str, str, str], dict[str, object]] = {}
    for consumer_id, exchange in unlinked_records:
        flow = exchange["flow"]
        key = (
            str(flow["@id"]),
            str(flow.get("name", "")),
            str(flow.get("refUnit", "")),
        )
        record = cutoff_totals.setdefault(
            key,
            {
                "flow_id": key[0],
                "flow_name": key[1],
                "reference_unit": key[2],
                "exchange_count": 0,
                "process_count": set(),
                "activity_weighted_amount": 0.0,
            },
        )
        record["exchange_count"] = int(record["exchange_count"]) + 1
        record["process_count"].add(consumer_id)
        record["activity_weighted_amount"] = float(
            record["activity_weighted_amount"]
        ) + _exchange_in_reference_units(exchange, unit_factors) * activities[
            consumer_id
        ]
    cutoff_summary = []
    for record in cutoff_totals.values():
        cutoff_summary.append(
            {
                **record,
                "process_count": len(record["process_count"]),
            }
        )
    return {
        "total": total,
        "direct_generation": direct_generation,
        "upstream_and_infrastructure": total - direct_generation,
        "process_count": len(process_ids),
        "link_count": len(coefficients),
        "unlinked_technosphere_inputs": unlinked_inputs,
        "solver_iterations": iterations,
        "solver_residual": residual,
        "cutoff_summary": sorted(
            cutoff_summary,
            key=lambda row: (
                str(row["reference_unit"]),
                -abs(float(row["activity_weighted_amount"])),
                str(row["flow_name"]),
            ),
        ),
    }


def lifecycle_electricity_factors(
    components: dict[str, dict[str, dict[str, float]]],
    *,
    residual: bool = False,
) -> list[dict[str, object]]:
    """Calculate 2023 consumption-based U.S. electricity GWP factors.

    The source is the official Federal LCA Commons U.S. Electricity Baseline
    2023. Residual mixes are excluded; the retained systems comprise balancing
    authorities, FERC market regions, and the national consumption mix.
    """
    with zipfile.ZipFile(ELECTRICITY_BASELINE_ZIP) as inventory_archive, zipfile.ZipFile(
        IPCC_GWP_ZIP
    ) as method_archive:
        processes = _zip_json_records(inventory_archive, "processes")
        product_systems = _zip_json_records(
            inventory_archive, "product_systems"
        )
        unit_factors = _unit_conversion_factors(
            (inventory_archive, method_archive)
        )
        categories = _zip_json_records(method_archive, "lcia_categories")
        category = categories[IPCC_AR5_100_CATEGORY_ID]
        if category.get("name") != "AR5-100":
            raise ValueError("Unexpected LCIA category identity for AR5-100")
        impact_factors = {
            str(record["flow"]["@id"]): (
                float(record["value"]),
                str(record["unit"]["@id"]),
            )
            for record in category["impactFactors"]
        }

        retained = [
            record
            for record in product_systems.values()
            if str(record.get("name", "")).startswith(
                "Electricity; at user; residual consumption mix - "
                if residual
                else "Electricity; at user; consumption mix - "
            )
            and (
                residual
                or "residual" not in str(record.get("name", "")).lower()
            )
        ]
        output: list[dict[str, object]] = []
        crossover = next(
            float(row["crossover_kgco2e_per_mwh"])
            for row in integrated.crossover_rows(components)
            if row["technology_a"] == "Cold plate"
            and row["technology_b"] == "One-phase"
        )
        for product_system in retained:
            name = str(product_system["name"])
            region_level = name.rsplit(" - ", 1)[-1]
            region_name = name.removeprefix(
                (
                    "Electricity; at user; residual consumption mix - "
                    if residual
                    else "Electricity; at user; consumption mix - "
                )
            ).rsplit(" - ", 1)[0]
            solved = _solve_openlca_product_system(
                product_system,
                processes,
                unit_factors,
                impact_factors,
            )
            factor = float(solved["total"])
            totals = {
                technology: total_at_factor(
                    components, technology, factor
                )[0]
                for technology in TECHNOLOGIES
            }
            order = sorted(totals, key=totals.get)
            output.append(
                {
                    "region_level": region_level,
                    "electricity_mix_type": (
                        "residual consumption mix"
                        if residual
                        else "consumption mix"
                    ),
                    "region_name": region_name,
                    "region_code": product_system["refProcess"].get(
                        "location", ""
                    ),
                    "reference_year": 2023,
                    "product_system_id": product_system["@id"],
                    "product_system_version": product_system.get("version", ""),
                    "lifecycle_ar5_gwp100_kgco2e_per_mwh": factor,
                    "direct_generation_ar5_gwp100_kgco2e_per_mwh": solved[
                        "direct_generation"
                    ],
                    "upstream_infrastructure_ar5_gwp100_kgco2e_per_mwh": solved[
                        "upstream_and_infrastructure"
                    ],
                    "upstream_infrastructure_share_pct": (
                        100
                        * float(solved["upstream_and_infrastructure"])
                        / factor
                        if factor
                        else 0.0
                    ),
                    "process_count": solved["process_count"],
                    "link_count": solved["link_count"],
                    "unlinked_technosphere_inputs": solved[
                        "unlinked_technosphere_inputs"
                    ],
                    "solver_iterations": solved["solver_iterations"],
                    "solver_residual": solved["solver_residual"],
                    "below_cp_one_phase_numerical_crossover": factor < crossover,
                    "above_released_high_numerical_anchor": (
                        factor > MICROSOFT_GRID_GHG_KG_PER_MWH
                    ),
                    "index_screening_lowest_technology": order[0],
                    "index_screening_second_technology": order[1],
                    "index_screening_margin_pct": 100
                    * (totals[order[1]] / totals[order[0]] - 1),
                    "interpretation": (
                        "Federal LCA Commons "
                        + ("residual " if residual else "")
                        + "consumption-mix lifecycle factor; "
                        "cooling ordering remains a numerical transferability "
                        "screen because the released cooling endpoints have an "
                        "unresolved LCIA-method identity."
                    ),
                }
            )
    return sorted(
        output,
        key=lambda row: (
            {"BA": 0, "FERC": 1, "US": 2}.get(str(row["region_level"]), 3),
            str(row["region_name"]),
        ),
    )


def national_lifecycle_cutoff_summary() -> list[dict[str, object]]:
    """List unlinked technosphere inputs in the national product system."""
    with zipfile.ZipFile(ELECTRICITY_BASELINE_ZIP) as inventory_archive, zipfile.ZipFile(
        IPCC_GWP_ZIP
    ) as method_archive:
        processes = _zip_json_records(inventory_archive, "processes")
        product_system = next(
            record
            for record in _zip_json_records(
                inventory_archive, "product_systems"
            ).values()
            if record.get("name")
            == "Electricity; at user; consumption mix - US - US"
        )
        unit_factors = _unit_conversion_factors(
            (inventory_archive, method_archive)
        )
        category = _zip_json_records(
            method_archive, "lcia_categories"
        )[IPCC_AR5_100_CATEGORY_ID]
        impact_factors = {
            str(record["flow"]["@id"]): (
                float(record["value"]),
                str(record["unit"]["@id"]),
            )
            for record in category["impactFactors"]
        }
        solved = _solve_openlca_product_system(
            product_system,
            processes,
            unit_factors,
            impact_factors,
        )
    return [
        {
            **record,
            "product_system": product_system["name"],
            "cutoff_treatment": (
                "Unlinked technosphere input assigned zero upstream burden "
                "by the linked product-system calculation."
            ),
            "decision_status": (
                "Magnitude not bounded; lifecycle factor is a partial linked-"
                "system screen until providers are linked or cutoffs bounded."
            ),
        }
        for record in solved["cutoff_summary"]
    ]


def _worst_case_rank_gap(
    components: dict[str, dict[str, dict[str, float]]],
    winner: str,
    competitor: str,
    factor: float,
    half_width: float,
    active_blocks: frozenset[str],
) -> float:
    """Return the largest winner-minus-competitor score over a bound box."""
    grid_width = half_width if "grid" in active_blocks else 0.0
    use_width = half_width if "use" in active_blocks else 0.0
    embodied_width = half_width if "embodied" in active_blocks else 0.0
    service_width = half_width if "service" in active_blocks else 0.0
    gaps = []
    for grid_multiplier in (1 - grid_width, 1 + grid_width):
        perturbed_factor = max(0.0, factor * grid_multiplier)
        _, winner_use, winner_embodied = total_at_factor(
            components, winner, perturbed_factor
        )
        _, competitor_use, competitor_embodied = total_at_factor(
            components, competitor, perturbed_factor
        )
        adverse_winner = (
            winner_use * (1 + use_width)
            + winner_embodied * (1 + embodied_width)
        ) * (1 + service_width)
        favorable_competitor = (
            competitor_use * (1 - use_width)
            + competitor_embodied * (1 - embodied_width)
        ) * (1 - service_width)
        gaps.append(adverse_winner - favorable_competitor)
    return max(gaps)


def standardized_rank_robustness(
    lifecycle_rows: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
) -> list[dict[str, object]]:
    """Compute exact equal-width, set-bounded first-rank certificates.

    The bounds are deterministic uncertainty sets, not distributions. The grid
    multiplier is common to all technologies; foreground use, embodied, and
    service-equivalence multipliers may vary independently by technology.
    """
    block_sets = {
        "grid only": frozenset({"grid"}),
        "use phase only": frozenset({"use"}),
        "embodied only": frozenset({"embodied"}),
        "service equivalence only": frozenset({"service"}),
        "all four equal-width": frozenset(
            {"grid", "use", "embodied", "service"}
        ),
    }
    output: list[dict[str, object]] = []
    for context in lifecycle_rows:
        factor = float(context["lifecycle_ar5_gwp100_kgco2e_per_mwh"])
        nominal = {
            technology: total_at_factor(components, technology, factor)[0]
            for technology in TECHNOLOGIES
        }
        winner = min(nominal, key=nominal.get)
        for block_label, blocks in block_sets.items():
            best_threshold: float | None = None
            critical_competitor = ""
            for competitor in TECHNOLOGIES:
                if competitor == winner:
                    continue
                upper = 0.999999
                if (
                    _worst_case_rank_gap(
                        components,
                        winner,
                        competitor,
                        factor,
                        upper,
                        blocks,
                    )
                    < 0
                ):
                    threshold = None
                else:
                    lower = 0.0
                    for _ in range(80):
                        midpoint = (lower + upper) / 2
                        if (
                            _worst_case_rank_gap(
                                components,
                                winner,
                                competitor,
                                factor,
                                midpoint,
                                blocks,
                            )
                            >= 0
                        ):
                            upper = midpoint
                        else:
                            lower = midpoint
                    threshold = upper
                if threshold is not None and (
                    best_threshold is None or threshold < best_threshold
                ):
                    best_threshold = threshold
                    critical_competitor = competitor
            output.append(
                {
                    "region_level": context["region_level"],
                    "region_name": context["region_name"],
                    "region_code": context["region_code"],
                    "lifecycle_ar5_gwp100_kgco2e_per_mwh": factor,
                    "nominal_index_screening_winner": winner,
                    "active_assumption_blocks": block_label,
                    "critical_competitor": critical_competitor or "none below 100%",
                    "critical_equal_half_width_pct": (
                        100 * best_threshold
                        if best_threshold is not None
                        else ""
                    ),
                    "robust_through_99_9999_pct": best_threshold is None,
                    "bound_structure": (
                        "Shared nonnegative grid multiplier; independent "
                        "technology-specific use, embodied, and service "
                        "multipliers; equal relative half-width for active blocks."
                    ),
                    "interpretation": (
                        "Deterministic set-bounded numerical certificate, not "
                        "a probability, confidence interval, or physical validation."
                    ),
                }
            )
    return output


def released_endpoint_method_audit() -> list[dict[str, object]]:
    """Audit the LCIA-method identity of the two released electricity anchors."""
    conventional = read_xlsx_rows(
        MICROSOFT_DETAILED_WORKBOOK, "Use-Phase Conv. Energy Results"
    )
    renewable = read_xlsx_rows(
        MICROSOFT_DETAILED_WORKBOOK, "Use-Phase Renew. Energy Resuts"
    )
    # read_xlsx_rows omits the blank first worksheet row: Excel F26 and F29
    # therefore map to zero-based indices [24][5] and [27][5].
    formulas = {
        "conventional electricity": (
            "Comparative results 0% RE",
            "D118",
        ),
        "100% renewable electricity": (
            "Comparative results 100% RE",
            "D122",
        ),
    }
    records = []
    for endpoint, rows in (
        ("conventional electricity", conventional),
        ("100% renewable electricity", renewable),
    ):
        formula_sheet, formula_cell = formulas[endpoint]
        formula = _xlsx_cell_formula(
            MICROSOFT_DETAILED_WORKBOOK, formula_sheet, formula_cell
        )
        records.append(
            {
                "endpoint": endpoint,
                "published_article_reported_method": "IPCC AR5 GWP100",
                "numeric_workbook_cell": (
                    "Use-Phase Conv. Energy Results!F26"
                    if endpoint == "conventional electricity"
                    else "Use-Phase Renew. Energy Resuts!F26"
                ),
                "numeric_workbook_label": rows[24][4],
                "numeric_workbook_value_kgco2e_per_mwh": rows[24][5],
                "gwp100_workbook_cell": (
                    "Use-Phase Conv. Energy Results!F29"
                    if endpoint == "conventional electricity"
                    else "Use-Phase Renew. Energy Resuts!F29"
                ),
                "gwp100_workbook_label": rows[27][4],
                "gwp100_workbook_value": rows[27][5],
                "formula_evidence_cell": f"{formula_sheet}!{formula_cell}",
                "formula_evidence": formula,
                "formula_evidence_interpretation": (
                    "The comparative use-phase formula references the blank "
                    "F29 GWP100 cell in the corresponding source worksheet."
                ),
                "audit_status": "unresolved public-archive method identity",
                "allowed_use": (
                    "label-free numerical endpoint reconstruction and response "
                    "coefficient; not a common-method comparative LCA"
                ),
            }
        )
    return records


def _xlsx_cell_formula(path: Path, sheet_name: str, cell: str) -> str:
    """Read one worksheet formula directly from an XLSX XML part."""
    spreadsheet_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    relationship_ns = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    )
    package_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(
            archive.read("xl/_rels/workbook.xml.rels")
        )
        targets = {
            record.attrib["Id"]: record.attrib["Target"]
            for record in relationships.findall(f"{{{package_ns}}}Relationship")
        }
        sheet = next(
            record
            for record in workbook.findall(
                f".//{{{spreadsheet_ns}}}sheet"
            )
            if record.attrib["name"] == sheet_name
        )
        relationship_id = sheet.attrib[f"{{{relationship_ns}}}id"]
        target = targets[relationship_id].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        worksheet = ET.fromstring(archive.read(target))
        formula_cell = next(
            record
            for record in worksheet.findall(f".//{{{spreadsheet_ns}}}c")
            if record.attrib.get("r") == cell
        )
        formula_node = formula_cell.find(f"{{{spreadsheet_ns}}}f")
        if formula_node is None or not formula_node.text:
            raise ValueError(f"No formula in {sheet_name}!{cell}")
        return formula_node.text


def implied_electricity_response_coefficients(
    components: dict[str, dict[str, dict[str, float]]],
    national_lifecycle_factor: float,
) -> list[dict[str, object]]:
    """Derive electricity-response slopes from the two released endpoints."""
    factor_difference = (
        MICROSOFT_GRID_GHG_KG_PER_MWH
        - MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
    )
    output = []
    for technology in TECHNOLOGIES:
        grid_use = components["grid"][technology]["Use Phase Impacts"]
        renewable_use = components["renewable"][technology][
            "Use Phase Impacts"
        ]
        response = (grid_use - renewable_use) / factor_difference
        intercept = renewable_use - response * MICROSOFT_RENEWABLE_GHG_KG_PER_MWH
        output.append(
            {
                "technology": technology,
                "released_grid_use_phase_kgco2e_per_vcore_year": grid_use,
                "released_renewable_use_phase_kgco2e_per_vcore_year": renewable_use,
                "implied_electricity_response_mwh_per_vcore_year": response,
                "implied_zero_intensity_intercept_kgco2e_per_vcore_year": intercept,
                "national_lifecycle_use_phase_screen_kgco2e_per_vcore_year": (
                    intercept + response * national_lifecycle_factor
                ),
                "interpretation": (
                    "Slope of the two released numerical endpoints. It has "
                    "energy units but is not an independently measured energy "
                    "demand or a common-method lifecycle result."
                ),
            }
        )
    return output


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
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    detailed = []
    summary = []
    for state_year in egrid:
        factor = float(state_year["co2e_kg_per_mwh"])
        totals = {}
        details = {}
        for technology in TECHNOLOGIES:
            total, use, embodied = total_at_factor(components, technology, factor)
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
) -> list[dict[str, object]]:
    output = []
    for row in factors:
        factor = float(row["generation_weighted_co2e_kg_per_mwh"])
        totals = {
            technology: total_at_factor(components, technology, factor)
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
) -> list[dict[str, object]]:
    """Stress an unrepresented lifecycle electricity-boundary allowance.

    The additive terms are deliberately not estimates. They show whether the
    qualitative ranking depends on treating direct eGRID output rates as if
    they had the same upstream boundary as the released GaBi anchors.
    """
    crossover = next(
        float(row["crossover_kgco2e_per_mwh"])
        for row in integrated.crossover_rows(components)
        if row["technology_a"] == "Cold plate"
        and row["technology_b"] == "One-phase"
    )
    minimum_factor = min(float(row["co2e_kg_per_mwh"]) for row in states_2023)
    exact_clearance = max(0.0, crossover - minimum_factor)
    output = []
    for adder in (0.0, 25.0, 50.0, 75.0, 100.0):
        winners = {technology: 0 for technology in TECHNOLOGIES}
        cp_below_one = 0
        margins = []
        for state in states_2023:
            factor = float(state["co2e_kg_per_mwh"]) + adder
            totals = {
                technology: total_at_factor(components, technology, factor)[0]
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
                "exact_adder_to_remove_all_cp_advantage_kgco2e_per_mwh": (
                    exact_clearance
                ),
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
                technology: total_at_factor(components, technology, factor)[0]
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


def _stress_contexts(
    states_2023: list[dict[str, object]],
    national_factors: list[dict[str, object]],
) -> dict[str, float]:
    national_2023 = next(
        float(row["generation_weighted_co2e_kg_per_mwh"])
        for row in national_factors
        if int(row["year"]) == 2023
    )
    low_state = min(
        states_2023, key=lambda row: float(row["co2e_kg_per_mwh"])
    )
    return {
        "2023 U.S. generation": national_2023,
        f"2023 low-carbon state ({low_state['state_abbreviation']})": float(
            low_state["co2e_kg_per_mwh"]
        ),
    }


def _stress_envelopes() -> dict[str, dict[str, float]]:
    return {
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


def _scenario_seed(*parts: object) -> int:
    """Derive an order-invariant seed for one declared stress design."""
    material = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _symmetric_triangular_inverse(u: float, half_width: float) -> float:
    """Inverse CDF for a symmetric triangular multiplier centered at one."""
    if half_width == 0:
        return 1.0
    if u < 0.5:
        return 1 - half_width + math.sqrt(2 * u * half_width**2)
    return 1 + half_width - math.sqrt(2 * (1 - u) * half_width**2)


def _correlated_triangular_multipliers(
    rng: random.Random,
    half_width: float,
    correlation: float,
) -> dict[str, float]:
    """Draw exact triangular marginals with a Gaussian-copula dependence."""
    if not 0 <= correlation <= 1:
        raise ValueError("correlation must be between zero and one")
    common = rng.gauss(0, 1)
    output = {}
    for technology in TECHNOLOGIES:
        z_value = (
            math.sqrt(correlation) * common
            + math.sqrt(1 - correlation) * rng.gauss(0, 1)
        )
        u_value = 0.5 * (1 + math.erf(z_value / math.sqrt(2)))
        output[technology] = _symmetric_triangular_inverse(
            u_value, half_width
        )
    return output


def joint_assumption_stress(
    states_2023: list[dict[str, object]],
    national_factors: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    *,
    iterations: int = 20000,
) -> list[dict[str, object]]:
    """Run the independent-marginal all-block stress used in the main screen.

    This is the all-block, zero-correlation member of
    :func:`stress_structure_sensitivity`. Keeping the same random design and
    scenario seed makes the headline and decomposition tables exactly
    reconcilable.
    """
    contexts = _stress_contexts(states_2023, national_factors)
    envelopes = _stress_envelopes()
    output = []
    for context, base_factor in contexts.items():
        for envelope, widths in envelopes.items():
            scenario_seed = _scenario_seed(
                JOINT_STRESS_SEED,
                context,
                envelope,
                "all four blocks",
                0.0,
            )
            rng = random.Random(scenario_seed)
            first = {technology: 0 for technology in TECHNOLOGIES}
            cp_below_one = 0
            margins = []
            for _ in range(iterations):
                grid_multiplier = rng.triangular(
                    1 - widths["grid"], 1 + widths["grid"], 1
                )
                factor = max(0.0, base_factor * grid_multiplier)
                multipliers = {
                    category: _correlated_triangular_multipliers(
                        rng, widths[category], 0.0
                    )
                    for category in ("use", "embodied", "service")
                }
                totals = {}
                for technology in TECHNOLOGIES:
                    base_total, base_use, base_embodied = total_at_factor(
                        components, technology, factor
                    )
                    del base_total
                    totals[technology] = (
                        base_use * multipliers["use"][technology]
                        + base_embodied
                        * multipliers["embodied"][technology]
                    ) * multipliers["service"][technology]
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
                        "base_seed": JOINT_STRESS_SEED,
                        "scenario_seed_hex": f"{scenario_seed:016x}",
                        "interpretation": (
                            "Seeded triangular assumption-stress frequency; "
                            "not a probability, confidence interval or fitted "
                            "parameter uncertainty."
                        ),
                    }
                )
    return output


def stress_structure_sensitivity(
    states_2023: list[dict[str, object]],
    national_factors: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    *,
    iterations: int = 20000,
) -> list[dict[str, object]]:
    """Decompose rank fragility by assumption block and dependence structure.

    All marginals retain the declared symmetric triangular envelopes. The
    technology-specific draws use a Gaussian copula with latent correlations
    of 0, 0.5, or 1. These are design diagnostics, not fitted correlations.
    """
    contexts = _stress_contexts(states_2023, national_factors)
    envelopes = _stress_envelopes()
    blocks = {
        "grid only": {"grid"},
        "use phase only": {"use"},
        "embodied only": {"embodied"},
        "service equivalence only": {"service"},
        "all four blocks": {"grid", "use", "embodied", "service"},
    }
    output = []
    for context, base_factor in contexts.items():
        for envelope, widths in envelopes.items():
            for block_name, active in blocks.items():
                for correlation in (0.0, 0.5, 1.0):
                    scenario_seed = _scenario_seed(
                        JOINT_STRESS_SEED,
                        context,
                        envelope,
                        block_name,
                        correlation,
                    )
                    rng = random.Random(scenario_seed)
                    first = {technology: 0 for technology in TECHNOLOGIES}
                    cp_below_one = 0
                    margins = []
                    for _ in range(iterations):
                        grid_multiplier = (
                            rng.triangular(
                                1 - widths["grid"],
                                1 + widths["grid"],
                                1,
                            )
                            if "grid" in active
                            else 1.0
                        )
                        factor = max(0.0, base_factor * grid_multiplier)
                        multipliers = {}
                        for category in ("use", "embodied", "service"):
                            multipliers[category] = (
                                _correlated_triangular_multipliers(
                                    rng, widths[category], correlation
                                )
                                if category in active
                                else {
                                    technology: 1.0
                                    for technology in TECHNOLOGIES
                                }
                            )
                        totals = {}
                        for technology in TECHNOLOGIES:
                            _, base_use, base_embodied = total_at_factor(
                                components, technology, factor
                            )
                            totals[technology] = (
                                base_use * multipliers["use"][technology]
                                + base_embodied
                                * multipliers["embodied"][technology]
                            ) * multipliers["service"][technology]
                        order = sorted(totals, key=totals.get)
                        first[order[0]] += 1
                        cp_below_one += (
                            totals["Cold plate"] < totals["One-phase"]
                        )
                        margins.append(
                            100 * (totals[order[1]] / totals[order[0]] - 1)
                        )
                    for technology in TECHNOLOGIES:
                        output.append(
                            {
                                "context": context,
                                "base_factor_kgco2e_per_mwh": base_factor,
                                "stress_envelope": envelope,
                                "active_assumption_blocks": block_name,
                                "latent_technology_correlation": correlation,
                                "iterations": iterations,
                                "technology": technology,
                                "first_rank_frequency_pct": (
                                    100 * first[technology] / iterations
                                ),
                                "cold_plate_below_one_phase_frequency_pct": (
                                    100 * cp_below_one / iterations
                                ),
                                "median_first_to_second_margin_pct": (
                                    statistics.median(margins)
                                ),
                                "base_seed": JOINT_STRESS_SEED,
                                "scenario_seed_hex": f"{scenario_seed:016x}",
                                "interpretation": (
                                    "Declared triangular-marginal stress with "
                                    "Gaussian-copula dependence; the latent "
                                    "correlation and frequencies are not fitted "
                                    "uncertainty or confidence."
                                ),
                            }
                        )
    return output


def stress_convergence_diagnostic(
    states_2023: list[dict[str, object]],
    national_factors: list[dict[str, object]],
    components: dict[str, dict[str, dict[str, float]]],
    *,
    sample_sizes: tuple[int, ...] = (5000, 20000, 80000),
) -> list[dict[str, object]]:
    """Check numerical convergence of headline rank-frequency estimates.

    Each larger run reuses the same deterministic scenario seed, so the draws
    are nested. The reported standard error describes Monte Carlo integration
    precision within the declared stress design; it is not epistemic
    uncertainty in the cooling comparison.
    """
    if not sample_sizes or any(size <= 0 for size in sample_sizes):
        raise ValueError("sample_sizes must contain positive integers")
    ordered_sizes = tuple(sorted(set(sample_sizes)))
    by_size: dict[int, list[dict[str, object]]] = {}
    for size in ordered_sizes:
        by_size[size] = [
            row
            for row in joint_assumption_stress(
                states_2023,
                national_factors,
                components,
                iterations=size,
            )
            if row["technology"] == "Two-phase"
        ]
    largest = {
        (str(row["context"]), str(row["stress_envelope"])): float(
            row["first_rank_frequency_pct"]
        )
        for row in by_size[ordered_sizes[-1]]
    }
    output = []
    for size in ordered_sizes:
        for row in by_size[size]:
            frequency = float(row["first_rank_frequency_pct"])
            probability = frequency / 100
            key = (str(row["context"]), str(row["stress_envelope"]))
            output.append(
                {
                    "context": row["context"],
                    "stress_envelope": row["stress_envelope"],
                    "iterations": size,
                    "two_phase_first_rank_frequency_pct": frequency,
                    "monte_carlo_standard_error_pct_points": (
                        100
                        * math.sqrt(
                            probability * (1 - probability) / size
                        )
                    ),
                    "difference_from_largest_run_pct_points": (
                        frequency - largest[key]
                    ),
                    "scenario_seed_hex": row["scenario_seed_hex"],
                    "interpretation": (
                        "Nested-seed numerical convergence within a declared "
                        "stress design; not empirical uncertainty or a "
                        "confidence interval for technology performance."
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
        '<text class="note" x="90" y="578">Dots: state-year scenarios; orange polyline: reported provider U.S. aggregate; blue dots fall below the released-model crossover.</text>',
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


def figure_stress_structure(rows: list[dict[str, object]]) -> None:
    """Show how rank frequencies depend on active blocks and dependence."""
    body = svg_header(
        "Rank fragility is driven by foreground structure, not grid-rate noise",
        width=1200,
        height=720,
    )
    blocks = (
        "grid only",
        "use phase only",
        "embodied only",
        "service equivalence only",
        "all four blocks",
    )
    correlations = (0.0, 0.5, 1.0)
    for panel, envelope in enumerate(("screening", "wide")):
        x0 = 230 + panel * 500
        body.append(
            f'<text class="label" x="{x0+150}" y="82" text-anchor="middle" '
            f'style="font-weight:700">{envelope.capitalize()} envelope</text>'
        )
        for column, correlation in enumerate(correlations):
            body.append(
                f'<text class="axis" x="{x0+column*130+55}" y="118" '
                f'text-anchor="middle">latent r={correlation:.1f}</text>'
            )
        for row_index, block in enumerate(blocks):
            y = 145 + row_index * 82
            if panel == 0:
                body.append(
                    f'<text class="axis" x="205" y="{y+28}" '
                    f'text-anchor="end">{block}</text>'
                )
            for column, correlation in enumerate(correlations):
                value = next(
                    float(row["first_rank_frequency_pct"])
                    for row in rows
                    if row["context"] == "2023 U.S. generation"
                    and row["stress_envelope"] == envelope
                    and row["active_assumption_blocks"] == block
                    and float(row["latent_technology_correlation"])
                    == correlation
                    and row["technology"] == "Two-phase"
                )
                x = x0 + column * 130
                red = int(232 - 1.2 * value)
                green = int(244 - 0.8 * value)
                blue = int(248 - 0.15 * value)
                body += [
                    f'<rect x="{x}" y="{y}" width="110" height="55" rx="5" '
                    f'fill="rgb({red},{green},{blue})" stroke="#CBD5E1"/>',
                    f'<text class="label" x="{x+55}" y="{y+33}" '
                    f'text-anchor="middle">{value:.1f}%</text>',
                ]
    body += [
        '<text class="axis" x="600" y="600" text-anchor="middle">Two-phase first-rank frequency in declared stress designs</text>',
        '<text class="note" x="95" y="642">Each cell uses 20,000 seeded draws with the same triangular marginals.</text>',
        '<text class="note" x="95" y="666">The latent Gaussian-copula correlation changes dependence among technology-specific multipliers; it is not an empirical estimate.</text>',
        '<text class="note" x="95" y="690">Grid-only perturbation is shared across technologies. Common-mode foreground errors preserve more of the released ordering than independent errors.</text>',
    ]
    write_svg(FIGURES / "figure9_stress_structure.svg", body)


def figure_lifecycle_electricity(
    rows: list[dict[str, object]], crossover: float
) -> None:
    """Plot lifecycle electricity factors for FERC regions and the U.S."""
    selected = sorted(
        [row for row in rows if row["region_level"] in {"FERC", "US"}],
        key=lambda row: float(row["lifecycle_ar5_gwp100_kgco2e_per_mwh"]),
    )
    body = svg_header(
        "Partial linked at-user electricity screening factors",
        width=1200,
        height=820,
    )
    x0, y0, chart_width, row_height = 250, 105, 820, 53
    maximum = 620.0
    for tick in range(0, 601, 100):
        x = x0 + chart_width * tick / maximum
        body += [
            f'<line x1="{x:.1f}" y1="{y0-20}" x2="{x:.1f}" y2="{y0+len(selected)*row_height}" stroke="#E5E7EB"/>',
            f'<text class="note" x="{x:.1f}" y="{y0+len(selected)*row_height+30}" text-anchor="middle">{tick}</text>',
        ]
    for index, row in enumerate(selected):
        y = y0 + index * row_height
        direct = float(row["direct_generation_ar5_gwp100_kgco2e_per_mwh"])
        upstream = float(
            row["upstream_infrastructure_ar5_gwp100_kgco2e_per_mwh"]
        )
        direct_width = chart_width * direct / maximum
        upstream_width = chart_width * upstream / maximum
        body += [
            f'<text class="axis" x="{x0-15}" y="{y+23}" text-anchor="end">{row["region_name"]}</text>',
            f'<rect x="{x0}" y="{y}" width="{direct_width:.1f}" height="30" fill="#0072B2"/>',
            f'<rect x="{x0+direct_width:.1f}" y="{y}" width="{upstream_width:.1f}" height="30" fill="#D55E00"/>',
            f'<text class="note" x="{x0+direct_width+upstream_width+8:.1f}" y="{y+21}">{direct+upstream:.1f}</text>',
        ]
    crossover_x = x0 + chart_width * crossover / maximum
    anchor_x = x0 + chart_width * MICROSOFT_GRID_GHG_KG_PER_MWH / maximum
    body += [
        f'<line x1="{crossover_x:.1f}" y1="{y0-25}" x2="{crossover_x:.1f}" y2="{y0+len(selected)*row_height}" stroke="#009E73" stroke-width="3" stroke-dasharray="8 5"/>',
        f'<text class="note" x="{crossover_x+5:.1f}" y="{y0-32}">green dashed: numerical CP/1P crossover {crossover:.1f}</text>',
        f'<line x1="{anchor_x:.1f}" y1="{y0-25}" x2="{anchor_x:.1f}" y2="{y0+len(selected)*row_height}" stroke="#7C3AED" stroke-width="3" stroke-dasharray="3 5"/>',
        f'<text class="note" x="{anchor_x-5:.1f}" y="{y0-50}" text-anchor="end">purple dashed: released high numerical anchor {MICROSOFT_GRID_GHG_KG_PER_MWH:.1f}</text>',
        '<rect x="250" y="735" width="18" height="14" fill="#0072B2"/><text class="note" x="278" y="747">generation processes</text>',
        '<rect x="450" y="735" width="18" height="14" fill="#D55E00"/><text class="note" x="478" y="747">upstream and infrastructure</text>',
        '<text class="axis" x="660" y="790" text-anchor="middle">IPCC AR5 GWP100 (kg CO₂e/MWh delivered at user)</text>',
        '<text class="note" x="250" y="772">Federal LCA Commons U.S. Electricity Baseline 2023; consumption mixes. Cooling ranks remain numerical screens.</text>',
    ]
    write_svg(FIGURES / "figure10_lifecycle_electricity.svg", body)


def figure_standardized_robustness(rows: list[dict[str, object]]) -> None:
    """Plot equal-width deterministic first-rank robustness certificates."""
    body = svg_header(
        "Equal-width bounds identify service and use-phase assumptions as limiting",
        width=1200,
        height=720,
    )
    body += [
        '<text class="label" x="70" y="82" style="font-weight:700">A  National lifecycle context</text>',
        '<text class="label" x="650" y="82" style="font-weight:700">B  All 71 lifecycle electricity contexts</text>',
    ]
    national = [row for row in rows if row["region_level"] == "US"]
    labels = (
        "grid only",
        "use phase only",
        "embodied only",
        "service equivalence only",
        "all four equal-width",
    )
    x0, y0, width = 210, 120, 350
    maximum = 25.0
    for tick in (0, 5, 10, 15, 20, 25):
        x = x0 + width * tick / maximum
        body += [
            f'<line x1="{x:.1f}" y1="{y0-15}" x2="{x:.1f}" y2="555" stroke="#E5E7EB"/>',
            f'<text class="note" x="{x:.1f}" y="580" text-anchor="middle">{tick}%</text>',
        ]
    for index, label in enumerate(labels):
        row = next(r for r in national if r["active_assumption_blocks"] == label)
        y = y0 + index * 82
        body.append(
            f'<text class="axis" x="{x0-15}" y="{y+27}" text-anchor="end">{label}</text>'
        )
        value = row["critical_equal_half_width_pct"]
        if value == "":
            bar_width = width
            value_label = ">99.999%"
        else:
            numeric = float(value)
            bar_width = width * min(numeric, maximum) / maximum
            value_label = f"{numeric:.2f}%"
        color = "#D55E00" if label in {"use phase only", "service equivalence only", "all four equal-width"} else "#0072B2"
        body += [
            f'<rect x="{x0}" y="{y}" width="{bar_width:.1f}" height="38" rx="4" fill="{color}"/>',
            f'<text class="note" x="{x0+bar_width+8:.1f}" y="{y+25}">{value_label}</text>',
        ]

    all_block = [
        row for row in rows if row["active_assumption_blocks"] == "all four equal-width"
    ]
    sx, sy, sw, sh = 680, 125, 430, 410
    for tick in (0, 200, 400, 600, 800, 1000):
        x = sx + sw * tick / 1000
        body += [
            f'<line x1="{x:.1f}" y1="{sy}" x2="{x:.1f}" y2="{sy+sh}" stroke="#E5E7EB"/>',
            f'<text class="note" x="{x:.1f}" y="{sy+sh+28}" text-anchor="middle">{tick}</text>',
        ]
    for tick in (1.0, 1.2, 1.4, 1.6):
        y = sy + sh - (tick - 1.0) / 0.6 * sh
        body += [
            f'<line x1="{sx}" y1="{y:.1f}" x2="{sx+sw}" y2="{y:.1f}" stroke="#E5E7EB"/>',
            f'<text class="note" x="{sx-10}" y="{y+4:.1f}" text-anchor="end">{tick:.1f}%</text>',
        ]
    level_colors = {"BA": "#0072B2", "FERC": "#D55E00", "US": "#009E73"}
    for row in all_block:
        factor = float(row["lifecycle_ar5_gwp100_kgco2e_per_mwh"])
        threshold = float(row["critical_equal_half_width_pct"])
        x = sx + sw * factor / 1000
        y = sy + sh - (threshold - 1.0) / 0.6 * sh
        radius = 7 if row["region_level"] == "US" else 4
        body.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{level_colors[str(row["region_level"])]}" opacity="0.82"/>'
        )
    body += [
        '<text class="axis" x="895" y="600" text-anchor="middle">Lifecycle electricity factor (kg CO₂e/MWh)</text>',
        '<text class="axis" x="635" y="330" text-anchor="middle" transform="rotate(-90 635 330)">critical equal half-width</text>',
        '<circle cx="730" cy="630" r="5" fill="#0072B2"/><text class="note" x="743" y="634">BA</text>',
        '<circle cx="805" cy="630" r="5" fill="#D55E00"/><text class="note" x="818" y="634">FERC</text>',
        '<circle cx="895" cy="630" r="6" fill="#009E73"/><text class="note" x="910" y="634">U.S.</text>',
        '<text class="note" x="70" y="660">Bounds are deterministic sets, not probability distributions. Lower thresholds indicate less rank robustness.</text>',
        '<text class="note" x="70" y="686">The grid multiplier is shared; foreground multipliers may differ by technology. No certificate is physical validation.</text>',
    ]
    write_svg(FIGURES / "figure11_standardized_robustness.svg", body)


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
    detailed, summary = historical_technology_results(historical, components)
    national = annual_national_results(factors, components)
    server_records, _ = integrated.boavizta_server_summary()
    stress = server_stress_test(current_states, components, server_records)
    crossover = float(
        next(
            row["crossover_kgco2e_per_mwh"]
            for row in integrated.crossover_rows(components)
            if row["technology_a"] == "Cold plate"
            and row["technology_b"] == "One-phase"
        )
    )
    comparison = method_comparison(components, crossover)
    extrapolation = anchor_extrapolation_diagnostics(historical)
    boundary = boundary_adder_stress(current_states, components)
    functional_unit = functional_unit_sensitivity(historical, components)
    joint = joint_assumption_stress(current_states, factors, components)
    stress_structure = stress_structure_sensitivity(
        current_states, factors, components
    )
    stress_convergence = stress_convergence_diagnostic(
        current_states, factors, components
    )
    pedigree = integrated.pedigree_scores()
    priority = integrated.data_priority(pedigree, components)
    priority_sensitivity = priority_index_sensitivity(priority)
    lifecycle_electricity = lifecycle_electricity_factors(components)
    residual_electricity = lifecycle_electricity_factors(
        components, residual=True
    )
    standardized_robustness = standardized_rank_robustness(
        lifecycle_electricity, components
    )
    national_lifecycle_factor = float(
        next(
            row["lifecycle_ar5_gwp100_kgco2e_per_mwh"]
            for row in lifecycle_electricity
            if row["region_level"] == "US"
        )
    )
    endpoint_method_audit = released_endpoint_method_audit()
    electricity_response = implied_electricity_response_coefficients(
        components, national_lifecycle_factor
    )
    lifecycle_cutoffs = national_lifecycle_cutoff_summary()
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
        "table26_stress_structure_sensitivity.csv": stress_structure,
        "table27_stress_convergence.csv": stress_convergence,
        "table28_lifecycle_electricity_factors.csv": lifecycle_electricity,
        "table29_standardized_rank_robustness.csv": standardized_robustness,
        "table30_released_endpoint_method_audit.csv": endpoint_method_audit,
        "table31_implied_electricity_response.csv": electricity_response,
        "table32_national_lifecycle_cutoffs.csv": lifecycle_cutoffs,
        "table33_residual_electricity_factors.csv": residual_electricity,
    }
    for name, rows in outputs.items():
        write_csv(TABLES / name, rows)
        write_csv(RESULTS / name, rows)
    figure_historical(historical, factors, crossover)
    figure_performance_robustness(summary)
    figure_scope_and_uncertainty(
        extrapolation, boundary, joint, functional_unit
    )
    figure_stress_structure(stress_structure)
    figure_lifecycle_electricity(lifecycle_electricity, crossover)
    figure_standardized_robustness(standardized_robustness)
    for figure_path in sorted(FIGURES.glob("*.svg")):
        normalize_figure_typography(figure_path)
    analysis_code_paths = [
        Path(__file__),
        ROOT / "scripts" / "run_integrated_evidence_analysis.py",
        ROOT / "scripts" / "normalize_figure_typography.py",
        ROOT / "src" / "opendc_lca" / "public_data.py",
        ROOT / "src" / "opendc_lca" / "provenance.py",
    ]
    analysis_output_paths = [
        *(RESULTS / name for name in outputs),
        *(TABLES / name for name in outputs),
        *(FIGURES / f"figure{number}_{stem}.svg" for number, stem in (
            (6, "historical_grid_transition"),
            (7, "performance_robustness"),
            (8, "scope_uncertainty"),
            (9, "stress_structure"),
            (10, "lifecycle_electricity"),
            (11, "standardized_robustness"),
        )),
    ]
    git_command = [
        "git",
        "-c",
        f"safe.directory={ROOT.as_posix()}",
        "-C",
        str(ROOT),
    ]
    git_commit = subprocess.run(
        [*git_command, "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    git_status = subprocess.run(
        [*git_command, "status", "--porcelain=v1"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    analysis_inputs = sorted(
        {
            *(egrid_source(year) for year in FILES),
            integrated.RAW
            / "microsoft-zenodo"
            / "LCA_Tool_w_Raw_&_Normalized_PlusUncertainty&Details.xlsx",
            MICROSOFT_DETAILED_WORKBOOK,
            integrated.RAW / "boavizta" / "boavizta-data-us.csv",
            ELECTRICITY_BASELINE_ZIP,
            IPCC_GWP_ZIP,
        }
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
        "federal_lca_commons_2023_us_lifecycle_ar5_gwp100_kgco2e_per_mwh": (
            national_lifecycle_factor
        ),
        "federal_lca_commons_nonresidual_product_systems": len(
            lifecycle_electricity
        ),
        "federal_lca_commons_residual_product_systems": len(
            residual_electricity
        ),
        "federal_lca_commons_2023_us_residual_ar5_gwp100_kgco2e_per_mwh": next(
            row["lifecycle_ar5_gwp100_kgco2e_per_mwh"]
            for row in residual_electricity
            if row["region_level"] == "US"
        ),
        "federal_lca_commons_product_systems_below_numerical_crossover": sum(
            bool(row["below_cp_one_phase_numerical_crossover"])
            for row in lifecycle_electricity
        ),
        "exact_2023_boundary_adder_to_remove_cp_advantage_kgco2e_per_mwh": (
            boundary[0][
                "exact_adder_to_remove_all_cp_advantage_kgco2e_per_mwh"
            ]
        ),
        "analysis_inputs": [
            {
                "local_path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in analysis_inputs
        ],
        "execution_manifest": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "git_commit": git_commit,
            "git_dirty": bool(git_status),
            "git_status_sha256": hashlib.sha256(
                git_status.encode("utf-8")
            ).hexdigest(),
            "code": [
                {
                    "local_path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
                for path in analysis_code_paths
            ],
            "outputs": [
                {
                    "local_path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
                for path in analysis_output_paths
            ],
            "joint_stress_base_seed": JOINT_STRESS_SEED,
            "iterations_per_design": 20000,
        },
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
            "stress_structure_sensitivity": (
                "triangular-marginal block and Gaussian-copula dependence "
                "diagnostic; no empirical correlation or probability"
            ),
            "stress_convergence": (
                "nested 5,000, 20,000, and 80,000 draw numerical check; "
                "Monte Carlo precision is not epistemic uncertainty"
            ),
            "boundary_mismatch": (
                "transparent additive stress; not an upstream inventory estimate"
            ),
            "lifecycle_electricity": (
                "Federal LCA Commons 2023 consumption-mix product systems "
                "calculated with the repository's IPCC AR5-100 method; "
                "unlinked technosphere inputs are reported as cutoffs"
            ),
            "standardized_rank_robustness": (
                "exact equal-relative-width deterministic uncertainty sets; "
                "not probability or physical validation"
            ),
            "released_endpoint_method_identity": (
                "published article reports AR5 GWP100; archived detailed "
                "workbook provides numeric endpoints in GTP100 cells while "
                "GWP100 cells are blank, and comparative use-phase formulas "
                "reference the blank F29 cells"
            ),
        },
    }
    (RESULTS / "analysis-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
