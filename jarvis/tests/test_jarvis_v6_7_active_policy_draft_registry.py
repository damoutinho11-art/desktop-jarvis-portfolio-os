import unittest
from dataclasses import replace

from jarvis.jarvis_v6_7_active_policy_draft_registry import (
    DRAFT_STATUS_MANUAL_APPROVAL_REQUIRED,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_7_active_policy_draft_registry,
)


class JarvisV67ActivePolicyDraftRegistryTests(unittest.TestCase):
    def test_draft_registry_is_ready_and_points_to_manual_approval_gate(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.8_active_policy_manual_approval_gate")
        self.assertTrue(result.active_policy_draft_registry_ready)
        self.assertEqual(result.source_review_item_count, 4)
        self.assertEqual(result.accepted_review_count, 1)
        self.assertEqual(result.active_policy_draft_count, 1)
        self.assertEqual(result.active_policy_count, 0)
        self.assertFalse(result.blockers)

    def test_draft_is_created_only_from_accepted_review(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        draft = result.draft_items[0]

        self.assertEqual(draft.source_policy_id, "balanced_aggressive_manual_review")
        self.assertEqual(draft.source_review_id, "review_balanced_aggressive_manual_review")
        self.assertEqual(draft.draft_status, DRAFT_STATUS_MANUAL_APPROVAL_REQUIRED)

    def test_draft_carries_policy_bands_and_assets(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        draft = result.draft_items[0]

        self.assertTrue(draft.allocation_bands)
        self.assertTrue(draft.selected_assets)
        self.assertTrue(draft.has_valid_bands())
        self.assertIn("global_all_world_etf_candidate", draft.selected_candidate_ids())
        self.assertIn("btc_candidate", draft.selected_candidate_ids())
        self.assertIn("money_market_candidate", draft.selected_candidate_ids())

    def test_draft_has_risk_constraints_and_activation_requirements(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        draft = result.draft_items[0]

        self.assertTrue(draft.risk_constraints)
        self.assertTrue(draft.activation_requirements)
        self.assertTrue(any("Crypto maximum" in item for item in draft.risk_constraints))
        self.assertTrue(any("Operator must review" in item for item in draft.activation_requirements))

    def test_draft_does_not_approve_activate_buy_or_execute(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        draft = result.draft_items[0]

        self.assertTrue(draft.manual_approval_required)
        self.assertFalse(draft.operator_approved_active_policy)
        self.assertFalse(draft.active_policy_created)
        self.assertFalse(draft.active_policy_mutated)
        self.assertFalse(draft.asset_approval_created)
        self.assertFalse(draft.creates_weekly_buy_ticket)
        self.assertFalse(draft.creates_buy_request)
        self.assertFalse(draft.executes_trade)
        self.assertTrue(draft.safe_draft_only())

    def test_crypto_ceiling_and_defensive_floor_are_enforced(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        draft = result.draft_items[0]

        self.assertLessEqual(draft.max_crypto_weight_pct(), 35.0)
        self.assertGreaterEqual(draft.min_defensive_weight_pct(), 3.0)

    def test_unsafe_draft_blocks(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        bad = replace(
            result.draft_items[0],
            operator_approved_active_policy=True,
            active_policy_created=True,
            active_policy_mutated=True,
            asset_approval_created=True,
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            executes_trade=True,
        )

        blocked = audit_v6_7_active_policy_draft_registry((bad,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("active policy approval is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("active policy creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("active policy mutation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("asset approval is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("weekly buy ticket creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_draft_id_blocks(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        duplicate = replace(result.draft_items[0], display_name="Duplicate")

        blocked = audit_v6_7_active_policy_draft_registry(result.draft_items + (duplicate,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_safety_flags_defer_approval_activation_buy_request_and_execution(self) -> None:
        result = audit_v6_7_active_policy_draft_registry()
        payload = result.to_dict()

        self.assertTrue(payload["draft_only"])
        self.assertTrue(payload["manual_approval_required"])
        self.assertTrue(payload["active_policy_approval_deferred"])
        self.assertTrue(payload["active_policy_activation_deferred"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
