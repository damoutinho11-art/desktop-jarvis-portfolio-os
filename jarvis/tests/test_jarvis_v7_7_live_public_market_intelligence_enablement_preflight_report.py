import unittest

from jarvis.jarvis_v7_7_live_public_market_intelligence_enablement_preflight_report import (
    report_v7_7_live_public_market_intelligence_enablement_preflight,
)


class JarvisV77LivePublicMarketIntelligenceEnablementPreflightReportTests(unittest.TestCase):
    def test_report_contains_preflight_and_safety(self) -> None:
        report = report_v7_7_live_public_market_intelligence_enablement_preflight()

        self.assertIn("J.A.R.V.I.S. v7.7 Live Public Market Intelligence Enablement Preflight", report)
        self.assertIn("status: JARVIS_V7_7_LIVE_PUBLIC_MARKET_INTELLIGENCE_ENABLEMENT_PREFLIGHT_READY_SAFE", report)
        self.assertIn("preflight status: LIVE_PUBLIC_MARKET_INTELLIGENCE_ENABLEMENT_PREFLIGHT_READY", report)
        self.assertIn("recommended next stage: v7_8_public_provider_configuration_registry", report)
        self.assertIn("live fetch enablement allowed: False", report)
        self.assertIn("disabled_adapter_skeleton_ready", report)
        self.assertIn("adapter_disabled_by_default", report)
        self.assertIn("boundary_dry_run_normalizer_wired", report)
        self.assertIn("live_fetch_deferred", report)
        self.assertIn("network_calls_deferred", report)
        self.assertIn("raw_response_storage_deferred", report)
        self.assertIn("live_adapter_record_emission_deferred", report)
        self.assertIn("execution_boundary_preserved", report)
        self.assertIn("adapter still disabled: True", report)
        self.assertIn("live fetch still disabled: True", report)
        self.assertIn("network calls still disabled: True", report)
        self.assertIn("raw response storage still disabled: True", report)
        self.assertIn("live adapter record emission still disabled: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("enablement preflight ready: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
