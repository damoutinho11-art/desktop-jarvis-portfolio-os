import subprocess
import sys
import unittest

from jarvis.ftaw_public_source_auto_draft_report import build_ftaw_public_source_auto_draft_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
RESEARCH_CONFIG = "jarvis/data/ftaw_public_source_research_pack.example.json"
VERIFICATION_CONFIG = "jarvis/data/ftaw_draft_evidence_verification_queue.example.json"
AUTO_CONFIG = "jarvis/data/ftaw_public_source_auto_draft.example.json"


class FTAWPublicSourceAutoDraftReportTests(unittest.TestCase):
    def test_report_contains_summary_and_safety_lines(self) -> None:
        report = build_ftaw_public_source_auto_draft_report(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, RESEARCH_CONFIG, VERIFICATION_CONFIG, AUTO_CONFIG
        )

        self.assertIn("Automated research. Manual trust.", report)
        self.assertIn("processed source count: 5", report)
        self.assertIn("skipped source count: 1", report)
        self.assertIn("draft evidence records count: 5", report)
        self.assertIn("needs-correction count: 5", report)
        self.assertIn("network fetch enabled count: 0", report)
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
                "jarvis.ftaw_public_source_auto_draft_report",
                SOURCE_REGISTRY,
                REVIEWED_REGISTRY,
                RESEARCH_CONFIG,
                VERIFICATION_CONFIG,
                AUTO_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Public Source Auto-Draft Report", result.stdout)
        self.assertIn("draft evidence records count: 5", result.stdout)


if __name__ == "__main__":
    unittest.main()
