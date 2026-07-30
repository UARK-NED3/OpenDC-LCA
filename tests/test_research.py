import unittest

from opendc_lca.research import illustrative_pue


class ResearchTests(unittest.TestCase):
    def test_pue_curves_are_physical(self):
        for technology in ("Air-cooled", "Cold plate", "One-phase", "Two-phase"):
            for temperature in (-20.0, 15.0, 45.0):
                self.assertGreaterEqual(illustrative_pue(technology, temperature), 1.0)

    def test_air_response_increases_in_hot_weather(self):
        self.assertGreater(
            illustrative_pue("Air-cooled", 35.0),
            illustrative_pue("Air-cooled", 15.0),
        )


if __name__ == "__main__":
    unittest.main()
