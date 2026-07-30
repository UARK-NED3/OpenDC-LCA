import unittest

from opendc_lca.public_data import operational_ghg_per_it_mwh, EgridStateFactor


class PublicDataTests(unittest.TestCase):
    def test_operational_factor(self):
        factor = EgridStateFactor(2023, "Arkansas", "AR", 452.8805904, "ST23!STC2ERTA")
        self.assertAlmostEqual(operational_ghg_per_it_mwh(factor, 1.2), 543.45670848)

    def test_pue_below_one_is_rejected(self):
        factor = EgridStateFactor(2023, "Arkansas", "AR", 452.8805904, "ST23!STC2ERTA")
        with self.assertRaises(ValueError):
            operational_ghg_per_it_mwh(factor, 0.99)


if __name__ == "__main__":
    unittest.main()
