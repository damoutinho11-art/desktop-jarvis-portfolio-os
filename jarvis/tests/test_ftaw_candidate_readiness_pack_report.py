import subprocess
import sys
import unittest

from jarvis.ftaw_candidate_readiness_pack_report import build_ftaw_candidate_readiness_pack_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
SYNTHETIC_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_complete.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
SYNTHETIC_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_complete.example.json"
PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
SYNTHETIC_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_complete.example.json"
DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json"
SYNTHETIC_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_complete.example.json"
READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.example.json"
SYNTHETIC_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_complete.example.json"


class FTAWCandidateReadinessPackReportTests(unittest.TestCase):
    def test_default_report_contains_blocked_and_safety_lines(self) -> None:
        report = build_ftaw_candidate_readiness_pack_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            QUEUE_CONFIG,
            DECISION_CONFIG,
            PREVIEW_CONFIG,
            DRY_RUN_CONFIG,
            READINESS_CONFIG,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Candidate Readiness Pack Report", report)
        self.assertIn("candidate readiness status: BLOCKED", report)
        self.assertIn("identity guard status: needs_identity_confirmation", report)
        self.assertIn("candidate readiness is not asset approval.", report)
        self.assertIn("candidate readiness is not verified evidence promotion.", report)
        self.assertIn("candidate readiness is not registry mutation.", report)
        self.assertIn("candidate readiness is not allocation advice.", report)
        self.assertIn("candidate readiness is not a buy/sell request.", report)
        self.assertIn("candidate readiness is not trade execution.", report)
        self.assertIn("no verified evidence promotion: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no allocation recommendation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_synthetic_report_contains_ready_for_promotion_not_approval(self) -> None:
        report = build_ftaw_candidate_readiness_pack_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            SYNTHETIC_QUEUE_CONFIG,
            SYNTHETIC_DECISION_CONFIG,
            SYNTHETIC_PREVIEW_CONFIG,
            SYNTHETIC_DRY_RUN_CONFIG,
            SYNTHETIC_READINESS_CONFIG,
        )

        self.assertIn("candidate readiness status: READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION", report)
        self.assertIn("planned promotion evidence types count: 1", report)
        self.assertIn("- fund_metadata", report)
        self.assertIn("missing evidence types count: 4", report)
        self.assertIn("ready for manual approval review: false", report)
        self.assertIn("candidate readiness is not asset approval.", report)

    def test_synthetic_complete_report_contains_full_coverage_and_manual_review_warnings(self) -> None:
        report = build_ftaw_candidate_readiness_pack_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            SYNTHETIC_COMPLETE_QUEUE_CONFIG,
            SYNTHETIC_COMPLETE_DECISION_CONFIG,
            SYNTHETIC_COMPLETE_PREVIEW_CONFIG,
            SYNTHETIC_COMPLETE_DRY_RUN_CONFIG,
            SYNTHETIC_COMPLETE_READINESS_CONFIG,
        )

        self.assertIn("candidate readiness status: READY_FOR_MANUAL_APPROVAL_REVIEW", report)
        self.assertIn("planned promotion evidence types count: 5", report)
        self.assertIn("missing evidence types count: 0", report)
        self.assertIn("ready for manual approval review: true", report)
        self.assertIn("manual approval review readiness is not asset approval.", report)
        self.assertIn("manual approval review readiness is not a buy signal.", report)
        self.assertIn("manual approval review readiness is not registry mutation.", report)
        self.assertIn("manual approval review readiness is not trade execution.", report)
        self.assertIn("no trades executed: true", report)

    def test_default_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_candidate_readiness_pack_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                QUEUE_CONFIG,
                DECISION_CONFIG,
                PREVIEW_CONFIG,
                DRY_RUN_CONFIG,
                READINESS_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("candidate readiness status: BLOCKED", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)

    def test_synthetic_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_candidate_readiness_pack_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                SYNTHETIC_QUEUE_CONFIG,
                SYNTHETIC_DECISION_CONFIG,
                SYNTHETIC_PREVIEW_CONFIG,
                SYNTHETIC_DRY_RUN_CONFIG,
                SYNTHETIC_READINESS_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("candidate readiness status: READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)

    def test_synthetic_complete_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_candidate_readiness_pack_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                SYNTHETIC_COMPLETE_QUEUE_CONFIG,
                SYNTHETIC_COMPLETE_DECISION_CONFIG,
                SYNTHETIC_COMPLETE_PREVIEW_CONFIG,
                SYNTHETIC_COMPLETE_DRY_RUN_CONFIG,
                SYNTHETIC_COMPLETE_READINESS_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("candidate readiness status: READY_FOR_MANUAL_APPROVAL_REVIEW", result.stdout)
        self.assertIn("planned promotion evidence types count: 5", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
