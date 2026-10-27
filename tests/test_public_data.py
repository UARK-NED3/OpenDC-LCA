import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from opendc_lca.public_data import operational_ghg_per_it_mwh, EgridStateFactor
from opendc_lca.provenance import build_file_manifest, verify_manifest_records


class PublicDataTests(unittest.TestCase):
    def test_operational_factor(self):
        factor = EgridStateFactor(2023, "Arkansas", "AR", 452.8805904, "ST23!STC2ERTA")
        self.assertAlmostEqual(operational_ghg_per_it_mwh(factor, 1.2), 543.45670848)

    def test_pue_below_one_is_rejected(self):
        factor = EgridStateFactor(2023, "Arkansas", "AR", 452.8805904, "ST23!STC2ERTA")
        with self.assertRaises(ValueError):
            operational_ghg_per_it_mwh(factor, 0.99)

    def test_source_manifest_detects_changed_input(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "private-data" / "incoming" / "provider"
            source.mkdir(parents=True)
            item = source / "dataset.csv"
            item.write_text("value\n1\n", encoding="utf-8")
            records = build_file_manifest(
                root / "private-data" / "incoming", root=root
            )
            self.assertEqual(records[0]["source_group"], "provider")
            self.assertEqual(
                verify_manifest_records(records, root=root, required_paths=[item]),
                [],
            )
            item.write_text("value\n2\n", encoding="utf-8")
            errors = verify_manifest_records(
                records, root=root, required_paths=[item]
            )
            self.assertTrue(any("sha256 mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
