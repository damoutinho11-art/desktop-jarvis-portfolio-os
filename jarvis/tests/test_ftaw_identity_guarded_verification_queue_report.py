import subprocess
import sys
import unittest

from jarvis.ftaw_identity_guarded_verification_queue_report import (
    build_ftaw_identity_guarded_verification_queue_report,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
SYNTHETIC_PASS_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"


class FTAWIdentityGuardedVerificationQueueReportTests(unittest.TestCase):
    def test_report_contains_counts_items_and_safety_lines(self) -> None:
        report = build_ftaw_identity_guarded_verification_queue_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            QUEUE_CONFIG,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Identity-Guarded Verification Queue Report", report)
        self.assertIn("target asset: ftaw_global_core_candidate", report)
        self.assertIn("total input evidence/source-fact items: 5", report)
        self.assertIn("queued count: 5", report)
        self.assertIn("eligible_for_manual_verification count: 0", report)
        self.assertIn("needs_source_facts count: 5", report)
        self.assertIn("needs_identity_confirmation count: 0", report)
        self.assertIn("blocked_source_identity_mismatch count: 0", report)
        self.assertIn("manual_only_skipped count: 0", report)
        self.assertIn("eligible_for_manual_verification is not approval.", report)
        self.assertIn("eligible_for_manual_verification is not verified evidence.", report)
        self.assertIn("eligible_for_manual_verification is not a buy signal.", report)
        self.assertIn("fund_metadata | source:", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no allocation recommendation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_identity_guarded_verification_queue_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                QUEUE_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Identity-Guarded Verification Queue Report", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)

    def test_synthetic_pass_report_shows_eligible_item_and_safety_lines(self) -> None:
        report = build_ftaw_identity_guarded_verification_queue_report(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            SYNTHETIC_PASS_CONFIG,
        )

        self.assertIn("queue status: READY_FOR_MANUAL_VERIFICATION", report)
        self.assertIn("eligible_for_manual_verification count: 1", report)
        self.assertIn("manual_only_skipped count: 2", report)
        self.assertIn("fund_metadata | source: Synthetic FTAW provider product page | status: eligible_for_manual_verification", report)
        self.assertIn("eligible_for_manual_verification is not approval.", report)
        self.assertIn("eligible_for_manual_verification is not verified evidence.", report)
        self.assertIn("eligible_for_manual_verification is not a buy signal.", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no allocation recommendation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_synthetic_pass_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_identity_guarded_verification_queue_report",
                SOURCE_REGISTRY,
                "None",
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
                GUARD_CONFIG,
                SYNTHETIC_PASS_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("queue status: READY_FOR_MANUAL_VERIFICATION", result.stdout)
        self.assertIn("eligible_for_manual_verification count: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
