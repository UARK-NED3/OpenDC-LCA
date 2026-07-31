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


def test_historical_national_series_uses_provider_us_aggregate():
    historical = applied_energy.historical_egrid()
    factors = applied_energy.generation_weighted_factors(historical)
    by_year = {row["year"]: row for row in factors}
    assert by_year[2012]["reconstruction_minus_official_pct"] == pytest.approx(
        0.0, abs=1e-10
    )
    assert by_year[2012][
        "generation_weighted_co2e_kg_per_mwh"
    ] == pytest.approx(517.7312752800638)
    assert by_year[2012][
        "reported_minus_harmonized_kgco2e_per_mwh"
    ] == pytest.approx(0.24790128623396868)
    assert by_year[2023]["generation_weighted_co2e_kg_per_mwh"] == pytest.approx(
        349.6670732319829
    )
    assert by_year[2023][
        "reconstructed_state_weighted_co2e_kg_per_mwh"
    ] == pytest.approx(348.1879057792226)
    assert by_year[2023]["state_generation_coverage_of_official_pct"] == pytest.approx(
        99.58240814876572
    )


def test_historical_series_has_expected_anchor_extrapolation():
    diagnostics = applied_energy.anchor_extrapolation_diagnostics(
        applied_energy.historical_egrid()
    )
    all_years = next(row for row in diagnostics if row["cohort"] == "all state-years")
    current = next(row for row in diagnostics if row["cohort"] == "2023 states/DC")
    assert (
        all_years["within_released_anchors"],
        all_years["below_renewable_anchor"],
        all_years["above_grid_anchor"],
    ) == (322, 1, 136)
    assert (
        current["within_released_anchors"],
        current["below_renewable_anchor"],
        current["above_grid_anchor"],
    ) == (42, 0, 9)


def test_boundary_stress_exposes_low_carbon_crossover_fragility():
    historical = applied_energy.historical_egrid()
    current = [row for row in historical if row["year"] == 2023]
    components = applied_energy.integrated.microsoft_ghg_components()
    reference = sum(
        row["co2e_kg_per_mwh"] * row["net_generation_mwh"] for row in current
    ) / sum(row["net_generation_mwh"] for row in current)
    rows = applied_energy.boundary_adder_stress(current, components, reference)
    assert rows[0]["cold_plate_below_one_phase_count"] == 1
    assert next(
        row for row in rows if row["boundary_adder_kgco2e_per_mwh"] == 75
    )["cold_plate_below_one_phase_count"] == 0
    assert all(row["two_phase_first_rank_count"] == 51 for row in rows)


def test_functional_unit_sensitivity_is_quantified():
    historical = applied_energy.historical_egrid()
    components = applied_energy.integrated.microsoft_ghg_components()
    current = [row for row in historical if row["year"] == 2023]
    reference = sum(
        row["co2e_kg_per_mwh"] * row["net_generation_mwh"] for row in current
    ) / sum(row["net_generation_mwh"] for row in current)
    rows = applied_energy.functional_unit_sensitivity(
        historical, components, reference
    )
    current_summary = next(
        row for row in rows if row["cohort"] == "2023 states/DC"
    )
    assert current_summary[
        "median_adverse_two_phase_service_correction_pct"
    ] == pytest.approx(5.502616740789978)
