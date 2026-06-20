from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.dashboard_calm_ui_freeze_gate import (
    REQUIRED_MARKERS,
    STATUS_READY,
    build_dashboard_calm_ui_freeze_gate_result,
    format_dashboard_calm_ui_freeze_gate,
)


def _dashboard() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V140_0_DASHBOARD_DAILY_UI_CLEANUP_READY_SAFE",
        dashboard_contract_ready=True,
        manual_only=True,
        blockers=[],
        warnings=[],
        sections={
            "safety": {
                "safety_check_blocked_execution": True,
                "manual_approval_required": True,
                "execution_forbidden": True,
                "broker_connection": False,
                "credentials_used": False,
                "order_created": False,
                "trade_executed": False,
            }
        },
    )


def _calm_html() -> str:
    return "\n".join(REQUIRED_MARKERS)


class JarvisV141DashboardCalmUiFreezeGateTests(unittest.TestCase):
    def _patch_ready(self, html: str | None = None):
        return (
            patch("jarvis.runtime.dashboard_calm_ui_freeze_gate.build_dashboard_contract_result", return_value=_dashboard()),
            patch("jarvis.runtime.dashboard_calm_ui_freeze_gate.render_dashboard_html", return_value=html or _calm_html()),
            patch(
                "jarvis.runtime.dashboard_calm_ui_freeze_gate.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
        )

    def test_calm_ui_freeze_gate_ready_safe(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            result = build_dashboard_calm_ui_freeze_gate_result(current_date="2026-06-20")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.calm_ui_freeze_gate_ready)
        self.assertTrue(result.dashboard_ready)
        self.assertTrue(result.required_markers_present)
        self.assertTrue(result.forbidden_markers_absent)
        self.assertTrue(result.safety_check_blocks_execution)
        self.assertEqual(result.blockers, [])

    def test_forbidden_marker_blocks(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready(html=_calm_html() + "\nplace order"):
                stack.enter_context(item)
            result = build_dashboard_calm_ui_freeze_gate_result(current_date="2026-06-20")

        self.assertFalse(result.calm_ui_freeze_gate_ready)
        self.assertIn("forbidden_calm_ui_markers_found", result.blockers)

    def test_format_lists_ready_verdict_and_safety(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            text = format_dashboard_calm_ui_freeze_gate(
                build_dashboard_calm_ui_freeze_gate_result(current_date="2026-06-20")
            )

        self.assertIn("J.A.R.V.I.S. FINAL CALM UI FREEZE GATE", text)
        self.assertIn("calm UI freeze gate ready: True", text)
        self.assertIn("manual_only: True", text)
        self.assertIn("auto_approval_enabled: False", text)

    def test_operator_routes_calm_ui_freeze_gate(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--dashboard-calm-ui-freeze-gate", "--current-date", "2026-06-20"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V141_0_FINAL_CALM_UI_FREEZE_GATE_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
