import subprocess
import sys
import unittest

from jarvis.verified_evidence_report import build_verified_evidence_report


class VerifiedEvidenceReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_verified_evidence_report(
            "jarvis/data/candidate_assets.v2.example.json",
            "jarvis/data/verified_evidence_intake.example.json",
        )

        self.assertIn("intake status", report)
        self.assertIn("total records:", report)
        self.assertIn("valid records:", report)
        self.assertIn("assets with real_status_promotion_allowed:", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no approvals created: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.verified_evidence_report",
                "jarvis/data/candidate_assets.v2.example.json",
                "jarvis/data/verified_evidence_intake.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Verified Evidence Intake Report", result.stdout)
        self.assertIn("no buy/sell requests: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
