import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_v5_4_research_draft_source_router import (
    ALLOWED_DOWNSTREAM_USE,
    BLOCKED_DOWNSTREAM_USE,
    FALSE_REQUIRED_SAFETY_FIELDS,
    SUPPORTED_FIXTURE_FORMATS,
    SUPPORTED_SOURCE_CATEGORIES,
    TRUE_REQUIRED_SAFETY_FIELDS,
    assign_route_priority,
    build_source_route_row,
    evaluate_review_row_for_source_routing,
    evaluate_v5_4_research_draft_source_router,
    execute_authorized_v5_4_source_router_snapshot_write,
    load_json,
    validate_review_row,
    validate_v5_4_research_draft_source_router_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.synthetic_authorized_write.json"


def _complete_data() -> dict:
    return load_json(COMPLETE_CONFIG)


def _row() -> dict:
    return copy.deepcopy(_complete_data()["review_rows"][0])


class V54ResearchDraftSourceRouterTests(unittest.TestCase):
    def test_default_example_partials_safely(self) -> None:
        result = evaluate_v5_4_research_draft_source_router(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_PARTIAL_SAFE")
        self.assertEqual(result.review_row_count, 0)
        self.assertTrue(result.no_external_file_read)
        self.assertTrue(result.research_draft_sources_unverified)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_v5_4_research_draft_source_router(_complete_data())

        self.assertEqual(result.status, "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_SAFE")
        self.assertEqual(result.source_route_count, 3)
        self.assertEqual(result.routed_reference_count, 3)
        self.assertEqual(result.blocked_route_count, 0)

    def test_synthetic_problematic_returns_blocked_safe(self) -> None:
        result = evaluate_v5_4_research_draft_source_router(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_BLOCKED_SAFE")
        self.assertGreater(result.blocked_route_count, 0)
        self.assertGreater(result.duplicate_review_id_count, 0)
        self.assertGreater(result.forbidden_flag_count, 0)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_report_writes_nothing(self) -> None:
        result = evaluate_v5_4_research_draft_source_router(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_TO_WRITE_SAFE")
        self.assertEqual(result.routed_reference_count, 1)

    def test_review_and_fixture_id_duplicates_block(self) -> None:
        result = evaluate_v5_4_research_draft_source_router(load_json(PROBLEMATIC_CONFIG))

        self.assertIn("duplicate review_id", " ".join(result.blockers))
        self.assertIn("duplicate fixture_id", " ".join(result.blockers))
        self.assertIn("block_duplicate_fixture_id", {row["route_decision"] for row in result.route_rows})

    def test_supported_source_categories_and_formats_are_accepted(self) -> None:
        for category in SUPPORTED_SOURCE_CATEGORIES:
            row = _row()
            row["source_category_id"] = category
            self.assertNotIn("unsupported source_category_id", " ".join(validate_review_row(row)))
        for fixture_format in SUPPORTED_FIXTURE_FORMATS:
            row = _row()
            row["fixture_format"] = fixture_format
            self.assertNotIn("unsupported fixture_format", " ".join(validate_review_row(row)))

    def test_unsupported_source_category_and_format_are_blocked(self) -> None:
        row = _row()
        row["source_category_id"] = "unsupported"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "block_unsupported_category")
        row = _row()
        row["fixture_format"] = "xlsx"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "block_unsupported_format")

    def test_credential_private_public_only_and_forbidden_flags_block(self) -> None:
        row = _row()
        row["api_key"] = "forbidden"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "block_private_or_credential_risk")
        row = _row()
        row["credential_or_private_risk"] = True
        self.assertEqual(evaluate_review_row_for_source_routing(row), "block_private_or_credential_risk")
        row = _row()
        row["public_only"] = False
        self.assertEqual(evaluate_review_row_for_source_routing(row), "block_not_public_only")
        for field in ("downloaded_by_jarvis", "evidence_verified", "approved_asset", "trusted_asset", "investable", "recommendation", "allocation", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "executor_created"):
            with self.subTest(field=field):
                row = _row()
                row[field] = True
                self.assertEqual(evaluate_review_row_for_source_routing(row), "block_forbidden_flags")

    def test_route_decisions_for_accepted_pending_deferred_and_rejected_rows(self) -> None:
        row = _row()
        self.assertEqual(evaluate_review_row_for_source_routing(row), "route_to_research_draft_reference_only")
        row = _row()
        row["review_decision"] = "needs_operator_review"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "block_not_operator_accepted")
        self.assertEqual(evaluate_review_row_for_source_routing(row, {"allow_pending_operator_review_reference": True}), "route_to_research_draft_reference_only")
        row = _row()
        row["review_decision"] = "deferred_missing_file"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "defer_missing_file")
        row = _row()
        row["review_decision"] = "deferred_stale_fixture"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "defer_stale_fixture")
        row = _row()
        row["review_decision"] = "deferred_manual_refresh_required"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "defer_manual_refresh_required")
        row = _row()
        row["review_decision"] = "rejected_unsafe_path"
        self.assertEqual(evaluate_review_row_for_source_routing(row), "block_unsafe_path")

    def test_routed_row_safety_flags_and_reference_type(self) -> None:
        routed = build_source_route_row(_row(), "route_to_research_draft_reference_only", "low", 1)

        self.assertEqual(routed["source_reference_type"], "research_draft_source_reference")
        for field in ("evidence_verified", "source_verified", "approved_asset", "trusted_asset", "investable", "recommendation", "allocation", "trade", "executor"):
            self.assertFalse(routed[field])

    def test_route_priority_high_medium_low(self) -> None:
        self.assertEqual(assign_route_priority(_row(), "block_unsafe_path"), "high")
        self.assertEqual(assign_route_priority(_row(), "defer_missing_file"), "high")
        self.assertEqual(assign_route_priority(_row(), "block_not_operator_accepted"), "medium")
        self.assertEqual(assign_route_priority(_row(), "route_to_research_draft_reference_only"), "low")

    def test_allowed_and_blocked_downstream_use(self) -> None:
        row = build_source_route_row(_row(), "route_to_research_draft_reference_only", "low", 1)

        for allowed in ("research_packet_draft_source_reference_only", "manual_source_review_context_only", "operator_dashboard_reference_only"):
            self.assertIn(allowed, ALLOWED_DOWNSTREAM_USE)
            self.assertIn(allowed, row["allowed_downstream_use"])
        for blocked in ("evidence_verification", "source_truth_verification", "approval", "trust", "investability", "registry_mutation", "recommendation", "allocation", "trade", "executor"):
            self.assertIn(blocked, BLOCKED_DOWNSTREAM_USE)
            self.assertIn(blocked, row["blocked_downstream_use"])

    def test_operator_runbook_is_deterministic(self) -> None:
        result = evaluate_v5_4_research_draft_source_router(_complete_data())

        self.assertIn("Review routed draft source references.", result.operator_runbook_steps[0])
        self.assertIn("v5.5 public research packet draft assembler", " ".join(result.operator_runbook_steps))

    def test_authorized_write_function_writes_snapshot_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_v5_4_research_draft_source_router(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_4_source_router_snapshot_write(
                config,
                result,
                now=datetime(2026, 6, 14, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            payload = json.loads(Path(write_result["output_path"]).read_text(encoding="utf-8"))
            metadata = json.loads(Path(write_result["metadata_path"]).read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(len(payload["route_rows"]), 1)
        self.assertTrue(payload["research_draft_sources_unverified"])
        for field in ("external_file_read", "fetch_executed", "download_executed", "ocr", "pdf_parsing", "html_scraping", "evidence_verified", "source_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_v5_4_research_draft_source_router(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_4_source_router_snapshot_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "jarvis_v5_4_research_draft_source_router.snapshot.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_BLOCKED_SAFE")

    def test_unsafe_top_level_safety_controls_are_blocked(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_v5_4_research_draft_source_router_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_v5_4_research_draft_source_router_config(mutated))

    def test_valid_and_invalid_next_manual_actions(self) -> None:
        config = _complete_data()
        valid = ("review_research_draft_source_routes", "fix_blocked_source_references", "refresh_deferred_public_fixtures", "proceed_to_v5_5_public_research_packet_draft_assembler", "proceed_to_v5_5_explicit_authorized_public_fetch_stub", "no_manual_asset_entry_required")
        for action in valid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_v5_4_research_draft_source_router_config(mutated) if "next_manual_action" in reason])
        invalid = ("live_fetch_now", "evidence_verification", "approval", "trust_asset", "mark_investable", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation")
        for action in invalid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_v5_4_research_draft_source_router_config(mutated) if "next_manual_action" in reason])

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_v5_4_research_draft_source_router as module

        self.assertTrue(hasattr(module, "evaluate_v5_4_research_draft_source_router"))


if __name__ == "__main__":
    unittest.main()
