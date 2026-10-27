"""Evidence-map and archetype-contract controls for transferable studies.

These utilities intentionally distinguish an unavailable or unreviewed record
from evidence that is known to be absent.  A source map is a screening aid. It
does not determine the quality of the underlying published science.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .models import ValidationError


REQUIRED_EVIDENCE_COLUMNS = {
    "study_key",
    "citation_number",
    "study_scope",
    "functional_unit_status",
    "system_boundary_status",
    "cooling_performance_status",
    "numeric_artifact_status",
    "lcai_method_status",
    "workload_equivalence_status",
    "transferability_status",
    "audit_scope",
}
STATUS_VALUES = {"documented", "unresolved", "not_audited", "not_applicable"}
TRANSFERABILITY_VALUES = {"screening_only", "numeric_transfer_blocked"}


def load_evidence_map(path: str | Path) -> list[dict[str, str]]:
    """Load a source map and enforce declared audit-state vocabulary."""
    source = Path(path)
    try:
        with source.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except OSError as exc:
        raise ValidationError(f"Cannot read evidence map {source}: {exc}") from exc
    if not rows:
        raise ValidationError("Evidence map must contain at least one study")
    fields = set(rows[0])
    missing = REQUIRED_EVIDENCE_COLUMNS - fields
    if missing:
        raise ValidationError(
            "Evidence map is missing: " + ", ".join(sorted(missing))
        )
    keys: set[str] = set()
    for row in rows:
        key = row["study_key"].strip()
        if not key or key in keys:
            raise ValidationError(f"Evidence map has a blank or duplicate study key: {key!r}")
        keys.add(key)
        for column in (
            "functional_unit_status",
            "system_boundary_status",
            "cooling_performance_status",
            "numeric_artifact_status",
            "lcai_method_status",
            "workload_equivalence_status",
        ):
            if row[column] not in STATUS_VALUES:
                raise ValidationError(f"Unknown {column} value for {key}: {row[column]}")
        if row["transferability_status"] not in TRANSFERABILITY_VALUES:
            raise ValidationError(
                f"Unknown transferability status for {key}: "
                f"{row['transferability_status']}"
            )
    return rows


def evidence_map_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    """Summarize a rapid evidence map without turning it into a quality score."""
    numeric_ready = [
        row
        for row in rows
        if all(
            row[field] == "documented"
            for field in (
                "functional_unit_status",
                "system_boundary_status",
                "cooling_performance_status",
                "numeric_artifact_status",
                "lcai_method_status",
                "workload_equivalence_status",
            )
        )
    ]
    return {
        "studies_screened": len(rows),
        "source_archives_audited": sum(
            row["numeric_artifact_status"] == "documented" for row in rows
        ),
        "records_not_audited_beyond_article_level": sum(
            row["audit_scope"] == "article_level_only" for row in rows
        ),
        "numerically_transferable_records": len(numeric_ready),
        "records_blocked_for_numeric_transfer": sum(
            row["transferability_status"] == "numeric_transfer_blocked"
            for row in rows
        ),
        "interpretation": (
            "This rapid map records what this repository audited. It does not "
            "claim that unreviewed studies lack a public artifact or that a "
            "documented study is scientifically valid for another facility."
        ),
    }
