import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_v5_3_operator_fixture_review_queue import (
    BLOCKED_NEXT_STAGES,
    FALSE_REQUIRED_SAFETY_FIELDS,
    SUPPORTED_FIXTURE_FORMATS,
    SUPPORTED_SOURCE_CATEGORIES,
    TRUE_REQUIRED_SAFETY_FIELDS,
    assign_review_priority,
    build_review_queue_row,
    evaluate_import_preview_row_for_review,
    evaluate_v5_3_operator_fixture_review_queue,
    execute_authorized_v5_3_review_queue_snapshot_write,
    load_json,
    validate_import_preview_row,
    validate_v5_3_operator_fixture_review_queue_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.synthetic_authorized_write.json"


def _complete_data() -> dict:
    return load_json(COMPLETE_CONFIG)


def _row() -> dict:
    return copy.deepcopy(_complete_data()["import_preview_rows"][0])


class V53OperatorFixtureReviewQueueTests(unittest.TestCase):
    def test_default_example_partials_safely(self) -> None:
        result = evaluate_v5_3_operator_fixture_review_queue(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_PARTIAL_SAFE")
        self.assertEqual(result.import_preview_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.review_queue_unverified)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_v5_3_operator_fixture_review_queue(_complete_data())

        self.assertEqual(result.status, "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_SAFE")
        self.assertEqual(result.review_queue_count, 3)
        self.assertEqual(result.accepted_for_research_draft_only_count, 3)
        self.assertEqual(result.rejected_count, 0)

    def test_synthetic_problematic_returns_blocked_safe(self) -> None:
        result = evaluate_v5_3_operator_fixture_review_queue(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_BLOCKED_SAFE")
        self.assertGreater(result.rejected_count, 0)
        self.assertGreater(result.duplicate_fixture_id_count, 0)
        self.assertGreater(result.forbidden_flag_count, 0)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_report_writes_nothing(self) -> None:
        result = evaluate_v5_3_operator_fixture_review_queue(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_TO_WRITE_SAFE")
        self.assertEqual(result.accepted_for_research_draft_only_count, 1)

    def test_import_preview_id_uniqueness_blocks_duplicates(self) -> None:
        result = evaluate_v5_3_operator_fixture_review_queue(load_json(PROBLEMATIC_CONFIG))

        self.assertIn("duplicate fixture_id", " ".join(result.blockers))
        self.assertIn("rejected_duplicate_fixture_id", {row["review_decision"] for row in result.review_rows})

    def test_supported_source_categories_and_formats_are_accepted(self) -> None:
        for category in SUPPORTED_SOURCE_CATEGORIES:
            row = _row()
            row["source_category_id"] = category
            self.assertNotIn("unsupported source_category_id", " ".join(validate_import_preview_row(row)))
        for fixture_format in SUPPORTED_FIXTURE_FORMATS:
            row = _row()
            row["fixture_format"] = fixture_format
            self.assertNotIn("unsupported fixture_format", " ".join(validate_import_preview_row(row)))

    def test_unsupported_source_category_and_format_are_rejected(self) -> None:
        row = _row()
        row["source_category_id"] = "unsupported"
        self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_unsupported_category")
        row = _row()
        row["fixture_format"] = "xlsx"
        self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_unsupported_format")

    def test_credential_private_and_public_only_checks_block(self) -> None:
        row = _row()
        row["api_key"] = "forbidden"
        self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_private_or_credential_risk")
        row = _row()
        row["credential_or_private_risk"] = True
        self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_private_or_credential_risk")
        row = _row()
        row["public_only"] = False
        self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_not_public_only")

    def test_forbidden_true_flags_block(self) -> None:
        for field in ("downloaded_by_jarvis", "evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "executor_created"):
            with self.subTest(field=field):
                row = _row()
                row[field] = True
                self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_forbidden_flags")

    def test_deferred_decisions_for_missing_stale_and_manual_refresh(self) -> None:
        row = _row()
        row["missing_fixture"] = True
        self.assertEqual(evaluate_import_preview_row_for_review(row), "deferred_missing_file")
        row = _row()
        row["stale_fixture"] = True
        self.assertEqual(evaluate_import_preview_row_for_review(row), "deferred_stale_fixture")
        row = _row()
        row["manual_refresh_required"] = True
        self.assertEqual(evaluate_import_preview_row_for_review(row), "deferred_manual_refresh_required")

    def test_rejected_decisions_for_unsafe_path_duplicate_and_risks(self) -> None:
        row = _row()
        row["unsafe_path"] = True
        self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_unsafe_path")
        row = _row()
        row["duplicate_fixture_id"] = True
        self.assertEqual(evaluate_import_preview_row_for_review(row), "rejected_duplicate_fixture_id")

    def test_valid_row_needs_review_by_default_and_can_be_accepted_when_enabled(self) -> None:
        config = _complete_data()
        config["review_queue_policy"]["auto_accept_for_research_draft_only"] = False
        config["import_preview_rows"] = [_row()]
        default_result = evaluate_v5_3_operator_fixture_review_queue(config)
        self.assertEqual(default_result.review_rows[0]["review_decision"], "needs_operator_review")

        config["review_queue_policy"]["auto_accept_for_research_draft_only"] = True
        accepted_result = evaluate_v5_3_operator_fixture_review_queue(config)
        accepted = accepted_result.review_rows[0]
        self.assertEqual(accepted["review_decision"], "accepted_for_research_draft_only")
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "recommendation", "allocation", "trade", "executor"):
            self.assertFalse(accepted[field])

    def test_review_priority_high_medium_low(self) -> None:
        self.assertEqual(assign_review_priority(_row(), "rejected_unsafe_path"), "high")
        self.assertEqual(assign_review_priority(_row(), "deferred_missing_file"), "high")
        self.assertEqual(assign_review_priority(_row(), "needs_operator_review"), "medium")
        row = _row()
        row["import_enabled"] = False
        self.assertEqual(assign_review_priority(row, "needs_operator_review"), "low")

    def test_allowed_and_blocked_next_stages_are_safe(self) -> None:
        row = build_review_queue_row(_row(), "accepted_for_research_draft_only", "medium", 1)

        self.assertEqual(row["allowed_next_stage"], "research_draft_source_router_only")
        for blocked in ("evidence_verification", "approval", "trust", "investability", "registry_mutation", "recommendation", "allocation", "trade", "executor"):
            self.assertIn(blocked, BLOCKED_NEXT_STAGES)
            self.assertIn(blocked, row["blocked_next_stage"])

    def test_operator_runbook_is_deterministic(self) -> None:
        result = evaluate_v5_3_operator_fixture_review_queue(_complete_data())

        self.assertIn("Review accepted draft-only source references.", result.operator_runbook_steps[0])
        self.assertIn("v5.4 research draft source router", " ".join(result.operator_runbook_steps))

    def test_authorized_write_function_writes_snapshot_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_v5_3_operator_fixture_review_queue(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_3_review_queue_snapshot_write(
                config,
                result,
                now=datetime(2026, 6, 14, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            payload = json.loads(Path(write_result["output_path"]).read_text(encoding="utf-8"))
            metadata = json.loads(Path(write_result["metadata_path"]).read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(len(payload["review_rows"]), 1)
        self.assertTrue(payload["review_queue_unverified"])
        for field in ("fetch_executed", "download_executed", "ocr", "pdf_parsing", "html_scraping", "evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_v5_3_operator_fixture_review_queue(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_3_review_queue_snapshot_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "jarvis_v5_3_operator_fixture_review_queue.snapshot.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_BLOCKED_SAFE")

    def test_unsafe_top_level_safety_controls_are_blocked(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_v5_3_operator_fixture_review_queue_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_v5_3_operator_fixture_review_queue_config(mutated))

    def test_valid_and_invalid_next_manual_actions(self) -> None:
        config = _complete_data()
        valid = ("review_operator_fixture_queue", "fix_rejected_fixture_metadata", "prepare_missing_local_public_fixtures", "refresh_stale_public_fixtures", "proceed_to_v5_4_research_draft_source_router", "proceed_to_v5_4_explicit_authorized_public_fetch_stub", "no_manual_asset_entry_required")
        for action in valid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_v5_3_operator_fixture_review_queue_config(mutated) if "next_manual_action" in reason])
        invalid = ("live_fetch_now", "evidence_verification", "approval", "trust_asset", "mark_investable", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation")
        for action in invalid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_v5_3_operator_fixture_review_queue_config(mutated) if "next_manual_action" in reason])

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_v5_3_operator_fixture_review_queue as module

        self.assertTrue(hasattr(module, "evaluate_v5_3_operator_fixture_review_queue"))


if __name__ == "__main__":
    unittest.main()
