import unittest

from jarvis.jarvis_v7_6_disabled_live_public_market_fetch_adapter_skeleton_report import (
    report_v7_6_disabled_live_public_market_fetch_adapter_skeleton,
)


class JarvisV76DisabledLivePublicMarketFetchAdapterSkeletonReportTests(unittest.TestCase):
    def test_report_contains_disabled_skeleton_and_safety(self) -> None:
        report = report_v7_6_disabled_live_public_market_fetch_adapter_skeleton()

        self.assertIn("J.A.R.V.I.S. v7.6 Disabled Live Public Market Fetch Adapter Skeleton", report)
        self.assertIn("status: JARVIS_V7_6_DISABLED_LIVE_PUBLIC_MARKET_FETCH_ADAPTER_SKELETON_READY_SAFE", report)
        self.assertIn("skeleton status: DISABLED_LIVE_PUBLIC_MARKET_FETCH_ADAPTER_SKELETON_READY", report)
        self.assertIn("recommended next stage: v7_7_live_public_market_intelligence_enablement_preflight", report)
        self.assertIn("disabled_live_fetch_skeleton_btc_public_price_context_boundary", report)
        self.assertIn("disabled_live_fetch_skeleton_btc_public_volatility_context_boundary", report)
        self.assertIn("enabled adapter count: 0", report)
        self.assertIn("live fetch enabled count: 0", report)
        self.assertIn("network call allowed count: 0", report)
        self.assertIn("network call attempt count: 0", report)
        self.assertIn("raw response storage allowed count: 0", report)
        self.assertIn("raw response storage count: 0", report)
        self.assertIn("live adapter record emit count: 0", report)
        self.assertIn("adapter enabled: False", report)
        self.assertIn("live fetch enabled: False", report)
        self.assertIn("network call allowed: False", report)
        self.assertIn("network call attempted: False", report)
        self.assertIn("raw response storage allowed: False", report)
        self.assertIn("raw response stored: False", report)
        self.assertIn("emits live adapter record: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("disabled adapter skeleton ready: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
