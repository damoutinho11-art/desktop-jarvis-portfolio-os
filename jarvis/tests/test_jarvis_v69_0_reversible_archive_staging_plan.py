from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.reversible_archive_staging_plan import (
    DEFAULT_ARCHIVE_ROOT,
    DEFAULT_OUTPUT_PATH,
    PLAN_READY,
    STATUS_READY,
    build_reversible_archive_staging_plan_result,
)


class JarvisV690ReversibleArchiveStagingPlanTests(unittest.TestCase):
    def test_report_only_archive_plan_is_conservative_and_non_mutating(self) -> None:
        result = build_reversible_archive_staging_plan_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.plan_status, PLAN_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertGreater(result.total_plan_item_count, 0)
        self.assertGreater(result.report_only_module_candidate_count, 0)
        self.assertGreater(result.report_only_test_candidate_count, 0)

        sources = {item["source_path"] for item in result.plan_items}
        self.assertIn("jarvis/jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py", sources)
        self.assertIn("jarvis/tests/test_jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py", sources)

        self.assertNotIn("jarvis/runtime/operator.py", sources)
        self.assertNotIn("jarvis/jarvis_v13_0_single_command_operator_launcher.py", sources)

        for item in result.plan_items:
            self.assertTrue(item["source_path"].endswith("_report.py"))
            self.assertTrue(item["proposed_archive_path"].startswith(DEFAULT_ARCHIVE_ROOT + "/"))

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

    def test_plan_does_not_include_active_or_validation_keep_paths(self) -> None:
        result = build_reversible_archive_staging_plan_result(current_date="2026-06-17")
        sources = {item["source_path"] for item in result.plan_items}

        active_forbidden = {
            "jarvis/runtime/operator.py",
            "jarvis/runtime/import_closure_safe_archive_plan.py",
            "jarvis_operator.py",
        }
        validation_forbidden = {
            "jarvis/tests/test_jarvis_v67_0_import_closure_relative_import_precision.py",
            "jarvis/tests/test_jarvis_v68_0_non_active_archive_candidate_report.py",
        }

        self.assertTrue(sources.isdisjoint(active_forbidden))
        self.assertTrue(sources.isdisjoint(validation_forbidden))

    def test_write_report_is_explicit_and_default_path_is_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/reversible_archive_staging_plan_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "archive_plan.json"
            result = build_reversible_archive_staging_plan_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("plan_items", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
