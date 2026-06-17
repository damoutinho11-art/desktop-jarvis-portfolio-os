import unittest

from jarvis.jarvis_v8_0_public_market_intelligence_operator_dashboard_report import (
    report_v8_0_public_market_intelligence_operator_dashboard,
)


class JarvisV80PublicMarketIntelligenceOperatorDashboardReportTests(unittest.TestCase):
    def test_report_contains_dashboard_cards_and_safety(self) -> None:
        report = report_v8_0_public_market_intelligence_operator_dashboard()

        self.assertIn("J.A.R.V.I.S. v8.0 Public Market Intelligence Operator Dashboard", report)
        self.assertIn("status: JARVIS_V8_0_PUBLIC_MARKET_INTELLIGENCE_OPERATOR_DASHBOARD_READY_SAFE", report)
        self.assertIn("dashboard status: PUBLIC_MARKET_INTELLIGENCE_OPERATOR_DASHBOARD_READY", report)
        self.assertIn("recommended next stage: v8_1_autonomous_research_cycle_status_panel", report)
        self.assertIn("v7_public_market_chain_closeout", report)
        self.assertIn("selected_candidate_public_intelligence_coverage", report)
        self.assertIn("provider_registry_and_binding_readiness", report)
        self.assertIn("live_fetch_disabled_status", report)
        self.assertIn("network_and_raw_storage_status", report)
        self.assertIn("execution_safety_boundary", report)
        self.assertIn("live fetch enabled card count: 0", report)
        self.assertIn("network call enabled card count: 0", report)
        self.assertIn("raw response storage enabled card count: 0", report)
        self.assertIn("live adapter record emission enabled card count: 0", report)
        self.assertIn("user visible: True", report)
        self.assertIn("live fetch enabled: False", report)
        self.assertIn("network call enabled: False", report)
        self.assertIn("raw response storage enabled: False", report)
        self.assertIn("live adapter record emission enabled: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("operator dashboard ready: True", report)
        self.assertIn("dashboard visibility only: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
