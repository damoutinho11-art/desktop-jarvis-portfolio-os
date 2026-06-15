import unittest

from jarvis.jarvis_v7_1_public_market_intelligence_adapter_contract_report import (
    report_v7_1_public_market_intelligence_adapter_contract,
)


class JarvisV71PublicMarketIntelligenceAdapterContractReportTests(unittest.TestCase):
    def test_report_contains_adapter_contract_and_safety(self) -> None:
        report = report_v7_1_public_market_intelligence_adapter_contract()

        self.assertIn("J.A.R.V.I.S. v7.1 Public Market Intelligence Adapter Contract", report)
        self.assertIn("status: JARVIS_V7_1_PUBLIC_MARKET_INTELLIGENCE_ADAPTER_CONTRACT_READY_SAFE", report)
        self.assertIn("adapter status: PUBLIC_MARKET_INTELLIGENCE_ADAPTER_CONTRACT_READY", report)
        self.assertIn("recommended next stage: v7_2_public_market_intelligence_fixture_ingestion", report)
        self.assertIn("compatible with v7.0: True", report)
        self.assertIn("btc_public_market_context", report)
        self.assertIn("btc_public_volatility_context", report)
        self.assertIn("global_all_world_public_context", report)
        self.assertIn("live fetch attempted: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("adapter contract ready: True", report)
        self.assertIn("contract only: True", report)
        self.assertIn("live fetch deferred: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
