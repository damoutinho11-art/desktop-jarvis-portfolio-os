import unittest

from jarvis.jarvis_v6_12_manual_weekly_candidate_shortlist_builder_report import (
    report_v6_12_manual_weekly_candidate_shortlist_builder,
)


class JarvisV612ManualWeeklyCandidateShortlistBuilderReportTests(unittest.TestCase):
    def test_report_contains_shortlist_and_safety(self) -> None:
        report = report_v6_12_manual_weekly_candidate_shortlist_builder()

        self.assertIn("J.A.R.V.I.S. v6.12 Manual Weekly Candidate Shortlist Builder", report)
        self.assertIn("status: JARVIS_V6_12_MANUAL_WEEKLY_CANDIDATE_SHORTLIST_BUILDER_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.13_manual_weekly_shortlist_review_queue", report)
        self.assertIn("global_all_world_etf_candidate", report)
        self.assertIn("btc_candidate", report)
        self.assertIn("quality_factor_etf_candidate", report)
        self.assertIn("SHORTLIST_MANUAL_REVIEW_REQUIRED", report)
        self.assertIn("CRYPTO_CEILING_GUARD_ACTIVE", report)
        self.assertIn("manual weekly shortlist ready: True", report)
        self.assertIn("shortlist only: True", report)
        self.assertIn("final recommendation deferred: True", report)
        self.assertIn("asset approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
