import unittest

from jarvis.jarvis_v6_6_manual_policy_review_queue_report import (
    report_v6_6_manual_policy_review_queue,
)


class JarvisV66ManualPolicyReviewQueueReportTests(unittest.TestCase):
    def test_report_contains_review_decisions_and_safety(self) -> None:
        report = report_v6_6_manual_policy_review_queue()

        self.assertIn("J.A.R.V.I.S. v6.6 Manual Policy Review Queue", report)
        self.assertIn("status: JARVIS_V6_6_MANUAL_POLICY_REVIEW_QUEUE_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.7_active_policy_draft_registry", report)
        self.assertIn("ACCEPT_FOR_ACTIVE_POLICY_REVIEW", report)
        self.assertIn("DEFER", report)
        self.assertIn("REJECT", report)
        self.assertIn("NEEDS_CORRECTION", report)
        self.assertIn("balanced_aggressive_manual_review", report)
        self.assertIn("core_etf_btc_accumulation", report)
        self.assertIn("manual review records only: True", report)
        self.assertIn("active policy creation deferred: True", report)
        self.assertIn("policy approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
