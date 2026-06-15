import unittest

from jarvis.jarvis_v6_9_active_policy_registry_report import (
    report_v6_9_active_policy_registry,
)


class JarvisV69ActivePolicyRegistryReportTests(unittest.TestCase):
    def test_report_contains_active_policy_and_safety(self) -> None:
        report = report_v6_9_active_policy_registry()

        self.assertIn("J.A.R.V.I.S. v6.9 Active Policy Registry", report)
        self.assertIn("status: JARVIS_V6_9_ACTIVE_POLICY_REGISTRY_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.10_active_policy_snapshot_gap_analyzer", report)
        self.assertIn("active_balanced_aggressive_manual_review", report)
        self.assertIn("ACTIVE_POLICY_MANUAL_ONLY", report)
        self.assertIn("global_all_world_etf_candidate", report)
        self.assertIn("btc_candidate", report)
        self.assertIn("money_market_candidate", report)
        self.assertIn("active policy count: 1", report)
        self.assertIn("active policy record created: True", report)
        self.assertIn("manual approval satisfied: True", report)
        self.assertIn("automatic policy change forbidden: True", report)
        self.assertIn("asset approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
