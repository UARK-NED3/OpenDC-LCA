"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys

from .engine import Result, analyze, compare
from .io import load_scenario
from .models import ValidationError


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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            scenario = load_scenario(args.scenario)
            print(f"Valid scenario: {scenario.name}")
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
    except (ValidationError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
