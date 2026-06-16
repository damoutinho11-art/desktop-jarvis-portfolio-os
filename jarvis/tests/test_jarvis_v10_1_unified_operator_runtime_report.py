import unittest

from jarvis.jarvis_v10_1_unified_operator_runtime_report import (
    report_v10_1_unified_operator_runtime,
)


class JarvisV101UnifiedOperatorRuntimeReportTests(unittest.TestCase):
    def test_report_contains_operator_runtime_sections(self) -> None:
        report = report_v10_1_unified_operator_runtime()

        self.assertIn("J.A.R.V.I.S. v10.1 Unified Operator Runtime", report)
        self.assertIn("status: JARVIS_V10_1_UNIFIED_OPERATOR_RUNTIME_READY_SAFE", report)
        self.assertIn("runtime status: UNIFIED_OPERATOR_RUNTIME_READY", report)
        self.assertIn("recommended next stage: v11_0_command_center_ui_shell", report)
        self.assertIn("component count: 6", report)
        self.assertIn("ready component count: 6", report)
        self.assertIn("blocked component count: 0", report)
        self.assertIn("autonomous_public_data_refresh_runtime", report)
        self.assertIn("weekly_recommendation_evidence_pack", report)
        self.assertIn("portfolio_action_brief", report)
        self.assertIn("voice summary ready: True", report)
        self.assertIn("voice interface available: False", report)
        self.assertIn("UI shell not built yet: True", report)
        self.assertIn("final user buy action required: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
