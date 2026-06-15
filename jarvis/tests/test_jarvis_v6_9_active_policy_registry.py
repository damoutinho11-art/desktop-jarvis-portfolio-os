import unittest
from dataclasses import replace

from jarvis.jarvis_v6_9_active_policy_registry import (
    ACTIVE_POLICY_STATUS_ACTIVE_MANUAL_ONLY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_9_active_policy_registry,
)


class JarvisV69ActivePolicyRegistryTests(unittest.TestCase):
    def test_active_policy_registry_is_ready_and_points_to_gap_analyzer(self) -> None:
        result = audit_v6_9_active_policy_registry()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.10_active_policy_snapshot_gap_analyzer")
        self.assertTrue(result.active_policy_registry_ready)
        self.assertEqual(result.source_draft_count, 1)
        self.assertEqual(result.source_approval_decision_count, 1)
        self.assertEqual(result.approved_draft_count, 1)
        self.assertEqual(result.active_policy_count, 1)
        self.assertFalse(result.blockers)

    def test_active_policy_record_is_created_from_manual_approval(self) -> None:
        result = audit_v6_9_active_policy_registry()
        policy = result.active_policies[0]

        self.assertEqual(policy.active_policy_id, "active_balanced_aggressive_manual_review")
        self.assertEqual(policy.source_approval_id, "approval_draft_balanced_aggressive_manual_review")
        self.assertEqual(policy.source_draft_id, "draft_balanced_aggressive_manual_review")
        self.assertEqual(policy.policy_status, ACTIVE_POLICY_STATUS_ACTIVE_MANUAL_ONLY)
        self.assertTrue(policy.manually_approved)
        self.assertTrue(policy.active_policy_created)

    def test_active_policy_preserves_bands_and_assets(self) -> None:
        result = audit_v6_9_active_policy_registry()
        policy = result.active_policies[0]

        self.assertTrue(policy.allocation_bands)
        self.assertTrue(policy.selected_assets)
        self.assertTrue(policy.has_valid_bands())
        self.assertIn("global_all_world_etf_candidate", policy.selected_candidate_ids())
        self.assertIn("btc_candidate", policy.selected_candidate_ids())
        self.assertIn("money_market_candidate", policy.selected_candidate_ids())

    def test_active_policy_has_constraints_and_monitoring_rules(self) -> None:
        result = audit_v6_9_active_policy_registry()
        policy = result.active_policies[0]

        self.assertTrue(policy.policy_constraints)
        self.assertTrue(policy.monitoring_rules)
        self.assertTrue(any("Protected cash" in item for item in policy.policy_constraints))
        self.assertTrue(any("Monitor portfolio sleeve weights" in item for item in policy.monitoring_rules))

    def test_active_policy_does_not_create_buy_request_broker_or_trade(self) -> None:
        result = audit_v6_9_active_policy_registry()
        policy = result.active_policies[0]

        self.assertFalse(policy.automatic_policy_change_allowed)
        self.assertFalse(policy.assets_individually_approved)
        self.assertFalse(policy.creates_weekly_buy_ticket)
        self.assertFalse(policy.creates_buy_request)
        self.assertFalse(policy.connects_broker)
        self.assertFalse(policy.executes_trade)
        self.assertTrue(policy.safe_active_policy_record_only())

    def test_crypto_ceiling_and_defensive_floor_are_enforced(self) -> None:
        result = audit_v6_9_active_policy_registry()
        policy = result.active_policies[0]

        self.assertLessEqual(policy.max_crypto_weight_pct(), 35.0)
        self.assertGreaterEqual(policy.min_defensive_weight_pct(), 3.0)

    def test_empty_active_policy_registry_blocks(self) -> None:
        blocked = audit_v6_9_active_policy_registry(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No active policy registry record" in blocker for blocker in blocked.blockers))

    def test_unsafe_active_policy_blocks(self) -> None:
        result = audit_v6_9_active_policy_registry()
        bad = replace(
            result.active_policies[0],
            automatic_policy_change_allowed=True,
            assets_individually_approved=True,
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            connects_broker=True,
            executes_trade=True,
        )

        blocked = audit_v6_9_active_policy_registry((bad,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("automatic policy change is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("asset approval is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("weekly buy ticket creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_active_policy_id_blocks(self) -> None:
        result = audit_v6_9_active_policy_registry()
        duplicate = replace(result.active_policies[0], display_name="Duplicate")

        blocked = audit_v6_9_active_policy_registry(result.active_policies + (duplicate,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_safety_flags_defer_asset_buy_request_and_execution(self) -> None:
        result = audit_v6_9_active_policy_registry()
        payload = result.to_dict()

        self.assertTrue(payload["active_policy_record_created"])
        self.assertTrue(payload["manual_approval_satisfied"])
        self.assertTrue(payload["automatic_policy_change_forbidden"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
