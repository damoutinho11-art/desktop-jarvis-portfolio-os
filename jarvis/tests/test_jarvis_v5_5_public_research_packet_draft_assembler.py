import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_v5_5_public_research_packet_draft_assembler import (
    ALLOWED_DOWNSTREAM_USE,
    BLOCKED_DOWNSTREAM_USE,
    FALSE_REQUIRED_SAFETY_FIELDS,
    SUPPORTED_SOURCE_REFERENCE_TYPES,
    TRUE_REQUIRED_SAFETY_FIELDS,
    build_packet_row,
    evaluate_route_row_for_packet_assembly,
    evaluate_v5_5_public_research_packet_draft_assembler,
    execute_authorized_v5_5_packet_draft_snapshot_write,
    group_route_rows_for_packets,
    load_json,
    validate_route_row,
    validate_v5_5_public_research_packet_draft_assembler_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_5_public_research_packet_draft_assembler.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_5_public_research_packet_draft_assembler.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_5_public_research_packet_draft_assembler.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_5_public_research_packet_draft_assembler.synthetic_authorized_write.json"


def _complete_data() -> dict:
    return load_json(COMPLETE_CONFIG)


def _row() -> dict:
    return copy.deepcopy(_complete_data()["route_rows"][0])


class V55PublicResearchPacketDraftAssemblerTests(unittest.TestCase):
    def test_default_example_partials_safely(self) -> None:
        result = evaluate_v5_5_public_research_packet_draft_assembler(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_PARTIAL_SAFE")
        self.assertEqual(result.route_row_count, 0)
        self.assertTrue(result.no_external_file_read)
        self.assertTrue(result.packet_drafts_unverified)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_v5_5_public_research_packet_draft_assembler(_complete_data())

        self.assertEqual(result.status, "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_READY_SAFE")
        self.assertEqual(result.packet_draft_count, 3)
        self.assertEqual(result.ready_packet_count, 3)
        self.assertEqual(result.blocked_packet_count, 0)
        self.assertEqual(result.source_reference_count, 3)

    def test_synthetic_problematic_returns_blocked_safe(self) -> None:
        result = evaluate_v5_5_public_research_packet_draft_assembler(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_BLOCKED_SAFE")
        self.assertGreater(result.blocked_packet_count, 0)
        self.assertGreater(result.duplicate_route_id_count, 0)
        self.assertGreater(result.forbidden_flag_count, 0)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_report_writes_nothing(self) -> None:
        result = evaluate_v5_5_public_research_packet_draft_assembler(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_READY_TO_WRITE_SAFE")
        self.assertEqual(result.ready_packet_count, 1)

    def test_route_and_source_reference_duplicates_block(self) -> None:
        result = evaluate_v5_5_public_research_packet_draft_assembler(load_json(PROBLEMATIC_CONFIG))

        self.assertIn("duplicate route_id", " ".join(result.blockers))
        self.assertIn("duplicate source reference", " ".join(result.blockers))
        self.assertGreater(result.duplicate_source_reference_count, 0)

    def test_supported_source_reference_types_are_accepted(self) -> None:
        for reference_type in SUPPORTED_SOURCE_REFERENCE_TYPES:
            row = _row()
            row["source_reference_type"] = reference_type
            self.assertNotIn("unsupported source_reference_type", " ".join(validate_route_row(row)))

    def test_unsupported_source_reference_type_is_blocked(self) -> None:
        row = _row()
        row["source_reference_type"] = "unsupported_reference"

        self.assertEqual(evaluate_route_row_for_packet_assembly(row), "block_unsupported_source_reference_type")

    def test_credential_private_and_forbidden_flags_block(self) -> None:
        row = _row()
        row["api_key"] = "forbidden"
        self.assertEqual(evaluate_route_row_for_packet_assembly(row), "block_private_or_credential_risk")
        row = _row()
        row["credential_or_private_risk"] = True
        self.assertEqual(evaluate_route_row_for_packet_assembly(row), "block_private_or_credential_risk")
        for field in ("downloaded_by_jarvis", "evidence_verified", "source_verified", "approved_asset", "trusted_asset", "investable", "recommendation", "allocation", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "executor_created"):
            with self.subTest(field=field):
                row = _row()
                row[field] = True
                self.assertEqual(evaluate_route_row_for_packet_assembly(row), "block_forbidden_flags")

    def test_route_decisions_for_ready_deferred_and_blocked_rows(self) -> None:
        row = _row()
        self.assertEqual(evaluate_route_row_for_packet_assembly(row), "assemble_public_research_packet_draft")
        row = _row()
        row["route_decision"] = "defer_stale_fixture"
        row["source_reference_type"] = "deferred_source_reference"
        self.assertEqual(evaluate_route_row_for_packet_assembly(row), "defer_source_reference")
        row = _row()
        row["route_decision"] = "block_not_operator_accepted"
        row["source_reference_type"] = "manual_fix_required_reference"
        self.assertEqual(evaluate_route_row_for_packet_assembly(row), "block_source_reference")
        row = _row()
        row["route_decision"] = "unknown"
        self.assertEqual(evaluate_route_row_for_packet_assembly(row), "block_not_routable_for_packet_draft")

    def test_group_route_rows_for_packets_is_deterministic(self) -> None:
        groups = group_route_rows_for_packets(_complete_data()["route_rows"])

        self.assertEqual([group["packet_group_key"] for group in groups], ["crypto", "etf", "public_document"])

    def test_packet_row_safety_flags_and_type(self) -> None:
        row = _row()
        group = {"packet_group_key": "crypto", "route_rows": (row,)}
        packet = build_packet_row(group, {row["route_id"]: "assemble_public_research_packet_draft"}, 1)

        self.assertEqual(packet["packet_draft_type"], "public_research_packet_draft")
        self.assertTrue(packet["packet_draft_unverified"])
        for field in ("evidence_extracted", "evidence_verified", "source_verified", "approved_asset", "trusted_asset", "investable", "recommendation", "allocation", "trade", "executor"):
            self.assertFalse(packet[field])

    def test_allowed_and_blocked_downstream_use(self) -> None:
        row = _row()
        packet = build_packet_row({"packet_group_key": "crypto", "route_rows": (row,)}, {row["route_id"]: "assemble_public_research_packet_draft"}, 1)

        for allowed in ("human_research_packet_review_only", "manual_source_review_context_only", "operator_dashboard_reference_only"):
            self.assertIn(allowed, ALLOWED_DOWNSTREAM_USE)
            self.assertIn(allowed, packet["allowed_downstream_use"])
        for blocked in ("evidence_extraction", "evidence_verification", "source_truth_verification", "approval", "trust", "investability", "registry_mutation", "recommendation", "allocation", "trade", "executor"):
            self.assertIn(blocked, BLOCKED_DOWNSTREAM_USE)
            self.assertIn(blocked, packet["blocked_downstream_use"])

    def test_operator_runbook_is_deterministic(self) -> None:
        result = evaluate_v5_5_public_research_packet_draft_assembler(_complete_data())

        self.assertIn("Review packet draft groups.", result.operator_runbook_steps[0])
        self.assertIn("v5.6 public research packet human review queue", " ".join(result.operator_runbook_steps))

    def test_authorized_write_function_writes_snapshot_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_v5_5_public_research_packet_draft_assembler(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_5_packet_draft_snapshot_write(
                config,
                result,
                now=datetime(2026, 6, 14, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            payload = json.loads(Path(write_result["output_path"]).read_text(encoding="utf-8"))
            metadata = json.loads(Path(write_result["metadata_path"]).read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(len(payload["packet_rows"]), 1)
        self.assertTrue(payload["packet_drafts_unverified"])
        for field in ("external_file_read", "fetch_executed", "download_executed", "ocr", "pdf_parsing", "html_scraping", "evidence_extracted", "evidence_verified", "source_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_v5_5_public_research_packet_draft_assembler(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_5_packet_draft_snapshot_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "jarvis_v5_5_public_research_packet_draft_assembler.snapshot.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_BLOCKED_SAFE")

    def test_unsafe_top_level_safety_controls_are_blocked(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_v5_5_public_research_packet_draft_assembler_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_v5_5_public_research_packet_draft_assembler_config(mutated))

    def test_valid_and_invalid_next_manual_actions(self) -> None:
        config = _complete_data()
        valid = ("review_public_research_packet_drafts", "fix_blocked_packet_draft_routes", "refresh_deferred_public_source_routes", "proceed_to_v5_6_public_research_packet_human_review_queue", "no_manual_asset_entry_required")
        for action in valid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_v5_5_public_research_packet_draft_assembler_config(mutated) if "next_manual_action" in reason])
        invalid = ("live_fetch_now", "evidence_extraction", "evidence_verification", "approval", "trust_asset", "mark_investable", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation")
        for action in invalid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_v5_5_public_research_packet_draft_assembler_config(mutated) if "next_manual_action" in reason])

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_v5_5_public_research_packet_draft_assembler as module

        self.assertTrue(hasattr(module, "evaluate_v5_5_public_research_packet_draft_assembler"))


if __name__ == "__main__":
    unittest.main()
