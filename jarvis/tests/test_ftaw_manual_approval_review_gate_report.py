import subprocess
import sys
import unittest

from jarvis.ftaw_manual_approval_review_gate_report import build_ftaw_manual_approval_review_gate_report


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


def _report(queue_config=QUEUE_CONFIG, decision_config=DECISION_CONFIG, preview_config=PREVIEW_CONFIG, dry_run_config=DRY_RUN_CONFIG, readiness_config=READINESS_CONFIG, gate_config=GATE_CONFIG):
    return build_ftaw_manual_approval_review_gate_report(
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
        gate_config,
    )


class FTAWManualApprovalReviewGateReportTests(unittest.TestCase):
    def test_default_report_blocks_and_prints_safety_lines(self) -> None:
        report = _report()

        self.assertIn("J.A.R.V.I.S. FTAW Manual Approval Review Gate Report", report)
        self.assertIn("approval review gate status: BLOCKED", report)
        self.assertIn("review packet created: false", report)
        self.assertIn("approval review packet is not asset approval.", report)
        self.assertIn("approval review packet is not verified evidence promotion.", report)
        self.assertIn("approval review packet is not registry mutation.", report)
        self.assertIn("approval review packet is not allocation advice.", report)
        self.assertIn("approval review packet is not a buy/sell request.", report)
        self.assertIn("approval review packet is not trade execution.", report)
        self.assertIn("no verified evidence promotion: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no allocation recommendations: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_partial_synthetic_report_blocks(self) -> None:
        report = _report(PARTIAL_QUEUE_CONFIG, PARTIAL_DECISION_CONFIG, PARTIAL_PREVIEW_CONFIG, PARTIAL_DRY_RUN_CONFIG, PARTIAL_READINESS_CONFIG)

        self.assertIn("approval review gate status: BLOCKED", report)
        self.assertIn("candidate readiness status: READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION", report)
        self.assertIn("review packet created: false", report)

    def test_synthetic_complete_report_creates_review_packet(self) -> None:
        report = _report(COMPLETE_QUEUE_CONFIG, COMPLETE_DECISION_CONFIG, COMPLETE_PREVIEW_CONFIG, COMPLETE_DRY_RUN_CONFIG, COMPLETE_READINESS_CONFIG, COMPLETE_GATE_CONFIG)

        self.assertIn("approval review gate status: READY_FOR_HUMAN_APPROVAL_REVIEW", report)
        self.assertIn("review packet created: true", report)
        self.assertIn("- approval_review_only: true", report)
        self.assertIn("- approved: false", report)
        self.assertIn("- approval_status_change: false", report)
        self.assertIn("- buy_signal: false", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_report_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_manual_approval_review_gate_report",
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
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("approval review gate status: READY_FOR_HUMAN_APPROVAL_REVIEW", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
