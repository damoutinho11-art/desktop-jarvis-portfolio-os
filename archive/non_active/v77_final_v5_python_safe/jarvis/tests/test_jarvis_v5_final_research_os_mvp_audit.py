import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_v5_final_research_os_mvp_audit import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    REQUIRED_STAGE_CHAIN,
    TRUE_REQUIRED_SAFETY_FIELDS,
    audit_final_audit_records,
    audit_required_capability_matrix,
    audit_required_stage_chain,
    compute_final_verdict,
    compute_mvp_readiness_label,
    evaluate_v5_final_research_os_mvp_audit,
    execute_authorized_v5_final_audit_cache_write,
    load_json,
    validate_final_audit_record,
    validate_v5_final_audit_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.synthetic_authorized_write.json"


def _complete_data() -> dict:
    return load_json(COMPLETE_CONFIG)


class V5FinalResearchOSMVPAuditTests(unittest.TestCase):
    def test_default_example_blocks_or_partials_safely(self) -> None:
        result = evaluate_v5_final_research_os_mvp_audit(load_json(DEFAULT_CONFIG))

        self.assertIn(result.status, {"V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE", "V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE"})
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_executor)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_v5_final_research_os_mvp_audit(_complete_data())

        self.assertEqual(result.status, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_SAFE")
        self.assertEqual(result.final_verdict, "JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE")
        self.assertEqual(result.mvp_readiness_label, "V5_RESEARCH_OS_MVP_READY_FOR_TAG_SAFE")
        self.assertEqual(result.present_stage_count, 13)
        self.assertEqual(result.present_capability_count, 14)
        self.assertEqual(result.ready_area_count, 12)

    def test_synthetic_problematic_returns_partial_or_blocked(self) -> None:
        result = evaluate_v5_final_research_os_mvp_audit(load_json(PROBLEMATIC_CONFIG))

        self.assertIn(result.status, {"V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE", "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE"})
        self.assertGreater(result.missing_stage_count, 0)
        self.assertGreater(result.blocker_count, 0)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_does_not_write(self) -> None:
        result = evaluate_v5_final_research_os_mvp_audit(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_TO_WRITE_SAFE")
        self.assertEqual(result.final_verdict, "JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE")
        self.assertTrue(result.no_cache_mutated)

    def test_missing_required_stage_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["required_stage_chain"] = config["required_stage_chain"][:-1]

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertIn(result.status, {"V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE", "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE"})
        self.assertIn("v4.71_public_universe_end_to_end_workflow_audit", " ".join(result.blockers))

    def test_duplicate_required_stage_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["required_stage_chain"].append(copy.deepcopy(config["required_stage_chain"][0]))

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertGreater(result.duplicate_stage_count, 0)
        self.assertIn("duplicate stage ids", " ".join(result.blockers))

    def test_out_of_order_required_stage_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["required_stage_chain"][0], config["required_stage_chain"][1] = config["required_stage_chain"][1], config["required_stage_chain"][0]

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertGreater(result.out_of_order_stage_count, 0)
        self.assertIn("stage order", " ".join(result.blockers))

    def test_missing_required_capability_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["required_capability_matrix"]["present_capabilities"] = config["required_capability_matrix"]["present_capabilities"][:-1]

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertIn(result.status, {"V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE", "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE"})
        self.assertIn("missing required capability", " ".join(result.blockers))

    def test_forbidden_capability_present_causes_block(self) -> None:
        config = _complete_data()
        config["required_capability_matrix"]["absent_capabilities"][0]["present"] = True
        config["required_capability_matrix"]["absent_capabilities"][0]["absent"] = False

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertEqual(result.status, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE")
        self.assertGreater(result.forbidden_capability_violation_count, 0)

    def test_missing_final_audit_area_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["final_audit_records"] = config["final_audit_records"][:-1]

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertIn(result.status, {"V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE", "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE"})
        self.assertIn("missing final audit areas", " ".join(result.blockers))

    def test_blocked_final_audit_area_causes_block(self) -> None:
        config = _complete_data()
        config["final_audit_records"][0]["status"] = "FINAL_AUDIT_AREA_BLOCKED_SAFE"
        config["final_audit_records"][0]["blocker_count"] = 1

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertEqual(result.status, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE")

    def test_manual_boundaries_false_cause_block(self) -> None:
        for key in ("manual_trust_boundary_summary", "manual_approval_boundary_summary", "no_execution_boundary_summary", "phase1_safety_audit_summary"):
            with self.subTest(key=key):
                config = _complete_data()
                config[key]["confirmed"] = False
                result = evaluate_v5_final_research_os_mvp_audit(config)
                self.assertEqual(result.status, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE")

    def test_v4_71_not_ready_causes_partial_or_block(self) -> None:
        config = _complete_data()
        config["public_universe_e2e_audit_summary"]["status"] = "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_PARTIAL_SAFE"
        config["public_universe_e2e_audit_summary"]["confirmed"] = False

        result = evaluate_v5_final_research_os_mvp_audit(config)

        self.assertIn(result.status, {"V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE", "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE"})
        self.assertIn("v4.71", " ".join(result.blockers))

    def test_safety_controls_are_enforced(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_v5_final_audit_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_v5_final_audit_config(mutated))

    def test_authorized_write_function_writes_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_v5_final_research_os_mvp_audit(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_final_audit_cache_write(
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
        self.assertEqual(write_result["status"], "V5_FINAL_RESEARCH_OS_MVP_AUDIT_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["final_verdict"], "JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE")
        self.assertEqual(metadata["mvp_readiness_label"], "V5_RESEARCH_OS_MVP_READY_FOR_TAG_SAFE")
        self.assertTrue(metadata["final_audit_data_unverified"])
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_v5_final_research_os_mvp_audit(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_final_audit_cache_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "jarvis_v5_final_research_os_mvp_audit.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE")

    def test_write_outside_allowed_roots_is_blocked(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_v5_final_research_os_mvp_audit(config)
        for output_root in ("docs", "templates", "jarvis/data"):
            with self.subTest(output_root=output_root):
                write_result = execute_authorized_v5_final_audit_cache_write(config, result, output_root_override=output_root)
                self.assertFalse(write_result["written"])
                self.assertIn("v5 final audit output root", write_result["blockers"][0])

    def test_valid_and_invalid_next_manual_actions(self) -> None:
        config = _complete_data()
        valid = ("review_v5_final_research_os_mvp_audit", "tag_v5_research_os_mvp_after_manual_review", "fix_final_audit_blockers", "rerun_end_to_end_public_universe_workflow_audit", "no_manual_asset_entry_required")
        for action in valid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_v5_final_audit_config(mutated) if "next_manual_action" in reason])
        invalid = ("evidence_verification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation")
        for action in invalid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_v5_final_audit_config(mutated) if "next_manual_action" in reason])

    def test_helper_audits_are_deterministic(self) -> None:
        config = _complete_data()
        stage_audit = audit_required_stage_chain(config["required_stage_chain"])
        capability_audit = audit_required_capability_matrix(config["required_capability_matrix"])
        final_records_audit = audit_final_audit_records(config["final_audit_records"])

        self.assertEqual(tuple(row["stage_id"] for row in stage_audit["rows"]), REQUIRED_STAGE_CHAIN)
        self.assertEqual(capability_audit["present_capability_count"], 14)
        self.assertEqual(final_records_audit["ready_area_count"], 12)
        verdict = compute_final_verdict(config, stage_audit, capability_audit, final_records_audit)
        self.assertEqual(verdict, "JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE")
        self.assertEqual(compute_mvp_readiness_label(config, verdict), "V5_RESEARCH_OS_MVP_READY_FOR_TAG_SAFE")

    def test_final_audit_record_validation_checks_required_flags(self) -> None:
        record = copy.deepcopy(_complete_data()["final_audit_records"][0])
        record["no_trade"] = False

        self.assertIn("no_trade must be true.", validate_final_audit_record(record))

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_v5_final_research_os_mvp_audit as module

        self.assertTrue(hasattr(module, "evaluate_v5_final_research_os_mvp_audit"))


if __name__ == "__main__":
    unittest.main()
