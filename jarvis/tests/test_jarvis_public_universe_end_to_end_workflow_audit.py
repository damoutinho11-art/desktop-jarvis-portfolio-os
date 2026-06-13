import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_public_universe_end_to_end_workflow_audit import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    REQUIRED_STAGE_ORDER,
    TRUE_REQUIRED_SAFETY_FIELDS,
    audit_count_coherence,
    audit_handoffs,
    audit_required_stage_order,
    audit_stage_safety,
    compute_v5_final_audit_readiness,
    compute_workflow_readiness,
    evaluate_public_universe_end_to_end_workflow_audit,
    execute_authorized_e2e_audit_cache_write,
    load_json,
    validate_e2e_audit_config,
    validate_stage_audit_record,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_universe_end_to_end_workflow_audit.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_universe_end_to_end_workflow_audit.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_universe_end_to_end_workflow_audit.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_universe_end_to_end_workflow_audit.synthetic_authorized_write.json"


def _complete_data():
    return load_json(COMPLETE_CONFIG)


def _stage(stage_id: str) -> dict:
    return copy.deepcopy(next(stage for stage in _complete_data()["stage_audit_records"] if stage["stage_id"] == stage_id))


class PublicUniverseEndToEndWorkflowAuditTests(unittest.TestCase):
    def test_default_example_partials_safely(self) -> None:
        result = evaluate_public_universe_end_to_end_workflow_audit(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_PARTIAL_SAFE")
        self.assertEqual(result.stage_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_cache_mutated)

    def test_synthetic_complete_returns_ready_for_v5_final_audit(self) -> None:
        result = evaluate_public_universe_end_to_end_workflow_audit(_complete_data())

        self.assertEqual(result.status, "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_READY_FOR_V5_FINAL_AUDIT_SAFE")
        self.assertEqual(result.stage_count, 10)
        self.assertEqual(result.handoff_count, 10)
        self.assertEqual(result.workflow_readiness_label, "PUBLIC_UNIVERSE_E2E_WORKFLOW_READY_FOR_V5_FINAL_AUDIT_SAFE")
        self.assertEqual(result.v5_final_audit_readiness_label, "V5_FINAL_AUDIT_READY_TO_RUN")

    def test_synthetic_problematic_returns_partial_or_blocked_safe(self) -> None:
        result = evaluate_public_universe_end_to_end_workflow_audit(load_json(PROBLEMATIC_CONFIG))

        self.assertIn(result.status, {"PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_PARTIAL_SAFE", "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_BLOCKED_SAFE"})
        self.assertGreater(result.missing_stage_count, 0)
        self.assertGreater(result.partial_handoff_count, 0)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_does_not_write(self) -> None:
        result = evaluate_public_universe_end_to_end_workflow_audit(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_READY_TO_WRITE_SAFE")
        self.assertEqual(result.stage_count, 10)
        self.assertTrue(result.no_cache_mutated)

    def test_all_required_stages_present_in_complete_fixture(self) -> None:
        ids = tuple(stage["stage_id"] for stage in _complete_data()["stage_audit_records"])

        self.assertEqual(REQUIRED_STAGE_ORDER, ids)

    def test_missing_required_stage_causes_partial(self) -> None:
        config = _complete_data()
        config["stage_audit_records"] = config["stage_audit_records"][:-1]

        result = evaluate_public_universe_end_to_end_workflow_audit(config)

        self.assertEqual(result.status, "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_PARTIAL_SAFE")
        self.assertIn("v4.70_public_research_operator_dashboard", " ".join(result.blockers))

    def test_duplicate_stage_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["stage_audit_records"].append(copy.deepcopy(config["stage_audit_records"][0]))

        result = evaluate_public_universe_end_to_end_workflow_audit(config)

        self.assertGreater(result.duplicate_stage_count, 0)
        self.assertIn("duplicate stage ids", " ".join(result.blockers))

    def test_wrong_stage_order_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["stage_audit_records"][0], config["stage_audit_records"][1] = config["stage_audit_records"][1], config["stage_audit_records"][0]

        result = evaluate_public_universe_end_to_end_workflow_audit(config)

        self.assertGreater(result.out_of_order_stage_count, 0)
        self.assertIn("stage order", " ".join(result.blockers))

    def test_blocked_critical_stage_causes_blocked_safe(self) -> None:
        config = _complete_data()
        config["stage_audit_records"][4]["status"] = "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_BLOCKED_SAFE"
        config["stage_audit_records"][4]["blocker_count"] = 1
        config["workflow_counts"]["blocked_stage_count"] = 1

        result = evaluate_public_universe_end_to_end_workflow_audit(config)

        self.assertEqual(result.status, "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_BLOCKED_SAFE")
        self.assertEqual(result.workflow_readiness_label, "PUBLIC_UNIVERSE_E2E_WORKFLOW_BLOCKED_SAFE")

    def test_unsafe_stage_safety_flag_causes_blocked_safe(self) -> None:
        config = _complete_data()
        config["stage_audit_records"][0]["no_trade"] = False

        result = evaluate_public_universe_end_to_end_workflow_audit(config)

        self.assertEqual(result.status, "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_BLOCKED_SAFE")
        self.assertIn("no_trade must be true", " ".join(result.blockers))

    def test_handoff_ready_partial_blocked_counted_correctly(self) -> None:
        records = copy.deepcopy(_complete_data()["handoff_audit_records"])
        records[0]["handoff_status"] = "HANDOFF_PARTIAL_SAFE"
        records[1]["handoff_status"] = "HANDOFF_BLOCKED_SAFE"
        records[1]["blockers"] = ["synthetic blocked handoff"]

        audit = audit_handoffs(records)

        self.assertEqual(audit["partial_handoff_count"], 1)
        self.assertEqual(audit["blocked_handoff_count"], 1)
        self.assertIn("synthetic blocked handoff", " ".join(audit["blockers"]))

    def test_count_coherence_works(self) -> None:
        audit = audit_count_coherence(_complete_data()["workflow_counts"])

        self.assertEqual(audit["blockers"], ())
        self.assertEqual(audit["warnings"], ())

    def test_classified_greater_than_normalized_causes_warning(self) -> None:
        counts = copy.deepcopy(_complete_data()["workflow_counts"])
        counts["classified_record_count"] = counts["normalized_record_count"] + 1

        self.assertIn("classified_record_count exceeds normalized_record_count", " ".join(audit_count_coherence(counts)["warnings"]))

    def test_queue_greater_than_classified_causes_warning(self) -> None:
        counts = copy.deepcopy(_complete_data()["workflow_counts"])
        counts["research_queue_item_count"] = counts["classified_record_count"] + 1

        self.assertIn("research_queue_item_count exceeds classified_record_count", " ".join(audit_count_coherence(counts)["warnings"]))

    def test_draft_packs_greater_than_queue_causes_warning(self) -> None:
        counts = copy.deepcopy(_complete_data()["workflow_counts"])
        counts["evidence_pack_draft_count"] = counts["research_queue_item_count"] + 1

        self.assertIn("evidence_pack_draft_count exceeds research_queue_item_count", " ".join(audit_count_coherence(counts)["warnings"]))

    def test_workflow_and_v5_readiness_labels_work(self) -> None:
        config = _complete_data()

        self.assertEqual(compute_workflow_readiness(tuple(config["stage_audit_records"]), tuple(config["handoff_audit_records"]), config["workflow_counts"]), "PUBLIC_UNIVERSE_E2E_WORKFLOW_READY_FOR_V5_FINAL_AUDIT_SAFE")
        self.assertEqual(compute_v5_final_audit_readiness(tuple(config["stage_audit_records"]), tuple(config["handoff_audit_records"]), config["workflow_counts"]), "V5_FINAL_AUDIT_READY_TO_RUN")

    def test_next_safe_action_is_deterministic(self) -> None:
        result = evaluate_public_universe_end_to_end_workflow_audit(_complete_data())

        self.assertEqual(result.next_safe_action, "proceed_to_v5_final_research_os_mvp_audit")

    def test_do_not_build_next_includes_forbidden_items(self) -> None:
        result = evaluate_public_universe_end_to_end_workflow_audit(_complete_data())
        joined = " ".join(result.do_not_build_next)

        for phrase in ("broker", "executor", "trade", "recommendation", "approval"):
            self.assertIn(phrase, joined)

    def test_safety_controls_are_enforced(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_e2e_audit_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_e2e_audit_config(mutated))

    def test_authorized_write_function_writes_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_universe_end_to_end_workflow_audit(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_e2e_audit_cache_write(
                config,
                result,
                now=datetime(2026, 6, 13, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            output_path = Path(write_result["output_path"])
            metadata_path = Path(write_result["metadata_path"])
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["status"], "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_READY_TO_WRITE_SAFE")
        self.assertEqual(metadata["stage_count"], 10)
        self.assertEqual(metadata["handoff_count"], 10)
        self.assertTrue(metadata["audit_data_unverified"])
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_public_universe_end_to_end_workflow_audit(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_e2e_audit_cache_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "public_asset_universe.e2e_workflow_audit.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_BLOCKED_SAFE")

    def test_write_outside_allowed_roots_is_blocked(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_universe_end_to_end_workflow_audit(config)
        for output_root in ("docs", "templates", "jarvis/data"):
            with self.subTest(output_root=output_root):
                write_result = execute_authorized_e2e_audit_cache_write(config, result, output_root_override=output_root)
                self.assertFalse(write_result["written"])
                self.assertIn("e2e audit output root", write_result["blockers"][0])

    def test_next_manual_actions_are_validated(self) -> None:
        config = _complete_data()
        for action in ("review_end_to_end_public_universe_workflow_audit", "proceed_to_v5_final_research_os_mvp_audit", "fix_public_universe_workflow_blockers", "rerun_public_universe_pipeline_reports", "no_manual_asset_entry_required"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_e2e_audit_config(mutated) if "next_manual_action" in reason])
        for action in ("evidence_verification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_e2e_audit_config(mutated) if "next_manual_action" in reason])

    def test_stage_validation_checks_all_safety_fields(self) -> None:
        stage = _stage("v4.61_discovery_plan")
        stage["no_recommendation"] = False

        self.assertIn("no_recommendation must be true.", validate_stage_audit_record(stage))

    def test_order_audit_reports_exact_order(self) -> None:
        audit = audit_required_stage_order(REQUIRED_STAGE_ORDER, _complete_data()["stage_audit_records"])

        self.assertEqual(audit["missing_stage_count"], 0)
        self.assertEqual(audit["duplicate_stage_count"], 0)
        self.assertEqual(audit["out_of_order_stage_count"], 0)

    def test_stage_safety_audit_counts_ready_rows(self) -> None:
        audit = audit_stage_safety(_complete_data()["stage_audit_records"])

        self.assertEqual(audit["ready_stage_count"], 10)
        self.assertEqual(audit["blocked_stage_count"], 0)

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_public_universe_end_to_end_workflow_audit as module

        self.assertTrue(hasattr(module, "evaluate_public_universe_end_to_end_workflow_audit"))


if __name__ == "__main__":
    unittest.main()
