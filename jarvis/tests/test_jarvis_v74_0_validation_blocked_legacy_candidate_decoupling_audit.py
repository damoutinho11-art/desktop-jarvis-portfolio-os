from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.validation_blocked_legacy_candidate_decoupling_audit import (
    AUDIT_READY,
    DEFAULT_OUTPUT_PATH,
    STATUS_READY,
    build_validation_blocked_legacy_candidate_decoupling_audit_result,
)


class JarvisV740ValidationBlockedLegacyCandidateDecouplingAuditTests(unittest.TestCase):
    def test_audit_is_non_mutating_and_resolved(self) -> None:
        result = build_validation_blocked_legacy_candidate_decoupling_audit_result(
            current_date="2026-06-17"
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.audit_status, AUDIT_READY)
        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertGreaterEqual(result.validation_blocked_module_count, 0)
        self.assertGreaterEqual(result.unique_blocking_test_count, 0)
        self.assertGreaterEqual(result.total_blocking_test_reference_count, 0)
        self.assertGreaterEqual(result.remaining_non_active_versioned_module_count, 0)

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

    def test_every_blocked_module_has_a_blocking_test_mapping(self) -> None:
        result = build_validation_blocked_legacy_candidate_decoupling_audit_result(
            current_date="2026-06-17"
        )

        for record in result.validation_blocked_module_records:
            self.assertGreater(record["blocking_test_count"], 0)
            self.assertTrue(record["blocking_test_paths"])

    def test_known_v5_candidate_is_mapped_if_still_present(self) -> None:
        result = build_validation_blocked_legacy_candidate_decoupling_audit_result(
            current_date="2026-06-17"
        )
        records = {record["module_path"]: record for record in result.validation_blocked_module_records}

        module = "jarvis/jarvis_v5_1_public_source_fixture_wiring.py"
        test = "jarvis/tests/test_jarvis_v5_1_public_source_fixture_wiring.py"

        if module in records:
            self.assertIn(test, records[module]["blocking_test_paths"])

    def test_blocked_modules_do_not_overlap_active_import_closure(self) -> None:
        result = build_validation_blocked_legacy_candidate_decoupling_audit_result(
            current_date="2026-06-17"
        )

        active = set(result.active_import_closure_paths)
        blocked = {record["module_path"] for record in result.validation_blocked_module_records}

        self.assertTrue(blocked.isdisjoint(active))

    def test_write_report_is_explicit_and_ignored_runtime_output(self) -> None:
        self.assertEqual(
            DEFAULT_OUTPUT_PATH,
            "outputs/validation_blocked_legacy_candidate_decoupling_audit_latest.json",
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "validation_blocked_decoupling.json"
            result = build_validation_blocked_legacy_candidate_decoupling_audit_result(
                current_date="2026-06-17",
                write_report=True,
                output_path=output,
            )

            self.assertTrue(result.report_written)
            self.assertTrue(output.exists())
            self.assertIn("validation_blocked_module_records", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
