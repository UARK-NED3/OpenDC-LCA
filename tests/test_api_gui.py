import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from urllib.request import Request, urlopen

from opendc_lca.api import (
    analyze_practitioner_study,
    analyze_scenario,
    new_practitioner_study,
    prepare_practitioner_study,
    summarize_performance_csv,
    validate_scenario,
)
from opendc_lca.gui import (
    GuiHandler,
    HTML,
    MAX_REQUEST_BYTES,
)


ROOT = Path(__file__).resolve().parents[1]


class ApiGuiTests(unittest.TestCase):
    def test_stable_api_analyzes_decoded_scenario(self):
        data = json.loads((ROOT / "examples" / "air-cooled.json").read_text())
        valid = validate_scenario(data)
        result = analyze_scenario(data)
        self.assertTrue(valid["valid"])
        self.assertIn("result", result)
        self.assertIn("audit", result)
        self.assertIn("comparative_claim_blocked", result)

    def test_performance_csv_api(self):
        text = (
            ROOT / "examples" / "performance-map-direct-to-chip.csv"
        ).read_text()
        result = summarize_performance_csv(text)
        self.assertGreater(result["summary"]["measured_pue"], 1)
        self.assertIn("evidence_notice", result)

    def test_gui_is_local_and_has_scientific_notice(self):
        self.assertLessEqual(MAX_REQUEST_BYTES, 2_000_000)
        self.assertIn("does not by itself authorize", HTML)
        self.assertIn("Audit findings are shown", HTML)
        self.assertIn("Guided study", HTML)
        self.assertIn("Data needed next", HTML)
        self.assertIn(".hidden{display:none!important}", HTML)

    def test_practitioner_template_prepares_and_interprets(self):
        compact = new_practitioner_study()
        scenario = prepare_practitioner_study(compact)
        result = analyze_practitioner_study(scenario)
        self.assertEqual(result["evidence_level"], "screening")
        self.assertEqual(
            result["interpretation_scope"],
            "Operational screening only; equipment and fluid omitted",
        )
        self.assertFalse(result["comparative_claim_allowed"])
        self.assertGreater(
            result["key_outputs"]["annual_facility_energy_mwh"], 0
        )
        codes = {
            item["code"] for item in result["audit_findings"]
        }
        self.assertIn("EQUIPMENT_INVENTORY_OMITTED", codes)
        self.assertTrue(result["next_data_required"])

    def test_gui_http_analyze_endpoint(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), GuiHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            with urlopen(base + "/", timeout=2) as response:
                self.assertIn(b"OpenDC-LCA", response.read())
            data = (ROOT / "examples" / "air-cooled.json").read_bytes()
            request = Request(
                base + "/api/analyze",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=2) as response:
                result = json.loads(response.read())
            self.assertIn("result", result)
            self.assertIn("audit", result)

            request = Request(
                base + "/api/practitioner-template",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=2) as response:
                template = json.loads(response.read())
            self.assertIn("it_capacity_kw", template)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
