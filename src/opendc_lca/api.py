"""Stable JSON-compatible API for OpenDC-LCA 1.0."""

from __future__ import annotations

from typing import Any

from .audit import audit
from .engine import analyze
from .io import load_scenario_data
from .performance import load_performance_map_text, summarize_performance


def validate_scenario(data: object) -> dict[str, Any]:
    scenario = load_scenario_data(data)
    return {
        "valid": True,
        "name": scenario.name,
        "cooling_architecture": scenario.cooling_architecture,
        "source_digest_sha256": scenario.source_digest_sha256,
    }


def analyze_scenario(data: object) -> dict[str, Any]:
    scenario = load_scenario_data(data)
    findings = audit(scenario)
    return {
        "result": analyze(scenario).as_dict(),
        "audit": [finding.as_dict() for finding in findings],
        "comparative_claim_blocked": any(
            finding.severity == "blocker" for finding in findings
        ),
    }


def audit_scenario(data: object) -> dict[str, Any]:
    findings = audit(load_scenario_data(data))
    return {
        "findings": [finding.as_dict() for finding in findings],
        "has_blocker": any(finding.severity == "blocker" for finding in findings),
    }


def summarize_performance_csv(text: str) -> dict[str, Any]:
    points = load_performance_map_text(text)
    return {
        "summary": summarize_performance(points).as_dict(),
        "evidence_notice": (
            "A performance summary is not authorization for a comparative "
            "environmental claim; review provenance and evidence status."
        ),
    }
