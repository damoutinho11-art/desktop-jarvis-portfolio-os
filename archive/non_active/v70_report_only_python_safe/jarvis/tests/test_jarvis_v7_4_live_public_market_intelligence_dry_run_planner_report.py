import unittest

from jarvis.jarvis_v7_4_live_public_market_intelligence_dry_run_planner_report import (
    report_v7_4_live_public_market_intelligence_dry_run_planner,
)


class JarvisV74LivePublicMarketIntelligenceDryRunPlannerReportTests(unittest.TestCase):
    def test_report_contains_dry_run_planner_and_safety(self) -> None:
        report = report_v7_4_live_public_market_intelligence_dry_run_planner()

        self.assertIn("J.A.R.V.I.S. v7.4 Live Public Market Intelligence Dry-Run Planner", report)
        self.assertIn("status: JARVIS_V7_4_LIVE_PUBLIC_MARKET_INTELLIGENCE_DRY_RUN_PLANNER_READY_SAFE", report)
        self.assertIn("dry-run status: LIVE_PUBLIC_MARKET_INTELLIGENCE_DRY_RUN_PLAN_READY", report)
        self.assertIn("recommended next stage: v7_5_live_public_market_intelligence_response_normalizer_contract", report)
        self.assertIn("dry_run_btc_public_price_context_boundary", report)
        self.assertIn("dry_run_btc_public_volatility_context_boundary", report)
        self.assertIn("planned network call count: 0", report)
        self.assertIn("planned live fetch count: 0", report)
        self.assertIn("raw response storage plan count: 0", report)
        self.assertIn("dry-run only: True", report)
        self.assertIn("live fetch allowed: False", report)
        self.assertIn("network call allowed: False", report)
        self.assertIn("raw response storage allowed: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("dry-run planner ready: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
