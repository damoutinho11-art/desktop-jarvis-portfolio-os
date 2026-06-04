import subprocess
import sys
import unittest

from jarvis.candidate_review_report import build_candidate_review_report


class CandidateReviewReportTests(unittest.TestCase):
    def test_report_contains_review_pack_sections(self) -> None:
        report = build_candidate_review_report(
            "jarvis/data/candidate_assets.example.json",
            "jarvis/data/market_data.example.json",
            "jarvis/data/asset_exposure.example.json",
        )

        self.assertIn("J.A.R.V.I.S. Candidate Review Pack Report", report)
        self.assertIn("quality_etf_candidate", report)
        self.assertIn("No trades executed.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.candidate_review_report",
                "jarvis/data/candidate_assets.example.json",
                "jarvis/data/market_data.example.json",
                "jarvis/data/asset_exposure.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("total candidates", result.stdout)
        self.assertIn("btc_test_position", result.stdout)


if __name__ == "__main__":
    unittest.main()
