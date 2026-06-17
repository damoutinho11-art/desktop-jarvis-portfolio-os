import unittest

from jarvis.jarvis_v7_5_live_public_market_intelligence_response_normalizer_contract_report import (
    report_v7_5_live_public_market_intelligence_response_normalizer_contract,
)


class JarvisV75LivePublicMarketIntelligenceResponseNormalizerContractReportTests(unittest.TestCase):
    def test_report_contains_response_normalizer_contract_and_safety(self) -> None:
        report = report_v7_5_live_public_market_intelligence_response_normalizer_contract()

        self.assertIn("J.A.R.V.I.S. v7.5 Live Public Market Intelligence Response Normalizer Contract", report)
        self.assertIn("status: JARVIS_V7_5_LIVE_PUBLIC_MARKET_INTELLIGENCE_RESPONSE_NORMALIZER_CONTRACT_READY_SAFE", report)
        self.assertIn("normalizer status: LIVE_PUBLIC_MARKET_INTELLIGENCE_RESPONSE_NORMALIZER_CONTRACT_READY", report)
        self.assertIn("recommended next stage: v7_6_disabled_live_public_market_fetch_adapter_skeleton", report)
        self.assertIn("btc_price_context_normalization", report)
        self.assertIn("btc_volatility_context_normalization", report)
        self.assertIn("global_all_world_context_normalization", report)
        self.assertIn("raw response payload count: 0", report)
        self.assertIn("raw response storage count: 0", report)
        self.assertIn("network call attempt count: 0", report)
        self.assertIn("live fetch attempt count: 0", report)
        self.assertIn("raw response payload present: False", report)
        self.assertIn("raw response stored: False", report)
        self.assertIn("live fetch attempted: False", report)
        self.assertIn("network call attempted: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("response normalizer contract ready: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
