from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.validation_blocked_v5_replacement_plan import (
    DEFAULT_OUTPUT_PATH,
    PLAN_READY,
    STATUS_READY,
    build_validation_blocked_v5_replacement_plan_result,
)


class JarvisV750ValidationBlockedV5ReplacementPlanTests(unittest.TestCase):
    def test_plan_is_non_mutating_and_resolved(self) -> None:
        result = build_validation_blocked_v5_replacement_plan_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.plan_status, PLAN_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertEqual(result.next_safe_module_candidate_count, 0)
        self.assertEqual(result.replacement_record_count, result.validation_blocked_module_count)

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

    def test_every_record_requires_replacement_before_archive(self) -> None:
        result = build_validation_blocked_v5_replacement_plan_result(current_date="2026-06-17")

        self.assertGreater(result.replacement_record_count, 0)
        for record in result.replacement_records:
            self.assertTrue(record["replacement_required_before_archive"])
            self.assertFalse(record["archive_allowed_now"])
            self.assertTrue(record["blocking_test_paths"])
            self.assertTrue(record["proposed_active_runtime_coverage"])

    def test_known_v5_categories_are_classified(self) -> None:
        result = build_validation_blocked_v5_replacement_plan_result(current_date="2026-06-17")
        records = {record["legacy_module_path"]: record for record in result.replacement_records}

        module = "jarvis/jarvis_v5_1_public_source_fixture_wiring.py"
        if module in records:
            self.assertEqual(records[module]["legacy_category"], "historical_public_source_fixture_wiring")
            self.assertIn("platform data completeness", records[module]["replacement_surface"])

        report_module = "jarvis/jarvis_v5_1_public_source_fixture_wiring_report.py"
        if report_module in records:
            self.assertEqual(records[report_module]["legacy_category"], "historical_v5_report_module")

    def test_replacement_plan_does_not_unlock_archive(self) -> None:
        result = build_validation_blocked_v5_replacement_plan_result(current_date="2026-06-17")
        self.assertTrue(all(not record["archive_allowed_now"] for record in result.replacement_records))

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/validation_blocked_v5_replacement_plan_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "v5_replacement_plan.json"
            result = build_validation_blocked_v5_replacement_plan_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("replacement_records", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
