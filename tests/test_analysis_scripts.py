import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "applied_energy", ROOT / "scripts" / "run_applied_energy_analysis.py"
)
assert SPEC and SPEC.loader
applied_energy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(applied_energy)

RAW_EVIDENCE_AVAILABLE = all(
    applied_energy.egrid_source(year).is_file() for year in applied_energy.FILES
) and (
    applied_energy.integrated.RAW
    / "microsoft-zenodo"
    / "LCA_Tool_w_Raw_&_Normalized_PlusUncertainty&Details.xlsx"
).is_file()


@unittest.skipUnless(
    RAW_EVIDENCE_AVAILABLE,
    "paper reconstruction tests require locally held, non-redistributed inputs",
)
class AppliedEnergyEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.components = applied_energy.integrated.microsoft_ghg_components()
        cls.historical = applied_energy.historical_egrid()
        cls.current = [row for row in cls.historical if row["year"] == 2023]
        cls.factors = applied_energy.generation_weighted_factors(cls.historical)

    def test_released_electricity_endpoints_are_reproduced(self):
        for technology in applied_energy.TECHNOLOGIES:
            grid_total, _, _ = applied_energy.total_at_factor(
                self.components,
                technology,
                applied_energy.MICROSOFT_GRID_GHG_KG_PER_MWH,
            )
            renewable_total, _, _ = applied_energy.total_at_factor(
                self.components,
                technology,
                applied_energy.MICROSOFT_RENEWABLE_GHG_KG_PER_MWH,
            )
            self.assertAlmostEqual(
                grid_total, self.components["grid"][technology]["Total"]
            )
            self.assertAlmostEqual(
                renewable_total,
                self.components["renewable"][technology]["Total"],
            )

    def test_crossover_uses_released_gabi_anchors(self):
        crossover = next(
            row
            for row in applied_energy.integrated.crossover_rows(self.components)
            if row["technology_a"] == "Cold plate"
            and row["technology_b"] == "One-phase"
        )
        self.assertAlmostEqual(
            crossover["crossover_kgco2e_per_mwh"], 96.70396924389829
        )

    def test_historical_national_series_uses_provider_us_aggregate(self):
        by_year = {row["year"]: row for row in self.factors}
        self.assertAlmostEqual(
            by_year[2012]["reconstruction_minus_official_pct"], 0.0, places=10
        )
        self.assertAlmostEqual(
            by_year[2012]["generation_weighted_co2e_kg_per_mwh"],
            517.7312752800638,
        )
        self.assertAlmostEqual(
            by_year[2012]["reported_minus_harmonized_kgco2e_per_mwh"],
            0.24790128623396868,
        )
        self.assertAlmostEqual(
            by_year[2023]["generation_weighted_co2e_kg_per_mwh"],
            349.6670732319829,
        )
        self.assertAlmostEqual(
            by_year[2023]["reconstructed_state_weighted_co2e_kg_per_mwh"],
            348.1879057792226,
        )
        self.assertAlmostEqual(
            by_year[2023]["state_generation_coverage_of_official_pct"],
            99.58240814876572,
        )

    def test_historical_series_has_expected_anchor_extrapolation(self):
        diagnostics = applied_energy.anchor_extrapolation_diagnostics(
            self.historical
        )
        all_years = next(
            row for row in diagnostics if row["cohort"] == "all state-years"
        )
        current = next(
            row for row in diagnostics if row["cohort"] == "2023 states/DC"
        )
        self.assertEqual(
            (
                all_years["within_released_anchors"],
                all_years["below_renewable_anchor"],
                all_years["above_grid_anchor"],
            ),
            (322, 1, 136),
        )
        self.assertEqual(
            (
                current["within_released_anchors"],
                current["below_renewable_anchor"],
                current["above_grid_anchor"],
            ),
            (42, 0, 9),
        )

    def test_boundary_stress_reports_exact_crossover_clearance(self):
        rows = applied_energy.boundary_adder_stress(
            self.current, self.components
        )
        self.assertEqual(rows[0]["cold_plate_below_one_phase_count"], 1)
        self.assertEqual(
            next(
                row
                for row in rows
                if row["boundary_adder_kgco2e_per_mwh"] == 75
            )["cold_plate_below_one_phase_count"],
            0,
        )
        self.assertTrue(
            all(row["two_phase_first_rank_count"] == 51 for row in rows)
        )
        self.assertAlmostEqual(
            rows[0][
                "exact_adder_to_remove_all_cp_advantage_kgco2e_per_mwh"
            ],
            73.00859459089514,
        )

    def test_functional_unit_sensitivity_is_quantified(self):
        rows = applied_energy.functional_unit_sensitivity(
            self.historical, self.components
        )
        current_summary = next(
            row for row in rows if row["cohort"] == "2023 states/DC"
        )
        self.assertAlmostEqual(
            current_summary[
                "median_adverse_two_phase_service_correction_pct"
            ],
            5.502616740789978,
        )

    def test_joint_stress_is_order_invariant_and_structure_is_explicit(self):
        first = applied_energy.joint_assumption_stress(
            self.current, self.factors, self.components, iterations=250
        )
        second = applied_energy.joint_assumption_stress(
            list(reversed(self.current)),
            list(reversed(self.factors)),
            self.components,
            iterations=250,
        )
        self.assertEqual(first, second)
        structure = applied_energy.stress_structure_sensitivity(
            self.current, self.factors, self.components, iterations=250
        )
        self.assertEqual(len(structure), 2 * 3 * 5 * 3 * 4)
        self.assertTrue(
            all(
                0 <= row["first_rank_frequency_pct"] <= 100
                for row in structure
            )
        )
        for headline in first:
            matching = next(
                row
                for row in structure
                if row["context"] == headline["context"]
                and row["stress_envelope"]
                == headline["stress_envelope"]
                and row["active_assumption_blocks"] == "all four blocks"
                and row["latent_technology_correlation"] == 0.0
                and row["technology"] == headline["technology"]
            )
            self.assertEqual(
                headline["first_rank_frequency_pct"],
                matching["first_rank_frequency_pct"],
            )
        convergence = applied_energy.stress_convergence_diagnostic(
            self.current,
            self.factors,
            self.components,
            sample_sizes=(100, 250),
        )
        self.assertEqual(len(convergence), 2 * 3 * 2)
        by_design = {}
        for row in convergence:
            key = (row["context"], row["stress_envelope"])
            by_design.setdefault(key, set()).add(row["scenario_seed_hex"])
        self.assertTrue(all(len(seeds) == 1 for seeds in by_design.values()))

    def test_computational_inputs_match_provider_manifest(self):
        metadata = json.loads(
            (
                ROOT / "results" / "applied-energy" / "analysis-metadata.json"
            ).read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (
                ROOT / "data" / "derived" / "source-file-manifest.json"
            ).read_text(encoding="utf-8")
        )
        by_path = {row["local_path"]: row for row in manifest}
        for record in metadata["analysis_inputs"]:
            path = record["local_path"]
            self.assertIn(path, by_path)
            self.assertEqual(record["sha256"], by_path[path]["sha256"])


if __name__ == "__main__":
    unittest.main()
