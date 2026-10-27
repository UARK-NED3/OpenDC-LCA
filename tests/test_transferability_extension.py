import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from opendc_lca.models import ValidationError
from opendc_lca.transferability import evidence_map_summary, load_evidence_map


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "derived" / "transferability_evidence_map.csv"


class TransferabilityExtensionTests(unittest.TestCase):
    def test_evidence_map_records_audit_scope_without_quality_claim(self):
        rows = load_evidence_map(SOURCE)
        summary = evidence_map_summary(rows)
        self.assertEqual(summary["studies_screened"], 4)
        self.assertEqual(summary["source_archives_audited"], 1)
        self.assertEqual(summary["records_not_audited_beyond_article_level"], 3)
        self.assertEqual(summary["numerically_transferable_records"], 0)
        self.assertIn("does not claim", summary["interpretation"])

    def test_evidence_map_rejects_unknown_status(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.csv"
            text = SOURCE.read_text(encoding="utf-8").replace(
                "documented,documented,unresolved,documented",
                "unknown,documented,unresolved,documented",
                1,
            )
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(ValidationError):
                load_evidence_map(path)

    def test_contract_does_not_claim_execution_or_ahpcc_representation(self):
        contract = json.loads(
            (ROOT / "data" / "derived" / "energyplus_archetype_contract.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(contract["evidence_status"], "reference_model_not_executed")
        self.assertIn("AHPCC representation without calibration and a shared-infrastructure boundary", contract["prohibited_interpretations"])
        self.assertEqual(len(contract["archetypes"]), 2)

    def test_extension_script_writes_declared_outputs(self):
        subprocess.run(
            [sys.executable, "scripts/run_transferability_extension.py"],
            cwd=ROOT,
            check=True,
        )
        status = json.loads(
            (ROOT / "results" / "transferability-extension" / "status.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(status["model_execution_status"], "not_executed")
        self.assertFalse(status["energyplus_runtime_found"])
        self.assertTrue((ROOT / "paper" / "figures" / "figure12_transferability_evidence_map.svg").is_file())


if __name__ == "__main__":
    unittest.main()
