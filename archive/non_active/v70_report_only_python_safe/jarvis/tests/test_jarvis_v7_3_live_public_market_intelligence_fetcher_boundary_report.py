import unittest

from jarvis.jarvis_v7_3_live_public_market_intelligence_fetcher_boundary_report import (
    report_v7_3_live_public_market_intelligence_fetcher_boundary,
)


class JarvisV73LivePublicMarketIntelligenceFetcherBoundaryReportTests(unittest.TestCase):
    def test_report_contains_fetch_boundary_and_safety(self) -> None:
        report = report_v7_3_live_public_market_intelligence_fetcher_boundary()

        self.assertIn("J.A.R.V.I.S. v7.3 Live Public Market Intelligence Fetcher Boundary", report)
        self.assertIn("status: JARVIS_V7_3_LIVE_PUBLIC_MARKET_INTELLIGENCE_FETCHER_BOUNDARY_READY_SAFE", report)
        self.assertIn("boundary status: LIVE_PUBLIC_MARKET_INTELLIGENCE_FETCHER_BOUNDARY_READY", report)
        self.assertIn("recommended next stage: v7_4_live_public_market_intelligence_dry_run_planner", report)
        self.assertIn("btc_public_price_context_boundary", report)
        self.assertIn("btc_public_volatility_context_boundary", report)
        self.assertIn("live fetch enabled: False", report)
        self.assertIn("network call attempted: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("live fetch boundary ready: True", report)
        self.assertIn("boundary only: True", report)
        self.assertIn("live fetch disabled by default: True", report)
        self.assertIn("network calls deferred: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
