import subprocess
import sys
import unittest

from jarvis.universe_review_report import build_universe_review_report


class UniverseReviewReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_universe_review_report(
            "jarvis/data/candidate_assets.example.json",
            "jarvis/data/market_data.example.json",
            "jarvis/data/asset_exposure.example.json",
            "jarvis/data/portfolio_policy.example.json",
        )

        self.assertIn("J.A.R.V.I.S. Universe Review Report", report)
        self.assertIn("suggested_next_status", report)
        self.assertIn("No approvals created.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.universe_review_report",
                "jarvis/data/candidate_assets.example.json",
                "jarvis/data/market_data.example.json",
                "jarvis/data/asset_exposure.example.json",
                "jarvis/data/portfolio_policy.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("total candidates", result.stdout)
        self.assertIn("No trades executed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
