import subprocess
import sys
import unittest

from jarvis.source_evidence_report import build_source_evidence_report


class SourceEvidenceReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_source_evidence_report(
            "jarvis/data/candidate_assets.v2.example.json",
            "jarvis/data/source_evidence_sources.example.json",
        )

        self.assertIn("source evidence status", report)
        self.assertIn("total source configs:", report)
        self.assertIn("draft evidence records created:", report)
        self.assertIn("extracted fact summary:", report)
        self.assertIn("user verification required: true", report)
        self.assertIn("no approvals created: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.source_evidence_report",
                "jarvis/data/candidate_assets.v2.example.json",
                "jarvis/data/source_evidence_sources.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Source Evidence Draft Report", result.stdout)
        self.assertIn("no registry mutation: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
