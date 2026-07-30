import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from opendc_lca.benchmark import (
    package_benchmark_release,
    validate_benchmark_manifest,
)
from opendc_lca.engine import (
    adjusted_characteristic_life,
    analyze,
    expected_weibull_failures,
)
from opendc_lca.interoperability import (
    export_scenario_openlca_jsonld,
    read_openlca_jsonld,
    to_brightway_data,
    write_brightway_json,
)
from opendc_lca.models import ReliabilityModel, Scenario, ValidationError
from test_engine import scenario_data


class InteroperabilityReliabilityTests(unittest.TestCase):
    def test_openlca_round_trip_and_brightway_mapping(self):
        scenario = Scenario.from_dict(scenario_data())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = export_scenario_openlca_jsonld(
                scenario, root / "foreground.zip"
            )
            processes = read_openlca_jsonld(archive)
            self.assertEqual(len(processes), 1)
            self.assertGreaterEqual(len(processes[0].exchanges), 4)
            reference = [
                exchange for exchange in processes[0].exchanges
                if exchange.is_reference
            ]
            self.assertEqual(len(reference), 1)
            data = to_brightway_data(
                processes, database_name="opendc-test"
            )
            self.assertEqual(len(data), 1)
            dataset = next(iter(data.values()))
            self.assertTrue(any(
                exchange["type"] == "production"
                for exchange in dataset["exchanges"]
            ))
            output = write_brightway_json(
                processes,
                root / "brightway.json",
                database_name="opendc-test",
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["format"], "brightway-database-write-v1")

    def test_zolca_requires_portable_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "database.zolca"
            path.write_bytes(b"not inspected")
            with self.assertRaisesRegex(ValidationError, "export JSON-LD"):
                read_openlca_jsonld(path)

    def test_exponential_renewal_matches_expected_rate(self):
        failures = expected_weibull_failures(10, 5, 1)
        self.assertAlmostEqual(failures, 2, places=2)

    def test_arrhenius_temperature_shortens_life(self):
        model = ReliabilityModel.from_dict({
            "model": "arrhenius_weibull",
            "characteristic_life_years": 10,
            "shape": 2,
            "reference_temperature_c": 25,
            "operating_temperature_c": 45,
            "activation_energy_ev": 0.4,
            "repair_downtime_hours": 8,
            "affected_capacity_fraction": 0.5,
            "maintenance_downtime_hours": 0,
        })
        self.assertLess(adjusted_characteristic_life(model), 10)

    def test_reliability_replacement_maintenance_and_downtime(self):
        data = scenario_data()
        data["study"]["replacement_model"] = "reliability"
        data["components"][0]["reliability"] = {
            "model": "weibull",
            "characteristic_life_years": 5,
            "shape": 1,
            "repair_downtime_hours": 10,
            "affected_capacity_fraction": 0.5,
            "maintenance_interval_years": 2,
            "maintenance_downtime_hours": 1,
            "maintenance_impacts": {
                "ghg_kgco2e": 10,
                "primary_energy_mj": 0,
                "blue_water_l": 0,
            },
        }
        result = analyze(Scenario.from_dict(data))
        self.assertAlmostEqual(
            result.contributions["equipment"].ghg_kgco2e, 60, places=1
        )
        self.assertAlmostEqual(
            result.contributions["maintenance"].ghg_kgco2e, 10
        )
        self.assertEqual(len(result.reliability), 1)
        self.assertGreater(result.reliability[0].annual_downtime_hours, 0)
        self.assertGreater(result.reliability[0].annual_unserved_it_kwh, 0)

    def test_reliability_mode_requires_component_data(self):
        data = scenario_data()
        data["study"]["replacement_model"] = "reliability"
        with self.assertRaisesRegex(ValidationError, "requires reliability"):
            Scenario.from_dict(data)

    def test_benchmark_packaging_and_review_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data_file = root / "performance.csv"
            data_file.write_text("test_id,value\\na,1\\n", encoding="utf-8")
            digest = hashlib.sha256(data_file.read_bytes()).hexdigest()
            manifest = {
                "title": "Test benchmark",
                "version": "0.1.0",
                "creators": [{"name": "Test Creator"}],
                "license": "CC-BY-4.0",
                "description": "Test-only benchmark",
                "functional_unit": "it_mwh",
                "system_boundary": "cooling_system_cradle_to_grave",
                "evidence_status": "experimental_unreviewed",
                "files": [{
                    "path": "performance.csv",
                    "role": "performance_map",
                    "sha256": digest,
                }],
            }
            manifest_path = root / "benchmark-manifest.json"
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            validate_benchmark_manifest(manifest_path)
            package = package_benchmark_release(
                manifest_path, root / "release.zip"
            )
            self.assertTrue(package.exists())
            manifest["evidence_status"] = "reviewed"
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValidationError, "critical-review"):
                package_benchmark_release(
                    manifest_path, root / "reviewed.zip"
                )


if __name__ == "__main__":
    unittest.main()
