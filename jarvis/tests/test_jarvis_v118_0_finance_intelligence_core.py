from __future__ import annotations

import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_market_data_bridge import build_assistant_market_data_bridge_result
from jarvis.runtime.current_runtime_fast_gate import STATUS_READY as FAST_GATE_READY
from jarvis.runtime.current_runtime_fast_gate import build_current_runtime_fast_gate_result
from jarvis.runtime.finance_intelligence_core import (
    STATUS_READY as CORE_READY,
    answer_finance_intelligence_question,
    build_finance_intelligence_core_result,
)
from jarvis.runtime.public_data_provider_registry import build_public_data_provider_registry_result
from jarvis.runtime.safety import build_safety_check_console_output


class JarvisV1180FinanceIntelligenceCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.current_date = "2026-06-18"
        cls.core = build_finance_intelligence_core_result(current_date=cls.current_date)
        cls.records = {item["symbol"]: item for item in cls.core.normalized_records}
        cls.coverage = {item["symbol"]: item for item in cls.core.selected_instrument_coverage}
        cls.fast_gate = build_current_runtime_fast_gate_result(current_date=cls.current_date)
        cls.provider = build_public_data_provider_registry_result(current_date=cls.current_date)
        cls.bridge = build_assistant_market_data_bridge_result(current_date=cls.current_date)

    def test_operator_surface_is_v118_finance_intelligence(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v118.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "finance_intelligence_core")
        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_finance_intelligence_core_module"], "jarvis.runtime.finance_intelligence_core")
        self.assertEqual(surface["active_current_runtime_fast_gate_module"], "jarvis.runtime.current_runtime_fast_gate")

    def test_no_forbidden_execution_capabilities(self) -> None:
        safety_output = build_safety_check_console_output()
        self.assertIn("BLOCKED:", safety_output)
        self.assertIn("No execution action was taken", safety_output)

        for result in (self.core, self.fast_gate):
            self.assertFalse(result.broker_connection)
            self.assertFalse(result.credentials_used)
            self.assertFalse(result.order_created)
            self.assertFalse(result.trade_executed)
            self.assertFalse(result.auto_approval_enabled)

    def test_current_runtime_fast_gate_finishes_quickly(self) -> None:
        self.assertEqual(self.fast_gate.status, FAST_GATE_READY)
        self.assertTrue(self.fast_gate.fast_gate_ready)
        self.assertLess(self.fast_gate.elapsed_seconds, 60.0)
        self.assertEqual(self.fast_gate.blockers, [])

    def test_existing_provider_registry_and_market_bridge_still_work(self) -> None:
        self.assertIn("PUBLIC_DATA_PROVIDER_REGISTRY_READY_SAFE", self.provider.status)
        self.assertGreaterEqual(self.provider.enabled_provider_count, 2)
        self.assertTrue(all(not plan["secrets_may_be_written"] for plan in self.provider.provider_plan))

        self.assertIn("ASSISTANT_MARKET_DATA_BRIDGE_READY_SAFE", self.bridge.status)
        bridge_symbols = {item["symbol"] for item in self.bridge.records}
        self.assertTrue({"BTC", "ETH", "MSFT"}.issubset(bridge_symbols))
        self.assertFalse(self.bridge.broker_connection)
        self.assertFalse(self.bridge.trade_executed)

    def test_normalized_records_include_core_selected_symbols(self) -> None:
        self.assertEqual(self.core.status, CORE_READY)
        self.assertTrue({"BTC", "ETH", "MSFT"}.issubset(self.records))
        self.assertEqual(self.records["BTC"]["lane"], "crypto")
        self.assertEqual(self.records["ETH"]["lane"], "crypto")
        self.assertEqual(self.records["MSFT"]["lane"], "individual_stock")
        self.assertTrue(self.records["BTC"]["trusted_for_assistant"])
        self.assertTrue(self.records["MSFT"]["trusted_for_assistant"])

    def test_etf_selected_instrument_gaps_are_honest(self) -> None:
        self.assertEqual(
            self.coverage["GLOBAL_CORE_ETF"]["classification"],
            "internal_sleeve_placeholder_not_tradable",
        )
        self.assertFalse(self.coverage["GLOBAL_CORE_ETF"]["trusted_quote"])
        self.assertIn("quote_price", self.records["GLOBAL_CORE_ETF"]["missing_fields"])

        self.assertEqual(self.coverage["VWCE"]["classification"], "etf_fund_candidate_missing_quote_source")
        self.assertFalse(self.coverage["VWCE"]["trusted_quote"])
        self.assertIn("source_as_of", self.records["VWCE"]["missing_fields"])

    def test_is3q_future_date_is_quarantined_not_trusted(self) -> None:
        is3q = self.coverage["IS3Q.DE"]
        self.assertEqual(is3q["classification"], "tradable_instrument_quarantined_future_source_date")
        self.assertEqual(is3q["freshness"], "quarantined_future_date")
        self.assertFalse(is3q["trusted_quote"])
        self.assertFalse(self.records["IS3Q.DE"]["trusted_for_assistant"])

    def test_fx_missing_or_metadata_only_is_disclosed(self) -> None:
        fx = self.core.fx_summary
        self.assertEqual(fx["portfolio_base_currency"], "EUR")
        self.assertFalse(fx["conversion_available"])
        self.assertIn("usd_to_eur_rate", fx["missing_fields"])
        self.assertIn("trusted EUR conversion is unavailable", " ".join(self.records["MSFT"]["warnings"]))

    def test_news_contract_discloses_disabled_live_news(self) -> None:
        news = self.core.news_summary
        self.assertFalse(news["live_news_fetch_enabled"])
        self.assertFalse(news["local_cached_news_available"])
        self.assertEqual(news["cached_headline_count"], 0)
        self.assertIn("must not invent headlines", news["answer_summary"])

    def test_answers_are_direct_and_source_aware(self) -> None:
        happened = self.core.answers["what_happened_today"]
        self.assertIn("local crypto cache", happened)
        self.assertIn("No market cause is claimed", happened)

        msft = answer_finance_intelligence_question("Tell me about MSFT", result=self.core)
        self.assertIn("MSFT", msft)
        self.assertIn("Data / Source / Freshness", msft)
        self.assertIn("source=yahoo_chart", msft)

        trust = self.core.answers["can_i_trust_this_data"]
        self.assertIn("Trust is mixed", trust)
        self.assertIn("FX conversion available: False", trust)

    def test_dashboard_browser_smoke_is_in_fast_gate(self) -> None:
        self.assertTrue(self.fast_gate.checks["local_server_live_smoke_ready"])
        self.assertFalse(self.fast_gate.checks["forbidden_capabilities"]["order_created"])
        self.assertFalse(self.fast_gate.checks["forbidden_capabilities"]["trade_executed"])


if __name__ == "__main__":
    unittest.main()
