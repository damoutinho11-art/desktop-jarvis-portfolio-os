from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.next_safe_python_archive_execution_plan import (
    DEFAULT_ARCHIVE_ROOT,
    DEFAULT_OUTPUT_PATH,
    PLAN_READY,
    STATUS_READY,
    build_next_safe_python_archive_execution_plan_result,
)


class JarvisV720NextSafePythonArchiveExecutionPlanTests(unittest.TestCase):
    def test_plan_is_paired_non_mutating_and_resolved(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.plan_status, PLAN_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertGreater(result.next_safe_module_source_count, 0)
        self.assertGreater(result.total_plan_item_count, 0)

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

    def test_known_next_safe_module_and_matching_test_are_planned(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")
        sources = {item["source_path"] for item in result.plan_items}

        self.assertIn("jarvis/jarvis_v13_0_single_command_operator_launcher.py", sources)
        self.assertIn("jarvis/tests/test_jarvis_v13_0_single_command_operator_launcher.py", sources)

    def test_orphan_tests_for_active_modules_are_not_moved(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")
        sources = {item["source_path"] for item in result.plan_items}

        self.assertNotIn("jarvis/tests/test_jarvis_v10_0_autonomous_public_data_refresh_runtime.py", sources)
        self.assertIn(
            "jarvis/tests/test_jarvis_v10_0_autonomous_public_data_refresh_runtime.py",
            result.orphan_next_safe_test_not_moved_paths,
        )

    def test_plan_items_are_not_active_validation_imported_or_validation_tests(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")

        active = set(result.active_import_closure_paths)
        validation_imported = set(result.validation_imported_module_paths)
        validation_tests = set(result.validation_test_keep_paths)

        for item in result.plan_items:
            source = item["source_path"]
            self.assertNotIn(source, active)
            self.assertTrue(item["proposed_archive_path"].startswith(DEFAULT_ARCHIVE_ROOT + "/"))

            if item["item_type"] == "module":
                self.assertNotIn(source, validation_imported)
            if item["item_type"] == "test":
                self.assertNotIn(source, validation_tests)

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/next_safe_python_archive_execution_plan_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "next_safe_plan.json"
            result = build_next_safe_python_archive_execution_plan_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("orphan_next_safe_test_not_moved_paths", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
