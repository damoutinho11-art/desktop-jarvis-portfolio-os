import unittest

from jarvis.jarvis_v6_7_active_policy_draft_registry_report import (
    report_v6_7_active_policy_draft_registry,
)


class JarvisV67ActivePolicyDraftRegistryReportTests(unittest.TestCase):
    def test_report_contains_draft_registry_and_safety(self) -> None:
        report = report_v6_7_active_policy_draft_registry()

        self.assertIn("J.A.R.V.I.S. v6.7 Active Policy Draft Registry", report)
        self.assertIn("status: JARVIS_V6_7_ACTIVE_POLICY_DRAFT_REGISTRY_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.8_active_policy_manual_approval_gate", report)
        self.assertIn("draft_balanced_aggressive_manual_review", report)
        self.assertIn("balanced_aggressive_manual_review", report)
        self.assertIn("global_all_world_etf_candidate", report)
        self.assertIn("btc_candidate", report)
        self.assertIn("money_market_candidate", report)
        self.assertIn("active policy count: 0", report)
        self.assertIn("draft only: True", report)
        self.assertIn("manual approval required: True", report)
        self.assertIn("active policy approval deferred: True", report)
        self.assertIn("active policy activation deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
