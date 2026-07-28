"""Scenario loading helpers."""

from __future__ import annotations

import json
import hashlib
from dataclasses import replace
from pathlib import Path

from .models import Scenario, ValidationError


def load_scenario(path: str | Path) -> Scenario:
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"Scenario not found: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {source}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError("Scenario root must be a JSON object")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return replace(
        Scenario.from_dict(data),
        source_digest_sha256=hashlib.sha256(canonical).hexdigest(),
    )
