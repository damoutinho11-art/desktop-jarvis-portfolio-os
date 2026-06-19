from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_market_context import (
    STATUS_READY,
    build_assistant_market_context_result,
    format_assistant_market_context,
)
from jarvis.runtime.chat_interface_contract import build_chat_interface_contract_result, format_chat_reply


class JarvisV1110AssistantMarketContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.crypto = build_assistant_market_context_result(context_type="crypto", current_date="2026-06-18")

    def test_crypto_question_returns_btc_eth_context(self) -> None:
        symbols = {asset["symbol"] for asset in self.crypto.assets}

        self.assertEqual(self.crypto.status, STATUS_READY)
        self.assertIn("BTC", symbols)
        self.assertIn("ETH", symbols)
        self.assertEqual(self.crypto.context_type, "crypto")

    def test_stale_or_missing_data_is_disclosed(self) -> None:
        output = format_assistant_market_context(self.crypto)

        self.assertIn("price=not available", output)
        self.assertIn("live fetch enabled=False", output)
        self.assertIn("local cache only=True", output)
        self.assertIn("cannot be determined", output)

    def test_no_fake_news_or_trade_recommendation(self) -> None:
        output = format_assistant_market_context(self.crypto)

        self.assertIn("Live news fetch is not enabled", output)
        self.assertIn("no headline or cause is claimed", output)
        self.assertIn("No broker, order, trade", output)
        self.assertNotIn("buy now", output.lower())
        self.assertFalse(self.crypto.trade_executed)
        self.assertFalse(self.crypto.order_created)

    def test_portfolio_impact_mentions_crypto_plan_constraints(self) -> None:
        self.assertIn("Crypto selected amount is EUR", self.crypto.portfolio_impact)
        self.assertIn("does not change allocations or create orders", self.crypto.portfolio_impact)

    def test_chat_routes_crypto_and_market_questions(self) -> None:
        crypto = build_chat_interface_contract_result(query="What is crypto doing today?", current_date="2026-06-18")
        market = build_chat_interface_contract_result(query="What changed today?", current_date="2026-06-18")

        self.assertEqual(crypto.detected_intent, "crypto_market_context")
        self.assertIn("BTC", format_chat_reply(crypto))
        self.assertEqual(market.detected_intent, "market_context")
        self.assertIn("Based on local data", format_chat_reply(market))

    def test_manual_only_safety_line(self) -> None:
        self.assertTrue(self.crypto.execution_forbidden)
        self.assertFalse(self.crypto.broker_connection)
        self.assertFalse(self.crypto.credentials_used)
        self.assertFalse(self.crypto.trade_executed)
        self.assertIn("Read-only market context", self.crypto.manual_only_safety_note)

    def test_operator_surface_v111_and_route(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(operator.CURRENT_OPERATOR_SURFACE, {"assistant_market_context", "assistant_news_context"})

        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_assistant_market_context_module"], "jarvis.runtime.assistant_market_context")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--assistant-market-context", source)
        self.assertIn("_assistant_market_context_main", source)


if __name__ == "__main__":
    unittest.main()
