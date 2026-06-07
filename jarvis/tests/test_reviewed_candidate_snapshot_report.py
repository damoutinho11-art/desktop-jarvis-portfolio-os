import subprocess
import sys
import unittest

from jarvis.reviewed_candidate_snapshot_report import build_reviewed_candidate_snapshot_report


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
FRESHNESS_POLICY = "jarvis/data/evidence_freshness_policy.example.json"
SNAPSHOT_CONFIG = "jarvis/data/reviewed_candidate_snapshot.example.json"


class ReviewedCandidateSnapshotReportTests(unittest.TestCase):
    def test_report_contains_snapshot_safety_lines(self) -> None:
        report = build_reviewed_candidate_snapshot_report(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, PRIVATE_INTAKE, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertIn("snapshot status: READY", report)
        self.assertIn("target asset: vwce_global_core_candidate", report)
        self.assertIn("previous_status: candidate_unreviewed", report)
        self.assertIn("current_status: candidate_reviewed", report)
        self.assertIn("not approved_investable: true", report)
        self.assertIn("no allocation recommendation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trade executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.reviewed_candidate_snapshot_report",
                SOURCE_REGISTRY,
                REVIEWED_REGISTRY,
                PRIVATE_INTAKE,
                FRESHNESS_POLICY,
                SNAPSHOT_CONFIG,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("snapshot status: READY", result.stdout)
        self.assertIn("future gates required:", result.stdout)


if __name__ == "__main__":
    unittest.main()
