import unittest
from dataclasses import replace

from jarvis.jarvis_v6_6_manual_policy_review_queue import (
    DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW,
    DECISION_DEFER,
    DECISION_NEEDS_CORRECTION,
    DECISION_REJECT,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_6_manual_policy_review_queue,
)


class JarvisV66ManualPolicyReviewQueueTests(unittest.TestCase):
    def test_review_queue_is_ready_and_points_to_active_policy_draft_registry(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.7_active_policy_draft_registry")
        self.assertTrue(result.manual_policy_review_queue_ready)
        self.assertEqual(result.source_policy_candidate_count, 4)
        self.assertEqual(result.review_item_count, 4)
        self.assertFalse(result.blockers)

    def test_all_manual_decision_states_are_present(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()
        decisions = {item.decision for item in result.review_items}

        self.assertEqual(
            decisions,
            {
                DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW,
                DECISION_DEFER,
                DECISION_REJECT,
                DECISION_NEEDS_CORRECTION,
            },
        )
        self.assertEqual(result.accept_for_active_policy_review_count, 1)
        self.assertEqual(result.defer_count, 1)
        self.assertEqual(result.reject_count, 1)
        self.assertEqual(result.needs_correction_count, 1)

    def test_accept_for_active_policy_review_does_not_activate_or_approve(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()
        accepted = next(
            item
            for item in result.review_items
            if item.decision == DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW
        )

        self.assertTrue(accepted.manual_review_recorded)
        self.assertFalse(accepted.creates_active_policy)
        self.assertFalse(accepted.operator_approved_active_policy)
        self.assertFalse(accepted.creates_weekly_buy_ticket)
        self.assertFalse(accepted.creates_buy_request)
        self.assertFalse(accepted.executes_trade)

    def test_needs_correction_item_has_required_corrections(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()
        needs_correction = next(
            item
            for item in result.review_items
            if item.decision == DECISION_NEEDS_CORRECTION
        )

        self.assertTrue(needs_correction.required_corrections)
        self.assertTrue(needs_correction.requires_corrections())

    def test_bad_review_item_blocks_unsafe_actions(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()
        bad = replace(
            result.review_items[0],
            creates_active_policy=True,
            operator_approved_active_policy=True,
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            executes_trade=True,
        )

        blocked = audit_v6_6_manual_policy_review_queue((bad,) + result.review_items[1:])

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("active policy creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("active policy approval is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("weekly buy ticket creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_review_policy_id_blocks(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()
        duplicate = replace(result.review_items[0], review_id="duplicate_review")

        blocked = audit_v6_6_manual_policy_review_queue(result.review_items + (duplicate,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_missing_correction_detail_blocks(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()
        bad = next(
            item
            for item in result.review_items
            if item.decision == DECISION_NEEDS_CORRECTION
        )
        bad = replace(bad, required_corrections=())
        others = tuple(item for item in result.review_items if item.policy_id != bad.policy_id)

        blocked = audit_v6_6_manual_policy_review_queue((bad,) + others)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("required corrections are missing" in blocker for blocker in blocked.blockers))

    def test_safety_flags_defer_approval_buy_request_and_execution(self) -> None:
        result = audit_v6_6_manual_policy_review_queue()
        payload = result.to_dict()

        self.assertTrue(payload["manual_review_records_only"])
        self.assertTrue(payload["active_policy_creation_deferred"])
        self.assertTrue(payload["policy_approval_deferred"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
