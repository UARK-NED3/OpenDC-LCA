"""Deterministic file-level provenance utilities for local research inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path, *, block_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 digest of *path* without loading it into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path, *, root: Path, source_root: Path) -> dict[str, object]:
    """Create one stable manifest record for a provider-native file."""
    relative = path.relative_to(root)
    source_relative = path.relative_to(source_root)
    return {
        "source_group": source_relative.parts[0],
        "local_path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def build_file_manifest(
    source_root: Path,
    *,
    root: Path,
    paths: Iterable[Path] | None = None,
) -> list[dict[str, object]]:
    """Hash all files below *source_root* or an explicit set of input files."""
    selected = paths if paths is not None else source_root.rglob("*")
    files = sorted(path for path in selected if path.is_file())
    return [
        file_record(path, root=root, source_root=source_root) for path in files
    ]


def write_file_manifest(path: Path, records: list[dict[str, object]]) -> None:
    """Write a newline-stable JSON manifest."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def manifest_index(
    records: Iterable[dict[str, object]],
) -> dict[str, dict[str, object]]:
    """Index manifest rows by repository-relative path and reject duplicates."""
    output: dict[str, dict[str, object]] = {}
    for record in records:
        local_path = str(record["local_path"])
        if local_path in output:
            raise ValueError(f"Duplicate manifest path: {local_path}")
        output[local_path] = record
    return output


def verify_manifest_records(
    records: Iterable[dict[str, object]],
    *,
    root: Path,
    required_paths: Iterable[Path] | None = None,
    verify_hashes: bool = True,
) -> list[str]:
    """Return human-readable errors for missing, stale, or untracked inputs."""
    index = manifest_index(records)
    errors: list[str] = []
    selected = (
        required_paths
        if required_paths is not None
        else (root / key for key in index)
    )
    for path in selected:
        local_path = path.relative_to(root).as_posix()
        record = index.get(local_path)
        if record is None:
            errors.append(f"missing manifest record: {local_path}")
            continue
        if not path.is_file():
            errors.append(f"missing local file: {local_path}")
            continue
        actual_size = path.stat().st_size
        if int(record["bytes"]) != actual_size:
            errors.append(
                f"size mismatch: {local_path} ({record['bytes']} != {actual_size})"
            )
        if verify_hashes:
            actual_hash = sha256_file(path)
            if str(record["sha256"]) != actual_hash:
                errors.append(f"sha256 mismatch: {local_path}")
    return errors
