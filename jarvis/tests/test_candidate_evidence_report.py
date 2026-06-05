import subprocess
import sys
import unittest

from jarvis.candidate_evidence_report import build_candidate_evidence_report


class CandidateEvidenceReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_candidate_evidence_report(
            "jarvis/data/candidate_assets.v2.example.json",
            "jarvis/data/market_data.example.json",
            "jarvis/data/asset_exposure.example.json",
            "jarvis/data/portfolio_policy.example.json",
        )

        self.assertIn("matrix status", report)
        self.assertIn("total candidates: 25", report)
        self.assertIn("eligible count: 0", report)
        self.assertIn("top missing evidence categories:", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.candidate_evidence_report",
                "jarvis/data/candidate_assets.v2.example.json",
                "jarvis/data/market_data.example.json",
                "jarvis/data/asset_exposure.example.json",
                "jarvis/data/portfolio_policy.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Candidate Evidence Coverage Matrix", result.stdout)
        self.assertIn("no buy/sell requests: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
