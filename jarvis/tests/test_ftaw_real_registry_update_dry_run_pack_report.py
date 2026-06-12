import subprocess
import sys
import unittest

from jarvis.ftaw_real_registry_update_dry_run_pack_report import build_ftaw_real_registry_update_dry_run_pack_report
from jarvis.tests import test_ftaw_real_human_approval_review_decision_recorder_report as v45
from jarvis.tests.test_ftaw_real_registry_update_dry_run_pack import (
    COMPLETE_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
    PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
    REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
)


def _report(
    queue_config=v45.v44.v43.v42.QUEUE_CONFIG,
    decision_config=v45.v44.v43.v42.DECISION_CONFIG,
    preview_config=v45.v44.v43.v42.PREVIEW_CONFIG,
    dry_run_config=v45.v44.v43.v42.DRY_RUN_CONFIG,
    readiness_config=v45.v44.v43.v42.READINESS_CONFIG,
    approval_gate_config=v45.v44.v43.v42.GATE_CONFIG,
    human_decision_config=v45.v44.v43.v42.HUMAN_DECISION_CONFIG,
    registry_dry_run_config=v45.v44.v43.v42.REGISTRY_DRY_RUN_CONFIG,
    apply_gate_config=v45.v44.v43.v42.APPLY_GATE_CONFIG,
    command_config=v45.v44.v43.v42.COMMAND_CONFIG,
    execution_review_config=v45.v44.v43.v42.EXECUTION_REVIEW_CONFIG,
    audit_config=v45.v44.v43.v42.AUDIT_CONFIG,
    real_intake_config=v45.v44.v43.v42.REAL_INTAKE_CONFIG,
    checklist_config=v45.v44.v43.v42.CHECKLIST_CONFIG,
    plan_config=v45.v44.v43.v42.PLAN_CONFIG,
    recorder_config=v45.v44.v43.v42.RECORDER_CONFIG,
    fact_config=v45.v44.v43.v42.FACT_CONFIG,
    bridge_config=v45.v44.v43.v42.BRIDGE_CONFIG,
    review_decision_config=v45.v44.v43.v42.REVIEW_DECISION_CONFIG,
    submission_dry_run_config=v45.v44.v43.v42.SUBMISSION_DRY_RUN_CONFIG,
    review_gate_config=v45.v44.v43.v42.REVIEW_GATE_CONFIG,
    command_contract_config=v45.v44.v43.v42.COMMAND_CONTRACT_CONFIG,
    submission_execution_review_config=v45.v44.v43.v42.EXECUTION_REVIEW_PACK_CONFIG,
    result_recorder_config=v45.v44.v43.v42.RESULT_RECORDER_CONFIG,
    queue_dry_run_bridge_config=v45.v44.v43.v42.QUEUE_DRY_RUN_BRIDGE_CONFIG,
    real_manual_decision_config=v45.v44.v43.v42.REAL_MANUAL_DECISION_CONFIG,
    real_preview_bridge_config=v45.v44.v43.v42.REAL_PREVIEW_BRIDGE_CONFIG,
    real_promotion_dry_run_config=v45.v44.v43.v42.REAL_PROMOTION_DRY_RUN_CONFIG,
    real_candidate_readiness_config=v45.v44.v43.REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
    real_manual_approval_gate_config=v45.v44.REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
    real_human_decision_config=v45.REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
    real_registry_update_dry_run_config=REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
):
    return build_ftaw_real_registry_update_dry_run_pack_report(
        v45.v44.v43.v42.SOURCE_REGISTRY,
        None,
        v45.v44.v43.v42.URL_FETCH_CONFIG,
        v45.v44.v43.v42.INTAKE_CONFIG,
        v45.v44.v43.v42.GUARD_CONFIG,
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
    )


class FTAWRealRegistryUpdateDryRunPackReportTests(unittest.TestCase):
    def test_default_report_prints_blocked_status_plan_and_safety_lines(self) -> None:
        report = _report()

        self.assertIn("dry-run status: BLOCKED_NO_REAL_HUMAN_APPROVAL_DECISION", report)
        self.assertIn("dry-run plan:", report)
        self.assertIn("blocked reasons:", report)
        self.assertIn("no registry mutation: true", report)

    def test_partial_report_prints_partial_status_and_blockers(self) -> None:
        report = _report(
            v45.v44.v43.v42.COMPLETE_QUEUE_CONFIG,
            v45.v44.v43.v42.COMPLETE_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_PREVIEW_CONFIG,
            v45.v44.v43.v42.COMPLETE_DRY_RUN_CONFIG,
            v45.v44.v43.v42.COMPLETE_READINESS_CONFIG,
            v45.v44.v43.v42.COMPLETE_GATE_CONFIG,
            v45.v44.v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
            v45.v44.v43.v42.COMPLETE_APPLY_GATE_CONFIG,
            v45.v44.v43.v42.COMPLETE_COMMAND_CONFIG,
            v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
            v45.v44.v43.v42.COMPLETE_AUDIT_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
            v45.v44.v43.v42.COMPLETE_CHECKLIST_CONFIG,
            v45.v44.v43.v42.COMPLETE_PLAN_CONFIG,
            v45.v44.v43.v42.COMPLETE_RECORDER_CONFIG,
            v45.v44.v43.v42.COMPLETE_FACT_CONFIG,
            v45.v44.v43.v42.COMPLETE_BRIDGE_CONFIG,
            v45.v44.v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
            v45.v44.v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
            v45.v44.v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
            v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
            v45.v44.v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
            v45.v44.v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
            v45.v44.v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
            v45.v44.COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
            real_human_decision_config=v45.PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
            real_registry_update_dry_run_config=PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
        )

        self.assertIn("dry-run status: PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_READY", report)
        self.assertIn("blocked reasons:", report)

    def test_complete_report_prints_final_audit_ready_status_and_safety_lines(self) -> None:
        report = _report(
            v45.v44.v43.v42.COMPLETE_QUEUE_CONFIG,
            v45.v44.v43.v42.COMPLETE_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_PREVIEW_CONFIG,
            v45.v44.v43.v42.COMPLETE_DRY_RUN_CONFIG,
            v45.v44.v43.v42.COMPLETE_READINESS_CONFIG,
            v45.v44.v43.v42.COMPLETE_GATE_CONFIG,
            v45.v44.v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
            v45.v44.v43.v42.COMPLETE_APPLY_GATE_CONFIG,
            v45.v44.v43.v42.COMPLETE_COMMAND_CONFIG,
            v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
            v45.v44.v43.v42.COMPLETE_AUDIT_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
            v45.v44.v43.v42.COMPLETE_CHECKLIST_CONFIG,
            v45.v44.v43.v42.COMPLETE_PLAN_CONFIG,
            v45.v44.v43.v42.COMPLETE_RECORDER_CONFIG,
            v45.v44.v43.v42.COMPLETE_FACT_CONFIG,
            v45.v44.v43.v42.COMPLETE_BRIDGE_CONFIG,
            v45.v44.v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
            v45.v44.v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
            v45.v44.v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
            v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
            v45.v44.v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
            v45.v44.v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
            v45.v44.v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
            v45.v44.v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
            v45.v44.COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
            v45.COMPLETE_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
            COMPLETE_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
        )

        self.assertIn("dry-run status: REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT", report)
        self.assertIn("proposed dry-run status: approved_by_human_review_dry_run", report)
        for line in (
            "registry update dry-run is not registry mutation.",
            "registry update dry-run is not asset approval.",
            "registry update dry-run is not allocation advice.",
            "registry update dry-run is not a buy/sell request.",
            "registry update dry-run is not trade execution.",
            "no registry mutation: true",
            "no registry file written: true",
            "no approvals created: true",
            "approved asset false: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
            "no private file auto-ingest: true",
            "no automatic source fetching: true",
            "no automatic downloads: true",
            "no automatic fact extraction: true",
        ):
            self.assertIn(line, report)

    def test_cli_report_runs_without_error_and_prints_dry_run_plan_and_safety_lines(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_real_registry_update_dry_run_pack_report",
                v45.v44.v43.v42.SOURCE_REGISTRY,
                "None",
                v45.v44.v43.v42.URL_FETCH_CONFIG,
                v45.v44.v43.v42.INTAKE_CONFIG,
                v45.v44.v43.v42.GUARD_CONFIG,
                v45.v44.v43.v42.COMPLETE_QUEUE_CONFIG,
                v45.v44.v43.v42.COMPLETE_DECISION_CONFIG,
                v45.v44.v43.v42.COMPLETE_PREVIEW_CONFIG,
                v45.v44.v43.v42.COMPLETE_DRY_RUN_CONFIG,
                v45.v44.v43.v42.COMPLETE_READINESS_CONFIG,
                v45.v44.v43.v42.COMPLETE_GATE_CONFIG,
                v45.v44.v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
                v45.v44.v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
                v45.v44.v43.v42.COMPLETE_APPLY_GATE_CONFIG,
                v45.v44.v43.v42.COMPLETE_COMMAND_CONFIG,
                v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
                v45.v44.v43.v42.COMPLETE_AUDIT_CONFIG,
                v45.v44.v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
                v45.v44.v43.v42.COMPLETE_CHECKLIST_CONFIG,
                v45.v44.v43.v42.COMPLETE_PLAN_CONFIG,
                v45.v44.v43.v42.COMPLETE_RECORDER_CONFIG,
                v45.v44.v43.v42.COMPLETE_FACT_CONFIG,
                v45.v44.v43.v42.COMPLETE_BRIDGE_CONFIG,
                v45.v44.v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
                v45.v44.v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
                v45.v44.v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
                v45.v44.v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
                v45.v44.v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
                v45.v44.v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
                v45.v44.v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
                v45.v44.v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
                v45.v44.v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
                v45.v44.v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
                v45.v44.v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
                v45.v44.COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
                v45.COMPLETE_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG,
                COMPLETE_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("dry-run status: REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT", result.stdout)
        self.assertIn("dry-run plan:", result.stdout)
        self.assertIn("no automatic fact extraction: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
