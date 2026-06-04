import subprocess
import sys
import unittest

from jarvis.approved_universe_report import build_approved_universe_report


class ApprovedUniverseReportTests(unittest.TestCase):
    def test_report_contains_summary(self) -> None:
        report = build_approved_universe_report("jarvis/data/candidate_assets.example.json")

        self.assertIn("J.A.R.V.I.S. Approved Universe Report", report)
        self.assertIn("total approved assets: 0", report)
        self.assertIn("Manual approval remains required", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "jarvis.approved_universe_report", "jarvis/data/candidate_assets.example.json"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("blocked/non-approved assets count", result.stdout)
        self.assertIn("No trades executed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
