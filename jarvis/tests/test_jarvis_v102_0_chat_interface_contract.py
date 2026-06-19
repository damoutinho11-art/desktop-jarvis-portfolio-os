from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.chat_interface_contract import (
    STATUS_READY,
    SUPPORTED_INTENTS,
    build_chat_interface_contract_result,
    format_chat_interface_contract,
)


class JarvisV1020ChatInterfaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.today = build_chat_interface_contract_result(
            query="what is my plan today?",
            current_date="2026-06-18",
        )

    def test_chat_contract_ready(self) -> None:
        self.assertEqual(self.today.status, STATUS_READY)
        self.assertTrue(self.today.chat_contract_ready)
        self.assertTrue(self.today.manual_only)
        self.assertEqual(self.today.blockers, [])
        self.assertEqual(set(self.today.supported_intents), set(SUPPORTED_INTENTS))

    def test_today_plan_answer_contains_manual_plan(self) -> None:
        self.assertEqual(self.today.detected_intent, "today_plan")
        self.assertIn("Today’s manual plan is ready", self.today.response)
        self.assertIn("BTC", self.today.response)
        self.assertIn("ETH", self.today.response)
        self.assertIn("MSFT", self.today.response)
        self.assertIn("read-only guidance", self.today.response)

    def test_instrument_rationale_answer(self) -> None:
        result = build_chat_interface_contract_result(
            query="why btc eth and msft?",
            current_date="2026-06-18",
        )

        self.assertEqual(result.detected_intent, "instrument_rationale")
        self.assertIn("validated product API", result.response)
        self.assertIn("manual review", result.response)
        self.assertEqual(result.blockers, [])

    def test_safety_answer_proves_no_execution(self) -> None:
        result = build_chat_interface_contract_result(
            query="is this safe, can it trade?",
            current_date="2026-06-18",
        )

        self.assertEqual(result.detected_intent, "safety")
        self.assertIn("Safety is active", result.response)
        self.assertIn("Broker connection: False", result.response)
        self.assertIn("Order created: False", result.response)
        self.assertIn("Trade executed: False", result.response)

    def test_blockers_and_dashboard_answers(self) -> None:
        blockers = build_chat_interface_contract_result(
            query="what are the blockers?",
            current_date="2026-06-18",
        )
        dashboard = build_chat_interface_contract_result(
            query="open dashboard",
            current_date="2026-06-18",
        )

        self.assertEqual(blockers.detected_intent, "blockers")
        self.assertIn("Current blockers: none", blockers.response)
        self.assertEqual(dashboard.detected_intent, "dashboard")
        self.assertIn("outputs/dashboard_latest.html", dashboard.response)
        self.assertIn("start .\\outputs\\dashboard_latest.html", dashboard.response)

    def test_format_output_is_operator_readable(self) -> None:
        output = format_chat_interface_contract(self.today)

        self.assertIn("J.A.R.V.I.S. CHAT INTERFACE CONTRACT", output)
        self.assertIn("chat contract ready: True", output)
        self.assertIn("SUPPORTED INTENTS:", output)
        self.assertIn("BLOCKERS:", output)

    def test_operator_routes_v102_surface(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v102.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "chat_interface_contract")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--chat-interface", source)
        self.assertIn("_chat_interface_contract_main", source)


if __name__ == "__main__":
    unittest.main()
