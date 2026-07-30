import unittest

from opendc_lca.models import ValidationError
from opendc_lca.performance import (
    HourlyPerformanceResult,
    PerformancePoint,
    integrate_hourly_performance,
    interpolate_performance,
    measurement_comparative_claim_allowed,
)
from opendc_lca.research import illustrative_pue


class ResearchTests(unittest.TestCase):
    @staticmethod
    def _surface():
        points = []
        for load in (50.0, 100.0):
            for temperature in (0.0, 20.0):
                cooling = 0.1 * load + 0.05 * temperature
                points.append(PerformancePoint(
                    test_id=f"{load}-{temperature}",
                    architecture="test-cooling",
                    it_load_kw=load,
                    heat_removed_kw=load,
                    coolant_supply_c=25,
                    coolant_return_c=35,
                    flow_kg_s=1,
                    pressure_drop_kpa=10,
                    pump_power_kw=cooling,
                    fan_power_kw=0,
                    cdu_power_kw=0,
                    heat_rejection_power_kw=0,
                    onsite_water_l_h=temperature / 10,
                    ambient_dry_bulb_c=temperature,
                    ambient_wet_bulb_c=temperature - 2,
                    duration_hours=1,
                    measurement_uncertainty_percent=5,
                    source_id="test-source",
                ))
        return points

    def test_pue_curves_are_physical(self):
        for technology in ("Air-cooled", "Cold plate", "One-phase", "Two-phase"):
            for temperature in (-20.0, 15.0, 45.0):
                self.assertGreaterEqual(illustrative_pue(technology, temperature), 1.0)

    def test_air_response_increases_in_hot_weather(self):
        self.assertGreater(
            illustrative_pue("Air-cooled", 35.0),
            illustrative_pue("Air-cooled", 15.0),
        )

    def test_bilinear_interpolation(self):
        point = interpolate_performance(
            self._surface(), it_load_kw=75, ambient_dry_bulb_c=10
        )
        self.assertAlmostEqual(point.cooling_power_kw, 8.0)
        self.assertAlmostEqual(point.onsite_water_l_h, 1.0)

    def test_extrapolation_is_rejected(self):
        with self.assertRaises(ValidationError):
            interpolate_performance(
                self._surface(), it_load_kw=110, ambient_dry_bulb_c=10
            )

    def test_hourly_integration_and_claim_gate(self):
        result = integrate_hourly_performance(
            self._surface(),
            [0.0, 20.0],
            [0.5, 1.0],
            rated_it_load_kw=100,
            grid_kgco2e_per_mwh=400,
            evidence_status="synthetic",
        )
        self.assertEqual(result.hours, 2)
        self.assertFalse(measurement_comparative_claim_allowed([result, result]))
        reviewed = HourlyPerformanceResult(
            **{**result.as_dict(), "evidence_status": "reviewed"}
        )
        self.assertTrue(
            measurement_comparative_claim_allowed([reviewed, reviewed])
        )


if __name__ == "__main__":
    unittest.main()
