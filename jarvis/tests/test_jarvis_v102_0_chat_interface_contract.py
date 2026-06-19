from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from jarvis.runtime import operator
from jarvis.runtime.chat_interface_contract import (
    SUPPORTED_INTENTS,
    build_chat_interface_contract_result,
    format_chat_interface_contract,
)


def _fake_dashboard_contract() -> SimpleNamespace:
    selections = [
        {"lane": "crypto", "symbol": "BTC", "amount_eur": 53.89},
        {"lane": "crypto", "symbol": "ETH", "amount_eur": 46.11},
        {"lane": "etf_fund", "symbol": "GLOBAL_CORE_ETF", "amount_eur": 108.22},
        {"lane": "etf_fund", "symbol": "VWCE", "amount_eur": 100.31},
        {"lane": "etf_fund", "symbol": "IS3Q.DE", "amount_eur": 66.47},
        {"lane": "individual_stock", "symbol": "MSFT", "amount_eur": 50.00},
    ]
    return SimpleNamespace(
        sections={
            "status": {"blockers": []},
            "week_plan": {
                "emergency_top_up_eur": 75,
                "crypto_eur": 100,
                "etf_fund_eur": 275,
                "individual_stock_eur": 50,
                "selected_instruments": selections,
            },
            "news": {"news_coverage_ready": True},
            "safety": {
                "safety_check_blocked_execution": True,
                "manual_approval_required": True,
                "execution_forbidden": True,
                "broker_connection": False,
                "credentials_used": False,
                "order_created": False,
                "trade_executed": False,
            },
        },
        dashboard_path="outputs/dashboard_latest.html",
        blockers=[],
        dashboard_contract_ready=True,
        manual_only=True,
        warnings=["fake warning for fast test"],
    )


class JarvisV1020ChatInterfaceContractTests(unittest.TestCase):
    def _build(self, query: str):
        with patch(
            "jarvis.runtime.chat_interface_contract.build_dashboard_contract_result",
            return_value=_fake_dashboard_contract(),
        ):
            return build_chat_interface_contract_result(
                query=query,
                current_date="2026-06-18",
            )

    def test_chat_contract_ready(self) -> None:
        result = self._build("what is my plan today?")

        self.assertTrue(result.status.endswith("READY_SAFE"))
        self.assertTrue(result.chat_contract_ready)
        self.assertTrue(result.manual_only)
        self.assertEqual(result.blockers, [])
        self.assertEqual(set(result.supported_intents), set(SUPPORTED_INTENTS))

    def test_today_plan_answer_contains_manual_plan(self) -> None:
        result = self._build("what is my plan today?")

        self.assertEqual(result.detected_intent, "today_plan")
        self.assertIn("Today’s manual plan is ready", result.response)
        self.assertIn("BTC", result.response)
        self.assertIn("ETH", result.response)
        self.assertIn("MSFT", result.response)
        self.assertIn("read-only guidance", result.response)

    def test_instrument_rationale_answer(self) -> None:
        result = self._build("why btc eth and msft?")

        self.assertEqual(result.detected_intent, "instrument_rationale")
        self.assertIn("validated product API", result.response)
        self.assertIn("manual review", result.response)
        self.assertEqual(result.blockers, [])

    def test_safety_answer_proves_no_execution(self) -> None:
        result = self._build("is this safe, can it trade?")

        self.assertEqual(result.detected_intent, "safety")
        self.assertIn("Safety is active", result.response)
        self.assertIn("Broker connection: False", result.response)
        self.assertIn("Order created: False", result.response)
        self.assertIn("Trade executed: False", result.response)

    def test_blockers_and_dashboard_answers(self) -> None:
        blockers = self._build("what are the blockers?")
        dashboard = self._build("open dashboard")

        self.assertEqual(blockers.detected_intent, "blockers")
        self.assertIn("Current blockers: none", blockers.response)
        self.assertEqual(dashboard.detected_intent, "dashboard")
        self.assertIn("outputs/dashboard_latest.html", dashboard.response)
        self.assertIn("start .\\outputs\\dashboard_latest.html", dashboard.response)

    def test_format_output_is_operator_readable(self) -> None:
        result = self._build("what is my plan today?")
        output = format_chat_interface_contract(result)

        self.assertIn("J.A.R.V.I.S. CHAT INTERFACE CONTRACT", output)
        self.assertIn("chat contract ready: True", output)
        self.assertIn("SUPPORTED INTENTS:", output)
        self.assertIn("BLOCKERS:", output)

    def test_operator_keeps_chat_interface_route_after_v102(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn("chat", operator.CURRENT_OPERATOR_SURFACE)

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--chat-interface", source)
        self.assertIn("_chat_interface_contract_main", source)


if __name__ == "__main__":
    unittest.main()
