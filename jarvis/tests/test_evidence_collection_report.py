import subprocess
import sys
import unittest

from jarvis.evidence_collection_report import build_evidence_collection_report


class EvidenceCollectionReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_evidence_collection_report(
            "jarvis/data/candidate_assets.v2.example.json",
            "jarvis/data/verified_evidence_intake.example.json",
        )

        self.assertIn("checklist status", report)
        self.assertIn("total candidates: 25", report)
        self.assertIn("complete checklists:", report)
        self.assertIn("top missing evidence types:", report)
        self.assertIn("candidates ready for real status review evidence collection complete:", report)
        self.assertIn("no approvals created: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.evidence_collection_report",
                "jarvis/data/candidate_assets.v2.example.json",
                "jarvis/data/verified_evidence_intake.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Evidence Collection Checklist Report", result.stdout)
        self.assertIn("no registry mutation: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
