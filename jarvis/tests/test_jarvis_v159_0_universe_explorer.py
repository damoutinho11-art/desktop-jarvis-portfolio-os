from __future__ import annotations

import contextlib
import io
import unittest

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.assistant_router import build_assistant_router_result, classify_assistant_intent
from jarvis.runtime.universe_explorer import (
    DEFAULT_FIXTURE_UNIVERSE,
    STATUS_READY,
    build_universe_explorer_result,
    format_universe_explorer,
    parse_universe_query,
)


class JarvisV159UniverseExplorerTests(unittest.TestCase):
    def test_filters_work_on_fixture_universe(self) -> None:
        result = build_universe_explorer_result(
            query="",
            filters={"asset_type": "fund", "currency": "EUR", "exchange": "XETRA", "keywords": ["global"]},
            fixture_universe=DEFAULT_FIXTURE_UNIVERSE,
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertGreaterEqual(result.candidate_count, 2)
        self.assertTrue(all(item["currency"] == "EUR" for item in result.top_candidates))
        self.assertTrue(all(item["exchange"] == "XETRA" for item in result.top_candidates))

    def test_natural_language_search_maps_to_filters_safely(self) -> None:
        filters = parse_universe_query("find European accumulating global ETFs")

        self.assertEqual(filters["asset_type"], "fund")
        self.assertEqual(filters["country"], ["Ireland", "Germany", "Netherlands", "France", "Luxembourg", "Euro Area"])
        self.assertIn("global", filters["keywords"])
        self.assertIn("accumulating", filters["keywords"])

    def test_similar_to_msft_excludes_msft(self) -> None:
        result = build_universe_explorer_result(
            query="find instruments similar to MSFT",
            fixture_universe=DEFAULT_FIXTURE_UNIVERSE,
        )

        symbols = {item["symbol"] for item in result.top_candidates}
        self.assertNotIn("MSFT", symbols)
        self.assertIn("ASML", symbols)

    def test_output_contains_manual_review_note(self) -> None:
        result = build_universe_explorer_result(
            query="find EUR-denominated funds",
            fixture_universe=DEFAULT_FIXTURE_UNIVERSE,
        )
        text = format_universe_explorer(result).lower()

        self.assertTrue(result.manual_review_required)
        self.assertIn("manual review required: true", text)

    def test_no_buy_sell_order_trade_or_action_language(self) -> None:
        result = build_universe_explorer_result(
            query="find quality large-cap software stocks",
            fixture_universe=DEFAULT_FIXTURE_UNIVERSE,
        )
        text = str(result.to_dict()).lower() + format_universe_explorer(result).lower()
        for forbidden in ("buy", "sell", "order", "trade", "broker", "credential", "password", "api_key", "action"):
            self.assertNotIn(forbidden, text)

    def test_operator_route_works(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime_operator.main(["--universe-explorer", "--query", "find EUR-denominated funds"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V159_0_UNIVERSE_EXPLORER_AI_SEARCH_READY_SAFE", output.getvalue())

    def test_chat_router_supports_universe_search(self) -> None:
        self.assertEqual(classify_assistant_intent("find quality large-cap software stocks"), "universe_explorer")
        result = build_assistant_router_result(query="find European accumulating global ETFs")

        self.assertEqual(result.intent, "universe_explorer")
        self.assertIn("Universe Explorer", result.reply)
        self.assertFalse(result.execution_refused)


if __name__ == "__main__":
    unittest.main()
