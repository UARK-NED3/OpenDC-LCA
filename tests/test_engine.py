import unittest

from opendc_lca.engine import analyze, compare, sensitivity
from opendc_lca.models import Scenario, ValidationError


def scenario_data():
    return {
        "name": "reference",
        "cooling_architecture": "air",
        "study": {
            "functional_unit": "it_mwh",
            "system_boundary": "cooling_system_cradle_to_grave",
            "electricity_accounting": "test annual average",
            "water_metric": "blue water consumption",
            "allocation_method": "cut-off",
            "intended_use": "unit testing",
            "comparative_assertion": False,
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


if __name__ == "__main__":
    unittest.main()
