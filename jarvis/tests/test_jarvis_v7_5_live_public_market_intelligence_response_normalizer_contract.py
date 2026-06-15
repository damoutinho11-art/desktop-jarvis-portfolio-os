import unittest
from dataclasses import replace

from jarvis.jarvis_v7_0_autonomous_market_intelligence_expansion import SIGNAL_BLOCKING
from jarvis.jarvis_v7_5_live_public_market_intelligence_response_normalizer_contract import (
    NORMALIZER_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_5_live_public_market_intelligence_response_normalizer_contract,
)


class JarvisV75LivePublicMarketIntelligenceResponseNormalizerContractTests(unittest.TestCase):
    def test_response_normalizer_contract_is_ready_and_points_to_disabled_fetch_adapter(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.normalizer_status, NORMALIZER_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_6_disabled_live_public_market_fetch_adapter_skeleton")
        self.assertTrue(result.response_normalizer_contract_ready)
        self.assertTrue(result.compatible_with_v7_4_dry_run_planner)
        self.assertTrue(result.compatible_with_v7_1_adapter_contract)
        self.assertTrue(result.selected_candidate_supported)
        self.assertFalse(result.selected_candidate_blocked)
        self.assertGreaterEqual(result.normalization_input_count, 4)
        self.assertEqual(result.normalization_input_count, result.normalized_adapter_record_count)
        self.assertGreaterEqual(result.selected_candidate_normalized_record_count, 1)
        self.assertFalse(result.blockers)

    def test_normalization_inputs_do_not_store_raw_responses_or_call_network(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()

        for item in result.normalization_inputs:
            self.assertFalse(item.raw_response_payload_present)
            self.assertFalse(item.raw_response_stored)
            self.assertFalse(item.live_fetch_attempted)
            self.assertFalse(item.network_call_attempted)
            self.assertFalse(item.creates_buy_request)
            self.assertFalse(item.connects_broker)
            self.assertFalse(item.places_order)
            self.assertFalse(item.executes_trade)
            self.assertTrue(item.safe_normalization_input_only())

    def test_normalized_adapter_records_are_non_executable(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()

        for record in result.normalized_adapter_records:
            self.assertEqual(record.adapter_name, "jarvis_v7_5_response_normalizer_contract")
            self.assertFalse(record.live_fetch_attempted)
            self.assertFalse(record.creates_buy_request)
            self.assertFalse(record.connects_broker)
            self.assertFalse(record.places_order)
            self.assertFalse(record.executes_trade)
            self.assertTrue(record.safe_adapter_record_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_5_live_public_market_intelligence_response_normalizer_contract(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Normalization input override must be" in blocker for blocker in blocked.blockers))

    def test_empty_inputs_block(self) -> None:
        blocked = audit_v7_5_live_public_market_intelligence_response_normalizer_contract(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No public market response normalization inputs" in blocker for blocker in blocked.blockers))

    def test_duplicate_normalization_input_id_blocks(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
        blocked = audit_v7_5_live_public_market_intelligence_response_normalizer_contract(
            result.normalization_inputs + (result.normalization_inputs[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_raw_response_payload_or_storage_blocks(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
        bad = replace(
            result.normalization_inputs[0],
            raw_response_payload_present=True,
            raw_response_stored=True,
        )

        blocked = audit_v7_5_live_public_market_intelligence_response_normalizer_contract(
            (bad,) + result.normalization_inputs[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("raw response payload must not be present" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))

    def test_live_fetch_or_network_attempt_blocks(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
        bad = replace(
            result.normalization_inputs[0],
            live_fetch_attempted=True,
            network_call_attempted=True,
        )

        blocked = audit_v7_5_live_public_market_intelligence_response_normalizer_contract(
            (bad,) + result.normalization_inputs[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))

    def test_unsafe_normalization_input_blocks(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
        bad = replace(
            result.normalization_inputs[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_5_live_public_market_intelligence_response_normalizer_contract(
            (bad,) + result.normalization_inputs[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_blocking_selected_candidate_blocks_contract(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
        selected_inputs = [
            item for item in result.normalization_inputs if item.candidate_id == result.selected_candidate_id
        ]
        bad = replace(
            selected_inputs[0],
            severity=SIGNAL_BLOCKING,
            blocks_recommendation=True,
        )
        inputs = tuple(
            bad if item.normalization_input_id == bad.normalization_input_id else item
            for item in result.normalization_inputs
        )

        blocked = audit_v7_5_live_public_market_intelligence_response_normalizer_contract(inputs)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(blocked.selected_candidate_blocked)
        self.assertTrue(any("block the selected weekly candidate" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
        payload = result.to_dict()

        self.assertTrue(payload["contract_only"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["raw_response_storage_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
