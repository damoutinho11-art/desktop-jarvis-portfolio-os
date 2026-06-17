import unittest

from jarvis.jarvis_v8_1_autonomous_research_cycle_status_panel_report import (
    report_v8_1_autonomous_research_cycle_status_panel,
)


class JarvisV81AutonomousResearchCycleStatusPanelReportTests(unittest.TestCase):
    def test_report_contains_status_panel_and_safety(self) -> None:
        report = report_v8_1_autonomous_research_cycle_status_panel()

        self.assertIn("J.A.R.V.I.S. v8.1 Autonomous Research Cycle Status Panel", report)
        self.assertIn("status: JARVIS_V8_1_AUTONOMOUS_RESEARCH_CYCLE_STATUS_PANEL_READY_SAFE", report)
        self.assertIn("panel status: AUTONOMOUS_RESEARCH_CYCLE_STATUS_PANEL_READY", report)
        self.assertIn("recommended next stage: v8_2_weekly_recommendation_evidence_pack_integration", report)
        self.assertIn("public_intelligence_readiness_review", report)
        self.assertIn("selected_candidate_coverage_review", report)
        self.assertIn("provider_and_binding_review", report)
        self.assertIn("live_data_freshness_review", report)
        self.assertIn("weekly_recommendation_pack_readiness", report)
        self.assertIn("execution_boundary_review", report)
        self.assertIn("reviewed by J.A.R.V.I.S.: True", report)
        self.assertIn("watch item count:", report)
        self.assertIn("recommendation pack ready item count:", report)
        self.assertIn("live fetch enabled item count: 0", report)
        self.assertIn("network call enabled item count: 0", report)
        self.assertIn("raw response storage enabled item count: 0", report)
        self.assertIn("live adapter record emission enabled item count: 0", report)
        self.assertIn("live fetch enabled: False", report)
        self.assertIn("network call enabled: False", report)
        self.assertIn("raw response storage enabled: False", report)
        self.assertIn("live adapter record emission enabled: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("research cycle panel ready: True", report)
        self.assertIn("product visibility stage: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
