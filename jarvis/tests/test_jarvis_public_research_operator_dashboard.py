import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_public_research_operator_dashboard import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    REQUIRED_STAGE_IDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    build_stage_rows,
    classify_stage_readiness,
    compute_pipeline_readiness,
    compute_v5_mvp_readiness,
    evaluate_public_research_operator_dashboard,
    execute_authorized_operator_dashboard_cache_write,
    load_json,
    validate_dashboard_config,
    validate_stage_summary,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.synthetic_authorized_write.json"


def _complete_data():
    return load_json(COMPLETE_CONFIG)


def _stage(stage_id: str) -> dict:
    return copy.deepcopy(next(stage for stage in _complete_data()["public_universe_stage_summaries"] if stage["stage_id"] == stage_id))


class PublicResearchOperatorDashboardTests(unittest.TestCase):
    def test_default_example_partials_safely(self) -> None:
        result = evaluate_public_research_operator_dashboard(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_PARTIAL_SAFE")
        self.assertEqual(result.stage_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_cache_mutated)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_public_research_operator_dashboard(_complete_data())

        self.assertEqual(result.status, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_SAFE")
        self.assertEqual(result.stage_count, 9)
        self.assertEqual(result.ready_stage_count, 9)
        self.assertEqual(result.blocked_stage_count, 0)

    def test_synthetic_problematic_returns_partial_safe(self) -> None:
        result = evaluate_public_research_operator_dashboard(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_PARTIAL_SAFE")
        self.assertEqual(result.partial_stage_count, 1)
        self.assertIn("missing required stage ids", " ".join(result.blockers))

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_does_not_write(self) -> None:
        result = evaluate_public_research_operator_dashboard(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_TO_WRITE_SAFE")
        self.assertEqual(result.stage_count, 9)
        self.assertTrue(result.no_cache_mutated)

    def test_all_required_stage_ids_present_in_complete_fixture(self) -> None:
        ids = {stage["stage_id"] for stage in _complete_data()["public_universe_stage_summaries"]}

        self.assertEqual(set(REQUIRED_STAGE_IDS), ids)

    def test_missing_required_stage_causes_partial(self) -> None:
        config = _complete_data()
        config["public_universe_stage_summaries"] = config["public_universe_stage_summaries"][:-1]

        result = evaluate_public_research_operator_dashboard(config)

        self.assertEqual(result.status, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_PARTIAL_SAFE")
        self.assertIn("v4.69_public_evidence_pack_draft_generator", " ".join(result.blockers))

    def test_blocked_critical_stage_causes_blocked_safe(self) -> None:
        config = _complete_data()
        config["public_universe_stage_summaries"][4]["status"] = "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_BLOCKED_SAFE"
        config["public_universe_stage_summaries"][4]["blocked_count"] = 1
        config["public_universe_stage_summaries"][4]["blocker_count"] = 1

        result = evaluate_public_research_operator_dashboard(config)

        self.assertEqual(result.status, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_BLOCKED_SAFE")
        self.assertEqual(result.pipeline_readiness_label, "PUBLIC_RESEARCH_PIPELINE_BLOCKED_SAFE")

    def test_warning_only_stage_keeps_dashboard_safe_and_surfaces_warning(self) -> None:
        config = _complete_data()
        config["public_universe_stage_summaries"][0]["warning_count"] = 2
        config["public_universe_warnings"] = ["synthetic warning only"]

        result = evaluate_public_research_operator_dashboard(config)

        self.assertEqual(result.status, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_SAFE")
        self.assertEqual(result.warning_count, 4)
        self.assertIn("synthetic warning only", result.warnings)

    def test_counts_aggregate_correctly(self) -> None:
        result = evaluate_public_research_operator_dashboard(_complete_data())

        self.assertEqual(result.normalized_record_count, 3)
        self.assertEqual(result.classified_record_count, 5)
        self.assertEqual(result.research_queue_item_count, 6)
        self.assertEqual(result.draft_pack_count, 6)
        self.assertEqual(result.high_ready_research_count, 1)
        self.assertEqual(result.medium_ready_research_count, 1)

    def test_pipeline_and_v5_readiness_labels_work(self) -> None:
        config = _complete_data()
        stages = tuple(config["public_universe_stage_summaries"])

        self.assertEqual(compute_pipeline_readiness(stages, config["public_universe_counts"]), "PUBLIC_RESEARCH_PIPELINE_READY_FOR_WORKFLOW_AUDIT_SAFE")
        self.assertEqual(compute_v5_mvp_readiness(stages, config["public_universe_counts"]), "V5_MVP_NEAR_READY_REQUIRES_END_TO_END_AUDIT")

    def test_next_safe_action_is_deterministic(self) -> None:
        result = evaluate_public_research_operator_dashboard(_complete_data())

        self.assertEqual(result.next_safe_action, "proceed_to_end_to_end_public_universe_workflow_audit")

    def test_do_not_build_next_includes_forbidden_items(self) -> None:
        result = evaluate_public_research_operator_dashboard(_complete_data())
        joined = " ".join(result.do_not_build_next)

        for phrase in ("broker", "executor", "trade", "recommendation", "approval"):
            self.assertIn(phrase, joined)

    def test_unsafe_stage_safety_flag_causes_block(self) -> None:
        stage = _stage("v4.69_public_evidence_pack_draft_generator")
        stage["no_trade"] = False

        self.assertIn("no_trade must be true.", validate_stage_summary(stage))

    def test_stage_readiness_classification(self) -> None:
        self.assertEqual(classify_stage_readiness(_stage("v4.69_public_evidence_pack_draft_generator")), "ready")
        partial = _stage("v4.65_cache_integrity_freshness_audit")
        partial["partial_count"] = 1
        self.assertEqual(classify_stage_readiness(partial), "partial")

    def test_stage_rows_are_sorted_by_required_stage_order(self) -> None:
        rows = build_stage_rows(tuple(reversed(_complete_data()["public_universe_stage_summaries"])))

        self.assertEqual(rows[0]["stage_id"], "v4.61_discovery_plan")
        self.assertEqual(rows[-1]["stage_id"], "v4.69_public_evidence_pack_draft_generator")

    def test_safety_controls_are_enforced(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_dashboard_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_dashboard_config(mutated))

    def test_authorized_write_function_writes_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_research_operator_dashboard(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_operator_dashboard_cache_write(
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
        self.assertEqual(write_result["status"], "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["status"], "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_TO_WRITE_SAFE")
        self.assertEqual(metadata["stage_count"], 9)
        self.assertTrue(metadata["dashboard_data_unverified"])
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_public_research_operator_dashboard(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_operator_dashboard_cache_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "public_asset_universe.operator_dashboard.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_BLOCKED_SAFE")

    def test_write_outside_allowed_roots_is_blocked(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_research_operator_dashboard(config)
        for output_root in ("docs", "templates", "jarvis/data"):
            with self.subTest(output_root=output_root):
                write_result = execute_authorized_operator_dashboard_cache_write(config, result, output_root_override=output_root)
                self.assertFalse(write_result["written"])
                self.assertIn("operator dashboard output root", write_result["blockers"][0])

    def test_next_manual_actions_are_validated(self) -> None:
        config = _complete_data()
        for action in ("review_operator_research_dashboard", "proceed_to_end_to_end_public_universe_workflow_audit", "fix_public_universe_stage_blockers", "rerun_public_universe_pipeline_reports", "no_manual_asset_entry_required"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_dashboard_config(mutated) if "next_manual_action" in reason])
        for action in ("evidence_verification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_dashboard_config(mutated) if "next_manual_action" in reason])

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_public_research_operator_dashboard as module

        self.assertTrue(hasattr(module, "evaluate_public_research_operator_dashboard"))


if __name__ == "__main__":
    unittest.main()
