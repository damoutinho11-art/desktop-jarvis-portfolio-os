import unittest

from jarvis.jarvis_v6_13_autonomous_weekly_recommendation_draft_builder_report import (
    report_v6_13_autonomous_weekly_recommendation_draft_builder,
)


class JarvisV613AutonomousWeeklyRecommendationDraftBuilderReportTests(unittest.TestCase):
    def test_report_contains_recommendation_and_safety(self) -> None:
        report = report_v6_13_autonomous_weekly_recommendation_draft_builder()

        self.assertIn("J.A.R.V.I.S. v6.13 Autonomous Weekly Recommendation Draft Builder", report)
        self.assertIn("status: JARVIS_V6_13_AUTONOMOUS_WEEKLY_RECOMMENDATION_DRAFT_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.14_recommendation_dashboard_integration", report)
        self.assertIn("AUTONOMOUS_RECOMMENDATION_DRAFT_READY", report)
        self.assertIn("BUY_CANDIDATE", report)
        self.assertIn("final user action required: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("order placement forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
