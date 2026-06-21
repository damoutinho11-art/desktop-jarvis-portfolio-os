from __future__ import annotations

import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime.dashboard_contract import DashboardContractResult, render_dashboard_html
from jarvis.runtime.local_server import (
    ROUTES,
    make_handler,
    render_briefing_page,
    render_chat_page,
    render_memory_page,
    render_safety_page,
)


def _request_text(*, host: str, port: int, path: str) -> tuple[int, str]:
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request("GET", path)
        response = conn.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        conn.close()


def _dashboard_result() -> DashboardContractResult:
    sections = {
        "status": {"blockers": []},
        "week_plan": {
            "monthly_contribution_eur": 500,
            "emergency_top_up_eur": 75,
            "crypto_eur": 100,
            "etf_fund_eur": 275,
            "individual_stock_eur": 50,
            "selected_instruments": [],
        },
        "data": {
            "data_readiness_ready": True,
            "missing_data": [],
            "missing_universe": [],
            "crypto_candidates": 2,
            "etf_candidates": 1,
            "stock_candidates": 1,
        },
        "news": {"cache_loaded": False, "headline_count": 0, "source_failures": [], "top_headlines": []},
        "finance_intelligence": {
            "data_trust_summary": {"trusted_records": 3, "partial_records": 0},
            "selected_instrument_coverage": [],
            "market_movement_summary": "Fresh public quote context is available.",
            "fx_summary": {"conversion_available": False},
        },
        "manual_holdings": {
            "file_exists": False,
            "holdings_ready": False,
            "positions_count": 0,
            "confirmed_positions_count": 0,
            "total_cost_basis_eur": 0,
            "total_market_value_available": False,
            "positions": [],
        },
        "safety": {
            "safety_check_blocked_execution": True,
            "manual_approval_required": True,
            "execution_forbidden": True,
            "broker_connection": False,
            "credentials_used": False,
            "order_created": False,
            "trade_executed": False,
        },
        "audit": {
            "formula_invariants_ready": True,
            "data_readiness_ready": True,
            "news_coverage_ready": True,
            "safety_ready": True,
            "speed_ready": True,
        },
        "session_memory": {
            "first_run": True,
            "memory_path": "jarvis/local/jarvis_session_memory.local.json",
            "summary_text": "First run: no previous J.A.R.V.I.S. session memory exists yet.",
        },
        "what_changed": {
            "first_run": True,
            "summary_text": "Since last time: first run.",
            "changes": [],
        },
    }
    return DashboardContractResult(
        status="JARVIS_V155_TEST_READY_SAFE",
        current_date="2026-06-21",
        dashboard_contract_ready=True,
        dashboard_html_written=False,
        dashboard_path="outputs/dashboard_latest.html",
        backend_ready=True,
        product_api_ready=True,
        full_audit_ready=True,
        product_recommendations_allowed=True,
        manual_only=True,
        sections=sections,
        warnings=[],
        blockers=[],
        report_written=False,
        report_path="outputs/dashboard_contract_latest.json",
    )


class JarvisV1550AppNavigationPolishTests(unittest.TestCase):
    def test_route_registry_has_app_navigation_pages(self) -> None:
        for route in ("GET /dashboard", "GET /chat", "GET /briefing", "GET /memory", "GET /safety"):
            self.assertIn(route, ROUTES)

    def test_chat_and_dashboard_have_top_navigation(self) -> None:
        chat_html = render_chat_page()
        dashboard_html = render_dashboard_html(_dashboard_result())

        for html in (chat_html, dashboard_html):
            self.assertIn("app-nav", html)
            self.assertIn('href="/dashboard"', html)
            self.assertIn('href="/chat"', html)
            self.assertIn('href="/briefing"', html)
            self.assertIn('href="/memory"', html)
            self.assertIn('href="/safety"', html)
            self.assertIn("Dashboard", html)
            self.assertIn("Chat", html)
            self.assertIn("Briefing", html)
            self.assertIn("Memory", html)
            self.assertIn("Safety", html)

    def test_chat_links_are_user_app_pages(self) -> None:
        html = render_chat_page()

        self.assertIn("Briefing", html)
        self.assertIn("Memory", html)
        self.assertIn("Safety", html)
        self.assertNotIn(">Health<", html)
        self.assertNotIn("API status", html)

    def test_briefing_memory_and_safety_pages_render_calm_shell(self) -> None:
        with patch(
            "jarvis.runtime.local_server.build_voice_briefing_result",
            return_value=SimpleNamespace(text="Safe local briefing text."),
        ), patch(
            "jarvis.runtime.local_server.build_jarvis_session_memory_result",
            return_value=SimpleNamespace(first_run=True, summary_text="First run: no previous memory yet."),
        ), patch(
            "jarvis.runtime.local_server.build_what_changed_since_last_time_result",
            return_value=SimpleNamespace(first_run=True, summary_text="Since last time: first run.", changes=[]),
        ), patch(
            "jarvis.runtime.local_server.build_safety_check_console_output",
            return_value="BLOCKED: dry run. No execution action was taken.",
        ):
            briefing = render_briefing_page(current_date="2026-06-21")
            memory = render_memory_page(current_date="2026-06-21")
            safety = render_safety_page(current_date="2026-06-21")

        self.assertIn("Safe local briefing text.", briefing)
        self.assertIn("First run: no previous memory yet.", memory)
        self.assertIn("Since last time: first run.", memory)
        self.assertIn("Safety check blocks execution: Yes", safety)
        for html in (briefing, memory, safety):
            self.assertIn("app-nav", html)
            self.assertIn("/dashboard", html)
            self.assertIn("/chat", html)

    def test_handler_serves_new_navigation_pages(self) -> None:
        host = "127.0.0.1"
        with patch("jarvis.runtime.local_server._dashboard_html", return_value="<html>Dashboard</html>"), \
             patch("jarvis.runtime.local_server.render_briefing_page", return_value="<html>Briefing</html>"), \
             patch("jarvis.runtime.local_server.render_memory_page", return_value="<html>Memory</html>"), \
             patch("jarvis.runtime.local_server.render_safety_page", return_value="<html>Safety</html>"):
            handler = make_handler(host=host, port=0, current_date="2026-06-21")
            server = ThreadingHTTPServer((host, 0), handler)
            port = int(server.server_address[1])
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                checks = [_request_text(host=host, port=port, path=path) for path in ("/dashboard", "/chat", "/briefing", "/memory", "/safety")]
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        for status, body in checks:
            self.assertEqual(status, 200)
            self.assertTrue(body)


if __name__ == "__main__":
    unittest.main()
