from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.final_v5_archive_execution import (
    DEFAULT_OUTPUT_PATH,
    EXECUTION_READY,
    STATUS_READY,
    build_final_v5_archive_execution_result,
)


class JarvisV780FinalV5ArchiveExecutionTests(unittest.TestCase):
    def test_execution_is_verified_after_reversible_git_mv(self) -> None:
        result = build_final_v5_archive_execution_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.execution_status, EXECUTION_READY)
        self.assertTrue(result.execution_verified)
        self.assertEqual(result.total_plan_item_count, 24)
        self.assertEqual(result.pending_move_count, 0)
        self.assertEqual(result.already_archived_count, 24)
        self.assertEqual(result.missing_item_count, 0)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertTrue(result.safety_check_blocked_execution)
        self.assertEqual(result.blockers, [])

    def test_archive_flags_are_honest_but_runtime_safety_still_intact(self) -> None:
        result = build_final_v5_archive_execution_result(current_date="2026-06-17")

        self.assertFalse(result.deletion_performed)
        self.assertTrue(result.archive_performed)
        self.assertTrue(result.file_move_performed)
        self.assertFalse(result.runtime_behavior_mutation)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.private_account_data_ingestion)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_final_v5_sources_are_archived_not_deleted(self) -> None:
        result = build_final_v5_archive_execution_result(current_date="2026-06-17")

        self.assertEqual(len(result.archived_items), 24)
        for item in result.archived_items:
            self.assertFalse(Path(item["source_path"]).exists())
            self.assertTrue(Path(item["destination_path"]).exists())

    def test_v77_plan_is_now_already_archived_not_pending(self) -> None:
        result = build_final_v5_archive_execution_result(current_date="2026-06-17")

        self.assertTrue(result.archived_items)
        self.assertTrue(all(item["already_archived"] for item in result.archived_items))
        self.assertTrue(all(not item["pending_move"] for item in result.archived_items))

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/final_v5_archive_execution_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "v78_execution.json"
            result = build_final_v5_archive_execution_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("archived_items", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
