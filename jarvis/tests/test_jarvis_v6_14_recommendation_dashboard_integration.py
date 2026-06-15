import unittest
from dataclasses import replace

from jarvis.jarvis_v6_14_recommendation_dashboard_integration import (
    CARD_ID_MANUAL_ACTION,
    CARD_ID_SAFETY_BOUNDARY,
    CARD_ID_WEEKLY_RECOMMENDATION,
    DASHBOARD_CARD_STATUS_VISIBLE,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_14_recommendation_dashboard_integration,
)


class JarvisV614RecommendationDashboardIntegrationTests(unittest.TestCase):
    def test_dashboard_integration_is_ready_and_points_to_closeout_audit(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.15_autonomous_command_center_closeout_audit")
        self.assertTrue(result.dashboard_integration_ready)
        self.assertTrue(result.autonomous_recommendation_displayed)
        self.assertTrue(result.selected_candidate_id)
        self.assertEqual(result.dashboard_card_count, 3)
        self.assertFalse(result.blockers)

    def test_dashboard_contains_required_cards(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.dashboard_payload
        assert payload is not None

        card_ids = {card.card_id for card in payload.cards}
        self.assertIn(CARD_ID_WEEKLY_RECOMMENDATION, card_ids)
        self.assertIn(CARD_ID_SAFETY_BOUNDARY, card_ids)
        self.assertIn(CARD_ID_MANUAL_ACTION, card_ids)

    def test_dashboard_surfaces_autonomous_recommendation(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.dashboard_payload
        assert payload is not None

        self.assertEqual(payload.dashboard_status, DASHBOARD_CARD_STATUS_VISIBLE)
        self.assertIn(result.selected_candidate_id, payload.headline)
        self.assertTrue(payload.confidence_score >= 0)

    def test_dashboard_cards_are_display_only(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.dashboard_payload
        assert payload is not None

        self.assertFalse(payload.creates_buy_request)
        self.assertFalse(payload.connects_broker)
        self.assertFalse(payload.places_order)
        self.assertFalse(payload.executes_trade)
        self.assertTrue(payload.safe_dashboard_only())

        for card in payload.cards:
            self.assertFalse(card.creates_buy_request)
            self.assertFalse(card.connects_broker)
            self.assertFalse(card.places_order)
            self.assertFalse(card.executes_trade)
            self.assertTrue(card.safe_display_only())

    def test_only_manual_action_card_requires_user_buy(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.dashboard_payload
        assert payload is not None

        manual_card = next(card for card in payload.cards if card.card_id == CARD_ID_MANUAL_ACTION)
        self.assertTrue(manual_card.user_action_required)
        self.assertIn("outside J.A.R.V.I.S.", manual_card.action_label)

    def test_safety_boundary_card_is_present(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.dashboard_payload
        assert payload is not None

        safety_card = next(card for card in payload.cards if card.card_id == CARD_ID_SAFETY_BOUNDARY)
        details = " ".join(safety_card.details)

        self.assertIn("No buy request", details)
        self.assertIn("No broker connection", details)
        self.assertIn("No order placement", details)
        self.assertIn("No trade execution", details)

    def test_invalid_dashboard_override_blocks_safely(self) -> None:
        blocked = audit_v6_14_recommendation_dashboard_integration(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Dashboard override must be" in blocker for blocker in blocked.blockers))

    def test_unsafe_dashboard_blocks(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.dashboard_payload
        assert payload is not None

        bad_payload = replace(
            payload,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v6_14_recommendation_dashboard_integration(bad_payload)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_card_id_blocks(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.dashboard_payload
        assert payload is not None

        duplicate_payload = replace(payload, cards=payload.cards + (payload.cards[0],))
        blocked = audit_v6_14_recommendation_dashboard_integration(duplicate_payload)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v6_14_recommendation_dashboard_integration()
        payload = result.to_dict()

        self.assertTrue(payload["dashboard_only"])
        self.assertTrue(payload["autonomous_recommendation_displayed"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
