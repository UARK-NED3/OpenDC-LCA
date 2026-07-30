import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "applied_energy", ROOT / "scripts" / "run_applied_energy_analysis.py"
)
assert SPEC and SPEC.loader
applied_energy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(applied_energy)


def test_released_electricity_endpoints_are_reproduced():
    components = applied_energy.integrated.microsoft_ghg_components()
    for technology in applied_energy.TECHNOLOGIES:
        grid_total, _, _ = applied_energy.total_at_factor(
            components,
            technology,
            applied_energy.MICROSOFT_GRID_GHG_KG_PER_MWH,
            348.19382629383307,
        )
        renewable_total, _, _ = applied_energy.total_at_factor(
            components,
            technology,
            applied_energy.MICROSOFT_RENEWABLE_GHG_KG_PER_MWH,
            348.19382629383307,
        )
        assert grid_total == pytest.approx(components["grid"][technology]["Total"])
        assert renewable_total == pytest.approx(
            components["renewable"][technology]["Total"]
        )


def test_crossover_uses_released_gabi_anchors():
    components = applied_energy.integrated.microsoft_ghg_components()
    crossover = next(
        row
        for row in applied_energy.integrated.crossover_rows(
            components, 348.19382629383307
        )
        if row["technology_a"] == "Cold plate"
        and row["technology_b"] == "One-phase"
    )
    assert crossover["crossover_kgco2e_per_mwh"] == pytest.approx(
        96.70396924389829
    )
