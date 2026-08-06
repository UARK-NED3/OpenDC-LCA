#!/usr/bin/env python3
"""Run the manuscript's declared analysis, verification, and build DAG."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(arguments: list[str], environment: dict[str, str]) -> None:
    print("+", " ".join(arguments), flush=True)
    subprocess.run(arguments, cwd=ROOT, env=environment, check=True)


def file_record(path: Path) -> dict[str, object]:
    return {
        "local_path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def write_execution_manifest() -> None:
    code_paths = sorted(
        {
            *ROOT.glob("scripts/*.py"),
            *ROOT.glob("src/**/*.py"),
            *ROOT.glob("tests/*.py"),
            *ROOT.glob("paper/build*.py"),
        }
    )
    output_paths = sorted(
        {
            *ROOT.glob("paper/tables/*.csv"),
            *ROOT.glob("paper/figures/*.svg"),
            *ROOT.glob("results/applied-energy/*"),
            *(ROOT / "paper" / name for name in (
                "MANUSCRIPT.md",
                "SUPPLEMENTARY_INFORMATION.md",
                "RESULTS_PACKAGE.md",
                "OpenDC-LCA_manuscript.docx",
                "OpenDC-LCA_manuscript.pdf",
                "OpenDC-LCA_supplementary_information.pdf",
                "OpenDC-LCA_Applied_Energy_Overleaf.zip",
            )),
            *(ROOT / "paper" / "overleaf" / name for name in (
                "main.tex", "supplement.tex", "main.pdf", "supplement.pdf"
            )),
        }
    )
    output_paths = [path for path in output_paths if path.is_file()]
    git_command = [
        "git", "-c", f"safe.directory={ROOT.as_posix()}", "-C", str(ROOT)
    ]
    git_commit = subprocess.run(
        [*git_command, "rev-parse", "HEAD"], check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    git_status = subprocess.run(
        [*git_command, "status", "--porcelain=v1"], check=True,
        capture_output=True, text=True,
    ).stdout
    source_manifest = ROOT / "data" / "derived" / "source-file-manifest.json"
    manifest = {
        "purpose": "submission claim-to-input-to-code-to-output execution record",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": git_commit,
        "git_dirty": bool(git_status),
        "git_status_sha256": hashlib.sha256(git_status.encode()).hexdigest(),
        "source_manifest": file_record(source_manifest),
        "code": [file_record(path) for path in code_paths],
        "outputs": [file_record(path) for path in output_paths],
        "claim_graph": {
            "24 released totals": {
                "inputs": ["private-data/incoming/microsoft-nature/41586_2025_8832_MOESM2_ESM.xlsx"],
                "code": ["src/opendc_lca/research.py", "scripts/run_research_analysis.py"],
                "outputs": ["paper/tables/table1_microsoft_reproduction_audit.csv"],
            },
            "endpoint method identity": {
                "inputs": ["private-data/incoming/microsoft-zenodo/LCA Tool with Detailed Equations.xlsx"],
                "code": ["scripts/run_applied_energy_analysis.py"],
                "outputs": ["paper/tables/table30_released_endpoint_method_audit.csv"],
            },
            "historical electricity trend": {
                "inputs": ["nine eGRID workbooks listed in the source manifest"],
                "code": ["scripts/run_applied_energy_analysis.py"],
                "outputs": ["paper/tables/table14_egrid_historical_state_factors.csv", "paper/tables/table15_egrid_historical_national_factors.csv"],
            },
            "partial linked-system electricity": {
                "inputs": ["private-data/incoming/us-electricity-baseline/US_electricity_baseline_2023_jsonld.zip", "private-data/incoming/us-electricity-baseline/IPCC_GWP_jsonld.zip"],
                "code": ["scripts/run_applied_energy_analysis.py"],
                "outputs": ["paper/tables/table28_lifecycle_electricity_factors.csv", "paper/tables/table32_national_lifecycle_cutoffs.csv", "paper/tables/table33_residual_electricity_factors.csv"],
            },
            "equal-width rank robustness": {
                "inputs": ["paper/tables/table28_lifecycle_electricity_factors.csv", "private-data/incoming/microsoft-zenodo/LCA_Tool_w_Raw_&_Normalized_PlusUncertainty&Details.xlsx"],
                "code": ["scripts/run_applied_energy_analysis.py"],
                "outputs": ["paper/tables/table29_standardized_rank_robustness.csv", "paper/figures/figure11_standardized_robustness.svg"],
            },
        },
        "verification": {
            "command": f"{sys.executable} -m unittest discover -s tests -v",
            "completed_before_manifest_write": True,
        },
    }
    destination = ROOT / "results" / "submission-execution-manifest.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {destination.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-refresh",
        action="store_true",
        help="Use the cached public-data downloads and derived tables.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Hash the current code, evidence graph, and outputs without rerunning stages.",
    )
    parser.add_argument(
        "--skip-documents",
        action="store_true",
        help="Run analysis and tests without rebuilding DOCX/Overleaf artifacts.",
    )
    options = parser.parse_args()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    python = sys.executable
    stages = []
    if options.manifest_only:
        write_execution_manifest()
        return
    if not options.skip_refresh:
        stages.append([python, "scripts/refresh_public_data.py"])
    stages.extend(
        [
            [python, "scripts/build_source_manifest.py"],
            [python, "scripts/run_research_analysis.py"],
            [python, "scripts/run_integrated_evidence_analysis.py"],
            [python, "scripts/run_applied_energy_analysis.py"],
            [python, "scripts/normalize_figure_typography.py"],
            [python, "-m", "unittest", "discover", "-s", "tests", "-v"],
        ]
    )
    if not options.skip_documents:
        stages.extend(
            [
                [python, "paper/build_manuscript.py"],
                [python, "paper/build_overleaf.py"],
            ]
        )
    for stage in stages:
        run(stage, environment)
    write_execution_manifest()


if __name__ == "__main__":
    main()
