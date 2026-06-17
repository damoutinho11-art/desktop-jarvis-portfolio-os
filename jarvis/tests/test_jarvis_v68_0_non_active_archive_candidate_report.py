from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.non_active_archive_candidate_report import (
    build_non_active_archive_candidate_report_result,
)


class JarvisV680NonActiveArchiveCandidateReportTests(unittest.TestCase):
    def test_non_active_report_is_non_mutating_and_resolved_after_archives(self) -> None:
        result = build_non_active_archive_candidate_report_result(current_date="2026-06-17")

        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertGreater(result.tracked_file_count, 0)
        self.assertGreater(result.active_import_closure_count, 0)
        self.assertGreaterEqual(result.non_active_versioned_module_count, 0)
        self.assertGreaterEqual(result.archive_candidate_test_count, 0)
        self.assertGreaterEqual(result.non_active_data_config_candidate_count, 0)

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
        self.assertEqual(result.blockers, [])

    def test_candidates_do_not_overlap_active_runtime_keep_paths(self) -> None:
        result = build_non_active_archive_candidate_report_result(current_date="2026-06-17")

        active = set(result.active_runtime_keep_paths)
        modules = set(result.non_active_versioned_module_paths)
        tests = set(result.archive_candidate_test_paths)

        self.assertTrue(modules.isdisjoint(active))
        self.assertTrue(tests.isdisjoint(active))
        self.assertNotIn("jarvis/runtime/operator.py", modules)
        self.assertNotIn("jarvis_operator.py", modules)

    def test_report_only_files_may_be_archived_already(self) -> None:
        result = build_non_active_archive_candidate_report_result(current_date="2026-06-17")

        archived_report = Path(
            "archive/non_active/v70_report_only_python_safe/"
            "jarvis/jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py"
        )
        if archived_report.exists():
            self.assertNotIn(
                "jarvis/jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py",
                result.non_active_versioned_module_paths,
            )

    def test_write_report_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "non_active_report.json"
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
