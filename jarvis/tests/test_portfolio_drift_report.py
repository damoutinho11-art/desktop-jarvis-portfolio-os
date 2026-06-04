import subprocess
import sys
import unittest

from jarvis.portfolio_drift_report import build_portfolio_drift_report


class PortfolioDriftReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_portfolio_drift_report(
            "jarvis/data/manual_snapshot.example.json",
            "jarvis/data/portfolio_policy.example.json",
            "jarvis/data/candidate_assets.example.json",
        )

        self.assertIn("J.A.R.V.I.S. Portfolio Drift Report", report)
        self.assertIn("sleeve drift table:", report)
        self.assertIn("Manual approval still required.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.portfolio_drift_report",
                "jarvis/data/manual_snapshot.example.json",
                "jarvis/data/portfolio_policy.example.json",
                "jarvis/data/candidate_assets.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("allocation_ready:", result.stdout)
        self.assertIn("No trades executed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
