from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.cockpit_dashboard_hard_rebuild import (
    COCKPIT_STRUCTURAL_CLASSES,
    FINAL_VERDICT_READY,
    FORBIDDEN_DASHBOARD_LABELS,
    STATUS_READY,
    CockpitDashboardHardRebuildResult,
    build_cockpit_dashboard_hard_rebuild_result,
)
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html


class JarvisV169CockpitDashboardHardRebuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dashboard_html = render_dashboard_html(build_dashboard_contract_result(current_date="2026-06-21"))
        cls.result = build_cockpit_dashboard_hard_rebuild_result(
            current_date="2026-06-21",
            dashboard_html=cls.dashboard_html,
        )

    def test_cockpit_dashboard_hard_rebuild_ready(self) -> None:
        result = self.result

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.final_verdict, FINAL_VERDICT_READY)
        self.assertTrue(result.cockpit_dashboard_ready)
        self.assertFalse(result.blockers)

    def test_dashboard_has_strict_cockpit_structure(self) -> None:
        for class_name in COCKPIT_STRUCTURAL_CLASSES:
            self.assertIn(class_name, self.dashboard_html)

        for marker in (
            "grid-template-columns:72px",
            "grid-template-rows:78px",
            "minmax(620px,1fr)",
            "minmax(360px,430px)",
        ):
            self.assertIn(marker, self.dashboard_html.replace(" ", ""))

    def test_dashboard_first_viewport_markers_present(self) -> None:
        for marker in (
            "J.A.R.V.I.S.",
            "PORTFOLIO OS",
            "READY FOR MANUAL USE",
            "Manual-only",
            "No broker",
            "No credentials",
            "No orders",
            "No trades",
            "Data Feed",
            "Local Cache",
            "Portfolio Core",
            "BTC",
            "ETH",
            "VWCE",
            "IS3Q.DE",
            "MSFT",
            "J.A.R.V.I.S. Note",
            "Today's Manual Plan",
            "Portfolio Health",
            "What Changed",
            "System Checks",
            "Market Movement",
            "Market Headlines",
            "assistant/chat/voice marker",
        ):
            self.assertIn(marker, self.dashboard_html)

    def test_dashboard_forbidden_labels_absent(self) -> None:
        lowered = self.dashboard_html.lower()
        for forbidden in FORBIDDEN_DASHBOARD_LABELS:
            self.assertNotIn(forbidden, lowered)

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
        fixture = CockpitDashboardHardRebuildResult(
            status=STATUS_READY,
            final_verdict=FINAL_VERDICT_READY,
            cockpit_dashboard_ready=True,
            structural_classes_present=True,
            compact_grid_contract_present=True,
            target_viewport_sections_present=True,
            forbidden_labels_absent=True,
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
        with patch("jarvis.runtime.cockpit_dashboard_hard_rebuild.build_cockpit_dashboard_hard_rebuild_result", return_value=fixture):
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--cockpit-dashboard-hard-rebuild"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V169_0_COCKPIT_DASHBOARD_HARD_REBUILD_READY_SAFE", output.getvalue())
        self.assertIn("READY_FOR_COCKPIT_DASHBOARD_HARD_REBUILD", output.getvalue())


if __name__ == "__main__":
    unittest.main()
