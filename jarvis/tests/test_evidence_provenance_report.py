import subprocess
import sys
import unittest

from jarvis.evidence_provenance_report import build_evidence_provenance_report


class EvidenceProvenanceReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_evidence_provenance_report(
            "jarvis/data/candidate_assets.v2.example.json",
            "jarvis/data/evidence_provenance.example.json",
        )

        self.assertIn("total candidates: 25", report)
        self.assertIn("candidates with only synthetic/test evidence", report)
        self.assertIn("real_status_promotion_allowed count: 0", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.evidence_provenance_report",
                "jarvis/data/candidate_assets.v2.example.json",
                "jarvis/data/evidence_provenance.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Evidence Provenance Gate Report", result.stdout)
        self.assertIn("no buy/sell requests: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
