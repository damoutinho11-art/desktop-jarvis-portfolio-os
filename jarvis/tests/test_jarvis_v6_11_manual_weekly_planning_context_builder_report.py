import unittest

from jarvis.jarvis_v6_11_manual_weekly_planning_context_builder_report import (
    report_v6_11_manual_weekly_planning_context_builder,
)


class JarvisV611ManualWeeklyPlanningContextBuilderReportTests(unittest.TestCase):
    def test_report_contains_context_and_safety(self) -> None:
        report = report_v6_11_manual_weekly_planning_context_builder()

        self.assertIn("J.A.R.V.I.S. v6.11 Manual Weekly Planning Context Builder", report)
        self.assertIn("status: JARVIS_V6_11_MANUAL_WEEKLY_PLANNING_CONTEXT_BUILDER_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.12_manual_weekly_candidate_shortlist_builder", report)
        self.assertIn("active_balanced_aggressive_manual_review", report)
        self.assertIn("context_crypto_core_btc", report)
        self.assertIn("CONSIDER_FUTURE_ALLOCATION", report)
        self.assertIn("context_cash_defensive", report)
        self.assertIn("AVOID_ADDITIONAL_EXPOSURE", report)
        self.assertIn("protected cash guard active: True", report)
        self.assertIn("crypto ceiling guard active: True", report)
        self.assertIn("weekly planning context ready: True", report)
        self.assertIn("context only: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
