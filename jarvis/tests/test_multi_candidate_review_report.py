import subprocess
import sys
import unittest

from jarvis.multi_candidate_review_report import build_multi_candidate_review_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"


class MultiCandidateReviewReportTests(unittest.TestCase):
    def test_report_contains_queue_summary_and_safety_lines(self) -> None:
        report = build_multi_candidate_review_report(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG)

        self.assertIn("queue status:", report)
        self.assertIn("total candidates: 25", report)
        self.assertIn("already reviewed count: 1", report)
        self.assertIn("top next evidence candidates:", report)
        self.assertIn("reviewed candidates:", report)
        self.assertIn("vwce_global_core_candidate", report)
        self.assertIn("no approved_investable: true", report)
        self.assertIn("no allocation recommendation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.multi_candidate_review_report",
                SOURCE_REGISTRY,
                REVIEWED_REGISTRY,
                QUEUE_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("J.A.R.V.I.S. Multi-Candidate Review Queue Report", result.stdout)
        self.assertIn("already reviewed count: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
