from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.cockpit_dashboard_hard_rebuild import COCKPIT_STRUCTURAL_CLASSES
from jarvis.runtime.strict_visual_layout_gate import (
    FINAL_VERDICT_READY,
    REQUIRED_ROUTE_KEYS,
    STATUS_READY,
    StrictVisualLayoutGateResult,
    build_strict_visual_layout_gate_result,
)


class JarvisV170StrictVisualLayoutGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_strict_visual_layout_gate_result(current_date="2026-06-21")

    def test_strict_visual_layout_gate_ready(self) -> None:
        result = self.result

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.final_verdict, FINAL_VERDICT_READY)
        self.assertTrue(result.strict_visual_layout_ready)
        self.assertFalse(result.blockers)

    def test_dashboard_contains_required_cockpit_classes(self) -> None:
        self.assertEqual(self.result.proof.get("cockpit_missing_structural_classes"), [])
        self.assertEqual(len(COCKPIT_STRUCTURAL_CLASSES), 12)

    def test_dashboard_contains_required_target_markers(self) -> None:
        self.assertEqual(self.result.proof.get("cockpit_missing_text_markers"), [])
        self.assertEqual(self.result.proof.get("cockpit_forbidden_labels_found"), [])

    def test_routes_existing_gates_and_safety_pass(self) -> None:
        result = self.result

        self.assertTrue(result.route_registry_ready)
        self.assertTrue(result.route_render_surfaces_ready)
        self.assertTrue(result.health_route_ready)
        self.assertTrue(result.api_status_ready)
        self.assertTrue(result.api_chat_ready)
        self.assertTrue(result.v156_experience_gate_ready)
        self.assertTrue(result.v166_premium_motion_gate_ready)
        self.assertTrue(result.v168_visual_acceptance_gate_ready)
        self.assertTrue(result.safety_check_blocks_execution)

        self.assertEqual(result.proof.get("missing_routes"), [])
        self.assertGreaterEqual(len(REQUIRED_ROUTE_KEYS), 12)

    def test_safety_invariants_true(self) -> None:
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
        fixture = StrictVisualLayoutGateResult(
            status=STATUS_READY,
            final_verdict=FINAL_VERDICT_READY,
            strict_visual_layout_ready=True,
            cockpit_layout_contract_ready=True,
            structural_classes_present=True,
            dashboard_text_markers_present=True,
            forbidden_labels_absent=True,
            route_registry_ready=True,
            route_render_surfaces_ready=True,
            health_route_ready=True,
            api_status_ready=True,
            api_chat_ready=True,
            v156_experience_gate_ready=True,
            v166_premium_motion_gate_ready=True,
            v168_visual_acceptance_gate_ready=True,
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
        with patch("jarvis.runtime.strict_visual_layout_gate.build_strict_visual_layout_gate_result", return_value=fixture):
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--strict-visual-layout-gate"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V170_0_STRICT_VISUAL_LAYOUT_GATE_READY_SAFE", output.getvalue())
        self.assertIn("READY_FOR_COCKPIT_VISUAL_REVIEW", output.getvalue())


if __name__ == "__main__":
    unittest.main()
