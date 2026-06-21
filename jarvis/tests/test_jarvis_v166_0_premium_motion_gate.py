from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.local_server import ROUTES, render_portfolio_health_page, render_settings_page, render_universe_page
from jarvis.runtime.premium_motion_gate import (
    FINAL_VERDICT_READY,
    STATUS_READY,
    PremiumMotionGateResult,
    build_premium_motion_gate_result,
)


class JarvisV166PremiumMotionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_premium_motion_gate_result(current_date="2026-06-21")

    def test_final_gate_reports_ready_verdict(self) -> None:
        result = self.result

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.final_verdict, FINAL_VERDICT_READY)
        self.assertTrue(result.premium_motion_gate_ready)
        self.assertFalse(result.blockers)

    def test_gate_confirms_premium_ui_and_motion_surfaces(self) -> None:
        result = self.result

        self.assertTrue(result.premium_design_system_present)
        self.assertTrue(result.command_center_dashboard_present)
        self.assertTrue(result.portfolio_orbit_view_present)
        self.assertTrue(result.orbital_instrument_detail_present)
        self.assertTrue(result.chat_voice_hud_polish_present)
        self.assertTrue(result.jarvis_orb_present)
        self.assertTrue(result.ticker_present)
        self.assertTrue(result.session_memory_visible)
        self.assertTrue(result.what_changed_visible)
        self.assertTrue(result.top_navigation_ready)

    def test_gate_confirms_routes_and_intelligence_foundation(self) -> None:
        result = self.result

        self.assertTrue(result.local_server_routes_ready)
        self.assertTrue(result.intelligence_routes_ready)
        self.assertTrue(result.v156_experience_gate_ready)
        for route in (
            "GET /health",
            "GET /dashboard",
            "GET /chat",
            "POST /api/chat",
            "GET /api/status",
            "GET /orbit",
            "GET /universe",
            "GET /instruments",
            "GET /portfolio-health",
            "GET /settings",
        ):
            self.assertIn(route, ROUTES)

        self.assertIn("Universe Explorer", render_universe_page())
        self.assertIn("Portfolio Health", render_portfolio_health_page(current_date="2026-06-21"))
        self.assertIn("Manual-Only Settings", render_settings_page())

    def test_safety_invariants_remain_true(self) -> None:
        result = self.result

        self.assertTrue(result.safety_check_blocks_execution)
        self.assertTrue(result.forbidden_capabilities_absent)
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
        fixture = PremiumMotionGateResult(
            status=STATUS_READY,
            final_verdict=FINAL_VERDICT_READY,
            premium_motion_gate_ready=True,
            premium_design_system_present=True,
            command_center_dashboard_present=True,
            portfolio_orbit_view_present=True,
            orbital_instrument_detail_present=True,
            chat_voice_hud_polish_present=True,
            jarvis_orb_present=True,
            ticker_present=True,
            session_memory_visible=True,
            what_changed_visible=True,
            top_navigation_ready=True,
            local_server_routes_ready=True,
            intelligence_routes_ready=True,
            v156_experience_gate_ready=True,
            safety_check_blocks_execution=True,
            forbidden_capabilities_absent=True,
            manual_only=True,
            execution_forbidden=True,
            broker_connection_enabled=False,
            credentials_required=False,
            account_login_enabled=False,
            private_account_ingestion_enabled=False,
            buy_sell_request_created=False,
            order_ticket_created=False,
            order_created=False,
            trade_created=False,
            auto_approval_enabled=False,
            approval_mutation=False,
            allocation_mutation=False,
            blockers=[],
            warnings=[],
            proof={},
        )
        output = io.StringIO()
        with patch("jarvis.runtime.premium_motion_gate.build_premium_motion_gate_result", return_value=fixture):
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--premium-motion-gate"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V166_0_FINAL_PREMIUM_MOTION_GATE_READY_SAFE", output.getvalue())
        self.assertIn("READY_FOR_PREMIUM_SAFE_JARVIS_OS", output.getvalue())


if __name__ == "__main__":
    unittest.main()
