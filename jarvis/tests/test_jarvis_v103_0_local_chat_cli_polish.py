from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from jarvis.runtime import operator
from jarvis.runtime.chat_interface_contract import (
    build_chat_interface_contract_result,
    format_chat_reply,
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


class JarvisV1030LocalChatCliPolishTests(unittest.TestCase):
    def _build(self, query: str):
        with patch(
            "jarvis.runtime.chat_interface_contract.build_dashboard_contract_result",
            return_value=_fake_dashboard_contract(),
        ):
            return build_chat_interface_contract_result(
                query=query,
                current_date="2026-06-18",
            )

    def test_status_promoted_to_v103(self) -> None:
        result = self._build("what is my plan today?")

        self.assertEqual(result.status, "JARVIS_V103_0_LOCAL_CHAT_CLI_POLISH_READY_SAFE")
        self.assertTrue(result.chat_contract_ready)
        self.assertEqual(result.blockers, [])

    def test_reply_only_is_clean_and_human_facing(self) -> None:
        result = self._build("what is my plan today?")
        reply = format_chat_reply(result)

        self.assertIn("Today’s manual plan is ready", reply)
        self.assertIn("BTC EUR 53.89", reply)
        self.assertIn("ETH EUR 46.11", reply)
        self.assertIn("MSFT EUR 50.00", reply)
        self.assertIn("Dashboard: start .\\outputs\\dashboard_latest.html", reply)
        self.assertIn("Safety: read-only and manual-only", reply)
        self.assertNotIn("SUPPORTED INTENTS:", reply)
        self.assertNotIn("report written:", reply)

    def test_dashboard_reply_does_not_duplicate_dashboard_line(self) -> None:
        result = self._build("open dashboard")
        reply = format_chat_reply(result)

        self.assertEqual(result.detected_intent, "dashboard")
        self.assertIn("Open it with: start .\\outputs\\dashboard_latest.html", reply)
        self.assertEqual(reply.count("start .\\outputs\\dashboard_latest.html"), 1)

    def test_operator_surface_and_ask_route(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v103.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "local_chat_cli_polish")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--ask", source)
        self.assertIn("_chat_interface_contract_main", source)


if __name__ == "__main__":
    unittest.main()
