import unittest
from dataclasses import replace

from jarvis.jarvis_v8_0_public_market_intelligence_operator_dashboard import (
    DASHBOARD_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v8_0_public_market_intelligence_operator_dashboard,
)


class JarvisV80PublicMarketIntelligenceOperatorDashboardTests(unittest.TestCase):
    def test_operator_dashboard_is_ready_and_points_to_research_cycle_panel(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.dashboard_status, DASHBOARD_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v8_1_autonomous_research_cycle_status_panel")
        self.assertTrue(result.operator_dashboard_ready)
        self.assertTrue(result.compatible_with_v7_10_readiness_closeout)
        self.assertGreaterEqual(result.card_count, 6)
        self.assertEqual(result.user_visible_card_count, result.card_count)
        self.assertEqual(result.blocked_card_count, 0)
        self.assertEqual(result.live_fetch_enabled_card_count, 0)
        self.assertEqual(result.network_call_enabled_card_count, 0)
        self.assertEqual(result.raw_response_storage_enabled_card_count, 0)
        self.assertEqual(result.live_adapter_record_emission_enabled_card_count, 0)
        self.assertFalse(result.blockers)

    def test_required_dashboard_cards_exist(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()
        card_ids = {card.card_id for card in result.cards}

        self.assertIn("v7_public_market_chain_closeout", card_ids)
        self.assertIn("selected_candidate_public_intelligence_coverage", card_ids)
        self.assertIn("provider_registry_and_binding_readiness", card_ids)
        self.assertIn("live_fetch_disabled_status", card_ids)
        self.assertIn("network_and_raw_storage_status", card_ids)
        self.assertIn("execution_safety_boundary", card_ids)

    def test_dashboard_cards_are_user_visible_and_non_executable(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()

        for card in result.cards:
            self.assertTrue(card.user_visible)
            self.assertFalse(card.live_fetch_enabled)
            self.assertFalse(card.network_call_enabled)
            self.assertFalse(card.raw_response_storage_enabled)
            self.assertFalse(card.live_adapter_record_emission_enabled)
            self.assertFalse(card.creates_buy_request)
            self.assertFalse(card.connects_broker)
            self.assertFalse(card.places_order)
            self.assertFalse(card.executes_trade)
            self.assertTrue(card.safe_dashboard_card_only())

    def test_dashboard_exposes_key_visibility_categories(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()

        self.assertTrue(result.v7_chain_closeout_visible)
        self.assertTrue(result.selected_candidate_visible)
        self.assertTrue(result.provider_readiness_visible)
        self.assertTrue(result.disabled_live_fetch_visible)
        self.assertTrue(result.execution_safety_visible)

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v8_0_public_market_intelligence_operator_dashboard(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Dashboard card override must be" in blocker for blocker in blocked.blockers))

    def test_empty_cards_block(self) -> None:
        blocked = audit_v8_0_public_market_intelligence_operator_dashboard(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No public market intelligence dashboard cards" in blocker for blocker in blocked.blockers))

    def test_duplicate_card_id_blocks(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()
        blocked = audit_v8_0_public_market_intelligence_operator_dashboard(
            result.cards + (result.cards[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_missing_required_card_blocks(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()
        cards = tuple(card for card in result.cards if card.card_id != "execution_safety_boundary")

        blocked = audit_v8_0_public_market_intelligence_operator_dashboard(cards)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must include all required" in blocker for blocker in blocked.blockers))

    def test_hidden_or_unsafe_card_blocks(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()
        bad = replace(
            result.cards[0],
            user_visible=False,
            live_fetch_enabled=True,
            network_call_enabled=True,
            raw_response_storage_enabled=True,
            live_adapter_record_emission_enabled=True,
        )

        blocked = audit_v8_0_public_market_intelligence_operator_dashboard(
            (bad,) + result.cards[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must be user-visible" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))

    def test_execution_fields_block(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()
        bad = replace(
            result.cards[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v8_0_public_market_intelligence_operator_dashboard(
            (bad,) + result.cards[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v8_0_public_market_intelligence_operator_dashboard()
        payload = result.to_dict()

        self.assertTrue(payload["dashboard_visibility_only"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["raw_response_storage_deferred"])
        self.assertTrue(payload["live_adapter_record_emission_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
