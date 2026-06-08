import subprocess
import sys
import unittest

from jarvis.ftaw_public_source_research_report import build_ftaw_public_source_research_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"
EXPANDER_CONFIG = "jarvis/data/global_core_source_template_expander.example.json"
PLANNER_CONFIG = "jarvis/data/global_core_source_collection_planner.example.json"
SOURCE_PACK_CONFIG = "jarvis/data/ftaw_source_collection_pack.example.json"
RESEARCH_CONFIG = "jarvis/data/ftaw_public_source_research_pack.example.json"


class FTAWPublicSourceResearchReportTests(unittest.TestCase):
    def test_report_contains_summary_and_safety_lines(self) -> None:
        report = build_ftaw_public_source_research_report(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            QUEUE_CONFIG,
            BATCH_CONFIG,
            EXPANDER_CONFIG,
            PLANNER_CONFIG,
            SOURCE_PACK_CONFIG,
            RESEARCH_CONFIG,
        )

        self.assertIn("FTAW public research pack status: READY", report)
        self.assertIn("target asset: ftaw_global_core_candidate", report)
        self.assertIn("public research tasks count: 5", report)
        self.assertIn("draft evidence records count: 5", report)
        self.assertIn("platform_availability", report)
        self.assertIn("tax_route", report)
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
                "jarvis.ftaw_public_source_research_report",
                SOURCE_REGISTRY,
                REVIEWED_REGISTRY,
                QUEUE_CONFIG,
                BATCH_CONFIG,
                EXPANDER_CONFIG,
                PLANNER_CONFIG,
                SOURCE_PACK_CONFIG,
                RESEARCH_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("J.A.R.V.I.S. FTAW Public Source Research Pack Report", result.stdout)
        self.assertIn("draft evidence records count: 5", result.stdout)


if __name__ == "__main__":
    unittest.main()
