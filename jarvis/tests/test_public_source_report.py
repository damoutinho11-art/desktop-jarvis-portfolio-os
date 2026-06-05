import subprocess
import sys
import unittest

from jarvis.public_source_report import build_public_source_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PUBLIC_SOURCES = "jarvis/data/public_source_fetch.example.json"


class PublicSourceReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_public_source_report(REGISTRY, PUBLIC_SOURCES)

        self.assertIn("public fetch status:", report)
        self.assertIn("total source configs:", report)
        self.assertIn("draft evidence records created:", report)
        self.assertIn("blocked sources:", report)
        self.assertIn("fetched/fallback mode:", report)
        self.assertIn("user verification required: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.public_source_report",
                REGISTRY,
                PUBLIC_SOURCES,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Public Source Fetch Report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
