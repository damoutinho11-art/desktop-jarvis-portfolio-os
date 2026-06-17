import unittest

from jarvis.jarvis_v6_10_active_policy_snapshot_gap_analyzer_report import (
    report_v6_10_active_policy_snapshot_gap_analyzer,
)


class JarvisV610ActivePolicySnapshotGapAnalyzerReportTests(unittest.TestCase):
    def test_report_contains_gap_analysis_and_safety(self) -> None:
        report = report_v6_10_active_policy_snapshot_gap_analyzer()

        self.assertIn("J.A.R.V.I.S. v6.10 Active Policy Snapshot Gap Analyzer", report)
        self.assertIn("status: JARVIS_V6_10_ACTIVE_POLICY_SNAPSHOT_GAP_ANALYZER_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.11_manual_weekly_planning_context_builder", report)
        self.assertIn("active_balanced_aggressive_manual_review", report)
        self.assertIn("crypto_core_btc", report)
        self.assertIn("UNDER_MIN", report)
        self.assertIn("cash_defensive", report)
        self.assertIn("OVER_MAX", report)
        self.assertIn("gap analyzer ready: True", report)
        self.assertIn("analysis only: True", report)
        self.assertIn("asset approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
