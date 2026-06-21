from __future__ import annotations

import contextlib
import io
import unittest

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.portfolio_orbit_view import build_portfolio_orbit_view_result, render_portfolio_orbit_view
from jarvis.runtime.premium_visual_parity_pass import (
    FORBIDDEN_DASHBOARD_LABELS,
    STATUS_READY,
    build_premium_visual_parity_pass_result,
)


class JarvisV167PremiumVisualParityPassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dashboard_html = render_dashboard_html(build_dashboard_contract_result(current_date="2026-06-21"))
        cls.orbit_html = render_portfolio_orbit_view(build_portfolio_orbit_view_result(current_date="2026-06-21"))
        cls.result = build_premium_visual_parity_pass_result(current_date="2026-06-21")

    def test_dashboard_has_target_command_center_structure(self) -> None:
        for marker in (
            "top-hud",
            "J.A.R.V.I.S.",
            "PORTFOLIO OS",
            "READY FOR MANUAL USE",
            "Manual-only",
            "No broker",
            "No credentials",
            "No orders",
            "No trades",
            "Data Feed",
            "Security",
            "left-nav-rail",
            "Portfolio Orbit",
            "dashboard-orbit",
            "dashboard-core",
            "dashboard-planet",
            "selected-asset-telemetry",
            "Today's Manual Plan",
            "Portfolio Health",
            "What Changed",
            "System Checks",
            "Market Movement",
            "Market Headlines",
            "assistant chat voice panel",
        ):
            self.assertIn(marker, self.dashboard_html)

    def test_dashboard_removes_internal_and_execution_labels(self) -> None:
        lowered = self.dashboard_html.lower()
        for forbidden in FORBIDDEN_DASHBOARD_LABELS:
            self.assertNotIn(forbidden, lowered)

        for friendly in ("Needs quote source", "Fresh trusted public quote", "No Action Taken", "Evidence Summary"):
            self.assertIn(friendly, self.dashboard_html)

    def test_orbit_page_uses_polished_sanitized_visual_language(self) -> None:
        self.assertIn("Portfolio Orbit", self.orbit_html)
        self.assertIn("needs-review selected", self.orbit_html)
        self.assertIn("Fresh trusted quote context", self.orbit_html)
        self.assertIn("Needs quote source", self.orbit_html)
        self.assertNotIn("partial_or_unavailable", self.orbit_html)
        self.assertNotIn("tradable_instrument_trusted_quote", self.orbit_html)
        self.assertNotIn("etf_fund_candidate_missing_quote_source", self.orbit_html)

    def test_visual_parity_result_is_ready_and_safe(self) -> None:
        result = self.result

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.visual_parity_ready)
        self.assertTrue(result.dashboard_target_structure_ready)
        self.assertTrue(result.dashboard_forbidden_labels_absent)
        self.assertTrue(result.orbit_visual_polish_ready)
        self.assertTrue(result.chat_hud_consistent)
        self.assertTrue(result.universe_surface_consistent)
        self.assertTrue(result.instruments_surface_consistent)
        self.assertTrue(result.portfolio_health_surface_consistent)
        self.assertTrue(result.manual_only)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.broker_connection_enabled)
        self.assertFalse(result.credentials_required)
        self.assertFalse(result.account_login_enabled)
        self.assertFalse(result.private_account_ingestion_enabled)
        self.assertFalse(result.buy_sell_request_created)
        self.assertFalse(result.order_ticket_created)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_created)
        self.assertFalse(result.auto_approval_enabled)
        self.assertFalse(result.approval_mutation)
        self.assertFalse(result.allocation_mutation)

    def test_operator_route_works(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime_operator.main(["--premium-visual-parity-pass"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V167_0_PREMIUM_VISUAL_PARITY_PASS_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
