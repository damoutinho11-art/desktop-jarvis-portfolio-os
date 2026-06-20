from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.post_app_acceptance_gate import (
    STATUS_READY,
    build_post_app_acceptance_gate_result,
    format_post_app_acceptance_gate,
)


def _daily() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V129_0_DAILY_OPERATOR_READY_SAFE",
        daily_operator_ready=True,
        final_acceptance_ready=True,
        blockers=[],
        warnings=[],
        proof={
            "dashboard_status": "JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE",
            "holdings_status": "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE",
            "holdings_ready": False,
            "holdings_file_exists": False,
        },
    )


def _product_api() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V96_0_PRODUCT_API_LAYER_READY_SAFE",
        api_ready=True,
        blockers=[],
        manual_holdings={
            "status": "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE",
            "holdings_ready": False,
            "file_exists": False,
        },
    )


def _dashboard() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE",
        dashboard_contract_ready=True,
        blockers=[],
        sections={
            "manual_holdings": {
                "title": "Manual Holdings",
                "status": "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE",
                "holdings_ready": False,
                "file_exists": False,
            }
        },
    )


def _runbook() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V133_0_USER_RUNBOOK_APP_UX_READY_SAFE",
        runbook_ready=True,
        blockers=[],
    )


class JarvisV134PostAppAcceptanceGateTests(unittest.TestCase):
    def _patch_ready_dependencies(self):
        return (
            patch("jarvis.runtime.post_app_acceptance_gate.build_daily_operator_result", return_value=_daily()),
            patch("jarvis.runtime.post_app_acceptance_gate.build_product_api_result", return_value=_product_api()),
            patch("jarvis.runtime.post_app_acceptance_gate.build_dashboard_contract_result", return_value=_dashboard()),
            patch("jarvis.runtime.post_app_acceptance_gate.build_user_runbook_result", return_value=_runbook()),
            patch(
                "jarvis.runtime.post_app_acceptance_gate.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
        )

    def test_post_app_acceptance_gate_ready_safe_even_when_holdings_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "missing_manual_holdings.local.json"
            patches = self._patch_ready_dependencies()
            with contextlib.ExitStack() as stack:
                for item in patches:
                    stack.enter_context(item)
                result = build_post_app_acceptance_gate_result(
                    current_date="2026-06-20",
                    manual_holdings_path=Path(tmp) / "manual_holdings.local.json",
                    missing_holdings_probe_path=missing_path,
                )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.post_app_acceptance_ready)
        self.assertTrue(result.daily_operator_ready)
        self.assertTrue(result.launcher_files_exist)
        self.assertTrue(result.final_product_acceptance_ready)
        self.assertTrue(result.dashboard_ready)
        self.assertTrue(result.holdings_workflow_ready)
        self.assertTrue(result.holdings_missing_handled_safely)
        self.assertTrue(result.product_api_includes_holdings)
        self.assertTrue(result.dashboard_includes_holdings)
        self.assertTrue(result.user_runbook_ready)
        self.assertTrue(result.safety_check_blocks_execution)
        self.assertEqual(result.blockers, [])
        self.assertEqual(result.proof["missing_holdings_status"], "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE")

    def test_format_is_user_facing_and_lists_required_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "missing_manual_holdings.local.json"
            patches = self._patch_ready_dependencies()
            with contextlib.ExitStack() as stack:
                for item in patches:
                    stack.enter_context(item)
                result = build_post_app_acceptance_gate_result(
                    current_date="2026-06-20",
                    missing_holdings_probe_path=missing_path,
                )

        text = format_post_app_acceptance_gate(result)

        self.assertIn("J.A.R.V.I.S. POST-APP ACCEPTANCE GATE", text)
        self.assertIn("post-app acceptance ready: True", text)
        self.assertIn("daily operator ready: True", text)
        self.assertIn("holdings missing handled safely: True", text)
        self.assertIn("product API includes holdings: True", text)
        self.assertIn("dashboard includes holdings: True", text)
        self.assertIn("safety check blocks execution: True", text)
        self.assertIn("- none", text)
        self.assertIn("no broker, credential, order, trade, or auto-approval", text)

    def test_operator_routes_post_app_acceptance_gate_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "missing_manual_holdings.local.json"
            patches = self._patch_ready_dependencies()
            with contextlib.ExitStack() as stack:
                for item in patches:
                    stack.enter_context(item)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = runtime_operator.main(
                        [
                            "--post-app-acceptance-gate",
                            "--current-date",
                            "2026-06-20",
                            "--missing-holdings-probe-path",
                            str(missing_path),
                        ]
                    )

        self.assertEqual(code, 0)
        text = output.getvalue()
        self.assertIn("J.A.R.V.I.S. POST-APP ACCEPTANCE GATE", text)
        self.assertIn("JARVIS_V134_0_POST_APP_ACCEPTANCE_GATE_READY_SAFE", text)

    def test_safety_check_failure_blocks_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "missing_manual_holdings.local.json"
            patches = list(self._patch_ready_dependencies())
            patches[-1] = patch(
                "jarvis.runtime.post_app_acceptance_gate.build_safety_check_console_output",
                return_value="not blocked",
            )
            for item in patches:
                item.__enter__()
            try:
                result = build_post_app_acceptance_gate_result(
                    current_date="2026-06-20",
                    missing_holdings_probe_path=missing_path,
                )
            finally:
                for item in reversed(patches):
                    item.__exit__(None, None, None)

        self.assertFalse(result.post_app_acceptance_ready)
        self.assertIn("safety_check_did_not_block_execution", result.blockers)

    def test_runtime_surface_tracks_post_app_gate_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_post_app_acceptance_gate_module"], "jarvis.runtime.post_app_acceptance_gate")


if __name__ == "__main__":
    unittest.main()
