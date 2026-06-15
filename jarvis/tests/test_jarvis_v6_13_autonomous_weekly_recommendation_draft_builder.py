import unittest
from dataclasses import replace

from jarvis.jarvis_v6_13_autonomous_weekly_recommendation_draft_builder import (
    DECISION_BUY_CANDIDATE,
    RECOMMENDATION_STATUS_DRAFT_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_13_autonomous_weekly_recommendation_draft_builder,
)


class JarvisV613AutonomousWeeklyRecommendationDraftBuilderTests(unittest.TestCase):
    def test_recommendation_builder_is_ready_and_points_to_dashboard_integration(self) -> None:
        result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.14_recommendation_dashboard_integration")
        self.assertTrue(result.autonomous_recommendation_ready)
        self.assertEqual(result.recommendation_count, 1)
        self.assertTrue(result.selected_candidate_id)
        self.assertFalse(result.blockers)

    def test_recommendation_is_autonomous_draft_not_order(self) -> None:
        result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()
        rec = result.recommendation
        assert rec is not None

        self.assertEqual(rec.recommendation_status, RECOMMENDATION_STATUS_DRAFT_READY)
        self.assertEqual(rec.decision, DECISION_BUY_CANDIDATE)
        self.assertTrue(rec.final_user_action_required)
        self.assertFalse(rec.creates_buy_request)
        self.assertFalse(rec.connects_broker)
        self.assertFalse(rec.places_order)
        self.assertFalse(rec.executes_trade)
        self.assertTrue(rec.safe_recommendation_draft_only())

    def test_recommendation_contains_reasoning_amount_logic_and_manual_instructions(self) -> None:
        result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()
        rec = result.recommendation
        assert rec is not None

        self.assertTrue(rec.primary_reason)
        self.assertTrue(rec.supporting_reasons)
        self.assertTrue(rec.suggested_manual_amount_logic)
        self.assertTrue(rec.risk_warnings)
        self.assertTrue(rec.manual_buy_instructions)
        self.assertIn("Protected cash", rec.suggested_manual_amount_logic)

    def test_only_final_user_buy_is_manual(self) -> None:
        result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()
        rec = result.recommendation
        assert rec is not None

        instructions = " ".join(rec.manual_buy_instructions)
        self.assertIn("Place the real-world buy manually", instructions)
        self.assertTrue(result.final_user_buy_action_required)

    def test_unsafe_recommendation_blocks(self) -> None:
        result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()
        rec = result.recommendation
        assert rec is not None

        bad = replace(
            rec,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v6_13_autonomous_weekly_recommendation_draft_builder(bad)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("Broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("Order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("Trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_missing_recommendation_blocks(self) -> None:
        blocked = audit_v6_13_autonomous_weekly_recommendation_draft_builder(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()
        payload = result.to_dict()

        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
