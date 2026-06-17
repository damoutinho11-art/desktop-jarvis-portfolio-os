import unittest

from jarvis.jarvis_v7_8_public_provider_configuration_registry_report import (
    report_v7_8_public_provider_configuration_registry,
)


class JarvisV78PublicProviderConfigurationRegistryReportTests(unittest.TestCase):
    def test_report_contains_provider_registry_and_safety(self) -> None:
        report = report_v7_8_public_provider_configuration_registry()

        self.assertIn("J.A.R.V.I.S. v7.8 Public Provider Configuration Registry", report)
        self.assertIn("status: JARVIS_V7_8_PUBLIC_PROVIDER_CONFIGURATION_REGISTRY_READY_SAFE", report)
        self.assertIn("registry status: PUBLIC_PROVIDER_CONFIGURATION_REGISTRY_READY", report)
        self.assertIn("recommended next stage: v7_9_public_provider_skeleton_binding_audit", report)
        self.assertIn("coingecko_public_crypto_context_provider", report)
        self.assertIn("coingecko_public_crypto_volatility_context_provider", report)
        self.assertIn("stooq_public_index_market_context_provider", report)
        self.assertIn("public_news_risk_context_provider", report)
        self.assertIn("enabled provider count: 0", report)
        self.assertIn("live fetch enabled count: 0", report)
        self.assertIn("network call allowed count: 0", report)
        self.assertIn("raw response storage allowed count: 0", report)
        self.assertIn("live adapter record emit count: 0", report)
        self.assertIn("provider enabled by default: False", report)
        self.assertIn("live fetch enabled: False", report)
        self.assertIn("network call allowed: False", report)
        self.assertIn("raw response storage allowed: False", report)
        self.assertIn("emits live adapter record: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("provider registry ready: True", report)
        self.assertIn("providers disabled by default: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
