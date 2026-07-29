"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys

from .engine import Result, analyze, compare, sensitivity
from .io import load_scenario
from .models import ValidationError
from .audit import audit
from .report import generate_experimental_report, generate_report
from .examples import install_examples
from .performance import (
    apply_performance,
    load_performance_map,
    summarize_performance,
)
from .uncertainty import ParameterDistribution, monte_carlo


def _print_table(results: list[Result]) -> None:
    headers = ("Scenario", "Architecture", "kg CO2e/IT MWh", "MJ/IT MWh",
               "L water/IT MWh")
    rows = [
        (
            result.scenario,
            result.cooling_architecture,
            f"{result.per_it_mwh.ghg_kgco2e:.3f}",
            f"{result.per_it_mwh.primary_energy_mj:.3f}",
            f"{result.per_it_mwh.blue_water_l:.3f}",
        )
        for result in results
    ]
    widths = [
        max(len(str(row[index])) for row in [headers, *rows])
        for index in range(len(headers))
    ]
    for row in [headers, *rows]:
        print("  ".join(str(value).ljust(widths[i]) for i, value in enumerate(row)))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opendc-lca")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("run", "validate"):
        child = subparsers.add_parser(command)
        child.add_argument("scenario")
        if command == "run":
            child.add_argument("--json", action="store_true")
    child = subparsers.add_parser("compare")
    child.add_argument("scenarios", nargs="+")
    child.add_argument("--json", action="store_true")
    child = subparsers.add_parser("sensitivity")
    child.add_argument("scenario")
    child.add_argument("--fraction", type=float, default=0.1)
    child.add_argument("--json", action="store_true")
    child = subparsers.add_parser("audit")
    child.add_argument("scenario")
    child.add_argument("--json", action="store_true")
    child = subparsers.add_parser("report")
    child.add_argument("scenarios", nargs="+")
    child.add_argument("--output-dir", required=True)
    child = subparsers.add_parser("examples")
    child.add_argument("--output-dir", required=True)
    child = subparsers.add_parser("performance")
    child.add_argument("performance_map")
    child.add_argument("--json", action="store_true")
    child = subparsers.add_parser("monte-carlo")
    child.add_argument("scenario")
    child.add_argument("uncertainty")
    child.add_argument("--samples", type=int)
    child.add_argument("--seed", type=int)
    child = subparsers.add_parser("experimental-report")
    child.add_argument("scenario")
    child.add_argument("performance_map")
    child.add_argument("uncertainty")
    child.add_argument("--output-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            scenario = load_scenario(args.scenario)
            print(f"Valid scenario: {scenario.name}")
            return 0
        if args.command == "examples":
            for path in install_examples(args.output_dir):
                print(path)
            return 0
        if args.command == "performance":
            summary = summarize_performance(
                load_performance_map(args.performance_map)
            )
            if args.json:
                print(json.dumps(summary.as_dict(), indent=2))
            else:
                print(f"Architecture: {summary.architecture}")
                print(f"Points: {summary.point_count}")
                print(f"Measured PUE: {summary.measured_pue:.4f}")
                print(
                    "On-site water: "
                    f"{summary.onsite_water_l_per_kwh_it:.4f} L/kWh IT"
                )
                print(
                    "Cooling COP: "
                    + (
                        f"{summary.cooling_cop:.3f}"
                        if summary.cooling_cop is not None
                        else "undefined"
                    )
                )
            return 0
        if args.command == "monte-carlo":
            with open(args.uncertainty, encoding="utf-8") as handle:
                specification = json.load(handle)
            distributions = [
                ParameterDistribution.from_dict(item)
                for item in specification.get("parameters", [])
            ]
            result = monte_carlo(
                load_scenario(args.scenario),
                distributions,
                samples=(
                    args.samples
                    if args.samples is not None
                    else int(specification.get("samples", 1000))
                ),
                seed=(
                    args.seed
                    if args.seed is not None
                    else int(specification.get("seed", 42))
                ),
            )
            print(json.dumps(result.as_dict(), indent=2))
            return 0
        if args.command == "experimental-report":
            points = load_performance_map(args.performance_map)
            summary = summarize_performance(points)
            scenario = apply_performance(load_scenario(args.scenario), summary)
            with open(args.uncertainty, encoding="utf-8") as handle:
                specification = json.load(handle)
            uncertainty = monte_carlo(
                scenario,
                [
                    ParameterDistribution.from_dict(item)
                    for item in specification.get("parameters", [])
                ],
                samples=int(specification.get("samples", 1000)),
                seed=int(specification.get("seed", 42)),
            )
            for name, path in generate_experimental_report(
                summary, points, uncertainty, args.output_dir
            ).items():
                print(f"{name}: {path}")
            return 0
        if args.command == "report":
            artifacts = generate_report(
                [load_scenario(path) for path in args.scenarios],
                args.output_dir,
            )
            for name, path in artifacts.items():
                print(f"{name}: {path}")
            return 0
        if args.command == "audit":
            findings = audit(load_scenario(args.scenario))
            if args.json:
                print(json.dumps(
                    [finding.as_dict() for finding in findings], indent=2
                ))
            else:
                for finding in findings:
                    print(
                        f"{finding.severity.upper():7} "
                        f"{finding.code}: {finding.message}"
                    )
            return 3 if any(
                finding.severity == "blocker" for finding in findings
            ) else 0
        if args.command == "sensitivity":
            results = sensitivity(
                load_scenario(args.scenario), fraction=args.fraction
            )
            if args.json:
                print(json.dumps([item.as_dict() for item in results], indent=2))
            else:
                print("Parameter  Elasticity  Low GHG  High GHG")
                for item in results:
                    print(
                        f"{item.parameter:36} {item.elasticity:10.3f} "
                        f"{item.low_ghg_kgco2e_per_it_mwh:8.3f} "
                        f"{item.high_ghg_kgco2e_per_it_mwh:9.3f}"
                    )
            return 0
        if args.command == "run":
            results = [analyze(load_scenario(args.scenario))]
        else:
            results = compare([load_scenario(path) for path in args.scenarios])
        if args.json:
            print(json.dumps([result.as_dict() for result in results], indent=2))
        else:
            _print_table(results)
        return 0
    except (
        ValidationError,
        ValueError,
        KeyError,
        FileExistsError,
        OSError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
