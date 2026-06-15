import unittest

from jarvis.jarvis_v8_2_weekly_recommendation_evidence_pack_integration_report import (
    report_v8_2_weekly_recommendation_evidence_pack_integration,
)


class JarvisV82WeeklyRecommendationEvidencePackIntegrationReportTests(unittest.TestCase):
    def test_report_contains_evidence_pack_and_safety(self) -> None:
        report = report_v8_2_weekly_recommendation_evidence_pack_integration()

        self.assertIn("J.A.R.V.I.S. v8.2 Weekly Recommendation Evidence Pack Integration", report)
        self.assertIn("status: JARVIS_V8_2_WEEKLY_RECOMMENDATION_EVIDENCE_PACK_INTEGRATION_READY_SAFE", report)
        self.assertIn("pack status: WEEKLY_RECOMMENDATION_EVIDENCE_PACK_INTEGRATION_READY", report)
        self.assertIn("recommended next stage: v8_3_portfolio_action_brief_generator", report)
        self.assertIn("research_cycle_review_summary", report)
        self.assertIn("selected_candidate_evidence_context", report)
        self.assertIn("public_intelligence_readiness_context", report)
        self.assertIn("provider_binding_context", report)
        self.assertIn("live_data_freshness_watch_context", report)
        self.assertIn("execution_boundary_context", report)
        self.assertIn("included section count:", report)
        self.assertIn("watch section count:", report)
        self.assertIn("ready for pack section count:", report)
        self.assertIn("live fetch enabled section count: 0", report)
        self.assertIn("network call enabled section count: 0", report)
        self.assertIn("raw response storage enabled section count: 0", report)
        self.assertIn("live adapter record emission enabled section count: 0", report)
        self.assertIn("included in weekly pack: True", report)
        self.assertIn("ready for pack: True", report)
        self.assertIn("final user action required: True", report)
        self.assertIn("live fetch enabled: False", report)
        self.assertIn("network call enabled: False", report)
        self.assertIn("raw response storage enabled: False", report)
        self.assertIn("live adapter record emission enabled: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("evidence pack integration ready: True", report)
        self.assertIn("product integration stage: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
