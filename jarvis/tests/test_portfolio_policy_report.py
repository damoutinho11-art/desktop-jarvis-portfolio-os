import subprocess
import sys
import unittest

from jarvis.portfolio_policy_report import build_portfolio_policy_report


class PortfolioPolicyReportTests(unittest.TestCase):
    def test_report_contains_policy_summary(self) -> None:
        report = build_portfolio_policy_report(
            "jarvis/data/portfolio_policy.example.json",
            "jarvis/data/candidate_assets.example.json",
        )

        self.assertIn("J.A.R.V.I.S. Portfolio Target Policy Report", report)
        self.assertIn("allocation_ready: False", report)
        self.assertIn("manual_approval_required: True", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.portfolio_policy_report",
                "jarvis/data/portfolio_policy.example.json",
                "jarvis/data/candidate_assets.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("sleeve targets and bands", result.stdout)
        self.assertIn("No trades executed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
