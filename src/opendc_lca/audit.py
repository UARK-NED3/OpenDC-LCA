"""Scientific-quality checks beyond structural scenario validation."""

from __future__ import annotations

from dataclasses import dataclass

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
    for source in scenario.data_sources:
        source_text = f"{source.source_type} {source.quality}".lower()
        if any(word in source_text for word in ("synthetic", "illustrative", "test")):
            weak_sources.append(source.id)
        if source.uncertainty["distribution"] == "not_quantified":
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

    if scenario.study.comparative_assertion and weak_sources:
        findings.append(Finding(
            "blocker",
            "UNSUPPORTED_COMPARATIVE_ASSERTION",
            "Comparative assertions cannot rely on synthetic, illustrative, "
            f"or test data sources: {', '.join(weak_sources)}.",
        ))

    if scenario.study.system_boundary == "custom":
        findings.append(Finding(
            "warning",
            "CUSTOM_BOUNDARY_REQUIRES_REVIEW",
            "A custom system boundary requires a complete boundary diagram "
            "and inclusion/exclusion table.",
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
