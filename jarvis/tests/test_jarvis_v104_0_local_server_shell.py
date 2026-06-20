from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from jarvis.runtime import operator
from jarvis.runtime.local_server import (
    ROUTES,
    STATUS_READY,
    build_local_server_smoke_result,
    format_local_server_smoke,
    make_handler,
)


def _fake_chat() -> SimpleNamespace:
    return SimpleNamespace(
        chat_contract_ready=True,
        manual_only=True,
        response=(
            "Safety is active. Safety-check blocked execution: True. "
            "Manual approval required: True. Execution forbidden: True. "
            "Broker connection: False. Credentials used: False. "
            "Order created: False. Trade executed: False."
        ),
        to_dict=lambda: {
            "chat_contract_ready": True,
            "manual_only": True,
            "response": "safe",
        },
    )


def _fake_dashboard() -> SimpleNamespace:
    return SimpleNamespace(
        dashboard_contract_ready=True,
        manual_only=True,
    )


def _fake_product_api() -> SimpleNamespace:
    return SimpleNamespace(
        api_ready=True,
        to_dict=lambda: {"api_ready": True},
    )


class JarvisV1040LocalServerShellTests(unittest.TestCase):
    def test_smoke_ready_with_no_execution_paths(self) -> None:
        with patch("jarvis.runtime.local_server.build_chat_interface_contract_result", return_value=_fake_chat()), \
             patch("jarvis.runtime.local_server.build_dashboard_contract_result", return_value=_fake_dashboard()), \
             patch("jarvis.runtime.local_server.build_product_api_result", return_value=_fake_product_api()):
            result = build_local_server_smoke_result(current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.local_server_ready)
        self.assertTrue(result.manual_only)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)
        self.assertEqual(result.blockers, [])

    def test_routes_are_present(self) -> None:
        self.assertIn("GET /health", ROUTES)
        self.assertIn("GET /dashboard", ROUTES)
        self.assertIn("GET /api/status", ROUTES)
        self.assertIn("POST /api/chat", ROUTES)

    def test_format_output_mentions_run_command_and_safety(self) -> None:
        with patch("jarvis.runtime.local_server.build_chat_interface_contract_result", return_value=_fake_chat()), \
             patch("jarvis.runtime.local_server.build_dashboard_contract_result", return_value=_fake_dashboard()), \
             patch("jarvis.runtime.local_server.build_product_api_result", return_value=_fake_product_api()):
            result = build_local_server_smoke_result(current_date="2026-06-18")

        output = format_local_server_smoke(result)

        self.assertIn("J.A.R.V.I.S. LOCAL SERVER SHELL", output)
        self.assertIn("GET /health", output)
        self.assertIn("POST /api/chat", output)
        self.assertIn("python -m jarvis.runtime.local_server --local-server", output)
        self.assertIn("trade executed: False", output)

    def test_handler_factory_creates_handler_class(self) -> None:
        handler = make_handler(host="127.0.0.1", port=8765, current_date="2026-06-18")

        self.assertTrue(hasattr(handler, "do_GET"))
        self.assertTrue(hasattr(handler, "do_POST"))

    def test_operator_keeps_local_server_route_after_v104(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(
            operator.CURRENT_OPERATOR_SURFACE,
            {"local_browser_chat_page", "browser_chat_ux_polish", "assistant_tool_registry", "assistant_data_source_registry", "assistant_asset_lookup", "assistant_market_context", "assistant_news_context", "assistant_router", "assistant_answer_style_polish", "assistant_system_audit", "live_news_ui_acceptance_gate"},
        )

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--local-server", source)
        self.assertIn("_local_server_main", source)


if __name__ == "__main__":
    unittest.main()
