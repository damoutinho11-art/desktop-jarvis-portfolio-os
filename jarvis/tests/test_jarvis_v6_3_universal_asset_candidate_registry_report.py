import unittest

from jarvis.jarvis_v6_3_universal_asset_candidate_registry_report import (
    report_v6_3_universal_asset_candidate_registry,
)


class JarvisV63UniversalAssetCandidateRegistryReportTests(unittest.TestCase):
    def test_report_contains_registry_coverage_and_safety(self) -> None:
        report = report_v6_3_universal_asset_candidate_registry()

        self.assertIn("J.A.R.V.I.S. v6.3 Universal Asset Candidate Registry", report)
        self.assertIn("status: JARVIS_V6_3_UNIVERSAL_ASSET_CANDIDATE_REGISTRY_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.4_asset_quality_scoring_gate", report)
        self.assertIn("global_all_world_etf_candidate", report)
        self.assertIn("sp_500_etf_candidate", report)
        self.assertIn("quality_factor_etf_candidate", report)
        self.assertIn("global_equity_fund_candidate", report)
        self.assertIn("single_stock_candidate_large_cap", report)
        self.assertIn("btc_candidate", report)
        self.assertIn("hype_candidate", report)
        self.assertIn("tao_candidate", report)
        self.assertIn("money_market_candidate", report)
        self.assertIn("short_duration_bond_etf_candidate", report)
        self.assertIn("gold_or_commodity_etf_candidate", report)
        self.assertIn("approved policy asset count: 0", report)
        self.assertIn("weekly buy candidate count: 0", report)
        self.assertIn("candidates only: True", report)
        self.assertIn("exact asset scoring deferred: True", report)
        self.assertIn("policy approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
