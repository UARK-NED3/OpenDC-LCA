import json
from pathlib import Path
import tempfile
import unittest

from opendc_lca.cli import main
from opendc_lca.practitioner import (
    practitioner_input_template,
    prepare_practitioner_scenario,
    write_practitioner_report,
)


class PractitionerWorkflowTests(unittest.TestCase):
    def test_capabilities_command(self):
        self.assertEqual(main(["capabilities"]), 0)

    def test_optional_equipment_is_annualized(self):
        compact = practitioner_input_template()
        compact["equipment"].update({
            "include": True,
            "production_ghg_kgco2e": 150000,
            "production_primary_energy_mj": 2500000,
            "production_blue_water_l": 300000,
        })
        scenario = prepare_practitioner_scenario(compact)
        self.assertEqual(len(scenario["components"]), 1)
        with tempfile.TemporaryDirectory() as temporary:
            artifacts = write_practitioner_report(scenario, temporary)
            result = json.loads(artifacts["results"].read_text())
            self.assertGreater(
                result["contributions"]["equipment"]["ghg_kgco2e"], 0
            )
            self.assertIn("operational-plus-equipment", result["interpretation_scope"].lower())

    def test_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            compact = folder / "input.json"
            scenario = folder / "scenario.json"
            output = folder / "results"
            self.assertEqual(main(["new-study", str(compact)]), 0)
            self.assertEqual(
                main(["prepare-study", str(compact), str(scenario)]), 0
            )
            self.assertEqual(
                main([
                    "practitioner-report",
                    str(scenario),
                    "--output-dir",
                    str(output),
                ]),
                0,
            )
            report = (output / "PRACTITIONER_REPORT.md").read_text()
            self.assertIn("Decision status", report)
            self.assertIn("Data needed for stronger interpretation", report)
