import unittest

from jarvis.jarvis_v6_15_autonomous_command_center_closeout_audit_report import (
    report_v6_15_autonomous_command_center_closeout_audit,
)


class JarvisV615AutonomousCommandCenterCloseoutAuditReportTests(unittest.TestCase):
    def test_report_contains_closeout_and_safety(self) -> None:
        report = report_v6_15_autonomous_command_center_closeout_audit()

        self.assertIn("J.A.R.V.I.S. v6.15 Autonomous Command Center Closeout Audit", report)
        self.assertIn("status: JARVIS_V6_15_AUTONOMOUS_COMMAND_CENTER_CLOSEOUT_AUDIT_READY_SAFE", report)
        self.assertIn("recommended next stage: v7_0_autonomous_market_intelligence_expansion", report)
        self.assertIn("v6 chain complete: True", report)
        self.assertIn("autonomous intelligence ready: True", report)
        self.assertIn("command center ready: True", report)
        self.assertIn("active_policy_gap_analysis_ready", report)
        self.assertIn("autonomous_recommendation_ready", report)
        self.assertIn("dashboard_integration_ready", report)
        self.assertIn("only_final_buy_is_manual", report)
        self.assertIn("no_execution_path_exists", report)
        self.assertIn("no manual review queue added: True", report)
        self.assertIn("no buy request created: True", report)
        self.assertIn("no broker connection created: True", report)
        self.assertIn("no order placement created: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
