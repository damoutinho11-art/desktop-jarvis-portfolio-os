import subprocess
import sys
import unittest

from jarvis.ftaw_real_verified_evidence_promotion_dry_run_pack_report import (
    build_ftaw_real_verified_evidence_promotion_dry_run_pack_report,
)
from jarvis.tests.test_ftaw_real_verified_evidence_promotion_dry_run_pack import (
    COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
    PARTIAL_REAL_PROMOTION_DRY_RUN_CONFIG,
    REAL_PROMOTION_DRY_RUN_CONFIG,
)
from jarvis.tests.test_ftaw_real_verified_evidence_preview_bridge import (
    COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
    PARTIAL_REAL_PREVIEW_BRIDGE_CONFIG,
    REAL_PREVIEW_BRIDGE_CONFIG,
)
from jarvis.tests.test_ftaw_real_manual_verification_decision_recorder import (
    COMPLETE_REAL_MANUAL_DECISION_CONFIG,
    PARTIAL_REAL_MANUAL_DECISION_CONFIG,
    REAL_MANUAL_DECISION_CONFIG,
)
from jarvis.tests.test_ftaw_real_identity_guarded_verification_queue_dry_run_bridge import (
    COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
    PARTIAL_QUEUE_DRY_RUN_BRIDGE_CONFIG,
    QUEUE_DRY_RUN_BRIDGE_CONFIG,
)
from jarvis.tests.test_ftaw_manual_identity_guard_result_recorder import (
    COMPLETE_RESULT_RECORDER_CONFIG,
    PARTIAL_RESULT_RECORDER_CONFIG,
    RESULT_RECORDER_CONFIG,
)
from jarvis.tests.test_ftaw_identity_guard_submission_execution_review_pack import (
    COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
    EXECUTION_REVIEW_PACK_CONFIG,
    PARTIAL_EXECUTION_REVIEW_PACK_CONFIG,
)
from jarvis.tests.test_ftaw_explicit_manual_identity_guard_submission_command_contract import (
    COMMAND_CONTRACT_CONFIG,
    COMPLETE_COMMAND_CONTRACT_CONFIG,
    PARTIAL_COMMAND_CONTRACT_CONFIG,
)
from jarvis.tests.test_ftaw_identity_guard_submission_review_gate import (
    COMPLETE_REVIEW_GATE_CONFIG,
    PARTIAL_REVIEW_GATE_CONFIG,
    REVIEW_GATE_CONFIG,
)
from jarvis.tests.test_ftaw_identity_guard_submission_dry_run_pack import (
    COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
    PARTIAL_SUBMISSION_DRY_RUN_CONFIG,
    SUBMISSION_DRY_RUN_CONFIG,
)
from jarvis.tests.test_ftaw_manual_public_source_reference_entry_recorder import (
    COMPLETE_RECORDER_CONFIG,
    PARTIAL_RECORDER_CONFIG,
    RECORDER_CONFIG,
)
from jarvis.tests.test_ftaw_manual_source_fact_entry_pack import (
    COMPLETE_FACT_CONFIG,
    FACT_CONFIG,
    PARTIAL_FACT_CONFIG,
)
from jarvis.tests.test_ftaw_real_evidence_collection_checklist_pack import (
    CHECKLIST_CONFIG,
    COMPLETE_CHECKLIST_CONFIG,
)
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import (
    APPLY_GATE_CONFIG,
    AUDIT_CONFIG,
    COMMAND_CONFIG,
    COMPLETE_APPLY_GATE_CONFIG,
    COMPLETE_AUDIT_CONFIG,
    COMPLETE_COMMAND_CONFIG,
    COMPLETE_DECISION_CONFIG,
    COMPLETE_DRY_RUN_CONFIG,
    COMPLETE_EXECUTION_REVIEW_CONFIG,
    COMPLETE_GATE_CONFIG,
    COMPLETE_HUMAN_DECISION_CONFIG,
    COMPLETE_PREVIEW_CONFIG,
    COMPLETE_QUEUE_CONFIG,
    COMPLETE_READINESS_CONFIG,
    COMPLETE_REAL_INTAKE_CONFIG,
    COMPLETE_REGISTRY_DRY_RUN_CONFIG,
    DECISION_CONFIG,
    DRY_RUN_CONFIG,
    EXECUTION_REVIEW_CONFIG,
    GATE_CONFIG,
    GUARD_CONFIG,
    HUMAN_DECISION_CONFIG,
    INTAKE_CONFIG,
    PARTIAL_DECISION_CONFIG,
    PARTIAL_DRY_RUN_CONFIG,
    PARTIAL_PREVIEW_CONFIG,
    PARTIAL_QUEUE_CONFIG,
    PARTIAL_READINESS_CONFIG,
    PREVIEW_CONFIG,
    QUEUE_CONFIG,
    READINESS_CONFIG,
    REAL_INTAKE_CONFIG,
    REGISTRY_DRY_RUN_CONFIG,
    SOURCE_REGISTRY,
    URL_FETCH_CONFIG,
)
from jarvis.tests.test_ftaw_real_manual_identity_guard_review_decision_recorder import (
    COMPLETE_REVIEW_DECISION_CONFIG,
    PARTIAL_REVIEW_DECISION_CONFIG,
    REVIEW_DECISION_CONFIG,
)
from jarvis.tests.test_ftaw_real_manual_source_fact_identity_guard_bridge import (
    BRIDGE_CONFIG,
    COMPLETE_BRIDGE_CONFIG,
    PARTIAL_BRIDGE_CONFIG,
)
from jarvis.tests.test_ftaw_real_public_source_reference_intake_plan import (
    COMPLETE_PLAN_CONFIG,
    PLAN_CONFIG,
)


def _report(
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
    real_intake_config=REAL_INTAKE_CONFIG,
    checklist_config=CHECKLIST_CONFIG,
    plan_config=PLAN_CONFIG,
    recorder_config=RECORDER_CONFIG,
    fact_config=FACT_CONFIG,
    bridge_config=BRIDGE_CONFIG,
    review_decision_config=REVIEW_DECISION_CONFIG,
    submission_dry_run_config=SUBMISSION_DRY_RUN_CONFIG,
    review_gate_config=REVIEW_GATE_CONFIG,
    command_contract_config=COMMAND_CONTRACT_CONFIG,
    submission_execution_review_config=EXECUTION_REVIEW_PACK_CONFIG,
    result_recorder_config=RESULT_RECORDER_CONFIG,
    queue_dry_run_bridge_config=QUEUE_DRY_RUN_BRIDGE_CONFIG,
    real_manual_decision_config=REAL_MANUAL_DECISION_CONFIG,
    real_preview_bridge_config=REAL_PREVIEW_BRIDGE_CONFIG,
    real_promotion_dry_run_config=REAL_PROMOTION_DRY_RUN_CONFIG,
):
    return build_ftaw_real_verified_evidence_promotion_dry_run_pack_report(
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
    )


class FTAWRealVerifiedEvidencePromotionDryRunPackReportTests(unittest.TestCase):
    def test_default_report_prints_blocked_status_planned_table_and_safety_lines(self) -> None:
        report = _report()

        self.assertIn("promotion dry-run status: BLOCKED_NO_VERIFIED_EVIDENCE_PREVIEW", report)
        self.assertIn("planned item table:", report)
        self.assertIn("blocked reasons:", report)
        self.assertIn("no evidence verified: true", report)

    def test_partial_report_prints_partial_status_and_blockers(self) -> None:
        report = _report(
            PARTIAL_QUEUE_CONFIG,
            PARTIAL_DECISION_CONFIG,
            PARTIAL_PREVIEW_CONFIG,
            PARTIAL_DRY_RUN_CONFIG,
            PARTIAL_READINESS_CONFIG,
            recorder_config=PARTIAL_RECORDER_CONFIG,
            fact_config=PARTIAL_FACT_CONFIG,
            bridge_config=PARTIAL_BRIDGE_CONFIG,
            review_decision_config=PARTIAL_REVIEW_DECISION_CONFIG,
            submission_dry_run_config=PARTIAL_SUBMISSION_DRY_RUN_CONFIG,
            review_gate_config=PARTIAL_REVIEW_GATE_CONFIG,
            command_contract_config=PARTIAL_COMMAND_CONTRACT_CONFIG,
            submission_execution_review_config=PARTIAL_EXECUTION_REVIEW_PACK_CONFIG,
            result_recorder_config=PARTIAL_RESULT_RECORDER_CONFIG,
            queue_dry_run_bridge_config=PARTIAL_QUEUE_DRY_RUN_BRIDGE_CONFIG,
            real_manual_decision_config=PARTIAL_REAL_MANUAL_DECISION_CONFIG,
            real_preview_bridge_config=PARTIAL_REAL_PREVIEW_BRIDGE_CONFIG,
            real_promotion_dry_run_config=PARTIAL_REAL_PROMOTION_DRY_RUN_CONFIG,
        )

        self.assertIn("promotion dry-run status: PARTIAL_VERIFIED_EVIDENCE_PROMOTION_DRY_RUN_READY", report)
        self.assertIn("planned promotion item count: 1", report)
        self.assertIn("blocked reasons:", report)

    def test_complete_report_prints_ready_status_warnings_and_safety_lines(self) -> None:
        report = _report(
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
            COMPLETE_REAL_INTAKE_CONFIG,
            COMPLETE_CHECKLIST_CONFIG,
            COMPLETE_PLAN_CONFIG,
            COMPLETE_RECORDER_CONFIG,
            COMPLETE_FACT_CONFIG,
            COMPLETE_BRIDGE_CONFIG,
            COMPLETE_REVIEW_DECISION_CONFIG,
            COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
            COMPLETE_REVIEW_GATE_CONFIG,
            COMPLETE_COMMAND_CONTRACT_CONFIG,
            COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
            COMPLETE_RESULT_RECORDER_CONFIG,
            COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
            COMPLETE_REAL_MANUAL_DECISION_CONFIG,
            COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
            COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
        )

        self.assertIn(
            "promotion dry-run status: VERIFIED_EVIDENCE_PROMOTION_DRY_RUN_READY_FOR_CANDIDATE_READINESS_REVIEW",
            report,
        )
        self.assertIn("planned promotion item count: 5", report)
        for line in (
            "promotion dry-run is not evidence verification.",
            "promotion dry-run is not verified evidence promotion.",
            "promotion dry-run is not asset approval.",
            "promotion dry-run is not registry mutation.",
            "promotion dry-run is not allocation advice.",
            "promotion dry-run is not a buy/sell request.",
            "promotion dry-run is not trade execution.",
            "no evidence verified: true",
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
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

    def test_cli_report_runs_without_error_and_prints_planned_table_and_safety_lines(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_real_verified_evidence_promotion_dry_run_pack_report",
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
                COMPLETE_REAL_INTAKE_CONFIG,
                COMPLETE_CHECKLIST_CONFIG,
                COMPLETE_PLAN_CONFIG,
                COMPLETE_RECORDER_CONFIG,
                COMPLETE_FACT_CONFIG,
                COMPLETE_BRIDGE_CONFIG,
                COMPLETE_REVIEW_DECISION_CONFIG,
                COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
                COMPLETE_REVIEW_GATE_CONFIG,
                COMPLETE_COMMAND_CONTRACT_CONFIG,
                COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
                COMPLETE_RESULT_RECORDER_CONFIG,
                COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
                COMPLETE_REAL_MANUAL_DECISION_CONFIG,
                COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG,
                COMPLETE_REAL_PROMOTION_DRY_RUN_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn(
            "promotion dry-run status: VERIFIED_EVIDENCE_PROMOTION_DRY_RUN_READY_FOR_CANDIDATE_READINESS_REVIEW",
            result.stdout,
        )
        self.assertIn("planned item table:", result.stdout)
        self.assertIn("no automatic fact extraction: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
