from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_news_context import (
    STATUS_READY,
    build_assistant_news_context_result,
    format_assistant_news_context,
)
from jarvis.runtime.chat_interface_contract import build_chat_interface_contract_result, format_chat_reply


class JarvisV1120AssistantNewsContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_assistant_news_context_result(current_date="2026-06-18")

    def test_news_readiness_answer_is_honest(self) -> None:
        self.assertEqual(self.result.status, STATUS_READY)
        self.assertIn("macro", self.result.categories)
        self.assertTrue(self.result.manual_review_required)
        self.assertFalse(self.result.local_cached_news_available)

    def test_live_fetch_disabled_and_manual_review_disclosed(self) -> None:
        output = format_assistant_news_context(self.result)

        self.assertIn("Live news fetch is not enabled", output)
        self.assertIn("Manual review required: True", output)
        self.assertIn("local cached news available=False", output)

    def test_no_fake_headlines_or_trade_language(self) -> None:
        output = format_assistant_news_context(self.result)

        self.assertIn("no headline", self.result.warnings[1].lower())
        self.assertNotIn("breaking:", output.lower())
        self.assertNotIn("buy now", output.lower())
        self.assertFalse(self.result.order_created)
        self.assertFalse(self.result.trade_executed)

    def test_chat_routes_news_questions(self) -> None:
        news = build_chat_interface_contract_result(query="Any news I should care about?", current_date="2026-06-18")
        moving = build_chat_interface_contract_result(query="Why is crypto moving?", current_date="2026-06-18")

        self.assertEqual(news.detected_intent, "news_context")
        self.assertIn("Live news fetch is not enabled", format_chat_reply(news))
        self.assertEqual(moving.detected_intent, "news_context")

    def test_operator_surface_v112_and_route(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(operator.CURRENT_OPERATOR_SURFACE, {"assistant_news_context", "assistant_router", "assistant_answer_style_polish"})

        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_assistant_news_context_module"], "jarvis.runtime.assistant_news_context")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--assistant-news-context", source)
        self.assertIn("_assistant_news_context_main", source)


if __name__ == "__main__":
    unittest.main()
