import subprocess
import sys
import unittest

from jarvis.contribution_plan_report import build_contribution_plan_report


class ContributionPlanReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_contribution_plan_report(
            "jarvis/data/contribution_plan.example.json",
            "jarvis/data/manual_snapshot.example.json",
            "jarvis/data/portfolio_policy.example.json",
            "jarvis/data/candidate_assets.example.json",
        )

        self.assertIn("J.A.R.V.I.S. Contribution Plan Report", report)
        self.assertIn("plan lines:", report)
        self.assertIn("No buy/sell requests created.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.contribution_plan_report",
                "jarvis/data/contribution_plan.example.json",
                "jarvis/data/manual_snapshot.example.json",
                "jarvis/data/portfolio_policy.example.json",
                "jarvis/data/candidate_assets.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("status:", result.stdout)
        self.assertIn("No trades executed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
