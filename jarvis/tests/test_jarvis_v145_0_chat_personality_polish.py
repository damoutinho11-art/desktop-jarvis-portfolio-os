from __future__ import annotations

import contextlib
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime.assistant_router import build_assistant_router_result, classify_assistant_intent


def _product() -> SimpleNamespace:
    return SimpleNamespace(
        dashboard_ready=True,
        week_plan={
            "emergency_top_up_eur": 75,
            "crypto_eur": 100,
            "etf_fund_eur": 275,
            "individual_stock_eur": 50,
            "selected_instruments": [
                {"symbol": "BTC", "amount_eur": 75},
                {"symbol": "MSFT", "amount_eur": 50},
            ],
        },
        live_news_context={"usable_count": 0},
        manual_holdings={"holdings_ready": False},
        warnings=[],
    )


class JarvisV145ChatPersonalityPolishTests(unittest.TestCase):
    def test_friendly_concise_daily_plan_uses_product_api_data(self) -> None:
        with patch("jarvis.runtime.assistant_router.build_product_api_result", return_value=_product()):
            result = build_assistant_router_result(
                query="what is my plan today?",
                current_date="2026-06-20",
            )

        self.assertEqual(result.intent, "today_plan")
        self.assertIn("Good evening, Diogo.", result.reply)
        self.assertIn("emergency EUR 75.00", result.reply)
        self.assertIn("crypto EUR 100.00", result.reply)
        self.assertIn("ETF/fund EUR 275.00", result.reply)
        self.assertIn("MSFT EUR 50.00", result.reply)
        self.assertIn("Manual-only safety is active.", result.reply)
        self.assertIn("Ready when you are.", result.reply)

    def test_safety_refusal_for_execution_and_broker_requests(self) -> None:
        samples = [
            "buy BTC now",
            "sell MSFT now",
            "place order",
            "liquidate",
            "connect broker",
            "log into Lightyear",
            "auto rebalance",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                result = build_assistant_router_result(query=sample, current_date="2026-06-20")
                self.assertEqual(result.intent, "safety")
                self.assertTrue(result.execution_refused)
                self.assertIn("Request refused safely", result.reply)
                self.assertFalse(result.broker_connection)
                self.assertFalse(result.credentials_used)
                self.assertFalse(result.order_created)
                self.assertFalse(result.trade_executed)

    def test_common_prompts_route_to_polished_answers(self) -> None:
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch("jarvis.runtime.assistant_router.build_product_api_result", return_value=_product()))
            stack.enter_context(
                patch(
                    "jarvis.runtime.assistant_router.build_voice_briefing_result",
                    return_value=SimpleNamespace(text="Good evening, Diogo. Ready when you are.", warnings=[], blockers=[]),
                )
            )
            expected = {
                "is the dashboard ready?": "dashboard",
                "what should I review?": "review_list",
                "open dashboard": "dashboard",
                "read me the briefing": "voice_briefing",
                "why is crypto capped?": "allocation_explanation",
                "what are the risks?": "risk_summary",
                "what changed?": "what_changed",
            }
            for query, intent in expected.items():
                result = build_assistant_router_result(query=query, current_date="2026-06-20")
                self.assertEqual(result.intent, intent)
                self.assertIn("Diogo", result.reply)

    def test_classifier_catches_lightyear_lhv_ibkr(self) -> None:
        self.assertEqual(classify_assistant_intent("log into LHV"), "safety")
        self.assertEqual(classify_assistant_intent("connect Interactive Brokers"), "safety")


if __name__ == "__main__":
    unittest.main()
