from __future__ import annotations

import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_router import build_assistant_router_result
from jarvis.runtime.local_server import _chat_payload


class JarvisV1140AssistantAnswerStylePolishTests(unittest.TestCase):
    def test_asset_reply_is_human_readable_with_sections(self) -> None:
        result = build_assistant_router_result(query="Tell me about VWCE", current_date="2026-06-18")

        self.assertIn("VWCE is", result.reply)
        self.assertIn("Why:", result.reply)
        self.assertIn("Data / Source / Freshness:", result.reply)
        self.assertIn("Manual checklist:", result.reply)
        self.assertIn("Safety:", result.reply)
        self.assertNotIn("{", result.reply)

    def test_crypto_reply_contains_source_freshness_and_safety(self) -> None:
        result = build_assistant_router_result(query="What is crypto doing today?", current_date="2026-06-18")

        self.assertIn("Based on local data", result.reply)
        self.assertIn("Data / Source / Freshness:", result.reply)
        self.assertIn("live fetch enabled=False", result.reply)
        self.assertIn("Safety:", result.reply)

    def test_news_reply_is_concise_and_honest(self) -> None:
        result = build_assistant_router_result(query="Any news?", current_date="2026-06-18")

        self.assertTrue(result.reply.startswith("Live news fetch is not enabled"))
        self.assertIn("Manual checklist:", result.reply)
        self.assertIn("Safety:", result.reply)
        self.assertNotIn("breaking:", result.reply.lower())

    def test_api_chat_reply_has_no_raw_contract_dump(self) -> None:
        payload = _chat_payload(query="Tell me about BTC", current_date="2026-06-18")

        self.assertIn("BTC", payload["reply"])
        self.assertIn("Data / Source / Freshness:", payload["reply"])
        self.assertNotIn("AssistantRouterResult", payload["reply"])
        self.assertNotIn('"status"', payload["reply"])

    def test_operator_surface_v114(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v114.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "assistant_answer_style_polish")

        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_assistant_answer_style_module"], "jarvis.runtime.assistant_router")


if __name__ == "__main__":
    unittest.main()
