import unittest

from jarvis.jarvis_v6_personal_finance_command_center_audit import (
    CAPABILITY_MISSING,
    CAPABILITY_PARTIAL,
    CAPABILITY_READY,
    STATUS_READY,
    audit_jarvis_v6_personal_finance_command_center,
)


class JarvisV6PersonalFinanceCommandCenterAuditTests(unittest.TestCase):
    def test_audit_marks_foundation_ready_and_next_stage_policy_intelligence(self) -> None:
        result = audit_jarvis_v6_personal_finance_command_center()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.release_anchor, "v5.11-coingecko-raw-fixture-transformer-safe")
        self.assertEqual(result.recommended_next_stage, "v6.1_policy_intelligence_boundary")
        self.assertEqual(result.capability_count, 9)
        self.assertGreaterEqual(result.ready_count, 2)
        self.assertGreaterEqual(result.partial_count, 3)
        self.assertGreaterEqual(result.missing_count, 2)
        self.assertFalse(result.blockers)

    def test_public_data_foundation_is_ready(self) -> None:
        result = audit_jarvis_v6_personal_finance_command_center()
        capabilities = {capability.capability_id: capability for capability in result.capabilities}

        public_data = capabilities["public_data_foundation"]

        self.assertEqual(public_data.status, CAPABILITY_READY)
        self.assertTrue(public_data.wired_to_current_system)
        self.assertIn("jarvis/dynamic_market_raw_cache_normalizer.py", public_data.existing_files)
        self.assertIn("jarvis/dynamic_coingecko_market_chart_transformer.py", public_data.existing_files)

    def test_policy_intelligence_is_the_next_missing_build(self) -> None:
        result = audit_jarvis_v6_personal_finance_command_center()
        capabilities = {capability.capability_id: capability for capability in result.capabilities}

        policy = capabilities["policy_intelligence"]

        self.assertEqual(policy.status, CAPABILITY_MISSING)
        self.assertEqual(policy.classification, "NEXT_BUILD")
        self.assertEqual(policy.next_stage, "v6.1_policy_intelligence_boundary")
        self.assertTrue(
            any("Candidate policy generator" in item for item in policy.missing_requirements)
        )
        self.assertTrue(
            any("Flexible allocation bands" in item for item in policy.missing_requirements)
        )

    def test_private_portfolio_and_weekly_buy_layers_are_partial_not_rebuilt(self) -> None:
        result = audit_jarvis_v6_personal_finance_command_center()
        capabilities = {capability.capability_id: capability for capability in result.capabilities}

        self.assertEqual(capabilities["private_portfolio_wing"].status, CAPABILITY_PARTIAL)
        self.assertEqual(capabilities["manual_weekly_buy_planner"].status, CAPABILITY_PARTIAL)
        self.assertIn(
            "jarvis/portfolio_snapshot_engine.py",
            capabilities["private_portfolio_wing"].existing_files,
        )
        self.assertIn(
            "jarvis/dynamic_allocation_weekly_plan.py",
            capabilities["manual_weekly_buy_planner"].existing_files,
        )

    def test_v6_product_boundary_requires_broad_universe_and_flexible_bands(self) -> None:
        result = audit_jarvis_v6_personal_finance_command_center()

        self.assertTrue(result.broad_universe_scan_required)
        self.assertTrue(result.flexible_policy_bands_required)
        self.assertTrue(result.policy_intelligence_required)
        self.assertTrue(result.weekly_crypto_buy_allowed_if_within_risk_bands)

    def test_safety_flags_forbid_autonomous_execution_and_policy_changes(self) -> None:
        result = audit_jarvis_v6_personal_finance_command_center()
        payload = result.to_dict()

        self.assertTrue(payload["manual_policy_approval_required"])
        self.assertTrue(payload["manual_buy_execution_only"])
        self.assertTrue(payload["automatic_policy_change_forbidden"])
        self.assertTrue(payload["automatic_approval_forbidden"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
