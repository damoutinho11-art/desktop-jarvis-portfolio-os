import json
import subprocess
import sys
import unittest
from pathlib import Path

from jarvis.asset_registry import CRYPTO_REQUIRED_FIELDS, ETF_REQUIRED_FIELDS, load_asset_registry, registry_summary
from jarvis.candidate_data_quality_report import build_candidate_data_quality_report


V2_REGISTRY = Path("jarvis/data/candidate_assets.v2.example.json")


class CandidateDataQualityReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_asset_registry(V2_REGISTRY)
        cls.raw_assets = json.loads(V2_REGISTRY.read_text(encoding="utf-8"))["assets"]

    def test_v2_candidate_file_loads(self) -> None:
        self.assertEqual(len(self.registry.assets), 25)

    def test_all_25_candidates_pass_registry_validation(self) -> None:
        asset_ids = {asset.asset_id for asset in self.registry.assets}

        self.assertEqual(len(asset_ids), 25)
        self.assertEqual(len(self.registry.assets), 25)

    def test_no_asset_is_approved_investable(self) -> None:
        self.assertFalse(any(asset.approval_status == "approved_investable" for asset in self.registry.assets))

    def test_counts_by_sleeve_are_correct(self) -> None:
        counts: dict[str, int] = {}
        for asset in self.registry.assets:
            counts[asset.sleeve] = counts.get(asset.sleeve, 0) + 1

        self.assertEqual(
            counts,
            {
                "crypto_core": 5,
                "global_core": 5,
                "growth_innovation": 5,
                "quality_factor": 5,
                "speculative_crypto": 5,
            },
        )

    def test_counts_by_asset_type_are_correct(self) -> None:
        summary = registry_summary(self.registry)

        self.assertEqual(summary["asset_type"], {"ETF": 15, "crypto": 10})

    def test_etf_candidates_have_etf_required_fields(self) -> None:
        for asset in self.raw_assets:
            if asset["asset_type"] == "ETF":
                for field in ETF_REQUIRED_FIELDS:
                    self.assertIn(field, asset)
                    self.assertTrue(asset[field])
                self.assertIn("notes", asset)
                self.assertTrue(asset["notes"])

    def test_crypto_candidates_have_crypto_required_fields(self) -> None:
        for asset in self.raw_assets:
            if asset["asset_type"] == "crypto":
                for field in CRYPTO_REQUIRED_FIELDS:
                    self.assertIn(field, asset)
                    self.assertIsNotNone(asset[field])
                self.assertIn("notes", asset)
                self.assertTrue(asset["notes"])

    def test_report_contains_required_quality_summary(self) -> None:
        report = build_candidate_data_quality_report(V2_REGISTRY)

        self.assertIn("total candidates: 25", report)
        self.assertIn("- global_core: 5", report)
        self.assertIn("- ETF: 15", report)
        self.assertIn("- crypto: 10", report)
        self.assertIn("registry validation status: valid", report)
        self.assertIn("approved_investable count: 0", report)
        self.assertIn("allocation allowed: false", report)

    def test_data_quality_report_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "jarvis.candidate_data_quality_report", str(V2_REGISTRY)],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Candidate Data Quality Report", result.stdout)
        self.assertIn("No trades executed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
