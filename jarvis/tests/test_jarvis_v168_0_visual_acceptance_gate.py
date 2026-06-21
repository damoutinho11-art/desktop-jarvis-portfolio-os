from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.premium_visual_parity_pass import FORBIDDEN_DASHBOARD_LABELS
from jarvis.runtime.visual_acceptance_gate import (
    FINAL_VERDICT_READY,
    STATUS_READY,
    VisualAcceptanceGateResult,
    build_visual_acceptance_gate_result,
)


class JarvisV168VisualAcceptanceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dashboard_html = render_dashboard_html(build_dashboard_contract_result(current_date="2026-06-21"))
        cls.result = build_visual_acceptance_gate_result(current_date="2026-06-21")

    def test_final_visual_acceptance_gate_ready(self) -> None:
        result = self.result

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.final_verdict, FINAL_VERDICT_READY)
        self.assertTrue(result.visual_acceptance_ready)
        self.assertFalse(result.blockers)

    def test_dashboard_target_markers_present_and_forbidden_labels_absent(self) -> None:
        for marker in (
            "J.A.R.V.I.S.",
            "PORTFOLIO OS",
            "READY FOR MANUAL USE",
            "Manual-only",
            "No broker",
            "No credentials",
            "No orders",
            "No trades",
            "Portfolio Orbit",
            "selected-asset-telemetry",
            "Today's Manual Plan",
            "Portfolio Health",
            "What Changed",
            "System Checks",
            "Market Movement",
            "Market Headlines",
            "assistant chat voice panel",
            "Prepare Manual Review",
        ):
            self.assertIn(marker, self.dashboard_html)

        lowered = self.dashboard_html.lower()
        for forbidden in FORBIDDEN_DASHBOARD_LABELS:
            self.assertNotIn(forbidden, lowered)

    def test_gate_confirms_routes_gates_intelligence_and_safety(self) -> None:
        result = self.result

        self.assertTrue(result.dashboard_markers_present)
        self.assertTrue(result.dashboard_forbidden_labels_absent)
        self.assertTrue(result.route_registry_ready)
        self.assertTrue(result.route_render_surfaces_ready)
        self.assertTrue(result.api_status_ready)
        self.assertTrue(result.api_chat_ready)
        self.assertTrue(result.v156_experience_gate_ready)
        self.assertTrue(result.v166_premium_motion_gate_ready)
        self.assertTrue(result.v167_visual_parity_ready)
        self.assertTrue(result.v157_v160_intelligence_ready)
        self.assertTrue(result.safety_check_blocks_execution)

    def test_gate_safety_invariants_true(self) -> None:
        result = self.result

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
        fixture = VisualAcceptanceGateResult(
            status=STATUS_READY,
            final_verdict=FINAL_VERDICT_READY,
            visual_acceptance_ready=True,
            dashboard_markers_present=True,
            dashboard_forbidden_labels_absent=True,
            route_registry_ready=True,
            route_render_surfaces_ready=True,
            api_status_ready=True,
            api_chat_ready=True,
            v156_experience_gate_ready=True,
            v166_premium_motion_gate_ready=True,
            v167_visual_parity_ready=True,
            v157_v160_intelligence_ready=True,
            safety_check_blocks_execution=True,
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
        with patch("jarvis.runtime.visual_acceptance_gate.build_visual_acceptance_gate_result", return_value=fixture):
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--visual-acceptance-gate"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V168_0_FINAL_VISUAL_ACCEPTANCE_GATE_READY_SAFE", output.getvalue())
        self.assertIn("READY_FOR_PREMIUM_VISUAL_ACCEPTANCE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
