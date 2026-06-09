import subprocess
import sys
import unittest

from jarvis.ftaw_verified_evidence_promotion_dry_run_report import (
    build_ftaw_verified_evidence_promotion_dry_run_report,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
SYNTHETIC_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
SYNTHETIC_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
SYNTHETIC_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json"
SYNTHETIC_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_pass.example.json"


class FTAWVerifiedEvidencePromotionDryRunReportTests(unittest.TestCase):
    def test_default_report_contains_zero_plan_and_safety_lines(self) -> None:
        report = build_ftaw_verified_evidence_promotion_dry_run_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            QUEUE_CONFIG,
            DECISION_CONFIG,
            PREVIEW_CONFIG,
            DRY_RUN_CONFIG,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Verified Evidence Promotion Dry-Run Report", report)
        self.assertIn("planned_for_promotion count: 0", report)
        self.assertIn("promotion dry-run is not verified evidence promotion.", report)
        self.assertIn("promotion dry-run is not asset approval.", report)
        self.assertIn("promotion dry-run is not registry mutation.", report)
        self.assertIn("promotion dry-run is not allocation advice.", report)
        self.assertIn("promotion dry-run is not a buy/sell request.", report)
        self.assertIn("promotion dry-run is not trade execution.", report)
        self.assertIn("no verified evidence promotion: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no allocation recommendation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_synthetic_report_contains_one_planned_promotion(self) -> None:
        report = build_ftaw_verified_evidence_promotion_dry_run_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            SYNTHETIC_QUEUE_CONFIG,
            SYNTHETIC_DECISION_CONFIG,
            SYNTHETIC_PREVIEW_CONFIG,
            SYNTHETIC_DRY_RUN_CONFIG,
        )

        self.assertIn("status: DRY_RUN_PLANNED", report)
        self.assertIn("planned_for_promotion count: 1", report)
        self.assertIn("ftaw_global_core_candidate | evidence_type: fund_metadata", report)
        self.assertIn("planned_promotion_status: planned_for_promotion", report)
        self.assertIn("no trades executed: true", report)

    def test_default_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_verified_evidence_promotion_dry_run_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                QUEUE_CONFIG,
                DECISION_CONFIG,
                PREVIEW_CONFIG,
                DRY_RUN_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("planned_for_promotion count: 0", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)

    def test_synthetic_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_verified_evidence_promotion_dry_run_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                SYNTHETIC_QUEUE_CONFIG,
                SYNTHETIC_DECISION_CONFIG,
                SYNTHETIC_PREVIEW_CONFIG,
                SYNTHETIC_DRY_RUN_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("status: DRY_RUN_PLANNED", result.stdout)
        self.assertIn("planned_for_promotion count: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
