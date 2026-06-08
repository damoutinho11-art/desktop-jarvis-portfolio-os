import subprocess
import sys
import unittest

from jarvis.global_core_source_collection_report import build_global_core_source_collection_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"
EXPANDER_CONFIG = "jarvis/data/global_core_source_template_expander.example.json"
PLANNER_CONFIG = "jarvis/data/global_core_source_collection_planner.example.json"


class GlobalCoreSourceCollectionReportTests(unittest.TestCase):
    def test_report_contains_summary_and_safety_lines(self) -> None:
        report = build_global_core_source_collection_report(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )

        self.assertIn("collection plan status: READY", report)
        self.assertIn("target candidates count: 4", report)
        self.assertIn("total collection tasks: 28", report)
        self.assertIn("account-specific manual tasks count: 4", report)
        self.assertIn("manual tax review tasks count: 4", report)
        self.assertIn("auto-fetch allowed count: 0", report)
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
                "jarvis.global_core_source_collection_report",
                SOURCE_REGISTRY,
                REVIEWED_REGISTRY,
                QUEUE_CONFIG,
                BATCH_CONFIG,
                EXPANDER_CONFIG,
                PLANNER_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("J.A.R.V.I.S. Global Core Source Collection Plan Report", result.stdout)
        self.assertIn("total collection tasks: 28", result.stdout)


if __name__ == "__main__":
    unittest.main()
