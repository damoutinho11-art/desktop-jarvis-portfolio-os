import unittest

from jarvis.jarvis_v7_9_public_provider_skeleton_binding_audit_report import (
    report_v7_9_public_provider_skeleton_binding_audit,
)


class JarvisV79PublicProviderSkeletonBindingAuditReportTests(unittest.TestCase):
    def test_report_contains_binding_audit_and_safety(self) -> None:
        report = report_v7_9_public_provider_skeleton_binding_audit()

        self.assertIn("J.A.R.V.I.S. v7.9 Public Provider Skeleton Binding Audit", report)
        self.assertIn("status: JARVIS_V7_9_PUBLIC_PROVIDER_SKELETON_BINDING_AUDIT_READY_SAFE", report)
        self.assertIn("binding status: PUBLIC_PROVIDER_SKELETON_BINDING_AUDIT_READY", report)
        self.assertIn("recommended next stage: v7_10_live_public_market_intelligence_readiness_closeout_audit", report)
        self.assertIn("unbound skeleton count: 0", report)
        self.assertIn("provider disabled binding count:", report)
        self.assertIn("adapter disabled binding count:", report)
        self.assertIn("live fetch enabled count: 0", report)
        self.assertIn("network call allowed count: 0", report)
        self.assertIn("raw response storage allowed count: 0", report)
        self.assertIn("live adapter record emission allowed count: 0", report)
        self.assertIn("provider disabled by default: True", report)
        self.assertIn("adapter disabled: True", report)
        self.assertIn("endpoint category match: True", report)
        self.assertIn("binding ready: True", report)
        self.assertIn("live fetch enabled: False", report)
        self.assertIn("network call allowed: False", report)
        self.assertIn("raw response storage allowed: False", report)
        self.assertIn("live adapter record emission allowed: False", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("binding audit ready: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
