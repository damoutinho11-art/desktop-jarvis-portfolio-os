import subprocess
import sys
import unittest

from jarvis.ftaw_source_identity_guard_report import build_ftaw_source_identity_guard_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"


class FTAWSourceIdentityGuardReportTests(unittest.TestCase):
    def test_report_contains_summary_and_safety_lines(self) -> None:
        report = build_ftaw_source_identity_guard_report(SOURCE_REGISTRY, REVIEWED_REGISTRY, INTAKE_CONFIG, GUARD_CONFIG)

        self.assertIn("Do not trust facts unless they belong to the exact asset.", report)
        self.assertIn("FTAW source identity guard status: needs_identity_confirmation", report)
        self.assertIn("target asset: ftaw_global_core_candidate", report)
        self.assertIn("placeholder identity fields:", report)
        self.assertIn("identity guard passed: false", report)
        self.assertIn("manual verification still required: true", report)
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
                "jarvis.ftaw_source_identity_guard_report",
                SOURCE_REGISTRY,
                REVIEWED_REGISTRY,
                INTAKE_CONFIG,
                GUARD_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Source Identity Guard Report", result.stdout)
        self.assertIn("identity guard passed: false", result.stdout)


if __name__ == "__main__":
    unittest.main()
