from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.active_runtime_surface_redundancy_audit import (
    DEFAULT_REPORT_PATH,
    build_active_runtime_surface_redundancy_audit_result,
    format_active_runtime_surface_redundancy_audit,
)


class JarvisV630ActiveRuntimeSurfaceRedundancyAuditTests(unittest.TestCase):
    def test_audit_is_read_only_and_reports_safe_runtime_surface(self) -> None:
        result = build_active_runtime_surface_redundancy_audit_result(
            current_date="2026-06-17",
            repo_root=".",
            write_report=False,
        )

        self.assertEqual(
            result["status"],
            "JARVIS_V63_0_ACTIVE_RUNTIME_SURFACE_REDUNDANCY_AUDIT_READY_SAFE",
        )
        self.assertGreaterEqual(result["tracked_file_count"], 1)
        self.assertIn("jarvis/runtime/operator.py", result["active_runtime_modules"])
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["runtime_behavior_mutation"])
        self.assertFalse(result["allocation_mutation"])
        self.assertFalse(result["approval_ticket_mutation"])
        self.assertFalse(result["buy_request_created"])
        self.assertTrue(result["broker_connection_forbidden"])
        self.assertTrue(result["credentials_forbidden"])
        self.assertTrue(result["order_creation_forbidden"])
        self.assertTrue(result["no_trades_executed"])

    def test_write_report_is_generated_output_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = "outputs/active_runtime_surface_redundancy_audit_latest.json"

            result = build_active_runtime_surface_redundancy_audit_result(
                current_date="2026-06-17",
                repo_root=tmp,
                write_report=True,
                report_path=report_path,
            )

            written = Path(tmp) / report_path
            self.assertTrue(result["report_written"])
            self.assertTrue(written.exists())
            outputs = {item["path"]: item for item in result["generated_output_files"]}
            self.assertTrue(outputs[report_path]["exists"])
            self.assertFalse(outputs[report_path]["tracked"])

    def test_formatter_contains_cleanup_warning_without_deletion(self) -> None:
        result = build_active_runtime_surface_redundancy_audit_result(
            current_date="2026-06-17",
            repo_root=".",
            write_report=False,
            report_path=DEFAULT_REPORT_PATH,
        )
        formatted = format_active_runtime_surface_redundancy_audit(result)

        self.assertIn("ACTIVE RUNTIME SURFACE + REDUNDANCY AUDIT", formatted)
        self.assertIn("deletion performed: False", formatted)
        self.assertIn("runtime behavior mutation: False", formatted)
        self.assertIn("do not remove legacy modules", formatted.lower())


if __name__ == "__main__":
    unittest.main()
