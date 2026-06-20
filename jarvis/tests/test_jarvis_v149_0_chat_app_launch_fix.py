from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime.local_server import ROUTES
from jarvis.runtime.local_server_live_endpoint_smoke import build_local_server_live_endpoint_smoke_result


class JarvisV1490ChatAppLaunchFixTests(unittest.TestCase):
    def test_launchers_open_local_dashboard_and_chat_by_default(self) -> None:
        batch = Path("Start Jarvis.bat").read_text(encoding="utf-8")
        powershell = Path("Start-Jarvis.ps1").read_text(encoding="utf-8")

        for source in (batch, powershell):
            self.assertIn("--local-server", source)
            self.assertIn("127.0.0.1:8765", source)
            self.assertIn("/dashboard", source)
            self.assertIn("/chat", source)
            self.assertIn("outputs\\dashboard_latest.html", source)
            self.assertIn("No broker. No credentials. No orders. No trades. No auto-approval.", source)

        self.assertNotIn("Optional chat is off", batch)
        self.assertNotIn("Optional chat is off", powershell)
        self.assertNotIn("JARVIS_OPEN_CHAT", batch)
        self.assertNotIn("JARVIS_OPEN_CHAT", powershell)

    def test_local_routes_include_dashboard_chat_and_read_only_apis(self) -> None:
        self.assertIn("GET /health", ROUTES)
        self.assertIn("GET /dashboard", ROUTES)
        self.assertIn("GET /chat", ROUTES)
        self.assertIn("POST /api/chat", ROUTES)
        self.assertIn("GET /api/status", ROUTES)

    def test_live_server_smoke_covers_launch_targets(self) -> None:
        result = build_local_server_live_endpoint_smoke_result(
            current_date="2026-06-21",
            host="127.0.0.1",
            port=0,
        )

        self.assertTrue(result.live_endpoint_smoke_ready)
        self.assertTrue(result.health_ready)
        self.assertTrue(result.dashboard_ready)
        self.assertTrue(result.chat_page_ready)
        self.assertTrue(result.api_status_ready)
        self.assertTrue(result.api_chat_ready)
        self.assertEqual(result.blockers, [])
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

        for route in ("GET /health", "GET /dashboard", "GET /chat", "POST /api/chat", "GET /api/status"):
            self.assertIn(route, result.http_checks)
            self.assertEqual(result.http_checks[route]["status"], 200)
            self.assertTrue(result.http_checks[route]["ready"])


if __name__ == "__main__":
    unittest.main()
