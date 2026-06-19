from __future__ import annotations

from pathlib import Path
import json
import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_router import (
    STATUS_READY,
    STATUS_REFUSED,
    build_assistant_router_result,
    classify_assistant_intent,
)
from jarvis.runtime.local_server import _chat_payload


class JarvisV1130AssistantRouterTests(unittest.TestCase):
    def test_representative_questions_route_correctly(self) -> None:
        self.assertEqual(classify_assistant_intent("Tell me about VWCE"), "asset_lookup")
        self.assertEqual(classify_assistant_intent("Compare my ETFs"), "etf_compare")
        self.assertEqual(classify_assistant_intent("What is crypto doing today?"), "crypto_market_context")
        self.assertEqual(classify_assistant_intent("Any news I should care about?"), "news_context")

    def test_asset_lookup_uses_asset_tool(self) -> None:
        result = build_assistant_router_result(query="Tell me about VWCE", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.intent, "asset_lookup")
        self.assertIn("VWCE", result.reply)
        self.assertIn("Data / Source / Freshness", result.reply)

    def test_market_and_news_questions_use_tools(self) -> None:
        market = build_assistant_router_result(query="What is crypto doing today?", current_date="2026-06-18")
        news = build_assistant_router_result(query="Any news?", current_date="2026-06-18")

        self.assertEqual(market.intent, "crypto_market_context")
        self.assertIn("today's movement cannot be determined", market.reply)
        self.assertEqual(news.intent, "news_context")
        self.assertIn("Live news fetch is not enabled", news.reply)

    def test_execution_requests_are_refused(self) -> None:
        result = build_assistant_router_result(query="Buy BTC now", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_REFUSED)
        self.assertTrue(result.execution_refused)
        self.assertIn("I cannot create buy/sell requests", result.reply)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_source_freshness_and_safety_are_disclosed(self) -> None:
        result = build_assistant_router_result(query="Any news?", current_date="2026-06-18")

        self.assertEqual(result.source, "news_coverage_readiness")
        self.assertEqual(result.as_of, "2026-06-18")
        self.assertIn("readiness", result.freshness)
        self.assertFalse(result.live_fetch_enabled)
        self.assertTrue(result.local_cache_only)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)

    def test_api_chat_payload_uses_router_reply(self) -> None:
        payload = _chat_payload(query="Tell me about MSFT", current_date="2026-06-18")

        self.assertEqual(payload["intent"], "asset_lookup")
        self.assertIn("MSFT", payload["reply"])
        self.assertIn("Data / Source / Freshness", payload["reply"])
        self.assertFalse(payload["trade_executed"])
        json.dumps(payload)

    def test_operator_surface_v113_and_route(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v113.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "assistant_router")

        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_assistant_router_module"], "jarvis.runtime.assistant_router")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--assistant-router", source)
        self.assertIn("_assistant_router_main", source)


if __name__ == "__main__":
    unittest.main()
