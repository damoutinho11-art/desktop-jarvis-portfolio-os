from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.remaining_python_archive_risk_audit import (
    AUDIT_READY,
    DEFAULT_OUTPUT_PATH,
    STATUS_READY,
    build_remaining_python_archive_risk_audit_result,
)


class JarvisV710RemainingPythonArchiveRiskAuditTests(unittest.TestCase):
    def test_remaining_python_audit_is_non_mutating_and_resolved(self) -> None:
        result = build_remaining_python_archive_risk_audit_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.audit_status, AUDIT_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)

        self.assertGreater(result.active_import_closure_count, 0)
        self.assertGreater(result.active_runtime_module_count, 0)
        self.assertGreater(result.active_versioned_module_count, 0)

        self.assertGreaterEqual(result.remaining_non_active_versioned_module_count, 0)
        self.assertGreaterEqual(result.validation_blocked_module_count, 0)
        self.assertGreaterEqual(result.next_safe_module_candidate_count, 0)
        self.assertGreaterEqual(result.remaining_non_active_test_count, 0)
        self.assertGreaterEqual(result.validation_blocked_test_count, 0)
        self.assertGreaterEqual(result.next_safe_test_candidate_count, 0)

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
        self.assertEqual(result.blockers, [])

    def test_current_validation_tests_are_kept_and_not_safe_candidates(self) -> None:
        result = build_remaining_python_archive_risk_audit_result(current_date="2026-06-17")

        self.assertIn(
            "jarvis/tests/test_jarvis_v70_0_reversible_report_archive_execution.py",
            result.validation_test_keep_paths,
        )
        self.assertNotIn(
            "jarvis/tests/test_jarvis_v70_0_reversible_report_archive_execution.py",
            result.next_safe_test_candidate_paths,
        )

    def test_safe_candidates_are_not_active_or_validation_imported(self) -> None:
        result = build_remaining_python_archive_risk_audit_result(current_date="2026-06-17")

        active = set(result.active_import_closure_paths)
        validation_imported = set(result.validation_imported_module_paths)
        validation_tests = set(result.validation_test_keep_paths)

        self.assertTrue(set(result.next_safe_module_candidate_paths).isdisjoint(active))
        self.assertTrue(set(result.next_safe_module_candidate_paths).isdisjoint(validation_imported))
        self.assertTrue(set(result.next_safe_test_candidate_paths).isdisjoint(active))
        self.assertTrue(set(result.next_safe_test_candidate_paths).isdisjoint(validation_tests))

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/remaining_python_archive_risk_audit_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "remaining_python_audit.json"
            result = build_remaining_python_archive_risk_audit_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("next_safe_module_candidate_paths", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
