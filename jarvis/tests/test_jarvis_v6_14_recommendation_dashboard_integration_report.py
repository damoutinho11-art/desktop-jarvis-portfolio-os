import unittest

from jarvis.jarvis_v6_14_recommendation_dashboard_integration_report import (
    report_v6_14_recommendation_dashboard_integration,
)


class JarvisV614RecommendationDashboardIntegrationReportTests(unittest.TestCase):
    def test_report_contains_dashboard_payload_and_safety(self) -> None:
        report = report_v6_14_recommendation_dashboard_integration()

        self.assertIn("J.A.R.V.I.S. v6.14 Recommendation Dashboard Integration", report)
        self.assertIn("status: JARVIS_V6_14_RECOMMENDATION_DASHBOARD_INTEGRATION_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.15_autonomous_command_center_closeout_audit", report)
        self.assertIn("weekly_recommendation_card", report)
        self.assertIn("safety_boundary_card", report)
        self.assertIn("manual_action_card", report)
        self.assertIn("Autonomous Weekly Recommendation", report)
        self.assertIn("Only Manual Step", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("dashboard integration ready: True", report)
        self.assertIn("dashboard only: True", report)
        self.assertIn("autonomous recommendation displayed: True", report)
        self.assertIn("final user buy action required: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
