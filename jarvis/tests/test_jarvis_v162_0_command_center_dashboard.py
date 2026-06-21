from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.dashboard_contract import render_dashboard_html
from jarvis.runtime.premium_command_center_dashboard import (
    STATUS_READY,
    build_command_center_dashboard_result,
    render_command_center_dashboard_html,
)


def _dashboard_fixture() -> SimpleNamespace:
    return SimpleNamespace(
        current_date="2026-06-21",
        dashboard_contract_ready=True,
        blockers=[],
        sections={
            "week_plan": {
                "emergency_top_up_eur": 75,
                "etf_fund_eur": 250,
                "crypto_eur": 100,
                "individual_stock_eur": 75,
                "selected_instruments": [
                    {"lane": "etf_fund", "symbol": "VWCE", "amount_eur": 250},
                    {"lane": "crypto", "symbol": "BTC", "amount_eur": 100},
                    {"lane": "individual_stock", "symbol": "MSFT", "amount_eur": 75},
                ],
            },
            "news": {
                "top_headlines": [
                    {
                        "title": "Macro context stays calm",
                        "source": "fixture",
                        "freshness_status": "fresh",
                    }
                ]
            },
            "finance_intelligence": {
                "data_trust_summary": {"partial_records": 0},
                "selected_instrument_coverage": [
                    {"symbol": "VWCE", "freshness": "ready", "classification": "trusted"},
                    {"symbol": "BTC", "freshness": "partial_or_unavailable", "classification": "review"},
                ],
                "market_movement_summary": "Movement context is available for manual review.",
            },
            "manual_holdings": {
                "holdings_ready": False,
                "positions": [],
            },
            "safety": {
                "safety_check_blocked_execution": True,
                "manual_approval_required": True,
            },
            "audit": {
                "formula_invariants_ready": True,
                "data_readiness_ready": True,
                "news_coverage_ready": True,
                "safety_ready": True,
            },
            "session_memory": {
                "summary_text": "Last session: safe local summary.",
            },
            "what_changed": {
                "summary_text": "Since last time: no blockers appeared.",
                "changes": ["No blockers appeared."],
            },
        },
    )


class JarvisV162CommandCenterDashboardTests(unittest.TestCase):
    def test_dashboard_renderer_uses_premium_command_center(self) -> None:
        html = render_command_center_dashboard_html(_dashboard_fixture())

        for marker in (
            "J.A.R.V.I.S. Portfolio Dashboard",
            "J.A.R.V.I.S.",
            "READY FOR MANUAL USE",
            "Today's Manual Plan",
            "Market Headlines",
            "Portfolio Health",
            "What Changed Since Last Time",
            "Last Session",
            "Market Movement",
            "Manual Holdings Summary",
            "System Checks / Safety",
            "Universe Explorer",
            "jarvis-shell",
            "hud-hero",
            "orbital-core",
            "orbit-ring",
            "headline-ticker",
            "ticker-scroll",
            "motion-panel-enter",
        ):
            self.assertIn(marker, html)

    def test_dashboard_contract_delegates_to_premium_renderer(self) -> None:
        html = render_dashboard_html(_dashboard_fixture())

        self.assertIn("Premium orbital portfolio command center", html)
        self.assertIn("glass-panel", html)
        self.assertIn("Market Headlines", html)

    def test_safety_language_uses_manual_review_terms(self) -> None:
        html = render_command_center_dashboard_html(_dashboard_fixture())

        self.assertIn("Prepare Manual Review", html)
        self.assertIn("No broker", html)
        self.assertIn("No credentials", html)
        self.assertIn("No order tickets", html)
        self.assertIn("No auto-approval", html)
        for forbidden in (
            "Rebalance Portfolio",
            "Execute trade",
            "Recommendation queued for execution",
            "Buy now",
            "Sell now",
            "Liquidate",
        ):
            self.assertNotIn(forbidden, html)

    def test_command_center_gate_ready(self) -> None:
        html = render_command_center_dashboard_html(_dashboard_fixture())
        result = build_command_center_dashboard_result(html)

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.command_center_ready)
        self.assertTrue(result.premium_design_system_present)
        self.assertTrue(result.dashboard_markers_present)
        self.assertTrue(result.safety_markers_present)
        self.assertTrue(result.motion_markers_present)
        self.assertTrue(result.manual_only)
        self.assertTrue(result.execution_forbidden)
        self.assertEqual(result.blockers, [])

    def test_operator_route_works(self) -> None:
        html = render_command_center_dashboard_html(_dashboard_fixture())
        with patch(
            "jarvis.runtime.premium_command_center_dashboard.build_command_center_dashboard_result",
            return_value=build_command_center_dashboard_result(html),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--command-center-dashboard"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V162_0_IRON_MAN_COMMAND_CENTER_DASHBOARD_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
