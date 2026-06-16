import unittest

from jarvis.jarvis_v9_1_capability_map_and_roadmap_lock_report import (
    report_v9_1_capability_map_and_roadmap_lock,
)


class JarvisV91CapabilityMapAndRoadmapLockReportTests(unittest.TestCase):
    def test_report_contains_lock_and_redundancy_controls(self) -> None:
        report = report_v9_1_capability_map_and_roadmap_lock()

        self.assertIn("J.A.R.V.I.S. v9.1 Capability Map and Roadmap Lock", report)
        self.assertIn("status: JARVIS_V9_1_CAPABILITY_MAP_AND_ROADMAP_LOCK_READY_SAFE", report)
        self.assertIn("roadmap lock status: CAPABILITY_MAP_AND_ROADMAP_LOCK_READY", report)
        self.assertIn("recommended next stage: operator_architecture_review_before_next_public_data_capability", report)
        self.assertIn("stale roadmap reference count: 0", report)
        self.assertIn("v7_4_live_public_dry_run_planner", report)
        self.assertIn("v7_8_provider_configuration_registry", report)
        self.assertIn("dynamic_market_source_binding", report)
        self.assertIn("v9_0_enablement_decision_layer", report)
        self.assertIn("source selection not repeated: True", report)
        self.assertIn("dry-run planner not rebuilt: True", report)
        self.assertIn("provider registry not rebuilt: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
