import unittest

from jarvis.jarvis_v7_0_autonomous_market_intelligence_expansion_report import (
    report_v7_0_autonomous_market_intelligence_expansion,
)


class JarvisV70AutonomousMarketIntelligenceExpansionReportTests(unittest.TestCase):
    def test_report_contains_market_intelligence_and_safety(self) -> None:
        report = report_v7_0_autonomous_market_intelligence_expansion()

        self.assertIn("J.A.R.V.I.S. v7.0 Autonomous Market Intelligence Expansion", report)
        self.assertIn("status: JARVIS_V7_0_AUTONOMOUS_MARKET_INTELLIGENCE_EXPANSION_READY_SAFE", report)
        self.assertIn("recommended next stage: v7_1_public_market_intelligence_adapter_contract", report)
        self.assertIn("btc_candidate", report)
        self.assertIn("SUPPORTIVE_WITH_CAUTION", report)
        self.assertIn("btc_policy_gap_signal", report)
        self.assertIn("btc_volatility_caution_signal", report)
        self.assertIn("global_core_stability_signal", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("autonomous market intelligence ready: True", report)
        self.assertIn("market intelligence only: True", report)
        self.assertIn("final user buy action required: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
