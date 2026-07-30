"""Practitioner-facing study preparation and result interpretation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit import audit
from .engine import analyze
from .io import load_scenario_data
from .models import ValidationError


CAPABILITIES = {
    "intended_use": [
        "screen annual GHG, primary-energy, and blue-water burdens",
        "compare contribution hotspots across consistently defined scenarios",
        "annualize equipment, fluid, maintenance, and replacement burdens",
        "record provenance and expose evidence limitations",
    ],
    "required_inputs": {
        "facility": [
            "IT capacity (kW)",
            "average IT utilization or capacity factor (0-1)",
            "PUE",
            "facility study life (years)",
            "on-site cooling-water consumption (L/kWh IT)",
        ],
        "electricity": [
            "GHG factor (kg CO2e/kWh)",
            "primary-energy factor (MJ/kWh)",
            "blue-water factor (L/kWh)",
        ],
        "equipment_optional_for_operational_screening": [
            "aggregate equipment production impacts",
            "equipment quantity and service life",
        ],
        "evidence": [
            "source title and citation",
            "geography and reference year",
            "review status and uncertainty status",
        ],
    },
    "outputs": [
        "annual IT and facility electricity",
        "annual and per-IT-MWh GHG, primary energy, and blue water",
        "contribution breakdown",
        "scientific audit findings",
        "automated evidence classification",
        "explicit next-data requirements",
        "machine-readable scenario digest and results",
    ],
    "not_modeled": [
        "water scarcity without an externally characterized factor",
        "hourly or marginal grid effects in a static study",
        "workload output or useful computation",
        "redundancy and repair queues",
        "automatic completion of background LCA product systems",
    ],
}


def practitioner_input_template() -> dict[str, Any]:
    """Return an editable, deliberately conservative screening template."""
    return {
        "study_name": "My data-center cooling screening",
        "cooling_architecture": "direct-to-chip",
        "geography": "Arkansas, United States",
        "reference_year": 2023,
        "it_capacity_kw": 1000.0,
        "capacity_factor": 0.75,
        "pue": 1.20,
        "facility_lifetime_years": 15.0,
        "onsite_water_l_per_kwh_it": 0.0,
        "grid_ghg_kgco2e_per_kwh": 0.4529,
        "grid_primary_energy_mj_per_kwh": 6.0,
        "grid_blue_water_l_per_kwh": 0.30,
        "equipment": {
            "include": False,
            "name": "Cooling-system equipment",
            "quantity": 1.0,
            "service_life_years": 15.0,
            "production_ghg_kgco2e": 0.0,
            "production_primary_energy_mj": 0.0,
            "production_blue_water_l": 0.0,
            "end_of_life_ghg_kgco2e": 0.0,
            "end_of_life_primary_energy_mj": 0.0,
            "end_of_life_blue_water_l": 0.0,
        },
        "source": {
            "id": "replace-with-source-id",
            "title": "Replace with the source of these inputs",
            "citation": "Replace with URL, report, dataset, or internal record",
            "license": "not assessed",
            "quality": "screening; practitioner supplied",
            "uncertainty": "not_quantified",
            "review_status": "unreviewed",
            "confidentiality": "public",
        },
    }


def _number(data: dict[str, Any], key: str, *, minimum: float = 0.0) -> float:
    value = data.get(key)
    if isinstance(value, bool):
        raise ValidationError(f"{key} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{key} must be numeric") from exc
    if result < minimum:
        raise ValidationError(f"{key} must be at least {minimum}")
    return result


def prepare_practitioner_scenario(data: object) -> dict[str, Any]:
    """Expand a compact practitioner input into the governed scenario schema."""
    if not isinstance(data, dict):
        raise ValidationError("Practitioner input must be a JSON object")
    capacity_factor = _number(data, "capacity_factor")
    if not 0 < capacity_factor <= 1:
        raise ValidationError("capacity_factor must be greater than 0 and no more than 1")
    pue = _number(data, "pue", minimum=1.0)
    source = data.get("source")
    if not isinstance(source, dict):
        raise ValidationError("source must be a JSON object")
    for field in ("id", "title", "citation"):
        if not str(source.get(field, "")).strip():
            raise ValidationError(f"source.{field} is required")
    uncertainty_name = str(source.get("uncertainty", "not_quantified"))
    uncertainty = {
        "distribution": uncertainty_name,
        "parameters": {},
        "notes": (
            "No quantitative uncertainty supplied through practitioner input."
            if uncertainty_name == "not_quantified"
            else "Distribution declared in practitioner input; add parameters "
            "through the full scenario or uncertainty schema."
        ),
    }
    components: list[dict[str, Any]] = []
    equipment = data.get("equipment", {})
    if not isinstance(equipment, dict):
        raise ValidationError("equipment must be a JSON object")
    if equipment.get("include") is True:
        components.append({
            "name": str(equipment.get("name", "Cooling-system equipment")),
            "quantity": _number(equipment, "quantity", minimum=0.000001),
            "service_life_years": _number(
                equipment, "service_life_years", minimum=0.000001
            ),
            "production": {
                "ghg_kgco2e": _number(equipment, "production_ghg_kgco2e"),
                "primary_energy_mj": _number(
                    equipment, "production_primary_energy_mj"
                ),
                "blue_water_l": _number(equipment, "production_blue_water_l"),
            },
            "end_of_life": {
                "ghg_kgco2e": _number(
                    equipment, "end_of_life_ghg_kgco2e", minimum=-1e100
                ),
                "primary_energy_mj": _number(
                    equipment,
                    "end_of_life_primary_energy_mj",
                    minimum=-1e100,
                ),
                "blue_water_l": _number(
                    equipment, "end_of_life_blue_water_l", minimum=-1e100
                ),
            },
        })
    scenario = {
        "name": str(data.get("study_name", "")).strip(),
        "cooling_architecture": str(
            data.get("cooling_architecture", "")
        ).strip(),
        "study": {
            "functional_unit": "it_mwh",
            "system_boundary": "cooling_system_cradle_to_grave",
            "electricity_accounting": "location_based",
            "water_metric": "blue water consumption; not scarcity characterized",
            "allocation_method": "cut-off; no recovery credit unless declared",
            "intended_use": "practitioner screening and data-gap identification",
            "comparative_assertion": False,
            "ghg_method": "source-declared GWP100 factors",
            "primary_energy_method": "source-declared primary-energy factors",
            "water_method": "source-declared blue-water consumption factors",
            "replacement_model": "discrete",
            "critical_review_status": "planned",
        },
        "it_capacity_kw": _number(data, "it_capacity_kw", minimum=0.000001),
        "capacity_factor": capacity_factor,
        "pue": pue,
        "facility_lifetime_years": _number(
            data, "facility_lifetime_years", minimum=0.000001
        ),
        "onsite_water_l_per_kwh_it": _number(
            data, "onsite_water_l_per_kwh_it"
        ),
        "grid": {
            "ghg_kgco2e_per_kwh": _number(
                data, "grid_ghg_kgco2e_per_kwh"
            ),
            "primary_energy_mj_per_kwh": _number(
                data, "grid_primary_energy_mj_per_kwh"
            ),
            "blue_water_l_per_kwh": _number(
                data, "grid_blue_water_l_per_kwh"
            ),
        },
        "components": components,
        "data_sources": [{
            "id": str(source["id"]),
            "title": str(source["title"]),
            "source_type": "practitioner supplied",
            "citation": str(source["citation"]),
            "license": str(source.get("license", "not assessed")),
            "geography": str(data.get("geography", "not specified")),
            "reference_year": int(data.get("reference_year", 0)),
            "quality": str(source.get("quality", "screening")),
            "uncertainty": uncertainty,
            "review_status": str(source.get("review_status", "unreviewed")),
            "confidentiality": str(source.get("confidentiality", "public")),
        }],
        "metadata": {
            "input_profile": "practitioner-screening-v1",
            "equipment_inventory_included": bool(components),
            "interpretation": (
                "Operational-plus-equipment screening"
                if components
                else "Operational screening only; equipment and fluid omitted"
            ),
        },
    }
    load_scenario_data(scenario)
    return scenario


def interpret_practitioner_scenario(data: object) -> dict[str, Any]:
    """Analyze a full scenario and return plain-language evidence guidance."""
    scenario = load_scenario_data(data)
    result = analyze(scenario)
    findings = audit(scenario)
    blockers = [item for item in findings if item.severity == "blocker"]
    warnings = [item for item in findings if item.severity == "warning"]
    source_types = " ".join(
        f"{source.source_type} {source.quality}" for source in scenario.data_sources
    ).lower()
    if blockers:
        level = "blocked comparative claim"
    elif (
        scenario.study.critical_review_status == "independent_panel"
        and all(
            source.review_status == "independently_reviewed"
            for source in scenario.data_sources
        )
        and not warnings
    ):
        level = "decision-grade candidate; confirm critical-review scope"
    elif any(word in source_types for word in ("synthetic", "illustrative")):
        level = "demonstration"
    else:
        level = "screening"
    next_data: list[str] = []
    if not scenario.components:
        next_data.append(
            "Add cooling-system equipment quantities, production impacts, "
            "service lives, and end-of-life assumptions."
        )
    if scenario.fluid is None and "immersion" in scenario.cooling_architecture.lower():
        next_data.append(
            "Add fluid charge, production factor, annual loss, direct GWP, "
            "and end-of-life treatment."
        )
    if any(
        source.uncertainty["distribution"] == "not_quantified"
        for source in scenario.data_sources
    ):
        next_data.append("Quantify input uncertainty and relevant correlations.")
    if any(
        source.review_status != "independently_reviewed"
        for source in scenario.data_sources
    ):
        next_data.append("Review the foreground and background data sources.")
    next_data.extend([
        "Use hourly workload, weather, and grid factors if temporal variation "
        "could change the decision.",
        "Add watershed scarcity characterization before making a water-impact claim.",
    ])
    annual_it_mwh = result.annual_it_energy_kwh / 1000
    return {
        "evidence_level": level,
        "comparative_claim_allowed": not blockers
        and scenario.study.comparative_assertion,
        "interpretation_scope": scenario.metadata.get(
            "interpretation", "Full scenario supplied"
        ),
        "key_outputs": {
            "annual_it_energy_mwh": annual_it_mwh,
            "annual_facility_energy_mwh": result.annual_facility_energy_kwh / 1000,
            "annual_ghg_kgco2e": result.annual_impacts.ghg_kgco2e,
            "annual_primary_energy_mj": result.annual_impacts.primary_energy_mj,
            "annual_blue_water_l": result.annual_impacts.blue_water_l,
            "ghg_kgco2e_per_it_mwh": result.per_it_mwh.ghg_kgco2e,
            "primary_energy_mj_per_it_mwh": result.per_it_mwh.primary_energy_mj,
            "blue_water_l_per_it_mwh": result.per_it_mwh.blue_water_l,
        },
        "contributions": {
            name: impacts.as_dict()
            for name, impacts in result.contributions.items()
        },
        "audit_findings": [item.as_dict() for item in findings],
        "next_data_required": next_data,
        "model_version": result.model_version,
        "scenario_digest_sha256": result.scenario_digest_sha256,
        "capability_boundary": CAPABILITIES["not_modeled"],
    }


def write_practitioner_report(
    scenario_data: object, output_dir: str | Path
) -> dict[str, Path]:
    """Write concise JSON and Markdown practitioner outputs."""
    scenario = load_scenario_data(scenario_data)
    summary = interpret_practitioner_scenario(scenario_data)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "practitioner-results.json"
    report_path = destination / "PRACTITIONER_REPORT.md"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    output = summary["key_outputs"]
    findings = summary["audit_findings"]
    finding_lines = "\n".join(
        f"- **{item['severity'].upper()} — {item['code']}:** {item['message']}"
        for item in findings
    )
    next_lines = "\n".join(
        f"- {item}" for item in summary["next_data_required"]
    )
    report_path.write_text(
        f"""# OpenDC-LCA practitioner screening report

## Decision status

- Study: **{scenario.name}**
- Cooling architecture: **{scenario.cooling_architecture}**
- Evidence level: **{summary['evidence_level']}**
- Interpretation scope: **{summary['interpretation_scope']}**
- Public comparative claim allowed: **{'yes' if summary['comparative_claim_allowed'] else 'no'}**

## What the model calculated

| Output | Result |
|---|---:|
| Annual IT electricity | {output['annual_it_energy_mwh']:,.1f} MWh |
| Annual facility electricity | {output['annual_facility_energy_mwh']:,.1f} MWh |
| Annual GHG | {output['annual_ghg_kgco2e']:,.1f} kg CO2e |
| GHG intensity | {output['ghg_kgco2e_per_it_mwh']:,.3f} kg CO2e/IT MWh |
| Primary-energy intensity | {output['primary_energy_mj_per_it_mwh']:,.3f} MJ/IT MWh |
| Blue-water intensity | {output['blue_water_l_per_it_mwh']:,.3f} L/IT MWh |

These results use one MWh delivered to IT equipment as the functional unit.
They are annual screening indicators, not proof that the modeled architecture
is preferable to another design.

## Scientific audit

{finding_lines}

## Data needed for stronger interpretation

{next_lines}

## Reproducibility

- Model version: `{summary['model_version']}`
- Scenario SHA-256: `{summary['scenario_digest_sha256']}`
- Machine-readable result: [`practitioner-results.json`](practitioner-results.json)
""",
        encoding="utf-8",
    )
    return {"report": report_path, "results": json_path}
