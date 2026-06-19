from __future__ import annotations

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
        self.assertIn("python .\\jarvis\\runtime\\local_server.py", output)
        self.assertIn("trade executed: False", output)

    def test_handler_factory_creates_handler_class(self) -> None:
        handler = make_handler(host="127.0.0.1", port=8765, current_date="2026-06-18")

        self.assertTrue(hasattr(handler, "do_GET"))
        self.assertTrue(hasattr(handler, "do_POST"))

    def test_operator_surface_v104_and_route(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v104.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "local_server_shell")


if __name__ == "__main__":
    unittest.main()
