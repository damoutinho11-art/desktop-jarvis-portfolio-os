from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.final_v5_archive_execution_plan import (
    DEFAULT_ARCHIVE_ROOT,
    DEFAULT_OUTPUT_PATH,
    PLAN_READY,
    STATUS_READY,
    build_final_v5_archive_execution_plan_result,
)


class JarvisV770FinalV5ArchiveExecutionPlanTests(unittest.TestCase):
    def test_plan_is_unlocked_but_non_mutating(self) -> None:
        result = build_final_v5_archive_execution_plan_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.plan_status, PLAN_READY)
        self.assertTrue(result.plan_unlocked)
        self.assertFalse(result.execution_performed)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertTrue(result.safety_check_blocked_execution)

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

    def test_expected_final_v5_item_counts(self) -> None:
        result = build_final_v5_archive_execution_plan_result(current_date="2026-06-17")

        self.assertEqual(result.module_source_count, 12)
        self.assertEqual(result.blocking_test_source_count, 12)
        self.assertEqual(result.total_plan_item_count, 24)
        self.assertEqual(result.missing_item_count, 0)
        self.assertEqual(result.pending_move_count + result.already_archived_count, 24)

    def test_plan_destinations_are_under_final_v5_archive_root(self) -> None:
        result = build_final_v5_archive_execution_plan_result(current_date="2026-06-17")

        self.assertEqual(result.archive_root, DEFAULT_ARCHIVE_ROOT)
        for item in result.plan_items:
            self.assertTrue(item["destination_path"].startswith(DEFAULT_ARCHIVE_ROOT + "/"))
            self.assertIn("/jarvis/", item["destination_path"])

    def test_plan_uses_v76_replacement_coverage_without_unlocking_archive_in_v76(self) -> None:
        result = build_final_v5_archive_execution_plan_result(current_date="2026-06-17")

        self.assertEqual(result.replacement_record_count, 12)
        self.assertEqual(result.coverage_record_count, result.covered_record_count)
        self.assertEqual(result.archive_unlocked_record_count, 0)

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/final_v5_archive_execution_plan_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "v77_final_v5_plan.json"
            result = build_final_v5_archive_execution_plan_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("plan_items", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
