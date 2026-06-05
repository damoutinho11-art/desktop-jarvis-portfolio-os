import subprocess
import sys
import unittest

from jarvis.evidence_verification_report import build_evidence_verification_report


class EvidenceVerificationReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_evidence_verification_report(
            "jarvis/data/candidate_assets.v2.example.json",
            "jarvis/data/source_evidence_sources.example.json",
        )

        self.assertIn("verification queue status", report)
        self.assertIn("total draft evidence records:", report)
        self.assertIn("pending verification tasks:", report)
        self.assertIn("sample verification questions:", report)
        self.assertIn("no approvals created: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.evidence_verification_report",
                "jarvis/data/candidate_assets.v2.example.json",
                "jarvis/data/source_evidence_sources.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Evidence Verification Queue Report", result.stdout)
        self.assertIn("no registry mutation: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
