import subprocess
import sys
import unittest

from jarvis.ftaw_source_fact_intake_report import build_ftaw_source_fact_intake_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"


class FTAWSourceFactIntakeReportTests(unittest.TestCase):
    def test_report_contains_summary_and_safety_lines(self) -> None:
        report = build_ftaw_source_fact_intake_report(SOURCE_REGISTRY, REVIEWED_REGISTRY, URL_FETCH_CONFIG, INTAKE_CONFIG)

        self.assertIn("Automated structure. Manual trust.", report)
        self.assertIn("FTAW source fact intake status: READY_WITH_CORRECTIONS", report)
        self.assertIn("processed fact records count: 5", report)
        self.assertIn("draft evidence records count: 5", report)
        self.assertIn("draft-ready count: 0", report)
        self.assertIn("needs-correction count: 5", report)
        self.assertIn("distribution_policy: distribution_policy, accumulating_or_distributing, as_of_date", report)
        self.assertIn("exposure_data: top_holdings_source, country_exposure_source, sector_exposure_source, as_of_date", report)
        self.assertIn("sample draft record:", report)
        self.assertIn('"verified_by_user": false', report)
        self.assertIn("manual verification required: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no allocation recommendation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.ftaw_source_fact_intake_report",
                SOURCE_REGISTRY,
                REVIEWED_REGISTRY,
                URL_FETCH_CONFIG,
                INTAKE_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Source Fact Intake Report", result.stdout)
        self.assertIn("draft evidence records count: 5", result.stdout)


if __name__ == "__main__":
    unittest.main()
