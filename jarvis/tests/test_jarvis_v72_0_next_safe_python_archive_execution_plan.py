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


ARCHIVED_ROOT = Path("archive/non_active/v72_next_safe_python_safe")


class JarvisV720NextSafePythonArchiveExecutionPlanTests(unittest.TestCase):
    def test_plan_is_non_mutating_and_resolved_before_or_after_execution(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.plan_status, PLAN_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertGreaterEqual(result.next_safe_module_source_count, 0)
        self.assertGreaterEqual(result.total_plan_item_count, 0)

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

    def test_known_next_safe_pair_is_planned_or_already_archived(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")
        sources = {item["source_path"] for item in result.plan_items}

        module = "jarvis/jarvis_v13_0_single_command_operator_launcher.py"
        test = "jarvis/tests/test_jarvis_v13_0_single_command_operator_launcher.py"

        archived_module = ARCHIVED_ROOT / module
        archived_test = ARCHIVED_ROOT / test

        if archived_module.exists() and archived_test.exists():
            self.assertNotIn(module, sources)
            self.assertNotIn(test, sources)
            self.assertFalse(Path(module).exists())
            self.assertFalse(Path(test).exists())
        else:
            self.assertIn(module, sources)
            self.assertIn(test, sources)

    def test_orphan_tests_for_active_modules_are_not_moved(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")
        sources = {item["source_path"] for item in result.plan_items}

        orphan = "jarvis/tests/test_jarvis_v10_0_autonomous_public_data_refresh_runtime.py"
        self.assertNotIn(orphan, sources)
        self.assertTrue(Path(orphan).exists())

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
