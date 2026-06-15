import unittest

from jarvis.jarvis_v6_8_active_policy_manual_approval_gate_report import (
    report_v6_8_active_policy_manual_approval_gate,
)


class JarvisV68ActivePolicyManualApprovalGateReportTests(unittest.TestCase):
    def test_report_contains_manual_approval_gate_and_safety(self) -> None:
        report = report_v6_8_active_policy_manual_approval_gate()

        self.assertIn("J.A.R.V.I.S. v6.8 Active Policy Manual Approval Gate", report)
        self.assertIn("status: JARVIS_V6_8_ACTIVE_POLICY_MANUAL_APPROVAL_GATE_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.9_active_policy_registry", report)
        self.assertIn("APPROVE_ACTIVE_POLICY_DRAFT", report)
        self.assertIn("draft_balanced_aggressive_manual_review", report)
        self.assertIn("active policy count: 0", report)
        self.assertIn("manual approval gate ready: True", report)
        self.assertIn("manual approval records only: True", report)
        self.assertIn("active policy registry deferred: True", report)
        self.assertIn("asset approval deferred: True", report)
        self.assertIn("weekly buy ticket deferred: True", report)
        self.assertIn("buy request deferred: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
