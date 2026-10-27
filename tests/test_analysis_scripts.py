import importlib.util
import json
import unittest
from pathlib import Path

from opendc_lca.provenance import sha256_file
from opendc_lca.research import reproduce_microsoft_figure4


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
).is_file() and applied_energy.ELECTRICITY_BASELINE_ZIP.is_file() and (
    applied_energy.IPCC_GWP_ZIP.is_file()
) and applied_energy.MICROSOFT_DETAILED_WORKBOOK.is_file() and (
    applied_energy.integrated.RAW
    / "microsoft-nature"
    / "41586_2025_8832_MOESM2_ESM.xlsx"
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
        cls.lifecycle = applied_energy.lifecycle_electricity_factors(
            cls.components
        )
        cls.residual_lifecycle = applied_energy.lifecycle_electricity_factors(
            cls.components, residual=True
        )
        cls.standardized = applied_energy.standardized_rank_robustness(
            cls.lifecycle, cls.components
        )

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

    def test_residual_consumption_mix_is_kept_separate(self):
        self.assertEqual(len(self.residual_lifecycle), 71)
        residual_national = next(
            row
            for row in self.residual_lifecycle
            if row["region_level"] == "US"
        )
        self.assertAlmostEqual(
            residual_national["lifecycle_ar5_gwp100_kgco2e_per_mwh"],
            455.3502769224227,
        )
        self.assertAlmostEqual(
            residual_national["direct_generation_ar5_gwp100_kgco2e_per_mwh"],
            399.9337724051598,
        )

    def test_boavizta_candidate_flow_is_explicit(self):
        audit = applied_energy.integrated.boavizta_server_inclusion_audit()
        self.assertEqual(len(audit), 55)
        self.assertEqual(
            sum(row["inclusion_status"] == "included" for row in audit), 48
        )
        excluded = [row for row in audit if row["inclusion_status"] == "excluded"]
        self.assertEqual(len(excluded), 7)
        self.assertTrue(
            all(
                row["reason"]
                == "missing required numeric field(s): gwp_manufacturing_ratio"
                for row in excluded
            )
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

    def test_federal_lca_commons_lifecycle_factors_are_reproduced(self):
        levels = {
            level: sum(row["region_level"] == level for row in self.lifecycle)
            for level in ("BA", "FERC", "US")
        }
        self.assertEqual(levels, {"BA": 60, "FERC": 10, "US": 1})
        national = next(
            row for row in self.lifecycle if row["region_level"] == "US"
        )
        self.assertAlmostEqual(
            national["lifecycle_ar5_gwp100_kgco2e_per_mwh"],
            422.93128473601405,
        )
        self.assertAlmostEqual(
            national["direct_generation_ar5_gwp100_kgco2e_per_mwh"],
            369.8476632939138,
        )
        self.assertAlmostEqual(
            national["upstream_infrastructure_ar5_gwp100_kgco2e_per_mwh"],
            53.08362144210025,
        )
        self.assertEqual(national["unlinked_technosphere_inputs"], 287)
        self.assertLessEqual(float(national["solver_residual"]), 1e-12)
        self.assertEqual(
            sum(
                bool(row["below_cp_one_phase_numerical_crossover"])
                for row in self.lifecycle
            ),
            10,
        )
        self.assertEqual(
            sum(
                bool(row["above_released_high_numerical_anchor"])
                for row in self.lifecycle
            ),
            15,
        )
        self.assertTrue(
            all(
                not row["below_cp_one_phase_numerical_crossover"]
                for row in self.lifecycle
                if row["region_level"] == "FERC"
            )
        )

    def test_openlca_solver_toy_system_checks_units_signs_and_cutoff(self):
        unit_factors = {"kg": 1.0, "t": 1000.0}
        processes = {
            "p": {
                "@id": "p",
                "name": "Electricity - toy generation",
                "exchanges": [
                    {
                        "internalId": 1,
                        "amount": 2.0,
                        "unit": {"@id": "kg"},
                        "flow": {"@id": "fp", "flowType": "PRODUCT_FLOW"},
                        "isQuantitativeReference": True,
                    },
                    {
                        "internalId": 2,
                        "amount": 10.0,
                        "unit": {"@id": "kg"},
                        "flow": {"@id": "fq", "flowType": "PRODUCT_FLOW"},
                        "isInput": True,
                    },
                    {
                        "internalId": 3,
                        "amount": 3.0,
                        "unit": {"@id": "kg"},
                        "flow": {
                            "@id": "cut",
                            "name": "unlinked toy material",
                            "refUnit": "kg",
                            "flowType": "PRODUCT_FLOW",
                        },
                        "isInput": True,
                    },
                    {
                        "internalId": 4,
                        "amount": 1.0,
                        "unit": {"@id": "kg"},
                        "flow": {"@id": "co2", "flowType": "ELEMENTARY_FLOW"},
                    },
                ],
            },
            "q": {
                "@id": "q",
                "name": "upstream toy process",
                "exchanges": [
                    {
                        "internalId": 1,
                        "amount": 5.0,
                        "unit": {"@id": "kg"},
                        "flow": {"@id": "fq", "flowType": "PRODUCT_FLOW"},
                        "isQuantitativeReference": True,
                    },
                    {
                        "internalId": 2,
                        "amount": 0.2,
                        "unit": {"@id": "kg"},
                        "flow": {"@id": "co2", "flowType": "ELEMENTARY_FLOW"},
                        "isInput": True,
                    },
                ],
            },
        }
        system = {
            "name": "toy system",
            "processes": [{"@id": "p"}, {"@id": "q"}],
            "processLinks": [
                {
                    "process": {"@id": "p"},
                    "exchange": {"internalId": 2},
                    "provider": {"@id": "q"},
                }
            ],
            "refProcess": {"@id": "p"},
            "targetAmount": 0.01,
            "targetUnit": {"@id": "t"},
        }
        solved = applied_energy._solve_openlca_product_system(
            system, processes, unit_factors, {"co2": (1.0, "kg")}
        )
        self.assertAlmostEqual(solved["total"], 3.0)
        self.assertAlmostEqual(solved["direct_generation"], 5.0)
        self.assertAlmostEqual(solved["upstream_and_infrastructure"], -2.0)
        self.assertEqual(solved["link_count"], 1)
        self.assertEqual(solved["unlinked_technosphere_inputs"], 1)
        self.assertAlmostEqual(
            solved["cutoff_summary"][0]["activity_weighted_amount"], 15.0
        )

    def test_equal_width_bounds_replace_unequal_range_attribution(self):
        national = {
            row["active_assumption_blocks"]: row
            for row in self.standardized
            if row["region_level"] == "US"
        }
        self.assertTrue(national["grid only"]["robust_through_99_9999_pct"])
        self.assertAlmostEqual(
            national["use phase only"]["critical_equal_half_width_pct"],
            2.9936715348798275,
        )
        self.assertAlmostEqual(
            national["embodied only"]["critical_equal_half_width_pct"],
            22.15357633212597,
        )
        self.assertAlmostEqual(
            national["service equivalence only"][
                "critical_equal_half_width_pct"
            ],
            2.637287834120733,
        )
        self.assertAlmostEqual(
            national["all four equal-width"]["critical_equal_half_width_pct"],
            1.3178734413788307,
        )
        self.assertEqual(
            national["all four equal-width"]["critical_competitor"],
            "One-phase",
        )

    def test_released_endpoint_method_identity_is_flagged(self):
        audit = applied_energy.released_endpoint_method_audit()
        self.assertEqual(len(audit), 2)
        self.assertTrue(
            all(row["gwp100_workbook_value"] is None for row in audit)
        )
        self.assertTrue(
            all("GTP100" in row["numeric_workbook_label"] for row in audit)
        )
        self.assertEqual(
            [row["numeric_workbook_value_kgco2e_per_mwh"] for row in audit],
            [
                applied_energy.MICROSOFT_GRID_GHG_KG_PER_MWH,
                applied_energy.MICROSOFT_RENEWABLE_GHG_KG_PER_MWH,
            ],
        )
        self.assertIn(
            "'Use-Phase Conv. Energy Results'!$F$29",
            audit[0]["formula_evidence"],
        )
        self.assertIn(
            "'Use-Phase Renew. Energy Resuts'!$F$29",
            audit[1]["formula_evidence"],
        )
        national_factor = next(
            float(row["lifecycle_ar5_gwp100_kgco2e_per_mwh"])
            for row in self.lifecycle
            if row["region_level"] == "US"
        )
        response = applied_energy.implied_electricity_response_coefficients(
            self.components, national_factor
        )
        expected = {
            "Air-cooled": 0.06317272447196583,
            "Cold plate": 0.053641882997282286,
            "One-phase": 0.052585674995241104,
            "Two-phase": 0.05005751754354683,
        }
        for row in response:
            self.assertAlmostEqual(
                row["implied_electricity_response_mwh_per_vcore_year"],
                expected[row["technology"]],
            )

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
        expected_inputs = {
            path.relative_to(ROOT).as_posix()
            for path in [
                *(applied_energy.egrid_source(year) for year in applied_energy.FILES),
                applied_energy.integrated.RAW
                / "microsoft-zenodo"
                / "LCA_Tool_w_Raw_&_Normalized_PlusUncertainty&Details.xlsx",
                applied_energy.MICROSOFT_DETAILED_WORKBOOK,
                applied_energy.integrated.RAW / "boavizta" / "boavizta-data-us.csv",
                applied_energy.ELECTRICITY_BASELINE_ZIP,
                applied_energy.IPCC_GWP_ZIP,
            ]
        }
        self.assertEqual(
            {record["local_path"] for record in metadata["analysis_inputs"]},
            expected_inputs,
        )
        execution = metadata["execution_manifest"]
        for record in [*execution["code"], *execution["outputs"]]:
            path = ROOT / record["local_path"]
            self.assertTrue(path.is_file(), record["local_path"])
            self.assertEqual(record["bytes"], path.stat().st_size)
            self.assertEqual(record["sha256"], sha256_file(path))
        for name in (
            "table30_released_endpoint_method_audit.csv",
            "table31_implied_electricity_response.csv",
            "table32_national_lifecycle_cutoffs.csv",
            "table33_residual_electricity_factors.csv",
        ):
            self.assertTrue((ROOT / "paper" / "tables" / name).is_file())
            self.assertTrue((ROOT / "results" / "applied-energy" / name).is_file())
        self.assertTrue(
            (ROOT / "paper" / "tables" / "table34_boavizta_server_inclusion.csv").is_file()
        )


class SubmissionReleaseGateTests(unittest.TestCase):
    def test_execution_manifest_does_not_mislabel_local_state_as_archived(self):
        manifest = json.loads(
            (ROOT / "results" / "submission-execution-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        gate = manifest["submission_release_gate"]
        self.assertFalse(gate["exact_revision_is_immutable_public_archive"])
        self.assertIsNone(gate["doi"])
        self.assertIn("clean tagged commit", gate["required_before_submission"])
        self.assertIn(
            "public immutable archive with version DOI",
            gate["required_before_submission"],
        )

    @unittest.skipUnless(
        RAW_EVIDENCE_AVAILABLE,
        "paper reconstruction tests require locally held, non-redistributed inputs",
    )
    def test_all_24_released_totals_reconcile_from_seven_components(self):
        source = (
            applied_energy.integrated.RAW
            / "microsoft-nature"
            / "41586_2025_8832_MOESM2_ESM.xlsx"
        )
        reproduced = reproduce_microsoft_figure4(source)
        self.assertEqual(len(reproduced), 24)
        self.assertLessEqual(
            max(row.absolute_difference for row in reproduced), 1e-12
        )
        rows = applied_energy.read_xlsx_rows(source, "Figure4")
        for start in (1, 11, 21):
            component_rows = rows[start + 2 : start + 9]
            self.assertEqual(len(component_rows), 7)
            self.assertTrue(all(any(value is not None for value in row) for row in component_rows))


if __name__ == "__main__":
    unittest.main()
