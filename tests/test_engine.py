import unittest
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from opendc_lca.engine import analyze, compare, sensitivity
from opendc_lca.models import Scenario, ValidationError
from opendc_lca.audit import audit
from opendc_lca.examples import install_examples
from opendc_lca.io import load_scenario
from opendc_lca.report import generate_experimental_report, generate_report
from opendc_lca.performance import (
    apply_performance,
    load_performance_map,
    summarize_performance,
)
from opendc_lca.uncertainty import ParameterDistribution, monte_carlo


def scenario_data():
    return {
        "name": "reference",
        "cooling_architecture": "air",
        "study": {
            "functional_unit": "it_mwh",
            "system_boundary": "cooling_system_cradle_to_grave",
            "electricity_accounting": "location_based",
            "water_metric": "blue water consumption",
            "allocation_method": "cut-off",
            "intended_use": "unit testing",
            "comparative_assertion": False,
            "ghg_method": "illustrative test GWP100",
            "primary_energy_method": "illustrative test primary energy",
            "water_method": "illustrative test blue water",
            "replacement_model": "discrete",
            "critical_review_status": "not_required",
        },
        "it_capacity_kw": 1,
        "capacity_factor": 1,
        "pue": 1.2,
        "facility_lifetime_years": 10,
        "onsite_water_l_per_kwh_it": 0.1,
        "grid": {
            "ghg_kgco2e_per_kwh": 0.5,
            "primary_energy_mj_per_kwh": 5,
            "blue_water_l_per_kwh": 1,
        },
        "components": [{
            "name": "cooler",
            "quantity": 2,
            "service_life_years": 5,
            "production": {
                "ghg_kgco2e": 100,
                "primary_energy_mj": 1000,
                "blue_water_l": 200,
            },
            "end_of_life": {
                "ghg_kgco2e": 0,
                "primary_energy_mj": 0,
                "blue_water_l": 0,
            },
        }],
        "data_sources": [{
            "id": "test",
            "title": "Unit-test inputs",
            "source_type": "synthetic",
            "citation": "tests/test_engine.py",
            "license": "MIT",
            "geography": "test",
            "reference_year": 2026,
            "quality": "test-only",
            "uncertainty": {
                "distribution": "not_quantified",
                "parameters": {},
                "notes": "unit test",
            },
            "review_status": "unreviewed",
            "confidentiality": "public",
        }],
    }


class EngineTests(unittest.TestCase):
    def test_energy_and_annualization(self):
        result = analyze(Scenario.from_dict(scenario_data()))
        self.assertEqual(result.annual_it_energy_kwh, 8760)
        self.assertEqual(result.annual_facility_energy_kwh, 10512)
        self.assertAlmostEqual(result.contributions["equipment"].ghg_kgco2e, 40)
        self.assertAlmostEqual(result.annual_impacts.ghg_kgco2e, 5296)
        self.assertAlmostEqual(result.annual_impacts.blue_water_l, 11468)

    def test_fluid_loss_adds_direct_emissions(self):
        data = scenario_data()
        data["fluid"] = {
            "name": "test fluid",
            "initial_charge_kg": 100,
            "annual_loss_fraction": 0.01,
            "direct_gwp_kgco2e_per_kg": 10,
            "production_per_kg": {
                "ghg_kgco2e": 2,
                "primary_energy_mj": 0,
                "blue_water_l": 0,
            },
            "end_of_life_per_kg": {
                "ghg_kgco2e": 0,
                "primary_energy_mj": 0,
                "blue_water_l": 0,
            },
        }
        result = analyze(Scenario.from_dict(data))
        self.assertAlmostEqual(
            result.contributions["direct_fluid_emissions"].ghg_kgco2e, 10
        )
        self.assertAlmostEqual(
            result.contributions["fluid_lifecycle"].ghg_kgco2e, 22
        )

    def test_invalid_physical_values(self):
        data = scenario_data()
        data["pue"] = 0.9
        with self.assertRaises(ValidationError):
            Scenario.from_dict(data)

    def test_end_of_life_recovery_credit_is_allowed(self):
        data = scenario_data()
        data["components"][0]["end_of_life"]["ghg_kgco2e"] = -10
        result = analyze(Scenario.from_dict(data))
        self.assertAlmostEqual(result.contributions["equipment"].ghg_kgco2e, 36)

    def test_compare_requires_two_scenarios(self):
        with self.assertRaises(ValueError):
            compare([Scenario.from_dict(scenario_data())])

    def test_sensitivity_ranks_grid_and_pue(self):
        results = sensitivity(Scenario.from_dict(scenario_data()))
        names = {item.parameter for item in results}
        self.assertIn("pue", names)
        self.assertIn("grid.ghg_kgco2e_per_kwh", names)
        self.assertGreaterEqual(abs(results[0].elasticity), abs(results[-1].elasticity))

    def test_missing_provenance_is_rejected(self):
        data = scenario_data()
        data["data_sources"] = []
        with self.assertRaises(ValidationError):
            Scenario.from_dict(data)

    def test_comparative_claim_with_synthetic_data_is_blocked(self):
        data = scenario_data()
        data["study"]["comparative_assertion"] = True
        findings = audit(Scenario.from_dict(data))
        self.assertIn(
            "UNSUPPORTED_COMPARATIVE_ASSERTION",
            {finding.code for finding in findings},
        )

    def test_reviewed_comparative_claim_passes_automated_blockers(self):
        data = scenario_data()
        data["study"].update({
            "comparative_assertion": True,
            "ghg_method": "IPCC AR6 GWP100",
            "primary_energy_method": "Cumulative energy demand v1.11",
            "water_method": "AWARE 1.2c",
            "critical_review_status": "independent_panel",
        })
        source = data["data_sources"][0]
        source.update({
            "source_type": "manufacturer measurement",
            "quality": "decision-grade",
            "citation": "doi:10.0000/example",
            "review_status": "independently_reviewed",
            "confidentiality": "aggregated_confidential",
            "uncertainty": {
                "distribution": "lognormal",
                "parameters": {"geometric_sd": 1.1},
                "notes": "Reviewed measurement uncertainty.",
            },
        })
        blockers = [
            finding for finding in audit(Scenario.from_dict(data))
            if finding.severity == "blocker"
        ]
        self.assertEqual(blockers, [])

    def test_duplicate_source_ids_are_rejected(self):
        data = scenario_data()
        data["data_sources"].append(dict(data["data_sources"][0]))
        with self.assertRaises(ValidationError):
            Scenario.from_dict(data)

    def test_discrete_replacements_cover_study_period(self):
        data = scenario_data()
        data["facility_lifetime_years"] = 12
        data["components"][0]["service_life_years"] = 5
        result = analyze(Scenario.from_dict(data))
        # Two units installed three times over 12 years: 6/12 of per-unit impact.
        self.assertAlmostEqual(result.contributions["equipment"].ghg_kgco2e, 50)

    def test_linearized_replacements_remain_available_for_screening(self):
        data = scenario_data()
        data["facility_lifetime_years"] = 12
        data["components"][0]["service_life_years"] = 5
        data["study"]["replacement_model"] = "linearized"
        result = analyze(Scenario.from_dict(data))
        self.assertAlmostEqual(result.contributions["equipment"].ghg_kgco2e, 40)

    def test_bundled_examples_install_and_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = install_examples(temporary)
            self.assertEqual(len(paths), 5)
            self.assertTrue(all(path.exists() for path in paths))
            result = analyze(load_scenario(paths[0]))
            self.assertGreater(result.annual_impacts.ghg_kgco2e, 0)

    def test_report_contains_results_equations_and_figures(self):
        root = Path(__file__).resolve().parents[1]
        scenarios = [
            load_scenario(root / "examples" / name)
            for name in (
                "air-cooled.json",
                "direct-to-chip.json",
                "single-phase-immersion.json",
            )
        ]
        with tempfile.TemporaryDirectory() as temporary:
            artifacts = generate_report(scenarios, temporary)
            self.assertTrue(all(path.exists() for path in artifacts.values()))
            report = artifacts["report"].read_text(encoding="utf-8")
            self.assertIn("E_{IT}", report)
            self.assertIn("Illustrative, not decision-grade", report)
            self.assertIn("impact-comparison.svg", report)
            for key in ("impact_figure", "contribution_figure"):
                ET.fromstring(artifacts[key].read_text(encoding="utf-8"))
            results = artifacts["results"].read_text(encoding="utf-8")
            self.assertIn('"model_version": "0.3.0"', results)

    def test_performance_map_derives_energy_weighted_inputs(self):
        root = Path(__file__).resolve().parents[1]
        points = load_performance_map(
            root / "examples" / "performance-map-direct-to-chip.csv"
        )
        summary = summarize_performance(points)
        self.assertEqual(summary.point_count, 4)
        self.assertGreater(summary.measured_pue, 1)
        self.assertGreater(summary.cooling_cop, 0)
        data = scenario_data()
        data["cooling_architecture"] = "direct-to-chip"
        data["data_sources"][0]["id"] = summary.source_ids[0]
        scenario = apply_performance(Scenario.from_dict(data), summary)
        self.assertAlmostEqual(scenario.pue, summary.measured_pue)
        self.assertAlmostEqual(
            scenario.onsite_water_l_per_kwh_it,
            summary.onsite_water_l_per_kwh_it,
        )

    def test_seeded_monte_carlo_is_reproducible(self):
        distributions = [
            ParameterDistribution.from_dict({
                "parameter": "pue",
                "distribution": "uniform",
                "parameters": {"low": 1.1, "high": 1.3},
                "minimum": 1,
            }),
            ParameterDistribution.from_dict({
                "parameter": "grid.ghg_kgco2e_per_kwh",
                "distribution": "normal",
                "parameters": {"mean": 0.5, "sd": 0.05},
                "minimum": 0,
            }),
        ]
        first = monte_carlo(
            Scenario.from_dict(scenario_data()),
            distributions,
            samples=100,
            seed=7,
        )
        second = monte_carlo(
            Scenario.from_dict(scenario_data()),
            distributions,
            samples=100,
            seed=7,
        )
        self.assertEqual(first, second)
        self.assertLess(
            first.ghg_kgco2e_per_it_mwh["p05"],
            first.ghg_kgco2e_per_it_mwh["p95"],
        )

    def test_monte_carlo_rejects_unphysical_samples(self):
        distribution = ParameterDistribution.from_dict({
            "parameter": "pue",
            "distribution": "uniform",
            "parameters": {"low": 0.8, "high": 0.9},
        })
        with self.assertRaises(ValidationError):
            monte_carlo(
                Scenario.from_dict(scenario_data()),
                [distribution],
                samples=2,
            )

    def test_experimental_report_contains_valid_figures(self):
        root = Path(__file__).resolve().parents[1]
        points = load_performance_map(
            root / "examples" / "performance-map-direct-to-chip.csv"
        )
        summary = summarize_performance(points)
        distribution = ParameterDistribution.from_dict({
            "parameter": "pue",
            "distribution": "triangular",
            "parameters": {"low": 1.05, "mode": 1.08, "high": 1.12},
            "minimum": 1,
        })
        scenario_data_value = scenario_data()
        scenario_data_value["cooling_architecture"] = "direct-to-chip"
        scenario_data_value["data_sources"][0]["id"] = summary.source_ids[0]
        result = monte_carlo(
            apply_performance(
                Scenario.from_dict(scenario_data_value), summary
            ),
            [distribution],
            samples=25,
            seed=3,
        )
        with tempfile.TemporaryDirectory() as temporary:
            artifacts = generate_experimental_report(
                summary, points, result, temporary
            )
            self.assertTrue(all(path.exists() for path in artifacts.values()))
            for key in ("performance_figure", "uncertainty_figure"):
                ET.fromstring(artifacts[key].read_text(encoding="utf-8"))
            self.assertIn(
                "Synthetic demonstration",
                artifacts["report"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
