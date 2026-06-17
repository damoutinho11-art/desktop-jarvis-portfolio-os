import unittest

from jarvis.jarvis_v10_0_autonomous_public_data_refresh_runtime_report import (
    report_v10_0_autonomous_public_data_refresh_runtime,
)


class JarvisV100AutonomousPublicDataRefreshRuntimeReportTests(unittest.TestCase):
    def test_report_contains_runtime_and_safety(self) -> None:
        report = report_v10_0_autonomous_public_data_refresh_runtime()

        self.assertIn("J.A.R.V.I.S. v10.0 Autonomous Public Data Refresh Runtime", report)
        self.assertIn("status: JARVIS_V10_0_AUTONOMOUS_PUBLIC_DATA_REFRESH_RUNTIME_READY_SAFE", report)
        self.assertIn("runtime status: AUTONOMOUS_PUBLIC_DATA_REFRESH_RUNTIME_READY", report)
        self.assertIn("recommended next stage: v10_1_unified_operator_runtime", report)
        self.assertIn("source manifest loaded:", report)
        self.assertIn("demo manifest used:", report)
        self.assertIn("execute fetch requested: False", report)
        self.assertIn("source count: 1", report)
        self.assertIn("valid source count: 1", report)
        self.assertIn("blocked source count: 0", report)
        self.assertIn("runtime contract ready: True", report)
        self.assertIn("ready for downstream normalization: True", report)
        self.assertIn("recommendation quality current data: False", report)
        self.assertIn("local cache only: True", report)
        self.assertIn("source selection not repeated: True", report)
        self.assertIn("dry-run planner not rebuilt: True", report)
        self.assertIn("provider registry not rebuilt: True", report)
        self.assertIn("final user buy action required: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
