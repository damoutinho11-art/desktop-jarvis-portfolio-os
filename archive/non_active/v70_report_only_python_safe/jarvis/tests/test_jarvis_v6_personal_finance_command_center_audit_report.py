import unittest

from jarvis.jarvis_v6_personal_finance_command_center_audit_report import (
    report_jarvis_v6_personal_finance_command_center_audit,
)


class JarvisV6PersonalFinanceCommandCenterAuditReportTests(unittest.TestCase):
    def test_report_contains_verdict_next_stage_and_safety_boundary(self) -> None:
        report = report_jarvis_v6_personal_finance_command_center_audit()

        self.assertIn("J.A.R.V.I.S. v6 Personal Finance Command Center Audit", report)
        self.assertIn("status: JARVIS_V6_COMMAND_CENTER_FOUNDATION_READY_NEXT_POLICY_INTELLIGENCE", report)
        self.assertIn("recommended next stage: v6.1_policy_intelligence_boundary", report)
        self.assertIn("public_data_foundation", report)
        self.assertIn("policy_intelligence", report)
        self.assertIn("weekly crypto buy allowed if within risk bands: True", report)
        self.assertIn("manual policy approval required: True", report)
        self.assertIn("manual buy execution only: True", report)
        self.assertIn("automatic policy change forbidden: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
