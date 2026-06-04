import subprocess
import sys
import unittest

from jarvis.contribution_approval_report import build_contribution_approval_report


class ContributionApprovalReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_contribution_approval_report(
            "jarvis/data/contribution_plan.example.json",
            "jarvis/data/manual_snapshot.example.json",
            "jarvis/data/portfolio_policy.example.json",
            "jarvis/data/candidate_assets.example.json",
        )

        self.assertIn("J.A.R.V.I.S. Contribution Approval Bridge Report", report)
        self.assertIn("generated approval requests:", report)
        self.assertIn("execution forbidden: True", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.contribution_approval_report",
                "jarvis/data/contribution_plan.example.json",
                "jarvis/data/manual_snapshot.example.json",
                "jarvis/data/portfolio_policy.example.json",
                "jarvis/data/candidate_assets.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("bridge status", result.stdout)
        self.assertIn("No trades executed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
