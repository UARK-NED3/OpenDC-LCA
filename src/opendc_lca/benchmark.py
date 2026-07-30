"""Benchmark evidence, critical-review, and citable-release packaging."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from .models import ValidationError


BENCHMARK_REQUIRED = {
    "title",
    "version",
    "creators",
    "license",
    "description",
    "functional_unit",
    "system_boundary",
    "evidence_status",
    "files",
}
REVIEW_REQUIRED = {
    "review_type",
    "reviewers",
    "scope",
    "findings",
    "disposition",
    "completed_at",
}


def _load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Cannot read JSON record {source}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"JSON record must be an object: {source}")
    return data


def validate_benchmark_manifest(
    manifest_path: str | Path,
    *,
    verify_files: bool = True,
) -> dict[str, Any]:
    """Validate a benchmark manifest and optionally verify every checksum."""
    source = Path(manifest_path)
    data = _load_json(source)
    missing = BENCHMARK_REQUIRED - data.keys()
    if missing:
        raise ValidationError(
            "Benchmark manifest is missing: " + ", ".join(sorted(missing))
        )
    if data["evidence_status"] not in {
        "synthetic", "experimental_unreviewed", "reviewed"
    }:
        raise ValidationError(
            "evidence_status must be synthetic, experimental_unreviewed, or reviewed"
        )
    if not isinstance(data["creators"], list) or not data["creators"]:
        raise ValidationError("Benchmark manifest requires at least one creator")
    if not isinstance(data["files"], list) or not data["files"]:
        raise ValidationError("Benchmark manifest requires at least one file")
    seen: set[str] = set()
    for item in data["files"]:
        if not isinstance(item, dict):
            raise ValidationError("Each benchmark file record must be an object")
        required = {"path", "role", "sha256"}
        absent = required - item.keys()
        if absent:
            raise ValidationError(
                "Benchmark file record is missing: "
                + ", ".join(sorted(absent))
            )
        relative = str(item["path"])
        if relative in seen or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValidationError(f"Unsafe or duplicate benchmark path: {relative}")
        seen.add(relative)
        if verify_files:
            file_path = source.parent / relative
            if not file_path.is_file():
                raise ValidationError(f"Benchmark file not found: {relative}")
            digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if digest != item["sha256"]:
                raise ValidationError(
                    f"Checksum mismatch for benchmark file: {relative}"
                )
    return data


def validate_review_record(path: str | Path) -> dict[str, Any]:
    """Validate a completed critical-review record without inventing approval."""
    data = _load_json(path)
    missing = REVIEW_REQUIRED - data.keys()
    if missing:
        raise ValidationError(
            "Review record is missing: " + ", ".join(sorted(missing))
        )
    if data["review_type"] not in {"independent", "independent_panel"}:
        raise ValidationError("Review type must be independent or independent_panel")
    if not isinstance(data["reviewers"], list) or not data["reviewers"]:
        raise ValidationError("Review record requires at least one named reviewer")
    if data["disposition"] not in {
        "approved", "approved_with_conditions", "revision_required", "rejected"
    }:
        raise ValidationError("Unknown review disposition")
    return data


def package_benchmark_release(
    manifest_path: str | Path,
    destination: str | Path,
    *,
    review_path: str | Path | None = None,
) -> Path:
    """Create a deterministic citable ZIP after evidence and review validation."""
    manifest_file = Path(manifest_path)
    manifest = validate_benchmark_manifest(manifest_file)
    review = None
    if manifest["evidence_status"] == "reviewed":
        if review_path is None:
            raise ValidationError(
                "A reviewed benchmark requires a completed critical-review record"
            )
        review = validate_review_record(review_path)
        if review["disposition"] not in {"approved", "approved_with_conditions"}:
            raise ValidationError(
                "Reviewed benchmark cannot be packaged with this disposition"
            )
    destination_path = Path(destination)
    with ZipFile(destination_path, "w", ZIP_DEFLATED) as archive:
        archive.write(manifest_file, "benchmark-manifest.json")
        if review_path is not None:
            archive.write(Path(review_path), "critical-review.json")
        for item in sorted(manifest["files"], key=lambda value: value["path"]):
            archive.write(
                manifest_file.parent / item["path"],
                f"data/{item['path']}",
            )
        archive.writestr("datapackage.json", json.dumps({
            "name": manifest["title"],
            "version": manifest["version"],
            "description": manifest["description"],
            "licenses": [{"name": manifest["license"]}],
            "contributors": manifest["creators"],
            "resources": manifest["files"],
            "opendc_lca": {
                "functional_unit": manifest["functional_unit"],
                "system_boundary": manifest["system_boundary"],
                "evidence_status": manifest["evidence_status"],
                "critical_review_included": review is not None,
                "doi": manifest.get("doi"),
            },
        }, indent=2))
    return destination_path
