from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_data_source_registry import (
    STATUS_READY,
    build_assistant_data_source_registry_result,
    format_assistant_data_source_registry,
)


class JarvisV1090AssistantDataSourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_assistant_data_source_registry_result(current_date="2026-06-18")

    def test_major_data_types_are_covered(self) -> None:
        ids = {source.source_id for source in self.result.sources}
        self.assertIn("crypto_prices", ids)
        self.assertIn("etf_fund_prices", ids)
        self.assertIn("stock_prices", ids)
        self.assertIn("fx", ids)
        self.assertIn("macro_news", ids)
        self.assertIn("portfolio_manual_plan", ids)
        self.assertIn("candidate_scoring", ids)
        self.assertIn("emergency_fund_monthly_contribution", ids)
        self.assertIn("data_readiness_gates", ids)
        self.assertIn("dashboard_product_api", ids)

    def test_no_fake_freshness_or_live_news_claims(self) -> None:
        by_id = {source.source_id: source for source in self.result.sources}

        self.assertIsNone(by_id["crypto_prices"].latest_as_of)
        self.assertIsNone(by_id["macro_news"].latest_as_of)
        self.assertFalse(by_id["macro_news"].live_fetch_supported)
        self.assertTrue(any("live news fetch is disabled" in warning for warning in by_id["macro_news"].warnings))

    def test_local_cache_paths_are_ignored_or_generated_locations(self) -> None:
        for source in self.result.sources:
            if not source.local_cache_path:
                continue
            normalized = source.local_cache_path.replace("\\", "/")
            self.assertTrue(normalized.startswith("jarvis/local/") or normalized.startswith("outputs/"))

    def test_sources_are_reportable_to_chat_layer(self) -> None:
        payload = self.result.to_dict()

        self.assertEqual(payload["status"], STATUS_READY)
        self.assertTrue(payload["registry_ready"])
        self.assertIsInstance(payload["sources"], list)
        self.assertTrue(all("source_id" in source for source in payload["sources"]))
        self.assertTrue(all("freshness_policy" in source for source in payload["sources"]))

    def test_safety_unchanged(self) -> None:
        self.assertTrue(self.result.manual_only)
        self.assertTrue(self.result.execution_forbidden)
        self.assertFalse(self.result.broker_connection)
        self.assertFalse(self.result.credentials_used)
        self.assertFalse(self.result.order_created)
        self.assertFalse(self.result.trade_executed)

    def test_report_discloses_partial_sources_and_safety(self) -> None:
        output = format_assistant_data_source_registry(self.result)

        self.assertIn("J.A.R.V.I.S. ASSISTANT DATA SOURCE REGISTRY", output)
        self.assertIn("crypto_prices", output)
        self.assertIn("macro_news", output)
        self.assertIn("live news fetch is disabled", output)
        self.assertIn("manual-only: True", output)
        self.assertIn("trade executed: False", output)

    def test_operator_surface_v109_and_route(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(operator.CURRENT_OPERATOR_SURFACE, {"assistant_data_source_registry", "assistant_asset_lookup", "assistant_market_context"})

        surface = operator.get_active_runtime_surface()
        self.assertEqual(
            surface["active_assistant_data_source_registry_module"],
            "jarvis.runtime.assistant_data_source_registry",
        )

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--assistant-data-sources", source)
        self.assertIn("_assistant_data_source_registry_main", source)


if __name__ == "__main__":
    unittest.main()
