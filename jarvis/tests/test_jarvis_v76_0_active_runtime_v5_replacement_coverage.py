from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.active_runtime_v5_replacement_coverage import (
    COVERAGE_READY,
    DEFAULT_OUTPUT_PATH,
    STATUS_READY,
    build_active_runtime_v5_replacement_coverage_result,
)


class JarvisV760ActiveRuntimeV5ReplacementCoverageTests(unittest.TestCase):
    def test_coverage_pack_is_non_mutating_and_resolved(self) -> None:
        result = build_active_runtime_v5_replacement_coverage_result(current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.coverage_status, COVERAGE_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertTrue(result.safety_check_blocked_execution)
        self.assertGreater(result.replacement_record_count, 0)
        self.assertEqual(result.coverage_record_count, result.covered_record_count)
        self.assertEqual(result.archive_unlocked_record_count, 0)

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

    def test_expected_replacement_coverage_areas_exist(self) -> None:
        result = build_active_runtime_v5_replacement_coverage_result(current_date="2026-06-17")
        areas = {record["coverage_area"] for record in result.coverage_records}

        self.assertIn("public_source_and_platform_intake_boundary", areas)
        self.assertIn("free_research_cache_and_evidence_bridge", areas)
        self.assertIn("manual_review_weekly_packet_and_no_auto_approval", areas)
        self.assertIn("explicit_report_output_and_ignored_generated_files", areas)
        self.assertIn("import_closure_and_execution_safety_facade", areas)

    def test_archive_remains_locked_even_with_coverage(self) -> None:
        result = build_active_runtime_v5_replacement_coverage_result(current_date="2026-06-17")

        self.assertTrue(result.coverage_records)
        for record in result.coverage_records:
            self.assertTrue(record["covered"])
            self.assertFalse(record["archive_unlocked"])

    def test_v76_does_not_import_historical_v5_modules_directly(self) -> None:
        source = Path("jarvis/runtime/active_runtime_v5_replacement_coverage.py").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("import jarvis.jarvis_v5_", source)
        self.assertNotIn("from jarvis.jarvis_v5_", source)
        self.assertNotIn("from jarvis import jarvis_v5_", source)

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(DEFAULT_OUTPUT_PATH, "outputs/active_runtime_v5_replacement_coverage_latest.json")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "v76_coverage.json"
            result = build_active_runtime_v5_replacement_coverage_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("coverage_records", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
