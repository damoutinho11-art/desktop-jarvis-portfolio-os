from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.dashboard_noise_audit import (
    REQUIRED_CALM_MARKERS,
    STATUS_READY,
    build_dashboard_noise_audit_result,
    format_dashboard_noise_audit,
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
    return "\n".join([*REQUIRED_CALM_MARKERS, "<code>--safety-check</code>"])


class JarvisV139DashboardNoiseAuditTests(unittest.TestCase):
    def _patch_ready(self, html: str | None = None):
        return (
            patch("jarvis.runtime.dashboard_noise_audit.build_dashboard_contract_result", return_value=_dashboard()),
            patch("jarvis.runtime.dashboard_noise_audit.render_dashboard_html", return_value=html or _calm_html()),
            patch(
                "jarvis.runtime.dashboard_noise_audit.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
        )

    def test_dashboard_noise_audit_ready_safe(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            result = build_dashboard_noise_audit_result(current_date="2026-06-20")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.dashboard_noise_audit_ready)
        self.assertTrue(result.read_only)
        self.assertTrue(result.no_output_write_required)
        self.assertTrue(result.calm_markers_present)
        self.assertTrue(result.noisy_markers_absent)
        self.assertTrue(result.safety_check_blocks_execution)
        self.assertEqual(result.blockers, [])

    def test_noisy_dashboard_marker_blocks(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready(html=_calm_html() + "\nREADY_WITH_AUDIT_WARNINGS"):
                stack.enter_context(item)
            result = build_dashboard_noise_audit_result(current_date="2026-06-20")

        self.assertFalse(result.dashboard_noise_audit_ready)
        self.assertIn("noisy_dashboard_markers_found", result.blockers)

    def test_format_reports_safety_assertions(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            text = format_dashboard_noise_audit(build_dashboard_noise_audit_result(current_date="2026-06-20"))

        self.assertIn("J.A.R.V.I.S. DASHBOARD NOISE AUDIT", text)
        self.assertIn("read-only: True", text)
        self.assertIn("manual_only: True", text)
        self.assertIn("broker_connection_enabled: False", text)
        self.assertIn("- none", text)

    def test_operator_routes_dashboard_noise_audit(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--dashboard-noise-audit", "--current-date", "2026-06-20"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V139_0_DASHBOARD_NOISE_AUDIT_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
