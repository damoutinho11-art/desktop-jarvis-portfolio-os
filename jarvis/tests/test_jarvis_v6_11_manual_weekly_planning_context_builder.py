import unittest
from dataclasses import replace

from jarvis.jarvis_v6_11_manual_weekly_planning_context_builder import (
    CONTEXT_ACTION_AVOID_ADDITIONAL_EXPOSURE,
    CONTEXT_ACTION_CONSIDER_FUTURE_ALLOCATION,
    CONTEXT_PRIORITY_CRITICAL,
    CONTEXT_PRIORITY_HIGH,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_11_manual_weekly_planning_context_builder,
)


class JarvisV611ManualWeeklyPlanningContextBuilderTests(unittest.TestCase):
    def test_context_builder_is_ready_and_points_to_shortlist_builder(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.12_manual_weekly_candidate_shortlist_builder")
        self.assertTrue(result.weekly_planning_context_ready)
        self.assertEqual(result.analyzed_policy_id, "active_balanced_aggressive_manual_review")
        self.assertEqual(result.source_sleeve_gap_count, 6)
        self.assertEqual(result.planning_context_item_count, 6)
        self.assertFalse(result.blockers)

    def test_context_priorities_include_critical_and_high(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()

        self.assertGreaterEqual(result.critical_priority_count, 1)
        self.assertGreaterEqual(result.high_priority_count, 1)

        priorities = {item.priority for item in result.planning_items}
        self.assertIn(CONTEXT_PRIORITY_CRITICAL, priorities)
        self.assertIn(CONTEXT_PRIORITY_HIGH, priorities)

    def test_btc_context_considers_future_allocation_with_crypto_guard(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()
        by_sleeve = {item.sleeve_id: item for item in result.planning_items}

        btc = by_sleeve["crypto_core_btc"]
        self.assertEqual(btc.context_action, CONTEXT_ACTION_CONSIDER_FUTURE_ALLOCATION)
        self.assertTrue(btc.crypto_ceiling_guard_active)
        self.assertTrue(btc.protected_cash_guard_active)
        self.assertTrue(btc.investable_cash_considered)

    def test_cash_over_max_context_avoids_additional_exposure(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()
        by_sleeve = {item.sleeve_id: item for item in result.planning_items}

        cash = by_sleeve["cash_defensive"]
        self.assertEqual(cash.context_action, CONTEXT_ACTION_AVOID_ADDITIONAL_EXPOSURE)
        self.assertTrue(cash.protected_cash_guard_active)

    def test_context_does_not_create_buy_ticket_request_or_trade(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()

        for item in result.planning_items:
            self.assertFalse(item.creates_weekly_buy_ticket)
            self.assertFalse(item.creates_buy_request)
            self.assertFalse(item.executes_trade)
            self.assertTrue(item.safe_context_only())

    def test_manual_planning_notes_preserve_safety(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()
        notes = " ".join(result.manual_planning_notes)

        self.assertIn("Protected cash is not investable", notes)
        self.assertIn("No weekly buy ticket exists", notes)

    def test_empty_context_blocks(self) -> None:
        blocked = audit_v6_11_manual_weekly_planning_context_builder(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No manual planning context items" in blocker for blocker in blocked.blockers))

    def test_unsafe_context_blocks(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()
        bad = replace(
            result.planning_items[0],
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            executes_trade=True,
        )

        blocked = audit_v6_11_manual_weekly_planning_context_builder(
            (bad,) + result.planning_items[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("weekly buy ticket creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_context_id_blocks(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()
        duplicate = replace(result.planning_items[0], sleeve_id=result.planning_items[1].sleeve_id)

        blocked = audit_v6_11_manual_weekly_planning_context_builder(
            result.planning_items + (duplicate,)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_safety_flags_defer_asset_buy_request_and_execution(self) -> None:
        result = audit_v6_11_manual_weekly_planning_context_builder()
        payload = result.to_dict()

        self.assertTrue(payload["context_only"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
