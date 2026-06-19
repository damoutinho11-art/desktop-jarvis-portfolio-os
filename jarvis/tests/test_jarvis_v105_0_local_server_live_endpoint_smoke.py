from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.local_server_live_endpoint_smoke import (
    STATUS_READY,
    build_local_server_live_endpoint_smoke_result,
    format_local_server_live_endpoint_smoke,
)


class JarvisV1050LocalServerLiveEndpointSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_local_server_live_endpoint_smoke_result(
            current_date="2026-06-18",
            host="127.0.0.1",
            port=0,
        )

    def test_live_endpoint_smoke_ready(self) -> None:
        self.assertEqual(self.result.status, STATUS_READY)
        self.assertTrue(self.result.live_endpoint_smoke_ready)
        self.assertGreater(self.result.bound_port, 0)
        self.assertEqual(self.result.blockers, [])

    def test_all_http_endpoints_ready(self) -> None:
        self.assertTrue(self.result.health_ready)
        self.assertTrue(self.result.api_status_ready)
        self.assertTrue(self.result.api_chat_ready)
        self.assertTrue(self.result.dashboard_ready)

        for check in self.result.http_checks.values():
            self.assertEqual(check["status"], 200)
            self.assertTrue(check["ready"])

    def test_safety_invariants_hold(self) -> None:
        self.assertTrue(self.result.manual_only)
        self.assertTrue(self.result.execution_forbidden)
        self.assertFalse(self.result.broker_connection)
        self.assertFalse(self.result.credentials_used)
        self.assertFalse(self.result.order_created)
        self.assertFalse(self.result.trade_executed)

    def test_format_output_lists_endpoints_and_safety(self) -> None:
        output = format_local_server_live_endpoint_smoke(self.result)

        self.assertIn("J.A.R.V.I.S. LOCAL SERVER LIVE ENDPOINT SMOKE", output)
        self.assertIn("GET /health", output)
        self.assertIn("GET /api/status", output)
        self.assertIn("POST /api/chat", output)
        self.assertIn("GET /dashboard", output)
        self.assertIn("trade executed: False", output)
        self.assertIn("BLOCKERS:", output)

    def test_operator_keeps_live_endpoint_smoke_route_after_v105(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(
            operator.CURRENT_OPERATOR_SURFACE,
            {"local_browser_chat_page", "browser_chat_ux_polish", "assistant_tool_registry", "assistant_data_source_registry", "assistant_asset_lookup"},
        )

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--local-server-live-smoke", source)
        self.assertIn("_local_server_live_endpoint_smoke_main", source)


if __name__ == "__main__":
    unittest.main()
