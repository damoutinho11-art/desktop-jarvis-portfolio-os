import unittest

from jarvis.jarvis_v6_5_policy_candidate_generator_report import (
    report_v6_5_policy_candidate_generator,
)


class JarvisV65PolicyCandidateGeneratorReportTests(unittest.TestCase):
    def test_report_contains_policy_candidates_and_safety(self) -> None:
        report = report_v6_5_policy_candidate_generator()

        self.assertIn("J.A.R.V.I.S. v6.5 Policy Candidate Generator", report)
        self.assertIn("status: JARVIS_V6_5_POLICY_CANDIDATE_GENERATOR_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.6_manual_policy_review_queue", report)
        self.assertIn("balanced_aggressive_manual_review", report)
        self.assertIn("etf_heavy_with_crypto_allowance", report)
        self.assertIn("core_etf_btc_accumulation", report)
        self.assertIn("defensive_cash_bond_aware", report)
        self.assertIn("global_all_world_etf_candidate", report)
        self.assertIn("btc_candidate", report)
        self.assertIn("money_market_candidate", report)
        self.assertIn("hype_candidate excluded", report)
        self.assertIn("tao_candidate excluded", report)
        self.assertIn("manual review required: True", report)
        self.assertIn("policy approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
