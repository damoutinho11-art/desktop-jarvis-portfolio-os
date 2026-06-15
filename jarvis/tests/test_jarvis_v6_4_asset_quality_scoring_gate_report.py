import unittest

from jarvis.jarvis_v6_4_asset_quality_scoring_gate_report import (
    report_v6_4_asset_quality_scoring_gate,
)


class JarvisV64AssetQualityScoringGateReportTests(unittest.TestCase):
    def test_report_contains_quality_gate_and_safety(self) -> None:
        report = report_v6_4_asset_quality_scoring_gate()

        self.assertIn("J.A.R.V.I.S. v6.4 Asset Quality Scoring Gate", report)
        self.assertIn("status: JARVIS_V6_4_ASSET_QUALITY_SCORING_GATE_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.5_policy_candidate_generator", report)
        self.assertIn("global_all_world_etf_candidate", report)
        self.assertIn("global_equity_fund_candidate", report)
        self.assertIn("btc_candidate", report)
        self.assertIn("hype_candidate", report)
        self.assertIn("tao_candidate", report)
        self.assertIn("unverified_microcap_crypto_blocked", report)
        self.assertIn("quality scoring ready: True", report)
        self.assertIn("exact policy generation deferred: True", report)
        self.assertIn("policy approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
