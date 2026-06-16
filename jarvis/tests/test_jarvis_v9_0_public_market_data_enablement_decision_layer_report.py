import unittest

from jarvis.jarvis_v9_0_public_market_data_enablement_decision_layer_report import (
    report_v9_0_public_market_data_enablement_decision_layer,
)


class JarvisV90PublicMarketDataEnablementDecisionLayerReportTests(unittest.TestCase):
    def test_report_contains_decisions_and_safety(self) -> None:
        report = report_v9_0_public_market_data_enablement_decision_layer()

        self.assertIn("J.A.R.V.I.S. v9.0 Public Market Data Enablement Decision Layer", report)
        self.assertIn("status: JARVIS_V9_0_PUBLIC_MARKET_DATA_ENABLEMENT_DECISION_LAYER_READY_SAFE", report)
        self.assertIn("decision layer status: PUBLIC_MARKET_DATA_ENABLEMENT_DECISION_LAYER_READY", report)
        self.assertIn("recommended next stage: v9_1_controlled_public_data_dry_run_enablement_plan", report)
        self.assertIn("source_selection_not_repeated", report)
        self.assertIn("dry_run_public_data_path_allowed", report)
        self.assertIn("live_public_fetch_blocked", report)
        self.assertIn("live allowed decision count: 0", report)
        self.assertIn("source selection not repeated: True", report)
        self.assertIn("dry-run planning allowed: True", report)
        self.assertIn("live mode blocked: True", report)
        self.assertIn("explicit operator authorization required: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
