import unittest

from jarvis.jarvis_v6_1_policy_intelligence_boundary_report import (
    report_v6_1_policy_intelligence_boundary,
)


class JarvisV61PolicyIntelligenceBoundaryReportTests(unittest.TestCase):
    def test_report_contains_policy_boundary_and_safety(self) -> None:
        report = report_v6_1_policy_intelligence_boundary()

        self.assertIn("J.A.R.V.I.S. v6.1 Policy Intelligence Boundary", report)
        self.assertIn("status: JARVIS_V6_1_POLICY_INTELLIGENCE_BOUNDARY_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.2_private_portfolio_snapshot_v2", report)
        self.assertIn("balanced_aggressive_flexible_bands", report)
        self.assertIn("weekly crypto buy allowed if within risk bands: True", report)
        self.assertIn("global_all_world_etf", report)
        self.assertIn("quality_factor_etf", report)
        self.assertIn("manual approval required: True", report)
        self.assertIn("active policy mutated: False", report)
        self.assertIn("automatic policy change forbidden: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
