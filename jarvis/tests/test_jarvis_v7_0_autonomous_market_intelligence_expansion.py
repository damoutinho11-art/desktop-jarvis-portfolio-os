import unittest
from dataclasses import replace

from jarvis.jarvis_v7_0_autonomous_market_intelligence_expansion import (
    MARKET_STATE_BLOCKED,
    MARKET_STATE_SUPPORTIVE_WITH_CAUTION,
    SIGNAL_BLOCKING,
    SIGNAL_SUPPORTIVE,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_0_autonomous_market_intelligence_expansion,
)


class JarvisV70AutonomousMarketIntelligenceExpansionTests(unittest.TestCase):
    def test_market_intelligence_expansion_is_ready_and_points_to_adapter_contract(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_1_public_market_intelligence_adapter_contract")
        self.assertTrue(result.autonomous_market_intelligence_ready)
        self.assertTrue(result.selected_candidate_id)
        self.assertTrue(result.selected_sleeve_id)
        self.assertGreaterEqual(result.candidate_card_count, 3)
        self.assertGreaterEqual(result.total_signal_count, 4)
        self.assertFalse(result.blockers)

    def test_selected_candidate_receives_supportive_market_intelligence(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()

        self.assertEqual(result.selected_candidate_id, "btc_candidate")
        self.assertEqual(result.selected_candidate_market_state, MARKET_STATE_SUPPORTIVE_WITH_CAUTION)
        self.assertGreater(result.selected_candidate_market_score, 50)
        self.assertTrue(result.selected_candidate_supported)
        self.assertFalse(result.selected_candidate_blocked)

    def test_candidate_cards_are_non_executable(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()

        for card in result.candidate_cards:
            self.assertFalse(card.creates_buy_request)
            self.assertFalse(card.connects_broker)
            self.assertFalse(card.places_order)
            self.assertFalse(card.executes_trade)
            self.assertTrue(card.safe_card_only())

    def test_market_signals_are_non_executable(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()

        for card in result.candidate_cards:
            for signal in card.signals:
                self.assertFalse(signal.creates_buy_request)
                self.assertFalse(signal.connects_broker)
                self.assertFalse(signal.places_order)
                self.assertFalse(signal.executes_trade)
                self.assertTrue(signal.safe_signal_only())

    def test_selected_candidate_card_contains_supportive_and_caution_signals(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()
        selected_card = next(
            card for card in result.candidate_cards if card.candidate_id == result.selected_candidate_id
        )

        severities = {signal.severity for signal in selected_card.signals}
        self.assertIn(SIGNAL_SUPPORTIVE, severities)
        self.assertGreaterEqual(selected_card.caution_signal_count, 1)

    def test_blocking_signal_blocks_selected_candidate(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()
        selected_card = next(
            card for card in result.candidate_cards if card.candidate_id == result.selected_candidate_id
        )
        bad_signal = replace(
            selected_card.signals[0],
            severity=SIGNAL_BLOCKING,
            blocks_recommendation=True,
        )

        signals = tuple(
            bad_signal if signal.signal_id == bad_signal.signal_id else signal
            for card in result.candidate_cards
            for signal in card.signals
        )

        blocked = audit_v7_0_autonomous_market_intelligence_expansion(signals)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertEqual(blocked.selected_candidate_market_state, MARKET_STATE_BLOCKED)
        self.assertTrue(blocked.selected_candidate_blocked)
        self.assertTrue(any("Selected candidate is blocked" in blocker for blocker in blocked.blockers))

    def test_duplicate_signal_id_blocks(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()
        signals = tuple(signal for card in result.candidate_cards for signal in card.signals)
        blocked = audit_v7_0_autonomous_market_intelligence_expansion(signals + (signals[0],))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_unsafe_signal_blocks(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()
        signals = tuple(signal for card in result.candidate_cards for signal in card.signals)
        bad_signal = replace(
            signals[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )
        bad_signals = (bad_signal,) + signals[1:]

        blocked = audit_v7_0_autonomous_market_intelligence_expansion(bad_signals)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_empty_signals_block(self) -> None:
        blocked = audit_v7_0_autonomous_market_intelligence_expansion(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No autonomous market intelligence signals" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_0_autonomous_market_intelligence_expansion()
        payload = result.to_dict()

        self.assertTrue(payload["market_intelligence_only"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
