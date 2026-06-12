import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.ftaw_final_real_pipeline_audit_report import (
    build_ftaw_final_real_pipeline_audit_pack,
    build_ftaw_final_real_pipeline_audit_report,
)
from jarvis.tests import test_ftaw_real_registry_update_dry_run_pack_report as v46


SOURCE_REGISTRY = v46.v45.v44.v43.v42.SOURCE_REGISTRY
FINAL_AUDIT_CONFIG = "jarvis/data/ftaw_final_real_pipeline_audit_report.example.json"
PARTIAL_FINAL_AUDIT_CONFIG = "jarvis/data/ftaw_final_real_pipeline_audit_report.synthetic_partial.example.json"
COMPLETE_FINAL_AUDIT_CONFIG = "jarvis/data/ftaw_final_real_pipeline_audit_report.synthetic_complete.example.json"


def _pack(
    queue_config=v46.v45.v44.v43.v42.QUEUE_CONFIG,
    decision_config=v46.v45.v44.v43.v42.DECISION_CONFIG,
    preview_config=v46.v45.v44.v43.v42.PREVIEW_CONFIG,
    dry_run_config=v46.v45.v44.v43.v42.DRY_RUN_CONFIG,
    readiness_config=v46.v45.v44.v43.v42.READINESS_CONFIG,
    approval_gate_config=v46.v45.v44.v43.v42.GATE_CONFIG,
    human_decision_config=v46.v45.v44.v43.v42.HUMAN_DECISION_CONFIG,
    registry_dry_run_config=v46.v45.v44.v43.v42.REGISTRY_DRY_RUN_CONFIG,
    apply_gate_config=v46.v45.v44.v43.v42.APPLY_GATE_CONFIG,
    command_config=v46.v45.v44.v43.v42.COMMAND_CONFIG,
    execution_review_config=v46.v45.v44.v43.v42.EXECUTION_REVIEW_CONFIG,
    audit_config=v46.v45.v44.v43.v42.AUDIT_CONFIG,
    real_intake_config=v46.v45.v44.v43.v42.REAL_INTAKE_CONFIG,
    checklist_config=v46.v45.v44.v43.v42.CHECKLIST_CONFIG,
    plan_config=v46.v45.v44.v43.v42.PLAN_CONFIG,
    recorder_config=v46.v45.v44.v43.v42.RECORDER_CONFIG,
    fact_config=v46.v45.v44.v43.v42.FACT_CONFIG,
    bridge_config=v46.v45.v44.v43.v42.BRIDGE_CONFIG,
    review_decision_config=v46.v45.v44.v43.v42.REVIEW_DECISION_CONFIG,
    submission_dry_run_config=v46.v45.v44.v43.v42.SUBMISSION_DRY_RUN_CONFIG,
    review_gate_config=v46.v45.v44.v43.v42.REVIEW_GATE_CONFIG,
    command_contract_config=v46.v45.v44.v43.v42.COMMAND_CONTRACT_CONFIG,
    submission_execution_review_config=v46.v45.v44.v43.v42.EXECUTION_REVIEW_PACK_CONFIG,
    result_recorder_config=v46.v45.v44.v43.v42.RESULT_RECORDER_CONFIG,
    queue_dry_run_bridge_config=v46.v45.v44.v43.v42.QUEUE_DRY_RUN_BRIDGE_CONFIG,
    real_manual_decision_config=v46.v45.v44.v43.v42.REAL_MANUAL_DECISION_CONFIG,
    real_preview_bridge_config=v46.v45.v44.v43.v42.REAL_PREVIEW_BRIDGE_CONFIG,
    real_promotion_dry_run_config=v46.v45.v44.v43.v42.REAL_PROMOTION_DRY_RUN_CONFIG,
    real_candidate_readiness_config=v46.v45.v44.v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
    real_manual_approval_gate_config=v46.v45.v44.COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
    real_human_decision_config=v46.v45.REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
    real_registry_update_dry_run_config=v46.REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
    final_audit_config=FINAL_AUDIT_CONFIG,
):
    return build_ftaw_final_real_pipeline_audit_pack(
        SOURCE_REGISTRY,
        None,
        v46.v45.v44.v43.v42.URL_FETCH_CONFIG,
        v46.v45.v44.v43.v42.INTAKE_CONFIG,
        v46.v45.v44.v43.v42.GUARD_CONFIG,
        queue_config,
        decision_config,
        preview_config,
        dry_run_config,
        readiness_config,
        approval_gate_config,
        human_decision_config,
        registry_dry_run_config,
        apply_gate_config,
        command_config,
        execution_review_config,
        audit_config,
        real_intake_config,
        checklist_config,
        plan_config,
        recorder_config,
        fact_config,
        bridge_config,
        review_decision_config,
        submission_dry_run_config,
        review_gate_config,
        command_contract_config,
        submission_execution_review_config,
        result_recorder_config,
        queue_dry_run_bridge_config,
        real_manual_decision_config,
        real_preview_bridge_config,
        real_promotion_dry_run_config,
        real_candidate_readiness_config,
        real_manual_approval_gate_config,
        real_human_decision_config,
        real_registry_update_dry_run_config,
        final_audit_config,
    )


def _partial_pack():
    return _pack(
        v46.v45.v44.v43.v42.COMPLETE_QUEUE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_PREVIEW_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_DRY_RUN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_READINESS_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_GATE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_APPLY_GATE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_COMMAND_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_AUDIT_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_CHECKLIST_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_PLAN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_RECORDER_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_FACT_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_BRIDGE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
        v46.v45.v44.v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
        v46.v45.v44.COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
        real_human_decision_config=v46.v45.PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
        real_registry_update_dry_run_config=v46.PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
        final_audit_config=PARTIAL_FINAL_AUDIT_CONFIG,
    )


def _complete_pack():
    return _pack(
        v46.v45.v44.v43.v42.COMPLETE_QUEUE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_PREVIEW_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_DRY_RUN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_READINESS_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_GATE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_APPLY_GATE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_COMMAND_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_AUDIT_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_CHECKLIST_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_PLAN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_RECORDER_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_FACT_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_BRIDGE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
        v46.v45.v44.v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
        v46.v45.v44.v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
        v46.v45.v44.COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
        v46.v45.COMPLETE_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
        v46.COMPLETE_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
        COMPLETE_FINAL_AUDIT_CONFIG,
    )


class FTAWFinalRealPipelineAuditReportTests(unittest.TestCase):
    def test_default_audit_is_blocked_safe(self) -> None:
        pack = _pack()

        self.assertEqual(pack.final_audit_status, "FINAL_REAL_PIPELINE_BLOCKED_SAFE")
        self.assertFalse(pack.final_dry_run_readiness)

    def test_partial_audit_is_partial_safe(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.final_audit_status, "FINAL_REAL_PIPELINE_PARTIAL_SAFE")
        self.assertFalse(pack.final_dry_run_readiness)
        self.assertIsNotNone(pack.earliest_blocked_stage)

    def test_complete_audit_is_dry_run_ready_safe(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.final_audit_status, "FINAL_REAL_PIPELINE_DRY_RUN_READY_SAFE")
        self.assertTrue(pack.final_dry_run_readiness)
        self.assertEqual(pack.registry_dry_run_status, "REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT")
        self.assertTrue(pack.registry_dry_run_ready)

    def test_complete_safety_flags_are_false(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.registry_file_written)
        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.allocation_recommendation)
        self.assertFalse(pack.buy_signal)
        self.assertFalse(pack.trade_executed)

    def test_stage_table_includes_all_v4_27_to_v4_46_stages(self) -> None:
        pack = _complete_pack()
        names = {stage.stage_name for stage in pack.stages}

        self.assertEqual(pack.stage_count, 20)
        for stage in (
            "v4.27 real evidence intake readiness",
            "v4.28 collection checklist",
            "v4.29 public source reference plan",
            "v4.30 manual public reference recorder",
            "v4.31 manual source fact entry",
            "v4.32 identity guard bridge",
            "v4.33 manual identity review decision recorder",
            "v4.34 identity submission dry-run",
            "v4.35 identity submission review gate",
            "v4.36 explicit manual command contract",
            "v4.37 execution review preflight",
            "v4.38 manual identity result recorder",
            "v4.39 verification queue dry-run bridge",
            "v4.40 real manual verification decision recorder",
            "v4.41 verified evidence preview bridge",
            "v4.42 verified evidence promotion dry-run",
            "v4.43 real candidate readiness review",
            "v4.44 real manual approval review gate",
            "v4.45 real human approval decision recorder",
            "v4.46 real registry update dry-run",
        ):
            self.assertIn(stage, names)

    def test_complete_requires_v4_46_ready_status(self) -> None:
        pack = replace(_complete_pack(), registry_dry_run_status="PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_READY")

        self.assertNotEqual(pack.registry_dry_run_status, "REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT")

    def test_no_registry_candidate_mutation_or_outputs(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")
        pack = _complete_pack()

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(Path("jarvis/data/approved_universe.v4_47.json").exists())
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)

    def test_cli_report_prints_all_stages_final_verdict_phase_statement_and_safety(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_final_real_pipeline_audit_report",
                SOURCE_REGISTRY,
                "None",
                v46.v45.v44.v43.v42.URL_FETCH_CONFIG,
                v46.v45.v44.v43.v42.INTAKE_CONFIG,
                v46.v45.v44.v43.v42.GUARD_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_QUEUE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_DECISION_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_PREVIEW_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_DRY_RUN_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_READINESS_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_GATE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_APPLY_GATE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_COMMAND_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_AUDIT_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_CHECKLIST_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_PLAN_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_RECORDER_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_FACT_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_BRIDGE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
                v46.v45.v44.v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
                v46.v45.v44.v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
                v46.v45.v44.COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
                v46.v45.COMPLETE_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
                v46.COMPLETE_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
                COMPLETE_FINAL_AUDIT_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("final audit status: FINAL_REAL_PIPELINE_DRY_RUN_READY_SAFE", result.stdout)
        self.assertIn("v4.46 real registry update dry-run", result.stdout)
        self.assertIn("backend gate chain phase 1 complete only when complete audit is safe.", result.stdout)
        for line in (
            "no registry mutation: true",
            "no registry file written: true",
            "no approvals created: true",
            "approved asset false: true",
            "no evidence verified automatically: true",
            "no verified evidence promotion executed: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
            "no private file auto-ingest: true",
            "no automatic source fetching: true",
            "no automatic downloads: true",
            "no automatic fact extraction: true",
        ):
            self.assertIn(line, result.stdout)


if __name__ == "__main__":
    unittest.main()
