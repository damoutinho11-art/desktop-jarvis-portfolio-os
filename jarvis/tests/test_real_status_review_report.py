import subprocess
import sys
import unittest

from jarvis.real_status_review_report import build_real_status_review_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
SOURCES = "jarvis/data/source_evidence_sources.example.json"
PROMOTION = "jarvis/data/verified_evidence_promotion.example.json"


class RealStatusReviewReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_real_status_review_report(REGISTRY, SOURCES, PROMOTION)

        self.assertIn("bridge status:", report)
        self.assertIn("ready assets count:", report)
        self.assertIn("generated request preview count:", report)
        self.assertIn("manual approval required: True", report)
        self.assertIn("No registry mutation.", report)
        self.assertIn("No approvals created.", report)
        self.assertIn("No buy/sell requests created.", report)
        self.assertIn("No trades executed.", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.real_status_review_report",
                REGISTRY,
                SOURCES,
                PROMOTION,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Real Status Review Bridge Report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
