from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.non_active_archive_candidate_report import (
    DEFAULT_OUTPUT_PATH,
    REPORT_READY,
    STATUS_READY,
    build_non_active_archive_candidate_report_result,
)


class JarvisV680NonActiveArchiveCandidateReportTests(unittest.TestCase):
    def test_report_identifies_non_active_candidates_without_mutation(self) -> None:
        result = build_non_active_archive_candidate_report_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.report_status, REPORT_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)

        self.assertGreater(result.active_import_closure_count, 0)
        self.assertGreater(result.non_active_versioned_module_count, 0)
        self.assertGreater(result.archive_candidate_test_count, 0)
        self.assertGreater(result.non_active_data_config_candidate_count, 0)

        self.assertIn(
            "jarvis/runtime/operator.py",
            result.active_runtime_keep_paths,
        )
        self.assertIn(
            "jarvis/runtime/import_closure_safe_archive_plan.py",
            result.active_runtime_keep_paths,
        )
        self.assertIn(
            "jarvis/jarvis_v13_0_single_command_operator_launcher.py",
            result.non_active_versioned_module_paths,
        )

        self.assertFalse(result.deletion_performed)
        self.assertFalse(result.archive_performed)
        self.assertFalse(result.runtime_behavior_mutation)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.private_account_data_ingestion)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_validation_tests_are_kept_separately_from_archive_candidates(self) -> None:
        result = build_non_active_archive_candidate_report_result(current_date="2026-06-17")

        self.assertIn(
            "jarvis/tests/test_jarvis_v67_0_import_closure_relative_import_precision.py",
            result.validation_test_keep_paths,
        )
        self.assertNotIn(
            "jarvis/tests/test_jarvis_v67_0_import_closure_relative_import_precision.py",
            result.archive_candidate_test_paths,
        )

    def test_write_report_is_explicit_and_default_path_is_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/non_active_archive_candidate_report_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            result = build_non_active_archive_candidate_report_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("non_active_versioned_module_paths", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
