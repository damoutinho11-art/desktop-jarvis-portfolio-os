import subprocess
import sys
import unittest

from jarvis.exposure_report import build_exposure_report


class ExposureReportTests(unittest.TestCase):
    def test_report_contains_deterministic_sections(self) -> None:
        report = build_exposure_report("jarvis/data/asset_exposure.example.json")

        self.assertIn("J.A.R.V.I.S. Exposure & Concentration Fixture Report", report)
        self.assertIn("combined top holdings:", report)
        self.assertIn("No trades executed.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "jarvis.exposure_report", "jarvis/data/asset_exposure.example.json"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Read-only local fixture", result.stdout)
        self.assertIn("quality_etf_candidate", result.stdout)


if __name__ == "__main__":
    unittest.main()
