import unittest

from jarvis.jarvis_v8_4_operator_command_center_closeout_report import (
    report_v8_4_operator_command_center_closeout,
)


class JarvisV84OperatorCommandCenterCloseoutReportTests(unittest.TestCase):
    def test_report_contains_closeout_and_safety(self) -> None:
        report = report_v8_4_operator_command_center_closeout()

        self.assertIn("J.A.R.V.I.S. v8.4 Operator Command Center Closeout", report)
        self.assertIn("status: JARVIS_V8_4_OPERATOR_COMMAND_CENTER_CLOSEOUT_READY_SAFE", report)
        self.assertIn("closeout status: OPERATOR_COMMAND_CENTER_PRODUCT_LAYER_CLOSED_OUT", report)
        self.assertIn("recommended next stage: v9_0_public_market_data_source_selection_plan", report)
        self.assertIn("public_market_intelligence_operator_dashboard", report)
        self.assertIn("autonomous_research_cycle_status_panel", report)
        self.assertIn("weekly_recommendation_evidence_pack_integration", report)
        self.assertIn("portfolio_action_brief_generator", report)
        self.assertIn("execution_boundary_preservation", report)
        self.assertIn("v8 product layer complete: True", report)
        self.assertIn("product value not redundant: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
