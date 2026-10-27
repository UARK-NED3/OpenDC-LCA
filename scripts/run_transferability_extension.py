#!/usr/bin/env python3
"""Build the rapid evidence map and record reference-model execution status."""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendc_lca.transferability import evidence_map_summary, load_evidence_map  # noqa: E402


SOURCE = ROOT / "data" / "derived" / "transferability_evidence_map.csv"
CONTRACT = ROOT / "data" / "derived" / "energyplus_archetype_contract.json"
TABLE = ROOT / "paper" / "tables" / "table35_transferability_evidence_map.csv"
FIGURE = ROOT / "paper" / "figures" / "figure12_transferability_evidence_map.svg"
RESULTS = ROOT / "results" / "transferability-extension"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_svg(rows: list[dict[str, str]]) -> str:
    """Make a title-free Arial matrix for the manuscript body."""
    fields = [
        (("Functional", "unit"), "functional_unit_status"),
        (("System", "boundary"), "system_boundary_status"),
        (("Cooling", "data"), "cooling_performance_status"),
        (("Numeric", "archive"), "numeric_artifact_status"),
        (("LCIA", "identity"), "lcai_method_status"),
        (("Service", "equivalence"), "workload_equivalence_status"),
    ]
    width, height = 1060, 370
    left, top, cell_w, cell_h = 270, 104, 122, 48
    labels = {
        "alissa_2025": "Alissa et al. [14,15]",
        "isler_kaya_2023": "Isler-Kaya and Karaosmanoglu [12]",
        "zhang_2025": "Zhang et al. [19]",
        "dorgeval_2026": "d'Orgeval et al. [16]",
    }
    color = {
        "documented": "#009E73",
        "unresolved": "#D55E00",
        "not_audited": "#9AA5B1",
        "not_applicable": "#FFFFFF",
    }
    marker = {
        "documented": "documented",
        "unresolved": "unresolved",
        "not_audited": "not audited",
        "not_applicable": "not applicable",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Transferability evidence map">',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.head{font-size:18px;font-weight:700}.row{font-size:16px}.cell{font-size:16px;font-weight:700}.note{font-size:16px;fill:#52606d}</style>',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for index, (label_lines, _) in enumerate(fields):
        x = left + index * cell_w + cell_w / 2
        for line_index, label in enumerate(label_lines):
            parts.append(f'<text class="head" x="{x}" y="{30 + line_index * 22}" text-anchor="middle">{label}</text>')
    for row_index, row in enumerate(rows):
        y = top + row_index * cell_h
        parts.append(f'<text class="row" x="18" y="{y + 30}">{labels[row["study_key"]]}</text>')
        for column_index, (_, field) in enumerate(fields):
            x = left + column_index * cell_w
            status = row[field]
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 8}" height="{cell_h - 8}" rx="3" fill="{color[status]}" stroke="#52606d" stroke-width="0.7"/>')
            text_fill = "#17212b" if status == "not_audited" else "white"
            parts.append(f'<text class="cell" x="{x + (cell_w - 8) / 2}" y="{y + 27}" text-anchor="middle" fill="{text_fill}">{marker[status]}</text>')
    legend_y = 336
    for index, status in enumerate(("documented", "unresolved", "not_audited")):
        x = 270 + index * 240
        parts.append(f'<rect x="{x}" y="{legend_y - 14}" width="18" height="18" fill="{color[status]}" stroke="#52606d" stroke-width="0.7"/>')
        parts.append(f'<text class="note" x="{x + 26}" y="{legend_y}">{marker[status]} in this repository</text>')
    parts.extend(['</svg>', ''])
    return "\n".join(parts)


def main() -> None:
    rows = load_evidence_map(SOURCE)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["evidence_status"] != "reference_model_not_executed":
        raise ValueError("Archetype contract must not claim an executed model")
    if not contract["archetypes"]:
        raise ValueError("Archetype contract requires at least one archetype")

    TABLE.parent.mkdir(parents=True, exist_ok=True)
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_csv(TABLE, rows)
    FIGURE.write_text(make_svg(rows), encoding="utf-8")

    status = {
        "evidence_map": evidence_map_summary(rows),
        "energyplus_runtime_found": bool(shutil.which("energyplus")),
        "openstudio_runtime_found": bool(shutil.which("openstudio")),
        "model_execution_status": "not_executed",
        "model_execution_reason": (
            "No EnergyPlus or OpenStudio executable was available in the "
            "reproduction environment. No energy-model output was generated."
        ),
        "archetype_contract": str(CONTRACT.relative_to(ROOT).as_posix()),
    }
    (RESULTS / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (RESULTS / "REPORT.md").write_text(
        "# Transferability extension\n\n"
        "This rapid evidence map records the audit scope of four cited studies. "
        "It is not a systematic review and does not report a quality score. "
        f"One source archive was audited. {status['evidence_map']['records_not_audited_beyond_article_level']} records remain article-level context only. "
        "No record is numerically transferable under every declared gate.\n\n"
        "The EnergyPlus archetype contract records reference-model assumptions "
        "from Sun et al. (2021). It was not executed in this environment, so "
        "this result contains no simulated electricity, PUE, or LCA output.\n",
        encoding="utf-8",
    )
    print(f"Wrote {TABLE.relative_to(ROOT)}")
    print(f"Wrote {FIGURE.relative_to(ROOT)}")
    print(f"Wrote {(RESULTS / 'status.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
