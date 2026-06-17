from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime.product_mode_operator import (
    DEFAULT_OUTPUT_PATH,
    STATUS_READY,
    build_product_mode_result,
    main,
)


class JarvisV790ProductModeOperatorTests(unittest.TestCase):
    def test_today_mode_is_manual_safe_product_output(self) -> None:
        result = build_product_mode_result(mode="today", current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.mode, "today")
        self.assertTrue(result.product_ready_for_manual_use)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertTrue(result.safety_check_blocked_execution)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertEqual(result.blockers, [])

        self.assertFalse(result.deletion_performed)
        self.assertFalse(result.archive_performed)
        self.assertFalse(result.file_move_performed)
        self.assertFalse(result.runtime_behavior_mutation)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.private_account_data_ingestion)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_week_mode_surfaces_manual_action_lanes(self) -> None:
        result = build_product_mode_result(mode="week", current_date="2026-06-17")

        text = "\n".join(result.week_lines).lower()
        self.assertIn("crypto", text)
        self.assertIn("etf", text)
        self.assertIn("stock", text)
        self.assertIn("manual", text)

    def test_status_mode_reports_runtime_health(self) -> None:
        result = build_product_mode_result(mode="status", current_date="2026-06-17")

        text = "\n".join(result.status_lines).lower()
        self.assertIn("unresolved local imports", text)
        self.assertIn("components available", text)
        self.assertIn("full allocation blockers", text)

    def test_cli_routes_today_week_status(self) -> None:
        for flag, expected_title in [
            ("--today", "J.A.R.V.I.S. TODAY"),
            ("--week", "J.A.R.V.I.S. WEEK"),
            ("--status", "J.A.R.V.I.S. STATUS"),
        ]:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main([flag, "--current-date", "2026-06-17"])
            self.assertEqual(exit_code, 0)
            self.assertIn(expected_title, buffer.getvalue())

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/product_mode_operator_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "product_mode.json"
            result = build_product_mode_result(
                mode="today",
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("product_verdict", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
