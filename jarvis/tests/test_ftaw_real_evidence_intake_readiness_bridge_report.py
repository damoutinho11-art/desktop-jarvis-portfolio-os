import subprocess
import sys
import unittest

from jarvis.ftaw_real_evidence_intake_readiness_bridge_report import (
    build_ftaw_real_evidence_intake_readiness_bridge_report,
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
):
    return build_ftaw_real_evidence_intake_readiness_bridge_report(
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
    )


class FTAWRealEvidenceIntakeReadinessBridgeReportTests(unittest.TestCase):
    def test_default_report_prints_not_ready_status_and_safety_lines(self) -> None:
        report = _report()

        self.assertIn("real evidence intake readiness status: NOT_READY_FOR_REAL_EVIDENCE_INTAKE", report)
        self.assertIn("real evidence intake readiness is not asset approval.", report)
        self.assertIn("real evidence intake planning does not ingest private files automatically.", report)
        self.assertIn("no executor created: true", report)

    def test_partial_report_prints_partial_status_and_blockers(self) -> None:
        report = _report(
            PARTIAL_QUEUE_CONFIG,
            PARTIAL_DECISION_CONFIG,
            PARTIAL_PREVIEW_CONFIG,
            PARTIAL_DRY_RUN_CONFIG,
            PARTIAL_READINESS_CONFIG,
        )

        self.assertIn("real evidence intake readiness status: PARTIAL_READY_FOR_REAL_EVIDENCE_INTAKE", report)
        self.assertIn("blocked reasons:", report)

    def test_synthetic_complete_report_prints_ready_status_and_real_evidence_plan(self) -> None:
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
        )

        self.assertIn("real evidence intake readiness status: READY_FOR_REAL_EVIDENCE_INTAKE_PLANNING", report)
        self.assertIn("- platform_availability", report)
        self.assertIn("- broker/account-specific availability confirmation", report)
        self.assertIn("real evidence collected: false", report)
        self.assertIn("evidence verified: false", report)

    def test_cli_report_runs_without_error_and_prints_safety_text(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_real_evidence_intake_readiness_bridge_report",
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
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("real evidence intake readiness status: READY_FOR_REAL_EVIDENCE_INTAKE_PLANNING", result.stdout)
        self.assertIn("no executor created: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
