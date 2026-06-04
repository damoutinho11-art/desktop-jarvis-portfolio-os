import subprocess
import sys
import unittest

from jarvis.market_snapshot_report import report_market_snapshot


class MarketSnapshotReportTests(unittest.TestCase):
    def test_report_contains_deterministic_sections(self) -> None:
        report = report_market_snapshot("jarvis/data/market_data.example.json")

        self.assertIn("J.A.R.V.I.S. Market Data Fixture Report", report)
        self.assertIn("asset_id: quality_etf_candidate", report)
        self.assertIn("No trades executed.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "jarvis.market_snapshot_report", "jarvis/data/market_data.example.json"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Read-only local fixture", result.stdout)
        self.assertIn("btc_test_position", result.stdout)


if __name__ == "__main__":
    unittest.main()
