import unittest
from pathlib import Path
import subprocess
import sys

from jarvis.ftaw_full_pipeline_audit_report import (
    build_ftaw_full_pipeline_audit_pack,
    build_ftaw_full_pipeline_audit_report,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
PARTIAL_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
COMPLETE_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_complete.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
PARTIAL_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
COMPLETE_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_complete.example.json"
PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
PARTIAL_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
COMPLETE_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_complete.example.json"
DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json"
PARTIAL_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_pass.example.json"
COMPLETE_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_complete.example.json"
READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.example.json"
PARTIAL_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_pass.example.json"
COMPLETE_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_complete.example.json"
GATE_CONFIG = "jarvis/data/ftaw_manual_approval_review_gate.example.json"
COMPLETE_GATE_CONFIG = "jarvis/data/ftaw_manual_approval_review_gate.synthetic_complete.example.json"
HUMAN_DECISION_CONFIG = "jarvis/data/ftaw_human_approval_review_decision_recorder.example.json"
COMPLETE_HUMAN_DECISION_CONFIG = "jarvis/data/ftaw_human_approval_review_decision_recorder.synthetic_complete.example.json"
REGISTRY_DRY_RUN_CONFIG = "jarvis/data/ftaw_registry_update_dry_run_pack.example.json"
COMPLETE_REGISTRY_DRY_RUN_CONFIG = "jarvis/data/ftaw_registry_update_dry_run_pack.synthetic_complete.example.json"
APPLY_GATE_CONFIG = "jarvis/data/ftaw_registry_update_apply_gate.example.json"
COMPLETE_APPLY_GATE_CONFIG = "jarvis/data/ftaw_registry_update_apply_gate.synthetic_complete.example.json"
COMMAND_CONFIG = "jarvis/data/ftaw_explicit_manual_apply_command_contract.example.json"
COMPLETE_COMMAND_CONFIG = "jarvis/data/ftaw_explicit_manual_apply_command_contract.synthetic_complete.example.json"
EXECUTION_REVIEW_CONFIG = "jarvis/data/ftaw_registry_apply_execution_review_pack.example.json"
COMPLETE_EXECUTION_REVIEW_CONFIG = "jarvis/data/ftaw_registry_apply_execution_review_pack.synthetic_complete.example.json"
AUDIT_CONFIG = "jarvis/data/ftaw_full_pipeline_audit_report.example.json"
COMPLETE_AUDIT_CONFIG = "jarvis/data/ftaw_full_pipeline_audit_report.synthetic_complete.example.json"


def _pack(
    queue_config=QUEUE_CONFIG,
    decision_config=DECISION_CONFIG,
    preview_config=PREVIEW_CONFIG,
    dry_run_config=DRY_RUN_CONFIG,
    readiness_config=READINESS_CONFIG,
    approval_gate_config=GATE_CONFIG,
    human_decision_config=HUMAN_DECISION_CONFIG,
    registry_dry_run_config=REGISTRY_DRY_RUN_CONFIG,
    apply_gate_config=APPLY_GATE_CONFIG,
    command_config=COMMAND_CONFIG,
    execution_review_config=EXECUTION_REVIEW_CONFIG,
    audit_config=AUDIT_CONFIG,
):
    return build_ftaw_full_pipeline_audit_pack(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
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
    )


def _complete_pack():
    return _pack(
        COMPLETE_QUEUE_CONFIG,
        COMPLETE_DECISION_CONFIG,
        COMPLETE_PREVIEW_CONFIG,
        COMPLETE_DRY_RUN_CONFIG,
        COMPLETE_READINESS_CONFIG,
        COMPLETE_GATE_CONFIG,
        COMPLETE_HUMAN_DECISION_CONFIG,
        COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        COMPLETE_APPLY_GATE_CONFIG,
        COMPLETE_COMMAND_CONFIG,
        COMPLETE_EXECUTION_REVIEW_CONFIG,
        COMPLETE_AUDIT_CONFIG,
    )


def _partial_pack():
    return _pack(
        PARTIAL_QUEUE_CONFIG,
        PARTIAL_DECISION_CONFIG,
        PARTIAL_PREVIEW_CONFIG,
        PARTIAL_DRY_RUN_CONFIG,
        PARTIAL_READINESS_CONFIG,
        GATE_CONFIG,
        HUMAN_DECISION_CONFIG,
        REGISTRY_DRY_RUN_CONFIG,
        APPLY_GATE_CONFIG,
        COMMAND_CONFIG,
        EXECUTION_REVIEW_CONFIG,
        AUDIT_CONFIG,
    )


class FTAWFullPipelineAuditReportTests(unittest.TestCase):
    def test_default_audit_is_blocked_safe(self) -> None:
        pack = _pack()

        self.assertEqual(pack.audit_status, "BLOCKED_SAFE")
        self.assertFalse(pack.final_preflight_ready)

    def test_partial_synthetic_audit_is_partial_safe(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.audit_status, "PARTIAL_SAFE")
        self.assertFalse(pack.final_preflight_ready)

    def test_synthetic_complete_audit_is_final_preflight_ready_safe(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.audit_status, "FINAL_PREFLIGHT_READY_SAFE")
        self.assertTrue(pack.final_preflight_ready)

    def test_synthetic_complete_safety_flags_are_false(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertFalse(pack.buy_signal)
        self.assertFalse(pack.trade_execution)

    def test_audit_does_not_mutate_candidate_registry_or_outputs(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(Path("jarvis/data/approved_universe.v4_26.json").exists())
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)

    def test_report_prints_all_stage_names_safety_lines_and_warnings(self) -> None:
        report = build_ftaw_full_pipeline_audit_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
            COMPLETE_REGISTRY_DRY_RUN_CONFIG,
            COMPLETE_APPLY_GATE_CONFIG,
            COMPLETE_COMMAND_CONFIG,
            COMPLETE_EXECUTION_REVIEW_CONFIG,
            COMPLETE_AUDIT_CONFIG,
        )

        for stage in (
            "FTAW source fact intake",
            "FTAW source identity guard",
            "FTAW identity-guarded verification queue",
            "FTAW manual verification decision recorder",
            "FTAW verified evidence preview bridge",
            "FTAW verified evidence promotion dry-run pack",
            "FTAW candidate readiness pack",
            "FTAW manual approval review gate",
            "FTAW human approval review decision recorder",
            "FTAW registry update dry-run pack",
            "FTAW registry update apply gate",
            "FTAW explicit manual apply command contract",
            "FTAW registry apply execution review pack",
        ):
            self.assertIn(stage, report)
        self.assertIn("full pipeline audit is not asset approval.", report)
        self.assertIn("full pipeline audit is not registry mutation.", report)
        self.assertIn("full pipeline audit is not verified evidence promotion.", report)
        self.assertIn("full pipeline audit is not allocation advice.", report)
        self.assertIn("full pipeline audit is not a buy/sell request.", report)
        self.assertIn("full pipeline audit is not trade execution.", report)
        self.assertIn("final preflight readiness still requires a separate future executor that does not exist in this version.", report)
        self.assertIn("no verified evidence promotion: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no allocation recommendations: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_report_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_full_pipeline_audit_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                COMPLETE_QUEUE_CONFIG,
                COMPLETE_DECISION_CONFIG,
                COMPLETE_PREVIEW_CONFIG,
                COMPLETE_DRY_RUN_CONFIG,
                COMPLETE_READINESS_CONFIG,
                COMPLETE_GATE_CONFIG,
                COMPLETE_HUMAN_DECISION_CONFIG,
                COMPLETE_REGISTRY_DRY_RUN_CONFIG,
                COMPLETE_APPLY_GATE_CONFIG,
                COMPLETE_COMMAND_CONFIG,
                COMPLETE_EXECUTION_REVIEW_CONFIG,
                COMPLETE_AUDIT_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("audit status: FINAL_PREFLIGHT_READY_SAFE", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
