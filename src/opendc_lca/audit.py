"""Scientific-quality checks beyond structural scenario validation."""

from __future__ import annotations

from dataclasses import dataclass
import json

from .models import Scenario


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }


def audit(scenario: Scenario) -> list[Finding]:
    """Return deterministic scientific-quality findings for a scenario."""
    findings: list[Finding] = []
    weak_sources = []
    unquantified_sources = []
    insufficient_confidential_review = []
    for source in scenario.data_sources:
        source_text = f"{source.source_type} {source.quality}".lower()
        if any(word in source_text for word in ("synthetic", "illustrative", "test")):
            weak_sources.append(source.id)
        if source.uncertainty["distribution"] == "not_quantified":
            unquantified_sources.append(source.id)
            findings.append(Finding(
                "warning",
                "UNCERTAINTY_NOT_QUANTIFIED",
                f"Data source '{source.id}' has no quantified uncertainty.",
            ))
        if "no external source" in source.citation.lower():
            findings.append(Finding(
                "warning",
                "NO_EXTERNAL_CITATION",
                f"Data source '{source.id}' is not externally supported.",
            ))
        if any(
            "replace with" in value.lower()
            for value in (source.id, source.title, source.citation)
        ):
            findings.append(Finding(
                "warning",
                "SOURCE_PLACEHOLDER_NOT_REPLACED",
                f"Data source '{source.id}' still contains template placeholder text.",
            ))
        if source.review_status == "unreviewed":
            findings.append(Finding(
                "warning",
                "SOURCE_UNREVIEWED",
                f"Data source '{source.id}' has not been reviewed.",
            ))
        if (
            source.confidentiality != "public"
            and source.review_status != "independently_reviewed"
        ):
            insufficient_confidential_review.append(source.id)

    if scenario.study.comparative_assertion and weak_sources:
        findings.append(Finding(
            "blocker",
            "UNSUPPORTED_COMPARATIVE_ASSERTION",
            "Comparative assertions cannot rely on synthetic, illustrative, "
            f"or test data sources: {', '.join(weak_sources)}.",
        ))
    if scenario.study.comparative_assertion and unquantified_sources:
        findings.append(Finding(
            "blocker",
            "COMPARISON_REQUIRES_QUANTIFIED_UNCERTAINTY",
            "Public comparative assertions require quantified uncertainty for: "
            + ", ".join(unquantified_sources) + ".",
        ))
    if (
        scenario.study.comparative_assertion
        and scenario.study.critical_review_status != "independent_panel"
    ):
        findings.append(Finding(
            "blocker",
            "COMPARISON_REQUIRES_REVIEW_PANEL",
            "A public comparative assertion requires an independent critical "
            "review panel before release.",
        ))
    if scenario.study.comparative_assertion and insufficient_confidential_review:
        findings.append(Finding(
            "blocker",
            "CONFIDENTIAL_DATA_REQUIRES_INDEPENDENT_REVIEW",
            "Confidential or aggregated-confidential sources require independent "
            "review: " + ", ".join(insufficient_confidential_review) + ".",
        ))
    required_lineage = {
        "it_capacity_kw",
        "capacity_factor",
        "pue",
        "facility_lifetime_years",
        "onsite_water_l_per_kwh_it",
        "grid",
        *(f"component:{component.name}" for component in scenario.components),
    }
    if scenario.fluid is not None:
        required_lineage.add(f"fluid:{scenario.fluid.name}")
    missing_lineage = sorted(required_lineage - set(scenario.input_source_map))
    if scenario.study.comparative_assertion and missing_lineage:
        findings.append(Finding(
            "blocker",
            "COMPARISON_REQUIRES_FIELD_LEVEL_LINEAGE",
            "Public comparative assertions require field-level source mapping "
            "for: " + ", ".join(missing_lineage) + ".",
        ))
    methods = (
        scenario.study.ghg_method,
        scenario.study.primary_energy_method,
        scenario.study.water_method,
    )
    if scenario.study.comparative_assertion and any(
        "illustrative" in method.lower() for method in methods
    ):
        findings.append(Finding(
            "blocker",
            "COMPARISON_REQUIRES_CANONICAL_IMPACT_METHODS",
            "Illustrative impact methods cannot support a public comparative "
            "assertion.",
        ))

    if (
        scenario.study.system_boundary == "custom"
        and scenario.study.boundary_definition is None
    ):
        findings.append(Finding(
            "blocker" if scenario.study.comparative_assertion else "warning",
            "CUSTOM_BOUNDARY_REQUIRES_REVIEW",
            "A custom system boundary requires a complete boundary diagram "
            "and inclusion/exclusion table.",
        ))

    if scenario.study.replacement_model == "reliability":
        findings.append(Finding(
            "warning",
            "RELIABILITY_EXPECTATION_MODEL_LIMITS",
            "Reliability-driven replacements are expected values from independent "
            "component renewal models. Redundancy, common-cause failures, repair "
            "queues, workload migration, and time-varying damage are not modeled.",
        ))

    if not scenario.components:
        findings.append(Finding(
            "warning",
            "EQUIPMENT_INVENTORY_OMITTED",
            "No equipment inventory is included. Results represent operational "
            "electricity and on-site water only, plus any declared fluid.",
        ))
    if (
        "immersion" in scenario.cooling_architecture.lower()
        and scenario.fluid is None
    ):
        findings.append(Finding(
            "warning",
            "IMMERSION_FLUID_OMITTED",
            "The immersion scenario has no fluid inventory, loss rate, direct "
            "GWP, or end-of-life treatment.",
        ))

    has_credit = any(
        component.end_of_life.ghg_kgco2e < 0
        or component.end_of_life.primary_energy_mj < 0
        or component.end_of_life.blue_water_l < 0
        for component in scenario.components
    )
    allocation = scenario.study.allocation_method.lower()
    if has_credit and not any(
        word in allocation for word in ("credit", "substitution", "recycl")
    ):
        findings.append(Finding(
            "warning",
            "RECOVERY_CREDIT_UNEXPLAINED",
            "Negative end-of-life impacts are present, but the allocation "
            "method does not identify recovery, recycling, or substitution.",
        ))

    if not findings:
        findings.append(Finding(
            "info",
            "NO_AUTOMATED_FINDINGS",
            "No automated quality findings. This is not a critical review.",
        ))
    return findings


def audit_comparison(scenarios: list[Scenario]) -> list[Finding]:
    """Audit cross-scenario comparability and scenario-level claim blockers."""
    if len(scenarios) < 2:
        raise ValueError("Comparison audit requires at least two scenarios")
    findings: list[Finding] = []
    study_fields = (
        "functional_unit",
        "system_boundary",
        "electricity_accounting",
        "water_metric",
        "allocation_method",
        "ghg_method",
        "primary_energy_method",
        "water_method",
        "replacement_model",
    )
    for field_name in study_fields:
        values = {
            str(getattr(scenario.study, field_name)) for scenario in scenarios
        }
        if len(values) > 1:
            findings.append(Finding(
                "blocker",
                "INCOMPATIBLE_" + field_name.upper(),
                f"Compared scenarios do not share {field_name}: "
                + "; ".join(
                    f"{scenario.name}={getattr(scenario.study, field_name)}"
                    for scenario in scenarios
                )
                + ".",
            ))
    boundary_definitions = {
        json.dumps(
            scenario.study.boundary_definition,
            sort_keys=True,
            separators=(",", ":"),
        )
        for scenario in scenarios
        if scenario.study.system_boundary == "custom"
    }
    if len(boundary_definitions) > 1:
        findings.append(Finding(
            "blocker",
            "INCOMPATIBLE_CUSTOM_BOUNDARY_DEFINITION",
            "Compared custom-boundary scenarios do not share the same explicit "
            "inclusion, exclusion, and rationale record.",
        ))
    assertion_flags = {scenario.study.comparative_assertion for scenario in scenarios}
    if len(assertion_flags) > 1:
        findings.append(Finding(
            "blocker",
            "INCONSISTENT_COMPARATIVE_ASSERTION_INTENT",
            "All compared scenarios must declare the same comparative-assertion intent.",
        ))
    for scenario in scenarios:
        for finding in audit(scenario):
            if finding.severity == "blocker":
                findings.append(Finding(
                    "blocker",
                    f"SCENARIO_{finding.code}",
                    f"Scenario '{scenario.name}': {finding.message}",
                ))
    if not findings:
        findings.append(Finding(
            "info",
            "COMPARISON_METADATA_COMPATIBLE",
            "Automated metadata checks found no cross-scenario mismatch or "
            "declared claim blocker. This does not verify source truth, model "
            "validity, or constitute critical review.",
        ))
    return findings
