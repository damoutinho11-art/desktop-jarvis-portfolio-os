import subprocess
import sys
import unittest

from jarvis.ftaw_real_manual_approval_review_gate_report import build_ftaw_real_manual_approval_review_gate_report
from jarvis.tests import test_ftaw_real_candidate_readiness_review_pack_report as v43
from jarvis.tests.test_ftaw_real_manual_approval_review_gate import (
    COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
    PARTIAL_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
    REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
)


def _report(
    queue_config=v43.v42.QUEUE_CONFIG,
    decision_config=v43.v42.DECISION_CONFIG,
    preview_config=v43.v42.PREVIEW_CONFIG,
    dry_run_config=v43.v42.DRY_RUN_CONFIG,
    readiness_config=v43.v42.READINESS_CONFIG,
    approval_gate_config=v43.v42.GATE_CONFIG,
    human_decision_config=v43.v42.HUMAN_DECISION_CONFIG,
    registry_dry_run_config=v43.v42.REGISTRY_DRY_RUN_CONFIG,
    apply_gate_config=v43.v42.APPLY_GATE_CONFIG,
    command_config=v43.v42.COMMAND_CONFIG,
    execution_review_config=v43.v42.EXECUTION_REVIEW_CONFIG,
    audit_config=v43.v42.AUDIT_CONFIG,
    real_intake_config=v43.v42.REAL_INTAKE_CONFIG,
    checklist_config=v43.v42.CHECKLIST_CONFIG,
    plan_config=v43.v42.PLAN_CONFIG,
    recorder_config=v43.v42.RECORDER_CONFIG,
    fact_config=v43.v42.FACT_CONFIG,
    bridge_config=v43.v42.BRIDGE_CONFIG,
    review_decision_config=v43.v42.REVIEW_DECISION_CONFIG,
    submission_dry_run_config=v43.v42.SUBMISSION_DRY_RUN_CONFIG,
    review_gate_config=v43.v42.REVIEW_GATE_CONFIG,
    command_contract_config=v43.v42.COMMAND_CONTRACT_CONFIG,
    submission_execution_review_config=v43.v42.EXECUTION_REVIEW_PACK_CONFIG,
    result_recorder_config=v43.v42.RESULT_RECORDER_CONFIG,
    queue_dry_run_bridge_config=v43.v42.QUEUE_DRY_RUN_BRIDGE_CONFIG,
    real_manual_decision_config=v43.v42.REAL_MANUAL_DECISION_CONFIG,
    real_preview_bridge_config=v43.v42.REAL_PREVIEW_BRIDGE_CONFIG,
    real_promotion_dry_run_config=v43.v42.REAL_PROMOTION_DRY_RUN_CONFIG,
    real_candidate_readiness_config=v43.REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
    real_manual_approval_gate_config=REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
):
    return build_ftaw_real_manual_approval_review_gate_report(
        v43.v42.SOURCE_REGISTRY,
        None,
        v43.v42.URL_FETCH_CONFIG,
        v43.v42.INTAKE_CONFIG,
        v43.v42.GUARD_CONFIG,
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
    )


class FTAWRealManualApprovalReviewGateReportTests(unittest.TestCase):
    def test_default_report_prints_blocked_status_packet_table_and_safety_lines(self) -> None:
        report = _report()

        self.assertIn("approval review gate status: BLOCKED_NO_REAL_CANDIDATE_READINESS_REVIEW", report)
        self.assertIn("review packet table:", report)
        self.assertIn("blocked reasons:", report)
        self.assertIn("no approvals created: true", report)

    def test_partial_report_prints_partial_packet_and_blockers(self) -> None:
        report = _report(
            v43.v42.PARTIAL_QUEUE_CONFIG,
            v43.v42.PARTIAL_DECISION_CONFIG,
            v43.v42.PARTIAL_PREVIEW_CONFIG,
            v43.v42.PARTIAL_DRY_RUN_CONFIG,
            v43.v42.PARTIAL_READINESS_CONFIG,
            recorder_config=v43.v42.PARTIAL_RECORDER_CONFIG,
            fact_config=v43.v42.PARTIAL_FACT_CONFIG,
            bridge_config=v43.v42.PARTIAL_BRIDGE_CONFIG,
            review_decision_config=v43.v42.PARTIAL_REVIEW_DECISION_CONFIG,
            submission_dry_run_config=v43.v42.PARTIAL_SUBMISSION_DRY_RUN_CONFIG,
            review_gate_config=v43.v42.PARTIAL_REVIEW_GATE_CONFIG,
            command_contract_config=v43.v42.PARTIAL_COMMAND_CONTRACT_CONFIG,
            submission_execution_review_config=v43.v42.PARTIAL_EXECUTION_REVIEW_PACK_CONFIG,
            result_recorder_config=v43.v42.PARTIAL_RESULT_RECORDER_CONFIG,
            queue_dry_run_bridge_config=v43.v42.PARTIAL_QUEUE_DRY_RUN_BRIDGE_CONFIG,
            real_manual_decision_config=v43.v42.PARTIAL_REAL_MANUAL_DECISION_CONFIG,
            real_preview_bridge_config=v43.v42.PARTIAL_REAL_PREVIEW_BRIDGE_CONFIG,
            real_promotion_dry_run_config=v43.v42.PARTIAL_REAL_PROMOTION_DRY_RUN_CONFIG,
            real_candidate_readiness_config=v43.PARTIAL_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
            real_manual_approval_gate_config=PARTIAL_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
        )

        self.assertIn("approval review gate status: PARTIAL_REAL_MANUAL_APPROVAL_REVIEW_READY", report)
        self.assertIn("approval packet created: true", report)
        self.assertIn("blocked reasons:", report)

    def test_complete_report_prints_ready_status_packet_warnings_and_safety_lines(self) -> None:
        report = _report(
            v43.v42.COMPLETE_QUEUE_CONFIG,
            v43.v42.COMPLETE_DECISION_CONFIG,
            v43.v42.COMPLETE_PREVIEW_CONFIG,
            v43.v42.COMPLETE_DRY_RUN_CONFIG,
            v43.v42.COMPLETE_READINESS_CONFIG,
            v43.v42.COMPLETE_GATE_CONFIG,
            v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
            v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
            v43.v42.COMPLETE_APPLY_GATE_CONFIG,
            v43.v42.COMPLETE_COMMAND_CONFIG,
            v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
            v43.v42.COMPLETE_AUDIT_CONFIG,
            v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
            v43.v42.COMPLETE_CHECKLIST_CONFIG,
            v43.v42.COMPLETE_PLAN_CONFIG,
            v43.v42.COMPLETE_RECORDER_CONFIG,
            v43.v42.COMPLETE_FACT_CONFIG,
            v43.v42.COMPLETE_BRIDGE_CONFIG,
            v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
            v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
            v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
            v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
            v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
            v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
            v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
            v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
            v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
            v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
            v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
            COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
        )

        self.assertIn("approval review gate status: READY_FOR_REAL_HUMAN_APPROVAL_REVIEW", report)
        self.assertIn("approval packet created: true", report)
        for line in (
            "manual approval review gate is not asset approval.",
            "manual approval review gate is not registry mutation.",
            "manual approval review gate is not allocation advice.",
            "manual approval review gate is not a buy/sell request.",
            "manual approval review gate is not trade execution.",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
            "no evidence verified: true",
            "no verified evidence promotion: true",
            "no private file auto-ingest: true",
            "no automatic source fetching: true",
            "no automatic downloads: true",
            "no automatic fact extraction: true",
        ):
            self.assertIn(line, report)

    def test_cli_report_runs_without_error_and_prints_review_packet_and_safety_lines(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_real_manual_approval_review_gate_report",
                v43.v42.SOURCE_REGISTRY,
                "None",
                v43.v42.URL_FETCH_CONFIG,
                v43.v42.INTAKE_CONFIG,
                v43.v42.GUARD_CONFIG,
                v43.v42.COMPLETE_QUEUE_CONFIG,
                v43.v42.COMPLETE_DECISION_CONFIG,
                v43.v42.COMPLETE_PREVIEW_CONFIG,
                v43.v42.COMPLETE_DRY_RUN_CONFIG,
                v43.v42.COMPLETE_READINESS_CONFIG,
                v43.v42.COMPLETE_GATE_CONFIG,
                v43.v42.COMPLETE_HUMAN_DECISION_CONFIG,
                v43.v42.COMPLETE_REGISTRY_DRY_RUN_CONFIG,
                v43.v42.COMPLETE_APPLY_GATE_CONFIG,
                v43.v42.COMPLETE_COMMAND_CONFIG,
                v43.v42.COMPLETE_EXECUTION_REVIEW_CONFIG,
                v43.v42.COMPLETE_AUDIT_CONFIG,
                v43.v42.COMPLETE_REAL_INTAKE_CONFIG,
                v43.v42.COMPLETE_CHECKLIST_CONFIG,
                v43.v42.COMPLETE_PLAN_CONFIG,
                v43.v42.COMPLETE_RECORDER_CONFIG,
                v43.v42.COMPLETE_FACT_CONFIG,
                v43.v42.COMPLETE_BRIDGE_CONFIG,
                v43.v42.COMPLETE_REVIEW_DECISION_CONFIG,
                v43.v42.COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
                v43.v42.COMPLETE_REVIEW_GATE_CONFIG,
                v43.v42.COMPLETE_COMMAND_CONTRACT_CONFIG,
                v43.v42.COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
                v43.v42.COMPLETE_RESULT_RECORDER_CONFIG,
                v43.v42.COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
                v43.v42.COMPLETE_REAL_MANUAL_DECISION_CONFIG,
                v43.v42.COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
                v43.v42.COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
                v43.COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG,
                COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("approval review gate status: READY_FOR_REAL_HUMAN_APPROVAL_REVIEW", result.stdout)
        self.assertIn("review packet table:", result.stdout)
        self.assertIn("no automatic fact extraction: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
