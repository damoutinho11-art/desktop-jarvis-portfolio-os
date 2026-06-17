import unittest

from jarvis.jarvis_v7_2_public_market_intelligence_fixture_ingestion_report import (
    report_v7_2_public_market_intelligence_fixture_ingestion,
)


class JarvisV72PublicMarketIntelligenceFixtureIngestionReportTests(unittest.TestCase):
    def test_report_contains_fixture_ingestion_and_safety(self) -> None:
        report = report_v7_2_public_market_intelligence_fixture_ingestion()

        self.assertIn("J.A.R.V.I.S. v7.2 Public Market Intelligence Fixture Ingestion", report)
        self.assertIn("status: JARVIS_V7_2_PUBLIC_MARKET_INTELLIGENCE_FIXTURE_INGESTION_READY_SAFE", report)
        self.assertIn("ingestion status: PUBLIC_MARKET_INTELLIGENCE_FIXTURE_INGESTED", report)
        self.assertIn("recommended next stage: v7_3_live_public_market_intelligence_fetcher_boundary", report)
        self.assertIn("compatible with v7.1 contract: True", report)
        self.assertIn("v7_2_btc_fixture_support", report)
        self.assertIn("v7_2_btc_fixture_caution", report)
        self.assertIn("v7_2_global_core_fixture_support", report)
        self.assertIn("live fetch attempted: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("fixture ingestion ready: True", report)
        self.assertIn("fixture ingestion only: True", report)
        self.assertIn("live fetch deferred: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
